import { randomUUID } from "crypto"

import { createBlenderAgent, type AgentLog } from "@/lib/ai/agents"
import { type Plan, type PlanStep } from "@/lib/ai/chains"
import { type LlmProviderSpec } from "@/lib/llm"
import { createMcpClient, type McpCommand } from "@/lib/mcp"
import { ExecutionLogEntry, ExecutionPlan, PlanAnalysis } from "./types"

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

interface ExecutionOptions {
  allowHyper3d: boolean
  allowSketchfab: boolean
  allowPolyHaven: boolean
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

    // 1. Initialize BlenderAgent
    const agent = createBlenderAgent({
      maxRetries: 2,
      useRAG: false, // Not needed for execution phase validation (unless detailed context is required)
      onLog: (log: AgentLog) => {
        // Bridge agent logs to execution logs
        if (log.type === "error" || log.type === "execute" || log.type === "recover") {
          logs.push({
            timestamp: log.timestamp.toISOString(),
            tool: log.type === "execute" ? (log.data as PlanStep)?.action ?? "unknown" : "system",
            parameters: log.type === "execute" ? (log.data as PlanStep)?.parameters ?? {} : {},
            error: log.type === "error" ? log.message : undefined,
            result: log.type === "complete" ? log.data : undefined,
          })
        }
      },
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

          // Execute MCP command
          const command: McpCommand = {
            id: randomUUID(),
            type: step.action,
            params: normalizeParameters(step.action, step.parameters ?? {}),
          }

          const toolResult = await client.execute(command)

          // Log specific tool execution
          logs.push({
            timestamp: new Date().toISOString(),
            tool: step.action,
            parameters: step.parameters ?? {},
            result: toolResult,
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

      // 4. Final Scene Audit
      try {
        const finalState = await client.execute({ type: "get_scene_info" })
        logs.push({
          timestamp: new Date().toISOString(),
          tool: "get_scene_info",
          parameters: {},
          result: finalState,
        })
        const audit = await this.auditScene(client, finalState, userRequest, analysis)

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
    analysis?: PlanAnalysis
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

    if (/(car|vehicle|sedan|supercar|sports car|automobile|truck)/i.test(userRequest)) {
      const carAudit = this.auditCarScene(meshObjects)
      if (!carAudit.success) {
        return carAudit
      }
    }

    return { success: true }
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

  private auditCarScene(objects: Array<Record<string, unknown>>): { success: boolean; reason?: string } {
    const meshByName = objects
      .map((obj) => ({
        name: typeof obj.name === "string" ? obj.name : typeof obj["name"] === "string" ? (obj["name"] as string) : "",
        raw: obj,
      }))
      .filter((entry) => entry.name.trim().length > 0)

    const carBody = meshByName.find((entry) => /car.*(body|shell|chassis)/i.test(entry.name))
    if (!carBody) {
      return { success: false, reason: "Car audit failed: missing a car body mesh (expected name containing 'car_body')." }
    }

    const wheels = meshByName.filter((entry) => /(wheel|tyre|tire)/i.test(entry.name))
    const uniqueWheels = new Map<string, typeof wheels[number]>()
    for (const wheel of wheels) {
      uniqueWheels.set(wheel.name.toLowerCase(), wheel)
    }
    if (uniqueWheels.size < 4) {
      return { success: false, reason: `Car audit failed: expected 4 wheels, found ${uniqueWheels.size}.` }
    }

    const wheelLocations = Array.from(uniqueWheels.values())
      .map((entry) => {
        const location = Array.isArray(entry.raw.location)
          ? (entry.raw.location as unknown[])
          : Array.isArray(entry.raw["location"])
            ? (entry.raw["location"] as unknown[])
            : []
        return location.map((value) => (typeof value === "number" ? Number(value.toFixed(2)) : value))
      })
      .filter((loc) => Array.isArray(loc) && loc.length === 3)

    const wheelPositionHashes = new Set(wheelLocations.map((loc) => JSON.stringify(loc)))
    if (wheelPositionHashes.size < 3) {
      return {
        success: false,
        reason: "Car audit failed: wheel locations are overlapping; ensure wheels are positioned at four corners.",
      }
    }

    const lights = meshByName.filter((entry) => /(headlight|taillight|light)/i.test(entry.name))
    if (lights.length < 2) {
      return {
        success: false,
        reason: "Car audit failed: expected at least two headlight/taillight meshes.",
      }
    }

    const glass = meshByName.some((entry) => /(window|glass|windshield)/i.test(entry.name))
    if (!glass) {
      return {
        success: false,
        reason: "Car audit failed: expected window or windshield meshes.",
      }
    }

    return { success: true }
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

    if (typeof clone.code === "string") {
      clone.code = clone.code
    } else {
      throw new Error("execute_code requires a string 'code' parameter")
    }

    delete clone.script
    delete clone.lines
    delete clone.python
  }

  return clone
}

