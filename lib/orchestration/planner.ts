import { z } from "zod"

import { generateGeminiResponse } from "@/lib/gemini"
import { filterRelevantTools, formatToolListForPrompt } from "./tool-filter"
import { ExecutionPlan, PlanAnalysis, PlanGenerationResult, PlanStep } from "./types"

const PLAN_SCHEMA = z.object({
  plan_summary: z.string().min(1, "Plan summary missing"),
  steps: z
    .array(
      z.object({
        step_number: z.number().int().positive(),
        action: z.string().min(1),
        parameters: z.record(z.unknown()).default({}),
        rationale: z.string().min(1),
        expected_outcome: z.string().min(1),
      })
    )
    .min(1, "At least one plan step is required"),
  dependencies: z.array(z.string()).optional(),
  warnings: z.array(z.string()).optional(),
})

type RawPlan = z.infer<typeof PLAN_SCHEMA>

const ANALYSIS_SCHEMA = z.object({
  components: z.array(z.string()).min(1, "List at least one component"),
  material_guidelines: z.array(z.string()).default([]),
  minimum_mesh_objects: z.number().int().positive().optional(),
  require_lighting: z.boolean().optional(),
  require_camera: z.boolean().optional(),
  notes: z.array(z.string()).optional(),
})

type RawAnalysis = z.infer<typeof ANALYSIS_SCHEMA>

const PLANNING_SYSTEM_PROMPT = `You are ModelForge's orchestration planner. Your job is to produce reliable, step-by-step tool plans for controlling Blender through MCP **before** any commands execute.

Follow these principles:
- Think in ReAct style: observe → plan → act; never jump straight to code.
- Always begin with "get_scene_info" to capture current context unless a previous step already provided a fresh snapshot.
- Choose tools from the provided list only. If a capability is unavailable, omit it instead of inventing new tools.
- Prefer declarative tools over generic code. Resort to "execute_code" only when no other tool can accomplish the task, and keep scripts short, idempotent, and focused.
- When using "execute_code", the parameters object must include a single key "code" containing the Python string (do not use alternate names like "script", "python", or "body").
- Use descriptive object names (snake_case, no spaces). Default coordinates are Blender units in [x, y, z]. Colors are RGBA floats 0.0–1.0.
- Break complex requests into sub-components. Each major component from the analysis must have at least one dedicated step, with extra steps for repeated elements (e.g., four wheels).
- Materials and colors must be applied inside the same step that creates or modifies a mesh.
- Ensure every final scene has at least one light and one camera unless the user explicitly forbids it.
- Note dependencies or cautions when a later step assumes a previous result (e.g., material application requires the object to exist).
- Output strict JSON that matches the requested schema—no commentary, Markdown, or trailing text.`

interface PlanningOptions {
  sceneSummary?: string
  allowHyper3dAssets?: boolean
  allowSketchfabAssets?: boolean
  allowPolyHavenAssets?: boolean
}

export class BlenderPlanner {
  constructor(private readonly maxRetries = 2) {}

