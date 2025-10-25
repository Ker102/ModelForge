export interface PlanStep {
  stepNumber: number
  action: string
  parameters: Record<string, unknown>
  rationale: string
  expectedOutcome: string
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
}
