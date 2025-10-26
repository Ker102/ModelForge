import { randomUUID } from "crypto"

import { generateGeminiResponse } from "@/lib/gemini"
import { createMcpClient } from "@/lib/mcp"
import type { McpCommand } from "@/lib/mcp"
import { ExecutionLogEntry, ExecutionPlan, PlanAnalysis, PlanStep } from "./types"

export interface ExecutionResult {
  success: boolean
  completedSteps: Array<{ step: PlanStep; result: unknown }>
  failedSteps: Array<{ step: PlanStep; error: string }>
  finalSceneState?: unknown
  logs: ExecutionLogEntry[]
}

const VALIDATION_SYSTEM_PROMPT = `You are validating the outcome of a Blender MCP command. Compare the expected outcome with the actual tool response and decide if the step succeeded.`

const VALIDATION_OUTPUT_FORMAT = `Return strict JSON with:
{
  "success": true|false,
  "reason": "short explanation",
  "concerns": ["optional warnings"]
}`

const RECOVERY_SYSTEM_PROMPT = `You are assisting with recovery after a Blender MCP command failed. Suggest a single corrective action if possible.`

const RECOVERY_OUTPUT_FORMAT = `Return strict JSON with:
{
  "recovery_action": "tool_name or null",
  "recovery_params": { ... },
  "explanation": "why this helps"
}`

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
    plan: ExecutionPlan,
    userRequest: string,
    options: ExecutionOptions,
    analysis?: PlanAnalysis
  ): Promise<ExecutionResult> {
    const client = createMcpClient()
    const logs: ExecutionLogEntry[] = []
    const completedSteps: Array<{ step: PlanStep; result: unknown }> = []
    const failedSteps: Array<{ step: PlanStep; error: string }> = []

    const allowHyper3d = options.allowHyper3d
    const allowSketchfab = options.allowSketchfab
    const allowPolyHaven = options.allowPolyHaven

    try {
      for (const step of plan.steps) {
        if (!allowHyper3d && HYPER3D_TOOLS.has(step.action)) {
          const reason = "Hyper3D tools are disabled for this project"
          logs.push({
            timestamp: new Date().toISOString(),
            tool: step.action,
            parameters: step.parameters,
            error: reason,
          })
          failedSteps.push({ step, error: reason })
          return { success: false, completedSteps, failedSteps, logs }
        }

        if (!allowSketchfab && SKETCHFAB_TOOLS.has(step.action)) {
          const reason = "Sketchfab tools are disabled for this project"
          logs.push({
            timestamp: new Date().toISOString(),
            tool: step.action,
            parameters: step.parameters,
            error: reason,
          })
          failedSteps.push({ step, error: reason })
          return { success: false, completedSteps, failedSteps, logs }
        }

        if (!allowPolyHaven && POLYHAVEN_TOOLS.has(step.action)) {
          const reason = "Poly Haven tools are disabled for this project"
          logs.push({
            timestamp: new Date().toISOString(),
            tool: step.action,
            parameters: step.parameters,
            error: reason,
          })
          failedSteps.push({ step, error: reason })
          return { success: false, completedSteps, failedSteps, logs }
        }

        const command: McpCommand = {
          id: randomUUID(),
          type: step.action,
          params: normalizeParameters(step.action, step.parameters),
        }

        let result: unknown
        try {
          result = await client.execute(command)
          logs.push({
            timestamp: new Date().toISOString(),
            tool: step.action,
            parameters: step.parameters,
            result,
          })
        } catch (error) {
          const message = error instanceof Error ? error.message : "Command execution failed"
          logs.push({
            timestamp: new Date().toISOString(),
            tool: step.action,
            parameters: step.parameters,
            error: message,
          })
          failedSteps.push({ step, error: message })
          return { success: false, completedSteps, failedSteps, logs }
        }

        const structuralCheck = await this.performStructuredChecks(client, step)
        const validation = await this.validateStep(step, result, userRequest)
        const mergedValidation = structuralCheck.success
          ? validation
          : {
              success: false,
              reason: structuralCheck.reason ?? validation.reason,
              concerns: [...(validation.concerns ?? []), structuralCheck.reason].filter(Boolean),
            }

        if (mergedValidation.success) {
          completedSteps.push({ step, result })
          continue
        }

        const recovery = await this.attemptRecovery(
          client,
          step,
          result,
          mergedValidation.reason,
          userRequest
        )
        if (recovery.success) {
          completedSteps.push({ step, result: recovery.result })
          logs.push({
            timestamp: new Date().toISOString(),
            tool: recovery.action ?? "recovery",
            parameters: recovery.params ?? {},
            result: recovery.result,
          })
          continue
        }

        failedSteps.push({ step, error: mergedValidation.reason })
        return { success: false, completedSteps, failedSteps, logs }
      }

      // Fetch final state for reporting
      try {
        const finalState = await client.execute({ type: "get_scene_info" })
        logs.push({
          timestamp: new Date().toISOString(),
          tool: "get_scene_info",
          parameters: {},
          result: finalState,
        })
        const audit = await this.auditScene(client, finalState, userRequest, analysis)
        if (!audit.success) {
          failedSteps.push({
            step: plan.steps[plan.steps.length - 1] ?? plan.steps[0],
            error: audit.reason,
          })
          logs.push({
            timestamp: new Date().toISOString(),
            tool: "post_audit",
            parameters: {},
            error: audit.reason,
          })
          return { success: false, completedSteps, failedSteps, finalSceneState: finalState, logs }
        }
        return { success: true, completedSteps, failedSteps, finalSceneState: finalState, logs }
      } catch {
        return { success: true, completedSteps, failedSteps, logs }
      }
    } finally {
      await client.close().catch(() => undefined)
    }
  }

  private async validateStep(step: PlanStep, result: unknown, userRequest: string) {
    const prompt = `User goal: ${userRequest}

Step executed:
- Action: ${step.action}
- Parameters: ${JSON.stringify(step.parameters)}
- Expected outcome: ${step.expectedOutcome}

Tool result:
${JSON.stringify(result, null, 2)}

${VALIDATION_OUTPUT_FORMAT}`

    const response = await generateGeminiResponse({
      messages: [{ role: "user", content: prompt }],
      temperature: 0.0,
      topP: 0.1,
      topK: 1,
      maxOutputTokens: 256,
      systemPrompt: VALIDATION_SYSTEM_PROMPT,
    })

    const parsed = this.parseJson(response.text)
    const success = Boolean(parsed?.success)
    const reason = typeof parsed?.reason === "string" ? parsed.reason : "Validation failed"

    return {
      success,
      reason,
      concerns: Array.isArray(parsed?.concerns) ? parsed.concerns : [],
    }
  }

  private async attemptRecovery(
    client: ReturnType<typeof createMcpClient>,
    step: PlanStep,
    result: unknown,
    reason: string,
    userRequest: string
  ): Promise<{ success: boolean; action?: string; params?: Record<string, unknown>; result?: unknown }> {
    const prompt = `A Blender MCP command failed.

User goal: ${userRequest}
Failed step: ${step.action} with params ${JSON.stringify(step.parameters)}
Failure reason: ${reason}
Tool result: ${JSON.stringify(result, null, 2)}

Suggest exactly one recovery action if feasible.
${RECOVERY_OUTPUT_FORMAT}`

    const response = await generateGeminiResponse({
      messages: [{ role: "user", content: prompt }],
      temperature: 0.4,
      topP: 0.8,
      maxOutputTokens: 256,
      systemPrompt: RECOVERY_SYSTEM_PROMPT,
    })

    const parsed = this.parseJson(response.text)
    const action = typeof parsed?.recovery_action === "string" ? parsed.recovery_action : null
    const params = parsed?.recovery_params && typeof parsed.recovery_params === "object" ? parsed.recovery_params : {}

    if (!action) {
      return { success: false }
    }

    try {
      const recoveryResult = await client.execute({ type: action, params })
      return { success: true, action, params, result: recoveryResult }
    } catch (error) {
      return {
        success: false,
        action,
        params,
        result: error instanceof Error ? error.message : "Recovery failed",
      }
    }
  }

  private deriveObjectTargets(step: PlanStep): string[] {
    const params = step.parameters ?? {}
    const candidates: string[] = []
    const keys = ["object_name", "objectName", "target", "targetName", "mesh", "name"]
    const stepText = `${step.action} ${step.rationale} ${step.expectedOutcome}`.toLowerCase()
    const isCreation = /(create|add|spawn|generate|new)/.test(stepText)

    for (const key of keys) {
      const value = (params as Record<string, unknown>)[key]
      if (typeof value === "string" && value.trim()) {
        if (key === "name" && isCreation) continue
        candidates.push(value.trim())
      }
    }

    return Array.from(new Set(candidates))
  }

  private async performStructuredChecks(
    client: ReturnType<typeof createMcpClient>,
    step: PlanStep
  ): Promise<{ success: boolean; reason?: string }> {
    const targets = this.deriveObjectTargets(step)
    if (targets.length === 0) {
      return { success: true }
    }

    const missing: string[] = []
    for (const name of targets) {
      try {
        const response = await client.execute({
          type: "get_object_info",
          params: { name },
        })
        const status = typeof response.status === "string" ? response.status.toLowerCase() : "ok"
        if (status !== "ok" && status !== "success") {
          missing.push(name)
        }
      } catch {
        missing.push(name)
      }
    }

    if (missing.length > 0) {
      return {
        success: false,
        reason: `Expected objects not found after step ${step.stepNumber}: ${missing.join(", ")}`,
      }
    }

    return { success: true }
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

  private parseJson(raw: string): Record<string, unknown> | null {
    const match = raw.match(/\{[\s\S]*\}/)
    if (!match) return null
    try {
      return JSON.parse(match[0])
    } catch {
      return null
    }
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
