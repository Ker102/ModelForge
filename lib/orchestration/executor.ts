import { randomUUID } from "crypto"

import { createBlenderAgent, type AgentLog } from "@/lib/ai/agents"
import { type Plan, type PlanStep, generateCode } from "@/lib/ai/chains"
import { similaritySearch } from "@/lib/ai/vectorstore"
import { formatContextFromSources } from "@/lib/ai/rag"
import { createGeminiModel } from "@/lib/ai"
import { type LlmProviderSpec } from "@/lib/llm"
import { createMcpClient, getViewportScreenshot, type McpCommand } from "@/lib/mcp"
import { suggestImprovements } from "@/lib/ai/vision"
import { ExecutionLogEntry, ExecutionPlan, PlanAnalysis, AgentStreamEvent } from "./types"
import type { StrategyDecision } from "./strategy-types"

export interface ExecutionResult {
  success: boolean
  completedSteps: Array<{ step: PlanStep; result: unknown }>
  failedSteps: Array<{ step: PlanStep; error: string }>
  finalSceneState?: unknown
  logs: ExecutionLogEntry[]
}

const HYPER3D_TOOLS = new Set([
  "get_hyper3d_status",
  "create_rodin_job",
  "poll_rodin_job_status",
  "import_generated_asset",
])

const SKETCHFAB_TOOLS = new Set([
  "get_sketchfab_status",
  "search_sketchfab_models",
  "download_sketchfab_model",
])

const POLYHAVEN_TOOLS = new Set([
  "get_polyhaven_status",
  "search_polyhaven_assets",
  "download_polyhaven_asset",
])

export interface ExecutionOptions {
  allowHyper3d: boolean
  allowSketchfab: boolean
  allowPolyHaven: boolean
  /** Enable visual feedback loop for scene validation */
  enableVisualFeedback?: boolean
  /** Maximum visual validation iterations per step (default: 3) */
  maxVisualIterations?: number
  /** Callback to stream real-time agent events to the client */
  onStreamEvent?: (event: AgentStreamEvent) => void
  /** Strategy decision from the router */
  strategyDecision?: StrategyDecision
}

