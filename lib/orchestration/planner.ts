import { z } from "zod"

import { generateGeminiResponse } from "@/lib/gemini"
import { filterRelevantTools, formatToolListForPrompt } from "./tool-filter"
import { ExecutionPlan, PlanGenerationResult, PlanStep } from "./types"

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

const PLANNING_SYSTEM_PROMPT = `You are ModelForge's orchestration planner. Your job is to produce reliable, step-by-step tool plans for controlling Blender through MCP **before** any commands execute.

Follow these principles:
- Think in ReAct style: observe → plan → act; never jump straight to code.
- Always begin with \"get_scene_info\" to capture current context unless a previous step already provided a fresh snapshot.
- Choose tools from the provided list only. If a capability is unavailable, omit it instead of inventing new tools.
- Prefer declarative tools over generic code. Resort to \"execute_code\" only when no other tool can accomplish the task, and keep scripts short, idempotent, and focused.
- When using \"execute_code\", the parameters object must include a single key \"code\" containing the Python string (do not use alternate names like \"script\", \"python\", or \"body\").
- Use descriptive object names (snake_case, no spaces). Default coordinates are Blender units in [x, y, z]. Colors are RGBA floats 0.0–1.0.
- Break complex requests into atomic steps; each step must call exactly one tool with just the parameters that tool understands.
- Note dependencies or cautions when a later step assumes a previous result (e.g., material application requires the object to exist).
- Output strict JSON that matches the requested schema—no commentary, Markdown, or trailing text.`

export class BlenderPlanner {
  constructor(private readonly maxRetries = 1) {}

  async generatePlan(userRequest: string): Promise<PlanGenerationResult> {
    const filteredTools = filterRelevantTools(userRequest)
    const toolListing = formatToolListForPrompt(filteredTools)

    const planningPrompt = `User request: "${userRequest}"

Available tools (choose from this list):
${toolListing}

Produce a plan **before** executing anything. Requirement checklist:
1. Step 1 must be get_scene_info (unless the user explicitly supplied a recent scene snapshot).
2. Each subsequent step references exactly one tool from the list above.
3. Parameters must match the tool expectations. Omit optional parameters when not needed.
4. Rationale should state why the step is necessary and how it advances the user goal.
5. Expected outcome should describe what Blender should report after the tool call.
6. If a step depends on the result of a previous step, include that dependency in the dependencies array.
7. Highlight any risks or manual follow-up in the warnings array.

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
        maxOutputTokens: 768,
        systemPrompt: PLANNING_SYSTEM_PROMPT,
      })

      lastRaw = response.text

      const parsed = this.safeParsePlan(lastRaw)

      if (parsed.success) {
        const plan = this.toExecutionPlan(parsed.data)
        return { plan, rawResponse: lastRaw, retries }
      }

      errors.push(parsed.error)
      retries += 1
    }

    return { plan: null, rawResponse: lastRaw, errors, retries }
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
        return { success: false, error: result.error.flatten().formErrors.join("; ") }
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
}
