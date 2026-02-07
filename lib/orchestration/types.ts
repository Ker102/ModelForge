export interface PlanStep {
  stepNumber: number
  action: string
  parameters: Record<string, unknown>
  rationale: string
  expectedOutcome: string
}

export interface PlanAnalysis {
  components: string[]
  materialGuidelines: string[]
  minimumMeshObjects?: number
  requireLighting?: boolean
  requireCamera?: boolean
  notes?: string[]
}

export interface ExecutionPlan {
  planSummary: string
  steps: PlanStep[]
  dependencies?: string[]
  warnings?: string[]
}

export interface PlanGenerationResult {
  plan: ExecutionPlan | null
  rawResponse: string
  errors?: string[]
  retries?: number
  analysis?: PlanAnalysis
}

export interface ResearchSource {
  title: string
  url: string
  snippet?: string
}

export interface ToolMetadata {
  name: string
  description: string
  category: ToolCategory
}

export type ToolCategory =
  | "inspection"
  | "geometry"
  | "materials"
  | "lighting"
  | "camera"
  | "assets"
  | "advanced"
  | "other"

export interface ExecutionLogEntry {
  timestamp: string
  tool: string
  parameters: Record<string, unknown>
  result?: unknown
  error?: string
  /** Log entry type for filtering/display */
  logType?: "plan" | "execute" | "validate" | "recover" | "vision" | "audit" | "reasoning" | "system"
  /** Human-readable description of what happened */
  detail?: string
  /** Visual validation result (if vision feedback is enabled) */
  visualValidation?: {
    screenshot?: string
    analysis?: {
      description: string
      assessment: string
      issues: string[]
      suggestions: string[]
    }
    matches?: boolean
    differences?: string[]
  }
}

/**
 * Real-time stream event types sent during agent execution
 */
export type AgentStreamEvent =
  | { type: "agent:planning_start"; timestamp: string }
  | { type: "agent:planning_reasoning"; timestamp: string; reasoning: string }
  | { type: "agent:planning_complete"; timestamp: string; stepCount: number; summary: string }
  | { type: "agent:step_start"; timestamp: string; stepIndex: number; stepCount: number; action: string; rationale: string }
  | { type: "agent:step_result"; timestamp: string; stepIndex: number; action: string; result: unknown; success: boolean }
  | { type: "agent:step_validate"; timestamp: string; stepIndex: number; action: string; valid: boolean; reason?: string }
  | { type: "agent:step_recover"; timestamp: string; stepIndex: number; action: string; recoveryAction: string; rationale: string }
  | { type: "agent:step_error"; timestamp: string; stepIndex: number; action: string; error: string; attempt: number }
  | { type: "agent:vision"; timestamp: string; stepIndex?: number; assessment: string; issues: string[] }
  | { type: "agent:audit"; timestamp: string; success: boolean; reason?: string }
  | { type: "agent:complete"; timestamp: string; success: boolean; completedCount: number; failedCount: number }

export interface PlanningMetadata {
  planSummary: string
  planSteps: PlanStep[]
  rawPlan: string
  retries: number
  executionSuccess: boolean
  errors?: string[]
  fallbackUsed?: boolean
  executionLog?: ExecutionLogEntry[]
  sceneSnapshot?: string | null
  analysis?: PlanAnalysis
  researchSummary?: string
  researchSources?: ResearchSource[]
}
