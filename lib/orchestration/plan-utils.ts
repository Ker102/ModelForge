import type { PlanAnalysis, PlanStep, PlanningMetadata } from "./types"

const toNumber = (value: unknown, fallback: number) =>
  typeof value === "number" && !Number.isNaN(value) ? value : fallback

export const parsePlanStep = (raw: unknown, index: number): PlanStep | null => {
  if (!raw || typeof raw !== "object") return null
  const obj = raw as Record<string, unknown>
  const stepNumber = toNumber(obj.stepNumber ?? obj.step_number, index + 1)
  const action = typeof obj.action === "string" ? obj.action : ""
  if (!action) return null
  const parameters =
    obj.parameters && typeof obj.parameters === "object"
      ? (obj.parameters as Record<string, unknown>)
      : {}
  const rationale =
    typeof obj.rationale === "string"
      ? obj.rationale
      : typeof obj.rationale === "number"
      ? String(obj.rationale)
      : ""
  const expectedOutcome =
    typeof obj.expectedOutcome === "string"
      ? obj.expectedOutcome
      : typeof obj.expected_outcome === "string"
      ? obj.expected_outcome
      : ""

  return {
    stepNumber,
    action,
    parameters,
    rationale,
    expectedOutcome,
  }
}

const toBoolean = (value: unknown, fallback: boolean | undefined = undefined) => {
  if (typeof value === "boolean") return value
  return fallback
}

const toStringArray = (value: unknown) =>
  Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : undefined

export const parsePlanningMetadata = (raw: unknown): PlanningMetadata | undefined => {
  if (!raw || typeof raw !== "object") return undefined
  const obj = raw as Record<string, unknown>
  const planSummary =
    typeof obj.planSummary === "string"
      ? obj.planSummary
      : typeof obj.plan_summary === "string"
      ? obj.plan_summary
      : undefined
  const rawSteps = Array.isArray(obj.planSteps)
    ? obj.planSteps
    : Array.isArray(obj.plan_steps)
    ? obj.plan_steps
    : []
  const planSteps = rawSteps
    .map((step, index) => parsePlanStep(step, index))
    .filter((step): step is PlanStep => Boolean(step))

  if (!planSummary || planSteps.length === 0) {
    return undefined
  }

  const rawPlan =
    typeof obj.rawPlan === "string"
      ? obj.rawPlan
      : typeof obj.raw_plan === "string"
      ? obj.raw_plan
      : ""

  const sceneSnapshot =
    typeof obj.sceneSnapshot === "string"
      ? obj.sceneSnapshot
      : typeof obj.scene_snapshot === "string"
      ? obj.scene_snapshot
      : null

  return {
    planSummary,
    planSteps,
    rawPlan,
    retries: toNumber(obj.retries, 0),
    executionSuccess: toBoolean(obj.executionSuccess, false) ?? false,
    errors: toStringArray(obj.errors),
    fallbackUsed: toBoolean(obj.fallbackUsed ?? obj.fallback_used),
    executionLog: Array.isArray(obj.executionLog)
      ? (obj.executionLog as Array<Record<string, unknown>>)
      : undefined,
    sceneSnapshot,
    analysis: parsePlanAnalysis(obj.analysis ?? obj.planAnalysis ?? obj.analysis_summary),
  }
}

const parsePlanAnalysis = (raw: unknown): PlanAnalysis | undefined => {
  if (!raw || typeof raw !== "object") return undefined
  const obj = raw as Record<string, unknown>
  const components = Array.isArray(obj.components)
    ? obj.components.filter((item): item is string => typeof item === "string")
    : Array.isArray(obj.component_list)
    ? obj.component_list.filter((item): item is string => typeof item === "string")
    : []
  const materialGuidelines = Array.isArray(obj.materialGuidelines)
    ? obj.materialGuidelines.filter((item): item is string => typeof item === "string")
    : Array.isArray(obj.material_guidelines)
    ? obj.material_guidelines.filter((item): item is string => typeof item === "string")
    : []
  const notes = Array.isArray(obj.notes)
    ? obj.notes.filter((item): item is string => typeof item === "string")
    : undefined

  if (components.length === 0 && materialGuidelines.length === 0 && !notes?.length) {
    return undefined
  }

  return {
    components,
    materialGuidelines,
    minimumMeshObjects:
      typeof obj.minimumMeshObjects === "number"
        ? obj.minimumMeshObjects
        : typeof obj.minimum_mesh_objects === "number"
        ? obj.minimum_mesh_objects
        : undefined,
    requireLighting:
      typeof obj.requireLighting === "boolean"
        ? obj.requireLighting
        : typeof obj.require_lighting === "boolean"
        ? obj.require_lighting
        : undefined,
    requireCamera:
      typeof obj.requireCamera === "boolean"
        ? obj.requireCamera
        : typeof obj.require_camera === "boolean"
        ? obj.require_camera
        : undefined,
    notes,
  }
}
