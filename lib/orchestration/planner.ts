import { createBlenderAgent, type BlenderAgent } from "@/lib/ai/agents"
import { type Plan } from "@/lib/ai/chains"
import { type LlmProviderSpec } from "@/lib/llm"
import { createConversationMemory, type ConversationMemory } from "@/lib/memory"
import { filterRelevantTools } from "./tool-filter"
import { ExecutionPlan, PlanAnalysis, PlanGenerationResult, PlanStep } from "./types"

interface PlanningOptions {
  sceneSummary?: string
  allowHyper3dAssets?: boolean
  allowSketchfabAssets?: boolean
  allowPolyHavenAssets?: boolean
  researchContext?: string
  /** Project ID for conversation memory */
  projectId?: string
  /** Enable conversation memory for context-aware planning */
  useMemory?: boolean
  /** Existing conversation memory instance */
  memory?: ConversationMemory
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

    // 2. Retrieve conversation memory context if enabled
    let memoryContext = ""
    if (options.useMemory && (options.projectId || options.memory)) {
      try {
        const memory = options.memory ?? createConversationMemory(options.projectId!)
        const relevantMessages = await memory.retrieveContext(userRequest, {
          limit: 5,
          minSimilarity: 0.5,
          roles: ["user", "assistant"],
        })
        memoryContext = memory.formatContextForPrompt(relevantMessages)
      } catch (error) {
        console.warn("Memory retrieval failed:", error)
      }
    }

    // 3. Build enhanced request with context
    let enhancedRequest = userRequest
    if (options.sceneSummary) {
      enhancedRequest = `Current Scene: ${options.sceneSummary}\n\nRequest: ${userRequest}`
    }
    if (memoryContext) {
      enhancedRequest = `${memoryContext}\n\n${enhancedRequest}`
    }

    try {
      // 4. Generate Plan using LangChain Agent
      const plan = await agent.plan(enhancedRequest)

      // 5. Transform to legacy ExecutionPlan format
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

