/**
 * Agents Module
 * 
 * LangChain agent implementation for Blender MCP orchestration
 */

import { createGeminiModel } from "./index"
import { generatePlan, validateStep, generateRecovery, type Plan, type PlanStep } from "./chains"
import { formatContextFromSources, type RAGResult } from "./rag"
import { similaritySearch } from "./vectorstore"
import { analyzeViewport, compareWithExpectation, type VisionAnalysisResult } from "./vision"

// ============================================================================
// Types
// ============================================================================

export interface AgentState {
    request: string
    plan?: Plan
    currentStepIndex: number
    completedSteps: Array<{ step: PlanStep; result: unknown }>
    failedSteps: Array<{ step: PlanStep; error: string }>
    sceneState?: unknown
    logs: AgentLog[]
    /** Latest viewport screenshot (base64) */
    viewportImage?: string
    /** Latest vision analysis result */
    lastVisionAnalysis?: VisionAnalysisResult
}

export interface AgentLog {
    timestamp: Date
    type: "plan" | "execute" | "validate" | "recover" | "complete" | "error" | "vision"
    message: string
    data?: unknown
}

export interface AgentConfig {
    maxRetries: number
    useRAG: boolean
    ragSource?: string
    /** Enable visual feedback loop */
    useVision: boolean
    /** Max visual validation iterations per step */
    maxVisionIterations: number
    onLog?: (log: AgentLog) => void
    onStepComplete?: (step: PlanStep, result: unknown) => void
    /** Callback to capture viewport screenshot */
    onCaptureViewport?: () => Promise<string>
}

// ============================================================================
// MCP Tool Definitions
// ============================================================================

const MCP_TOOLS = [
    "get_scene_info",
    "get_object_info",
    "get_all_object_info",
    "get_viewport_screenshot",
    "execute_code",
    "get_polyhaven_status",
    "search_polyhaven_assets",
    "download_polyhaven_asset",
    "set_texture",
    "get_hyper3d_status",
    "create_rodin_job",
    "poll_rodin_job_status",
    "import_generated_asset",
    "get_sketchfab_status",
    "search_sketchfab_models",
    "download_sketchfab_model",
]

// ============================================================================
// Agent Class
// ============================================================================

/**
 * BlenderAgent - ReAct-style agent for orchestrating Blender via MCP
 */
export class BlenderAgent {
    private config: AgentConfig
    private state: AgentState

    constructor(config: Partial<AgentConfig> = {}) {
        this.config = {
            maxRetries: config.maxRetries ?? 2,
            useRAG: config.useRAG ?? true,
            ragSource: config.ragSource ?? "blender-docs",
            useVision: config.useVision ?? false,
            maxVisionIterations: config.maxVisionIterations ?? 3,
            onLog: config.onLog,
            onStepComplete: config.onStepComplete,
            onCaptureViewport: config.onCaptureViewport,
        }

        this.state = {
            request: "",
            currentStepIndex: 0,
            completedSteps: [],
            failedSteps: [],
            logs: [],
        }
    }

    /**
     * Log an event
     */
    private log(type: AgentLog["type"], message: string, data?: unknown) {
        const log: AgentLog = { timestamp: new Date(), type, message, data }
        this.state.logs.push(log)
        this.config.onLog?.(log)
    }

    /**
     * Generate a plan for the user request
     */
    async plan(request: string): Promise<Plan> {
        this.state.request = request
        this.log("plan", `Planning for: ${request}`)

        // Optionally retrieve context from RAG
        let context = ""
        if (this.config.useRAG) {
            try {
                const sources = await similaritySearch(request, {
                    limit: 5,
                    source: this.config.ragSource,
                    minSimilarity: 0.4,
                })
                context = formatContextFromSources(sources)
                this.log("plan", `Retrieved ${sources.length} relevant documents for context`)
            } catch (error) {
                this.log("error", `RAG retrieval failed: ${error}`)
            }
        }

        const plan = await generatePlan({
            request,
            tools: MCP_TOOLS,
            context,
            sceneState: JSON.stringify(this.state.sceneState ?? {}),
        })

        this.state.plan = plan
        this.log("plan", `Generated plan with ${plan.steps.length} steps`, plan)

        return plan
    }

    /**
     * Load an existing plan into the agent
     */
    loadPlan(plan: Plan) {
        this.state.plan = plan
        this.state.currentStepIndex = 0
        this.log("plan", `Loaded external plan with ${plan.steps.length} steps`, plan)
    }