export class PlanExecutor {
  async executePlan(
    executionPlan: ExecutionPlan,
    userRequest: string,
    options: ExecutionOptions,
    analysis: PlanAnalysis | undefined,
    _llmProvider?: LlmProviderSpec // Unused, kept for compatibility
  ): Promise<ExecutionResult> {
    const client = createMcpClient()
    const logs: ExecutionLogEntry[] = []

    // 1. Initialize BlenderAgent with vision support if enabled
    const agent = createBlenderAgent({
      maxRetries: 2,
      useRAG: false, // Not needed for execution phase validation
      useVision: options.enableVisualFeedback ?? false,
      maxVisionIterations: options.maxVisualIterations ?? 3,
      onCaptureViewport: options.enableVisualFeedback
        ? async () => {
          const screenshot = await getViewportScreenshot()
          return screenshot.image
        }
        : undefined,
      onLog: (log: AgentLog) => {
        // Bridge ALL agent logs to execution logs
        const VALID_LOG_TYPES = new Set<ExecutionLogEntry["logType"]>(["plan", "execute", "validate", "recover", "vision", "audit", "reasoning", "system"])
        const logType: ExecutionLogEntry["logType"] = VALID_LOG_TYPES.has(log.type as ExecutionLogEntry["logType"])
          ? (log.type as ExecutionLogEntry["logType"])
          : "system"
        logs.push({
          timestamp: log.timestamp.toISOString(),
          tool: log.type === "execute" ? (log.data as PlanStep)?.action ?? "unknown" :
            log.type === "vision" ? "vision_analysis" : "system",
          parameters: log.type === "execute" ? (log.data as PlanStep)?.parameters ?? {} : {},
          error: log.type === "error" ? log.message : undefined,
          result: log.type === "complete" ? log.data : undefined,
          logType,
          detail: log.message,
          visualValidation: log.type === "vision" ? log.data as ExecutionLogEntry["visualValidation"] : undefined,
        })
      },
      onStreamEvent: options.onStreamEvent,
    })

    // 2. Load plan into agent
    const plan: Plan = {
      steps: executionPlan.steps.map((step) => ({
        action: step.action,
        parameters: step.parameters,
        rationale: step.rationale,
        expected_outcome: step.expectedOutcome,
      })),
      dependencies: executionPlan.dependencies ?? [],
      warnings: executionPlan.warnings ?? [],
    }
    agent.loadPlan(plan)

    try {
      // 3. Execute steps via Agent
      const allowHyper3d = options.allowHyper3d
      const allowSketchfab = options.allowSketchfab
      const allowPolyHaven = options.allowPolyHaven

      // Track scene state from get_scene_info/get_all_object_info for code gen context
      let sceneObjectContext = ""

      for (let i = 0; i < plan.steps.length; i++) {
        const result = await agent.executeStep(i, async (step) => {
          // Tool restriction checks
          if (!allowHyper3d && HYPER3D_TOOLS.has(step.action)) {
            throw new Error("Hyper3D tools are disabled for this project")
          }
          if (!allowSketchfab && SKETCHFAB_TOOLS.has(step.action)) {
            throw new Error("Sketchfab tools are disabled for this project")
          }
          if (!allowPolyHaven && POLYHAVEN_TOOLS.has(step.action)) {
            throw new Error("Poly Haven tools are disabled for this project")
          }

          // For execute_code steps: generate Python from description if no code is provided
          let params = normalizeParameters(step.action, step.parameters ?? {})

          if (step.action === "execute_code" && typeof params.code !== "string") {
            // The planner provided a description instead of code — generate Python
            const description = typeof params.description === "string"
              ? params.description
              : step.rationale ?? step.expected_outcome ?? "Execute the requested Blender operation"

            options.onStreamEvent?.({
              type: "agent:code_generation",
              timestamp: new Date().toISOString(),
              stepIndex: i,
              description,
            })

            // Retrieve RAG context from ingested Blender scripts
            let ragContext = ""
            try {
              const ragSources = await similaritySearch(description, {
                limit: 5,
                source: "blender-scripts",
                minSimilarity: 0.4,
              })
              if (ragSources.length > 0) {
                ragContext = formatContextFromSources(ragSources)
                logs.push({
                  timestamp: new Date().toISOString(),
                  tool: "rag_retrieval",
                  parameters: { query: description.substring(0, 100) },
                  result: { sourcesRetrieved: ragSources.length, sources: ragSources.map(s => s.source) },
                  logType: "reasoning",
                  detail: `Retrieved ${ragSources.length} RAG sources for code generation`,
                })
              }
            } catch (ragError) {
              console.warn("RAG retrieval for code gen failed (non-fatal):", ragError)
            }

            let generatedCode: string
            try {
              generatedCode = await generateCode({
                request: description,
                context: `This is one step in a larger plan for: "${userRequest}". Generate code for ONLY the described task, not the entire plan.${sceneObjectContext ? `\n\n## Current Scene Objects\nThese objects already exist in the scene. Reference them by name, do NOT recreate them:\n${sceneObjectContext}` : ""}${ragContext ? `\n\n## Reference Blender Python Scripts\n${ragContext}` : ""}`,
                applyMaterials: true,
                namingPrefix: "ModelForge_",
                constraints: step.expected_outcome,
              })
            } catch (codeGenError) {
              console.error(`Code generation failed for step ${i + 1}: ${description.substring(0, 100)}`, codeGenError)
              throw codeGenError
            }

            params = { code: generatedCode }

            logs.push({
              timestamp: new Date().toISOString(),
              tool: "code_generation",
              parameters: { description },
              result: { codeLength: generatedCode.length, codePreview: generatedCode.substring(0, 200) },
              logType: "reasoning",
              detail: `Generated ${generatedCode.length} chars of Python for: ${description.substring(0, 100)}`,
            })
          }

          // Execute MCP command
          const command: McpCommand = {
            id: randomUUID(),
            type: step.action,
            params,
          }

          const toolResult = await client.execute(command)

          // Capture scene state from inspection steps for code gen context
          if ((step.action === "get_scene_info" || step.action === "get_all_object_info") && toolResult) {
            try {
              const payload = typeof toolResult === "object" ? toolResult as Record<string, unknown> : {}
              const result = typeof payload.result === "object" && payload.result ? payload.result as Record<string, unknown> : payload
              const objects = Array.isArray(result.objects) ? result.objects : []
              const compactObjects = objects.slice(0, 30)
                .filter((o): o is Record<string, unknown> => !!o && typeof o === "object")
                .map((o) => ({
                  name: o.name,
                  type: o.type,
                  location: Array.isArray(o.location) ? o.location.slice(0, 3).map((v) => typeof v === "number" ? Math.round(v * 100) / 100 : 0) : undefined,
                  dimensions: Array.isArray(o.dimensions) ? o.dimensions.slice(0, 3).map((v) => typeof v === "number" ? Math.round(v * 100) / 100 : 0) : undefined,
                }))
              if (compactObjects.length > 0) {
                sceneObjectContext = JSON.stringify(compactObjects, null, 2)
              }
            } catch {
              // Non-fatal — scene context is a nice-to-have
            }
          }

          // Log specific tool execution
          logs.push({
            timestamp: new Date().toISOString(),
            tool: step.action,
            parameters: step.parameters ?? {},
            result: toolResult,
            logType: "execute",
            detail: `Step result: ${step.action}`,
          })

          return toolResult
        })

        if (!result.success) {
          // Agent handles retries and logging errors internally
          // We can stop or continue based on severity. Usually, if the agent gives up, we stop.
          const agentState = agent.getState()
          return {
            success: false,
            completedSteps: agentState.completedSteps,
            failedSteps: agentState.failedSteps,
            logs,
          }
        }
      }

      // 4. Switch viewport to Material Preview so materials are visible
      try {
        await client.execute({ type: "execute_code", params: { code: `import bpy\nfor area in bpy.context.screen.areas:\n    if area.type == 'VIEW_3D':\n        for space in area.spaces:\n            if space.type == 'VIEW_3D':\n                space.shading.type = 'MATERIAL'\n                break` } })
      } catch {
        // Non-fatal — viewport shading is cosmetic
      }

      // 4b. Visual Feedback Loop — capture viewport, analyze, and correct
      const maxVisualIter = options.maxVisualIterations ?? 2
      if (options.enableVisualFeedback !== false) {
        try {
          for (let vIter = 0; vIter < maxVisualIter; vIter++) {
            // Capture viewport screenshot via the existing MCP client
            // Note: No params — the Blender MCP addon doesn't accept width/height/format
            const screenshotResult = await client.execute({
              type: "get_viewport_screenshot",
              params: {},
            })

            // The MCP client returns McpResponse<T> where .result contains the data.
            // Blender MCP addons may nest the response differently, so try multiple paths.
            const topLevel = screenshotResult as Record<string, unknown>
            const resultLevel = screenshotResult?.result as Record<string, unknown> | undefined

            // Try: result.image (standard), then top-level image, then result.result.image (double-nested)
            const imageBase64 = (
              resultLevel?.image ??
              topLevel?.image ??
              (resultLevel?.result as Record<string, unknown> | undefined)?.image
            ) as string | undefined

            if (!imageBase64) {
              // Log the actual response shape for debugging
              const debugKeys = {
                topLevelKeys: Object.keys(topLevel || {}),
                resultKeys: resultLevel ? Object.keys(resultLevel) : 'no result',
                status: screenshotResult?.status,
                message: screenshotResult?.message,
              }
              console.warn('[Executor] Screenshot data not found. Response shape:', JSON.stringify(debugKeys))
              logs.push({
                timestamp: new Date().toISOString(),
                tool: "visual_feedback",
                parameters: { iteration: vIter + 1, debugKeys },
                error: "No screenshot data received from Blender MCP",
                logType: "vision",
                detail: `Viewport screenshot capture failed — response keys: ${JSON.stringify(debugKeys)}`,
              })
              break
            }

            options.onStreamEvent?.({
              type: "agent:visual_analysis",
              timestamp: new Date().toISOString(),
              iteration: vIter + 1,
              description: `Analyzing viewport (iteration ${vIter + 1}/${maxVisualIter})...`,
            } as AgentStreamEvent)

            // Ask Gemini Vision to analyze the scene against the user request
            const visionResult = await suggestImprovements(imageBase64, userRequest)

            logs.push({
              timestamp: new Date().toISOString(),
              tool: "visual_analysis",
              parameters: { iteration: vIter + 1, userRequest: userRequest.substring(0, 100) },
              result: {
                currentState: visionResult.currentState,
                missingElements: visionResult.missingElements,
                improvementCount: visionResult.improvements.length,
                highPriorityCount: visionResult.improvements.filter(i => i.priority === "high").length,
              },
              logType: "vision",
              detail: `Vision analysis: ${visionResult.improvements.length} improvements suggested (${visionResult.improvements.filter(i => i.priority === "high").length} high priority)`,
            })

            // Only correct if there are high-priority issues
            const highPriority = visionResult.improvements.filter(i => i.priority === "high")
            if (highPriority.length === 0) {
              logs.push({
                timestamp: new Date().toISOString(),
                tool: "visual_feedback",
                parameters: { iteration: vIter + 1 },
                result: { action: "pass", reason: "No high-priority issues detected" },
                logType: "vision",
                detail: "Visual check passed — no high-priority corrections needed",
              })
              break // Scene looks good, proceed to audit
            }

            // Generate correction code based on vision feedback
            const correctionDescription = highPriority
              .map(hp => `FIX: ${hp.action} (Reason: ${hp.rationale})`)
              .join("\n")

            options.onStreamEvent?.({
              type: "agent:visual_correction",
              timestamp: new Date().toISOString(),
              iteration: vIter + 1,
              description: `Correcting ${highPriority.length} visual issues...`,
              issues: highPriority.map(hp => hp.action),
            } as AgentStreamEvent)

            // Retrieve RAG context for correction
            let correctionRagContext = ""
            try {
              const ragSources = await similaritySearch(correctionDescription, {
                limit: 3,
                source: "blender-scripts",
                minSimilarity: 0.4,
              })
              if (ragSources.length > 0) {
                correctionRagContext = formatContextFromSources(ragSources)
              }
            } catch { /* Non-fatal */ }

            try {
              const correctionCode = await generateCode({
                request: correctionDescription,
                context: `VISUAL CORRECTION: The scene for "${userRequest}" was analyzed by vision and these issues were found. Generate Python code to FIX these specific issues ONLY. Do NOT recreate the entire scene — only adjust existing objects.\n\nCurrent scene state: ${visionResult.currentState}\nMissing elements: ${visionResult.missingElements.join(", ") || "none"}${correctionRagContext ? `\n\n## Reference Scripts\n${correctionRagContext}` : ""}`,
                applyMaterials: false,
                namingPrefix: "ModelForge_Fix_",
              })

              // Execute the correction
              const correctionResult = await client.execute({
                type: "execute_code",
                params: { code: correctionCode },
              })

              logs.push({
                timestamp: new Date().toISOString(),
                tool: "visual_correction",
                parameters: {
                  iteration: vIter + 1,
                  issueCount: highPriority.length,
                  issues: highPriority.map(hp => hp.action),
                },
                result: correctionResult,
                logType: "vision",
                detail: `Applied visual correction (${highPriority.length} issues) — iteration ${vIter + 1}`,
              })
            } catch (correctionError) {
              logs.push({
                timestamp: new Date().toISOString(),
                tool: "visual_correction",
                parameters: { iteration: vIter + 1 },
                error: correctionError instanceof Error ? correctionError.message : String(correctionError),
                logType: "vision",
                detail: "Visual correction code generation/execution failed (non-fatal)",
              })
              break // Don't retry if correction itself fails
            }
          }
        } catch (visionError) {
          // Entire visual feedback loop is non-fatal
          logs.push({
            timestamp: new Date().toISOString(),
            tool: "visual_feedback",
            parameters: {},
            error: visionError instanceof Error ? visionError.message : String(visionError),
            logType: "vision",
            detail: "Visual feedback loop failed (non-fatal) — proceeding to scene audit",
          })
        }
      }

      // 5. Final Scene Audit
      try {
        const finalState = await client.execute({ type: "get_scene_info" })
        logs.push({
          timestamp: new Date().toISOString(),
          tool: "get_scene_info",
          parameters: {},
          result: finalState,
        })
        const audit = await this.auditScene(client, finalState, userRequest, analysis, logs)

        const agentState = agent.getState()

        if (!audit.success) {
          logs.push({
            timestamp: new Date().toISOString(),
            tool: "post_audit",
            parameters: {},
            error: audit.reason ?? "Scene audit failed",
          })

          // Mark the last step or a virtual 'audit' step as failed
          const auditFailStep = {
            step: plan.steps[plan.steps.length - 1],
            error: audit.reason ?? "Scene audit failed"
          }

          return {
            success: false,
            completedSteps: agentState.completedSteps,
            failedSteps: [...agentState.failedSteps, auditFailStep],
            finalSceneState: finalState,
            logs,
          }
        }

        return {
          success: true,
          completedSteps: agentState.completedSteps,
          failedSteps: agentState.failedSteps,
          finalSceneState: finalState,
          logs,
        }
      } catch {
        const agentState = agent.getState()
        return { success: true, completedSteps: agentState.completedSteps, failedSteps: agentState.failedSteps, logs }
      }

    } finally {
      await client.close().catch(() => undefined)
    }
  }