  async generatePlan(
    userRequest: string,
    options: PlanningOptions = {}
  ): Promise<PlanGenerationResult> {
    const analysis = await this.generateAnalysis(userRequest)

    const filteredTools = filterRelevantTools(userRequest, undefined, {
      allowHyper3d: options.allowHyper3dAssets !== false,
      allowSketchfab: options.allowSketchfabAssets !== false,
      allowPolyHaven: options.allowPolyHavenAssets !== false,
    })
    const toolListing = formatToolListForPrompt(filteredTools)

    const sceneContext = options.sceneSummary
      ? `Current scene snapshot (use these objects when possible):\n${options.sceneSummary}\n\n`
      : ""

    const restrictions: string[] = []
    if (options.allowHyper3dAssets === false) {
      restrictions.push(
        "Hyper3D / Rodin tools are disabled for this project. Do not call get_hyper3d_status, create_rodin_job, poll_rodin_job_status, or import_generated_asset."
      )
    }
    if (options.allowSketchfabAssets === false) {
      restrictions.push(
        "Sketchfab tools are disabled for this project. Do not call get_sketchfab_status, search_sketchfab_models, or download_sketchfab_model."
      )
    }
    if (options.allowPolyHavenAssets === false) {
      restrictions.push(
        "Poly Haven tools are disabled for this project. Do not call get_polyhaven_status, search_polyhaven_assets, or download_polyhaven_asset."
      )
    }
    const restrictionContext = restrictions.length ? `${restrictions.join("\n")}\n\n` : ""

    const analysisContext = analysis
      ? `Design analysis:\n- Components: ${analysis.components.join(", ")}\n- Material guidelines: ${
          analysis.materialGuidelines.join(", ") || "Apply realistic materials to every mesh"
        }\n- Minimum mesh objects: ${
          analysis.minimumMeshObjects ?? Math.max(analysis.components.length * 2, 6)
        }\n- Require lighting: ${analysis.requireLighting ? "yes" : "no"}\n- Require camera: ${
          analysis.requireCamera ? "yes" : "no"
        }\n${analysis.notes?.length ? `- Notes: ${analysis.notes.join("; ")}\n` : ""}`
      : ""

    const planningPrompt = `${sceneContext}${restrictionContext}${analysisContext}
User request: "${userRequest}"

Available tools (choose from this list):
${toolListing}

Produce a plan **before** executing anything. Requirement checklist:
1. Step 1 must be get_scene_info (unless the user explicitly supplied a recent scene snapshot).
2. Perform component-by-component construction. Each major component from the analysis must have at least one dedicated step, and repeated components (e.g., four wheels) must each receive attention.
3. Parameters must match the tool expectations. Omit optional parameters when not needed.
4. When the scene snapshot lists existing objects, modify or extend them instead of recreating duplicates with new names.
5. Consolidate repetitive work: prefer a single execute_code step that iterates over multiple targets instead of duplicating nearly identical steps for each object.
6. When recoloring or applying materials, operate only on mesh objects (obj.type == "MESH") and guard with hasattr(obj, "data") / hasattr(obj.data, "materials") before editing materials. Update every material slot on the mesh and never touch lights or cameras.
7. Every mesh created or modified must end with explicit material/color assignment inside the same execute_code payload.
8. Ensure there is at least one light and one camera positioned for a useful render unless the user forbids it.
9. Rationale must reference the analysis components and explain the design intent.
10. Expected outcome should describe what Blender should report after the tool call.
11. If a step depends on the result of a previous step, include that dependency in the dependencies array.
12. Highlight any risks or manual follow-up in the warnings array.

Return strict JSON with this shape:
{
  "plan_summary": "...",
  "steps": [
    {
      "step_number": 1,
      "action": "tool_name",
      "parameters": { ... },
      "rationale": "...",
      "expected_outcome": "..."
    }
  ],
  "dependencies": [ ... ],
  "warnings": [ ... ]
}`

    let lastRaw = ""
    let retries = 0
    const errors: string[] = []

    while (retries <= this.maxRetries) {
      const response = await generateGeminiResponse({
        messages: [
          {
            role: "user",
            content: planningPrompt,
          },
        ],
        temperature: 0.2,
        topP: 0.8,
        topK: 32,
        maxOutputTokens: 1536,
        systemPrompt: PLANNING_SYSTEM_PROMPT,
        responseMimeType: "application/json",
      })

      lastRaw = response.text

      const parsed = this.safeParsePlan(lastRaw)

      if (parsed.success) {
        const plan = this.toExecutionPlan(parsed.data)

        const componentTarget = analysis ? Math.min(analysis.components.length + 1, 6) : 0
        const minimumSteps = Math.max(componentTarget, 2)

        const hasMaterialSteps = plan.steps.some((step) => {
          const params = step.parameters ?? {}
          const code = typeof params.code === "string" ? params.code : ""
          return /material|color|shader/i.test(code)
        })

        if (plan.steps.length < minimumSteps || !hasMaterialSteps) {
          errors.push(
            `Plan lacks sufficient detail (steps=${plan.steps.length}, minimum=${minimumSteps}) or material assignments.`
          )
          retries += 1
          continue
        }

        return { plan, rawResponse: lastRaw, retries, analysis }
      }

      errors.push(parsed.error)
      retries += 1
    }

    return { plan: null, rawResponse: lastRaw, errors, retries, analysis }
  }