    /**
     * Execute the current plan
     * Note: This is a framework method - actual MCP execution happens externally
     */
    async executeStep(
        stepIndex: number,
        executor: (step: PlanStep) => Promise<unknown>
    ): Promise<{ success: boolean; result?: unknown; error?: string }> {
        if (!this.state.plan) {
            throw new Error("No plan available. Call plan() first.")
        }

        const step = this.state.plan.steps[stepIndex]
        if (!step) {
            throw new Error(`Invalid step index: ${stepIndex}`)
        }

        this.log("execute", `Executing step ${stepIndex + 1}: ${step.action}`, step)

        let lastError: string | undefined

        for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
            try {
                const result = await executor(step)

                // Validate the result
                const validation = await validateStep({
                    stepDescription: `${step.action} - ${step.rationale}`,
                    expectedOutcome: step.expected_outcome,
                    actualResult: JSON.stringify(result),
                })

                if (validation.success) {
                    this.state.completedSteps.push({ step, result })
                    this.config.onStepComplete?.(step, result)
                    this.log("validate", `Step ${stepIndex + 1} validated successfully`)
                    return { success: true, result }
                }

                lastError = validation.reason ?? "Validation failed"
                this.log("validate", `Step ${stepIndex + 1} validation failed: ${lastError}`)

                // Try recovery if we have retries left
                if (attempt < this.config.maxRetries) {
                    const recovery = await generateRecovery({
                        stepDescription: step.action,
                        error: lastError ?? "Unknown error",
                        sceneState: JSON.stringify(this.state.sceneState ?? {}),
                    })

                    this.log("recover", `Recovery suggestion: ${recovery.action}`, recovery)

                    if (recovery.action === "skip") {
                        break
                    }

                    // Update step parameters for retry
                    step.parameters = { ...step.parameters, ...recovery.parameters }
                }
            } catch (error) {
                lastError = error instanceof Error ? error.message : String(error)
                this.log("error", `Step ${stepIndex + 1} failed: ${lastError}`)
            }
        }

        this.state.failedSteps.push({ step, error: lastError ?? "Unknown error" })
        return { success: false, error: lastError }
    }

    /**
     * Capture viewport screenshot and analyze it with vision
     * Requires onCaptureViewport callback to be configured
     */
    async captureAndAnalyzeViewport(context?: string): Promise<VisionAnalysisResult | null> {
        if (!this.config.onCaptureViewport) {
            this.log("vision", "Vision capture not available - no onCaptureViewport callback")
            return null
        }

        try {
            this.log("vision", "Capturing viewport screenshot...")
            const imageBase64 = await this.config.onCaptureViewport()
            this.state.viewportImage = imageBase64

            this.log("vision", "Analyzing viewport with Gemini Vision...")
            const analysis = await analyzeViewport(imageBase64, context ?? this.state.request)
            this.state.lastVisionAnalysis = analysis

            this.log("vision", `Vision analysis complete: ${analysis.assessment}`, analysis)
            return analysis
        } catch (error) {
            this.log("error", `Vision capture/analysis failed: ${error}`)
            return null
        }
    }

    /**
     * Validate a step's expected outcome visually
     */
    async validateStepVisually(expectedOutcome: string): Promise<{
        matches: boolean
        analysis?: VisionAnalysisResult
        comparison?: { observed: string; differences: string[] }
    }> {
        if (!this.config.useVision || !this.config.onCaptureViewport) {
            return { matches: true } // Skip visual validation if not enabled
        }

        try {
            const imageBase64 = await this.config.onCaptureViewport()
            this.state.viewportImage = imageBase64

            // Compare with expected outcome
            const comparison = await compareWithExpectation(imageBase64, expectedOutcome)

            // Also get a full analysis for context
            const analysis = await analyzeViewport(imageBase64, expectedOutcome)
            this.state.lastVisionAnalysis = analysis

            this.log("vision", `Visual validation: ${comparison.matches ? "PASS" : "FAIL"}`, {
                comparison,
                analysis,
            })

            return {
                matches: comparison.matches,
                analysis,
                comparison: {
                    observed: comparison.observed,
                    differences: comparison.differences,
                },
            }
        } catch (error) {
            this.log("error", `Visual validation failed: ${error}`)
            return { matches: true } // Don't block on vision errors
        }
    }

    /**
     * Get the current agent state
     */
    getState(): AgentState {
        return { ...this.state }
    }

    /**
     * Reset the agent state
     */
    reset() {
        this.state = {
            request: "",
            currentStepIndex: 0,
            completedSteps: [],
            failedSteps: [],
            logs: [],
            viewportImage: undefined,
            lastVisionAnalysis: undefined,
        }
    }
}

/**
 * Create a new BlenderAgent instance
 */
export function createBlenderAgent(config?: Partial<AgentConfig>): BlenderAgent {
    return new BlenderAgent(config)
}