  private async auditScene(
    client: ReturnType<typeof createMcpClient>,
    finalState: unknown,
    userRequest: string,
    analysis?: PlanAnalysis,
    logs?: ExecutionLogEntry[]
  ): Promise<{ success: boolean; reason?: string }> {
    const resultRecord =
      finalState && typeof finalState === "object"
        ? ((finalState as Record<string, unknown>).result as Record<string, unknown> | undefined)
        : undefined

    const rawObjects = Array.isArray(resultRecord?.objects) ? (resultRecord?.objects as unknown[]) : []
    const objects = rawObjects.filter(
      (item): item is Record<string, unknown> => typeof item === "object" && item !== null
    )

    const meshObjects = objects.filter((obj) => {
      const typeValue = typeof obj.type === "string" ? obj.type : typeof obj["type"] === "string" ? (obj["type"] as string) : ""
      return typeValue === "MESH"
    })

    if (analysis?.minimumMeshObjects && meshObjects.length < analysis.minimumMeshObjects) {
      return {
        success: false,
        reason: `Scene contains ${meshObjects.length} mesh objects; expected at least ${analysis.minimumMeshObjects}.`,
      }
    }

    const lights = objects.filter((obj) => {
      const typeValue = typeof obj.type === "string" ? obj.type : typeof obj["type"] === "string" ? (obj["type"] as string) : ""
      return typeValue === "LIGHT"
    })
    const cameras = objects.filter((obj) => {
      const typeValue = typeof obj.type === "string" ? obj.type : typeof obj["type"] === "string" ? (obj["type"] as string) : ""
      return typeValue === "CAMERA"
    })

    if (analysis?.requireLighting !== false && lights.length === 0) {
      await this.ensureDefaultLighting(client)
    }

    if (analysis?.requireCamera !== false && cameras.length === 0) {
      await this.ensureDefaultCamera(client)
    }

    const missingMaterials: string[] = []
    for (const mesh of meshObjects) {
      const rawName = typeof mesh.name === "string" ? mesh.name : typeof mesh["name"] === "string" ? (mesh["name"] as string) : undefined
      const name = rawName?.trim()
      if (!name) continue
      try {
        const info = await client.execute({
          type: "get_object_info",
          params: { name },
        })
        const infoResult = info.result as Record<string, unknown> | undefined
        const materials = Array.isArray(infoResult?.materials)
          ? (infoResult?.materials as unknown[])
          : undefined
        if (!materials || materials.length === 0) {
          missingMaterials.push(name)
        }
      } catch {
        missingMaterials.push(name)
      }
    }

    if (missingMaterials.length > 0) {
      await this.ensureDefaultMaterials(client, missingMaterials)
    }

    // LLM-based scene completeness check
    try {
      const completenessCheck = await this.llmSceneCompletenessCheck(
        userRequest,
        objects,
        resultRecord
      )
      logs?.push({
        timestamp: new Date().toISOString(),
        tool: "llm_completeness_check",
        parameters: { userRequest: userRequest.substring(0, 100) },
        result: completenessCheck,
        logType: "reasoning",
        detail: completenessCheck.success
          ? "LLM completeness check passed"
          : `LLM completeness check failed: ${completenessCheck.reason}`,
      })
      if (!completenessCheck.success) {
        return completenessCheck
      }
    } catch (llmCheckError) {
      // Non-fatal — log and continue if LLM check fails
      console.warn("LLM scene completeness check failed (non-fatal):", llmCheckError)
      logs?.push({
        timestamp: new Date().toISOString(),
        tool: "llm_completeness_check",
        parameters: { userRequest: userRequest.substring(0, 100) },
        error: String(llmCheckError),
        logType: "reasoning",
        detail: "LLM completeness check threw an error (non-fatal)",
      })
    }

    return { success: true }
  }