  private async generateAnalysis(userRequest: string): Promise<PlanAnalysis | undefined> {
    const analysisPrompt = `Analyze the following Blender modeling request and respond with JSON describing the required components and quality targets.

Request: "${userRequest}"

Return JSON with this shape:
{
  "components": ["component name", ...],
  "material_guidelines": ["material or color suggestion", ...],
  "minimum_mesh_objects": number,
  "require_lighting": true/false,
  "require_camera": true/false,
  "notes": ["additional constraints", ...]
}

Components should reflect sub-assemblies (e.g., car body, four wheels, windows, lights). Materials should be realistic. Set require_lighting true unless the user explicitly forbids lighting.`

    try {
      const response = await generateGeminiResponse({
        messages: [{ role: "user", content: analysisPrompt }],
        temperature: 0.75,
        topP: 0.9,
        topK: 64,
        maxOutputTokens: 512,
        systemPrompt: "You are a meticulous 3D scene analyst. Return only JSON.",
        responseMimeType: "application/json",
      })

      const cleaned = this.extractJson(response.text)
      if (!cleaned) return undefined
      const parsed = JSON.parse(cleaned)
      const result = ANALYSIS_SCHEMA.safeParse(parsed)
      if (!result.success) {
        const repaired = this.repairJson(cleaned)
        if (!repaired) {
          return this.refineAnalysis(userRequest)
        }
        try {
          const repairedParsed = JSON.parse(repaired)
          const repairedResult = ANALYSIS_SCHEMA.safeParse(repairedParsed)
          if (!repairedResult.success) {
            return this.refineAnalysis(userRequest)
          }
          const baseAnalysis = this.toAnalysis(repairedResult.data)
          return this.refineAnalysis(userRequest, baseAnalysis)
        } catch {
          return this.refineAnalysis(userRequest)
        }
      }

      const baseAnalysis = this.toAnalysis(result.data)
      return this.refineAnalysis(userRequest, baseAnalysis)
    } catch {
      return this.refineAnalysis(userRequest)
    }
  }

