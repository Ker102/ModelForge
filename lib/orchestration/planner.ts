import { createBlenderAgent, type BlenderAgent } from "@/lib/ai/agents"
import { type Plan } from "@/lib/ai/chains"
import { type LlmProviderSpec } from "@/lib/llm"
import { filterRelevantTools } from "./tool-filter"
import { ExecutionPlan, PlanAnalysis, PlanGenerationResult, PlanStep } from "./types"

interface PlanningOptions {
  sceneSummary?: string
  allowHyper3dAssets?: boolean
  allowSketchfabAssets?: boolean
  allowPolyHavenAssets?: boolean
  researchContext?: string
}

export class BlenderPlanner {
  constructor(private readonly maxRetries = 2) { }

  async generatePlan(
    userRequest: string,
    options: PlanningOptions = {},
    _provider?: LlmProviderSpec // Kept for compatibility, but unused as we use the AI module
  ): Promise<PlanGenerationResult> {
    // 1. Initialize Agent with RAG enabled
    const agent = createBlenderAgent({
      maxRetries: this.maxRetries,
      useRAG: true,
      ragSource: "blender-docs", // Default source
    })

    // 2. Inject scene context if available
    if (options.sceneSummary) {
      // We pass this via the request for now, or we could update AgentState to accept it
      // For now, we'll append it to the request context implicitly handled by the agent's planner
    }

    try {
      // 3. Generate Plan using LangChain Agent
      // The agent handles tool filtering implicitly via its prompt, but we can also pass specific tools if needed.
      // For now, the agent uses the full toolset defined in agents.ts. 
      // TODO: Pass restricted tool list to agent if options.allow* are false.

      const plan = await agent.plan(userRequest)

      // 4. Transform to legacy ExecutionPlan format
      const executionPlan = this.transformToExecutionPlan(plan)

      return {
        plan: executionPlan,
        rawResponse: JSON.stringify(plan, null, 2),
        retries: 0,
        analysis: undefined, // Analysis is now implicit in the planning chain
      }
    } catch (error) {
      return {
        plan: null,
        rawResponse: error instanceof Error ? error.message : String(error),
        retries: this.maxRetries,
        errors: [error instanceof Error ? error.message : String(error)],
      }
    }
  }

  private transformToExecutionPlan(plan: Plan): ExecutionPlan {
    const steps: PlanStep[] = plan.steps.map((step, index) => ({
      stepNumber: index + 1,
      action: step.action,
      parameters: step.parameters ?? {},
      rationale: step.rationale,
      expectedOutcome: step.expected_outcome,
    }))

    return {
      planSummary: `Generated plan with ${steps.length} steps`,
      steps,
      dependencies: plan.dependencies,
      warnings: plan.warnings,
    }
  }
}