  /**
   * Use the LLM to verify the final scene matches the user's original request.
   * Checks for missing objects, missing materials, and placement issues.
   */
  private async llmSceneCompletenessCheck(
    userRequest: string,
    objects: Array<Record<string, unknown>>,
    sceneResult?: Record<string, unknown>
  ): Promise<{ success: boolean; reason?: string }> {
    try {
      const model = createGeminiModel({ temperature: 0.1, maxOutputTokens: 1024 })

      const objectSummary = (objects ?? []).map(obj => {
        const name = (obj?.name as string) ?? "unknown"
        const type = (obj?.type as string) ?? "unknown"
        const loc = obj?.location
        const location = Array.isArray(loc) && loc.length >= 3
          ? `(${(loc as number[]).map(v => typeof v === 'number' ? v.toFixed(2) : '?').join(", ")})`
          : "unknown"
        return `  - ${name} [${type}] @ ${location}`
      }).join("\n")

      const materialsCount = typeof sceneResult?.materials_count === "number"
        ? sceneResult.materials_count
        : "unknown"

      const prompt = `You are a Blender scene quality auditor. A user requested the following scene:

"${userRequest}"

The scene now contains these objects:
${objectSummary}

Total materials in scene: ${materialsCount}

Evaluate whether the scene fulfills the user's request. Consider:
1. Are all requested objects present (by name or type)?
2. Are materials likely assigned (material count should be > 2 for scenes with colored objects)?
3. Are object positions reasonable (not all at origin, correct relative placement)?

IMPORTANT — Be LENIENT:
- Objects may have been joined/merged into a single mesh (e.g., "Castle_Tower" may contain the wall section too). This is FINE — do not flag merged sub-components as missing.
- Minor naming differences are fine (e.g., "Grassy_Hill" vs "Hill").
- Only flag something as missing if there is NO object that could plausibly represent it.
- The material count being >= the number of distinct materials requested is sufficient.
- Geometric sub-components (doors, windows, arches) may be boolean-cut into parent objects — they won't appear as separate scene objects.

Respond with ONLY valid JSON — no markdown, no explanation:
{
  "complete": true or false,
  "issues": ["list of specific issues if incomplete, empty array if complete"]
}

Only flag CLEARLY missing top-level objects or completely absent material assignments.`

      const response = await model.invoke(prompt)
      const rawContent = response?.content
      let text = ""
      if (typeof rawContent === "string") {
        text = rawContent.trim()
      } else if (Array.isArray(rawContent)) {
        text = rawContent
          .map(part => {
            if (typeof part === "string") return part
            if (part && typeof part === "object" && "text" in part) return String((part as Record<string, unknown>).text ?? "")
            return ""
          })
          .join("")
          .trim()
      } else {
        text = String(rawContent ?? "")
      }

      if (!text) {
        return { success: true } // Empty response — don't block
      }

      // Parse LLM response
      const jsonMatch = text.match(/\{[\s\S]*\}/)
      if (!jsonMatch) {
        return { success: true } // Can't parse — don't block
      }

      let result: { complete: boolean; issues?: string[] }
      try {
        result = JSON.parse(jsonMatch[0]) as { complete: boolean; issues?: string[] }
      } catch {
        return { success: true } // Malformed JSON — don't block
      }

      if (result.complete === false && Array.isArray(result.issues) && result.issues.length > 0) {
        return {
          success: false,
          reason: `Scene completeness check: ${result.issues.join("; ")}`,
        }
      }

      return { success: true }
    } catch (error) {
      // Catch any unexpected errors (TypeError, etc.) — never block execution
      console.warn("[llmSceneCompletenessCheck] Non-fatal error:", error)
      return { success: true }
    }
  }