  private safeParsePlan(raw: string): { success: true; data: RawPlan } | { success: false; error: string } {
    const cleaned = this.extractJson(raw)
    if (!cleaned) {
      return { success: false, error: "Planner response did not contain valid JSON" }
    }

    try {
      const parsed = JSON.parse(cleaned)
      const result = PLAN_SCHEMA.safeParse(parsed)
      if (!result.success) {
        const repaired = this.repairJson(cleaned)
        if (!repaired) {
          return { success: false, error: result.error.flatten().formErrors.join("; ") }
        }
        try {
          const repairedParsed = JSON.parse(repaired)
          const repairedResult = PLAN_SCHEMA.safeParse(repairedParsed)
          if (!repairedResult.success) {
            return { success: false, error: repairedResult.error.flatten().formErrors.join("; ") }
          }
          return { success: true, data: repairedResult.data }
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : "Failed to parse repaired plan JSON",
          }
        }
      }
      return { success: true, data: result.data }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Failed to parse plan JSON",
      }
    }
  }

  private extractJson(raw: string): string | null {
    const jsonMatch = raw.match(/\{[\s\S]*\}/)
    return jsonMatch ? jsonMatch[0] : null
  }

  private toExecutionPlan(raw: RawPlan): ExecutionPlan {
    const steps: PlanStep[] = raw.steps.map((step) => ({
      stepNumber: step.step_number,
      action: step.action,
      parameters: step.parameters ?? {},
      rationale: step.rationale,
      expectedOutcome: step.expected_outcome,
    }))

    steps.sort((a, b) => a.stepNumber - b.stepNumber)

    return {
      planSummary: raw.plan_summary,
      steps,
      dependencies: raw.dependencies,
      warnings: raw.warnings,
    }
  }

  private toAnalysis(raw: RawAnalysis): PlanAnalysis {
    return {
      components: raw.components,
      materialGuidelines: raw.material_guidelines,
      minimumMeshObjects: raw.minimum_mesh_objects,
      requireLighting: raw.require_lighting,
      requireCamera: raw.require_camera,
      notes: raw.notes,
    }
  }

  private refineAnalysis(userRequest: string, existing?: PlanAnalysis): PlanAnalysis | undefined {
    const isCarRequest = /(car|vehicle|sedan|supercar|sports car|automobile|truck)/i.test(userRequest)

    if (!isCarRequest) {
      return existing
    }

    const base: PlanAnalysis = existing ?? {
      components: [],
      materialGuidelines: [],
      minimumMeshObjects: undefined,
      requireLighting: undefined,
      requireCamera: undefined,
      notes: [],
    }

    const componentSet = new Map<string, string>()
    for (const component of base.components) {
      const key = component.trim().toLowerCase()
      if (key) {
        componentSet.set(key, component)
      }
    }

    const ensureComponent = (key: string, label: string) => {
      const normalized = key.trim().toLowerCase()
      if (!componentSet.has(normalized)) {
        componentSet.set(normalized, label)
      }
    }

    ensureComponent("car body shell", "Car body shell with cockpit")
    ensureComponent("front-left wheel", "Front-left wheel assembly")
    ensureComponent("front-right wheel", "Front-right wheel assembly")
    ensureComponent("rear-left wheel", "Rear-left wheel assembly")
    ensureComponent("rear-right wheel", "Rear-right wheel assembly")
    ensureComponent("windows and windshield", "Windows and windshield glazing")
    ensureComponent("lighting", "Headlights and taillights")
    ensureComponent("interior basics", "Interior basics (driver seat + steering wheel)")

    const components = Array.from(componentSet.values())

    const materialGuidelines =
      base.materialGuidelines.length > 0
        ? base.materialGuidelines
        : [
            "Apply contrasting materials to body paint, glass, tires, and lights.",
            "Use metallic paint for the body and rubber for the tires.",
          ]

    const notes = Array.from(
      new Set([
        ...(base.notes ?? []),
        "Scale wheels proportionally (0.6–0.8m diameter) and align them with the body.",
        "Position lights at the front and rear; ensure glass materials for windows.",
      ])
    )

    const minimumMeshObjects = Math.max(base.minimumMeshObjects ?? 0, 12)

    return {
      components,
      materialGuidelines,
      minimumMeshObjects,
      requireLighting: base.requireLighting !== false ? true : base.requireLighting,
      requireCamera: base.requireCamera !== false ? true : base.requireCamera,
      notes,
    }
  }

  private repairJson(raw: string): string | null {
    let candidate = raw.trim()
    if (!candidate) return null

    const firstBrace = candidate.indexOf("{")
    if (firstBrace === -1) {
      return null
    }
    candidate = candidate.slice(firstBrace)

    const lastObjectClose = candidate.lastIndexOf("}")
    const lastArrayClose = candidate.lastIndexOf("]")
    const lastClose = Math.max(lastObjectClose, lastArrayClose)
    if (lastClose !== -1 && lastClose < candidate.length - 1) {
      candidate = candidate.slice(0, lastClose + 1)
    }

    candidate = candidate.replace(/,\s*(\}|\])/g, "$1")

    const openBraces = (candidate.match(/{/g) ?? []).length
    let closeBraces = (candidate.match(/}/g) ?? []).length
    while (closeBraces < openBraces) {
      candidate += "}"
      closeBraces += 1
    }

    const openBrackets = (candidate.match(/\[/g) ?? []).length
    let closeBrackets = (candidate.match(/]/g) ?? []).length
    while (closeBrackets < openBrackets) {
      candidate += "]"
      closeBrackets += 1
    }

    try {
      JSON.parse(candidate)
      return candidate
    } catch {
      return null
    }
  }
}
