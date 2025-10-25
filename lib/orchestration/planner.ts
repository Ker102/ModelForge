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

const PLANNING_SYSTEM_PROMPT = `You are a Blender MCP automation planner. Produce structured plans that describe which MCP tools to call and why before any actions are executed.`

export class BlenderPlanner {
  constructor(private readonly maxRetries = 1) {}

  async generatePlan(userRequest: string): Promise<PlanGenerationResult> {
    const filteredTools = filterRelevantTools(userRequest)
    const toolListing = formatToolListForPrompt(filteredTools)

    const planningPrompt = `User request: "${userRequest}"

Plan before acting. Use only the tools listed below and start every plan with get_scene_info to capture context. Provide concise, numbered steps.

${toolListing}

Return JSON with the shape:
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
}

Rules:
- Each step should call exactly one tool.
- Only include parameters required by the tool; omit null/undefined.
- Provide rationales that explain why the step is needed.
- Explicitly mention when follow-up steps rely on previous results.`

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