  private async ensureDefaultMaterials(
    client: ReturnType<typeof createMcpClient>,
    meshNames: string[]
  ) {
    if (meshNames.length === 0) return
    const pythonList = meshNames.map((name) => JSON.stringify(name)).join(", ")
    const script = `import bpy\n\nDEFAULT_NAME = "ModelForge_Default_Material"\nmat = bpy.data.materials.get(DEFAULT_NAME)\nif mat is None:\n    mat = bpy.data.materials.new(name=DEFAULT_NAME)\n    mat.use_nodes = True\n    bsdf = mat.node_tree.nodes.get('Principled BSDF')\n    if bsdf:\n        bsdf.inputs['Base Color'].default_value = (0.85, 0.82, 0.78, 1.0)\n        bsdf.inputs['Roughness'].default_value = 0.4\n\nfor obj_name in [${pythonList}]:\n    obj = bpy.data.objects.get(obj_name)\n    if not obj or obj.type != 'MESH':\n        continue\n    if not obj.data.materials:\n        obj.data.materials.append(mat)\n    else:\n        obj.data.materials[0] = mat\n`

    await client.execute({ type: "execute_code", params: { code: script } })
  }

  private async ensureDefaultLighting(client: ReturnType<typeof createMcpClient>) {
    const script = `import bpy\n\nif not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):\n    bpy.ops.object.light_add(type='AREA', location=(6, -6, 8))\n    light = bpy.context.active_object\n    light.name = 'ModelForge_KeyLight'\n    light.data.energy = 1200\n    light.data.shape = 'RECTANGLE'\n    light.data.size = 6\n    light.data.size_y = 4\n`

    await client.execute({ type: "execute_code", params: { code: script } })
  }

