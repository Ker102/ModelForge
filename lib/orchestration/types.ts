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
}

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
