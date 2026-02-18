/**
 * Guided Workflow System — Type Definitions
 *
 * Provides types for the human-in-the-loop workflow where each creation step
 * gets a tool recommendation and the user controls execution.
 */

import type { Strategy } from "./strategy-types"

// ─── Tool classification for each step ────────────────────────────

export type WorkflowTool = "blender_agent" | "neural" | "manual"

export type WorkflowCategory =
    | "geometry"
    | "topology"
    | "uv"
    | "texturing"
    | "rigging"
    | "animation"
    | "lighting"
    | "export"
    | "composition"
    | "other"

// ─── Step status lifecycle ────────────────────────────────────────

export type WorkflowStepStatus =
    | "pending"     // Not yet acted on
    | "running"     // Currently executing
    | "completed"   // Successfully executed
    | "failed"      // Execution failed
    | "skipped"     // User chose to skip
    | "manual"      // User handled it manually

export type WorkflowStepAction = "execute" | "skip" | "manual_done"

// ─── Individual workflow step ─────────────────────────────────────

export interface WorkflowStep {
    /** Unique step ID (e.g. "step-1-geometry") */
    id: string
    stepNumber: number
    /** Short title (e.g. "Base Mesh Generation") */
    title: string
    /** What this step does (e.g. "Generate the initial dragon geometry from text description") */
    description: string
    /** Best tool for this step */
    recommendedTool: WorkflowTool
    /** WHY this tool is the best choice */
    toolReasoning: string
    /** Other valid tools the user could use instead */
    alternativeTools: WorkflowTool[]
    /** Creation category */
    category: WorkflowCategory
    /** Estimated time (e.g. "~30s", "~2min") */
    estimatedDuration: string
    /** Whether the previous step must complete first */
    requiresPreviousStep: boolean
    /** Pro tip for this step */
    tips?: string
    /** Current status */
    status: WorkflowStepStatus
    /** Neural provider slug if tool is "neural" (e.g. "hunyuan-shape") */
    neuralProvider?: string
    /** Blender agent action if tool is "blender_agent" (e.g. "execute_code") */
    blenderAction?: string
    /** Error message if step failed */
    error?: string
    /** Output path if step produced a file */
    outputPath?: string
}

// ─── Full workflow proposal ───────────────────────────────────────

export interface WorkflowProposal {
    /** Unique workflow ID */
    id: string
    /** Human-readable title (e.g. "Dragon Character Creation Workflow") */
    title: string
    /** Strategy from the router */
    strategy: Strategy
    /** Ordered list of recommended steps */
    steps: WorkflowStep[]
    /** General tips for the overall workflow */
    overallTips: string[]
    /** The original user request */
    userRequest: string
    /** Timestamp */
    createdAt: string
}

// ─── Step execution request (from UI to API) ──────────────────────

export interface WorkflowStepRequest {
    conversationId: string
    workflowId: string
    stepId: string
    action: WorkflowStepAction
}

// ─── Step execution result (API to UI) ────────────────────────────

export interface WorkflowStepResult {
    stepId: string
    status: WorkflowStepStatus
    /** Result message */
    message?: string
    /** Error details if failed */
    error?: string
    /** Output file path if applicable */
    outputPath?: string
    /** Execution time in ms */
    durationMs?: number
}