  private async ensureDefaultCamera(client: ReturnType<typeof createMcpClient>) {
    const script = `import bpy\n\nif not bpy.context.scene.camera:\n    bpy.ops.object.camera_add(location=(10, -10, 7))\n    cam = bpy.context.active_object\n    cam.rotation_euler = (0.9, 0, 0.8)\n    bpy.context.scene.camera = cam\n`

    await client.execute({ type: "execute_code", params: { code: script } })
  }


}

function normalizeParameters(action: string, parameters: Record<string, unknown> = {}) {
  if (!parameters) return {}

  const clone: Record<string, unknown> = { ...parameters }

  if (action === "execute_code") {
    if (typeof clone.code !== "string" && typeof clone.script === "string") {
      clone.code = clone.script
    }
    if (typeof clone.code !== "string" && Array.isArray(clone.lines)) {
      clone.code = clone.lines.join("\n")
    }
    if (typeof clone.code !== "string" && typeof clone.python === "string") {
      clone.code = clone.python
    }

    // If there's still no code, the caller (executor) will handle code generation
    // from the description parameter — don't throw here
    delete clone.script
    delete clone.lines
    delete clone.python

    // If we have actual code, strip description so the addon doesn't reject it
    // (addon only accepts `code` kwarg)
    if (typeof clone.code === "string") {
      delete clone.description
    }
  }

  return clone
}

