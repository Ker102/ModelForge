/**
 * Chains Module
 * 
 * LangChain chains for orchestrating AI operations
 */

import { createGeminiModel } from "./index"
import { planningPrompt, validationPrompt, recoveryPrompt, codeGenerationPrompt } from "./prompts"
import { z } from "zod"

// ============================================================================
// Output Schemas
// ============================================================================

const PlanStepSchema = z.object({
    action: z.string(),
    parameters: z.record(z.unknown()).optional().default({}),
    rationale: z.string(),
    expected_outcome: z.string(),
})

const PlanSchema = z.object({
    steps: z.array(PlanStepSchema).min(1),
    dependencies: z.array(z.string()).optional().default([]),
    warnings: z.array(z.string()).optional().default([]),
})

const ValidationSchema = z.object({
    success: z.boolean(),
    reason: z.string().optional(),
    suggestions: z.array(z.string()).optional().default([]),
})

const RecoverySchema = z.object({
    action: z.string(),
    parameters: z.record(z.unknown()).optional().default({}),
    rationale: z.string(),
})

export type PlanStep = z.infer<typeof PlanStepSchema>
export type Plan = z.infer<typeof PlanSchema>
export type ValidationResult = z.infer<typeof ValidationSchema>
export type RecoveryAction = z.infer<typeof RecoverySchema>

// ============================================================================
// Chain Functions
// ============================================================================

/**
 * Generate an execution plan for a user request
 */
export async function generatePlan(options: {
    request: string
    sceneState?: string
    tools: string[]
    context?: string
}): Promise<Plan> {
    const model = createGeminiModel({ temperature: 0.3 })

    const formattedPrompt = await planningPrompt.format({
        request: options.request,
        sceneState: options.sceneState ?? "Unknown",
        tools: options.tools.join(", "),
        context: options.context ?? "",
    })

    const response = await model.invoke(formattedPrompt)
    const content = response.content as string

    // Extract JSON from response
    const jsonMatch = content.match(/\{[\s\S]*\}/)
    if (!jsonMatch) {
        throw new Error("Failed to extract JSON plan from response")
    }

    const parsed = JSON.parse(jsonMatch[0])
    return PlanSchema.parse(parsed)
}

/**
 * Validate a step execution result
 */
export async function validateStep(options: {
    stepDescription: string
    expectedOutcome: string
    actualResult: string
}): Promise<ValidationResult> {
    const model = createGeminiModel({ temperature: 0.1 })

    const formattedPrompt = await validationPrompt.format({
        stepDescription: options.stepDescription,
        expectedOutcome: options.expectedOutcome,
        actualResult: options.actualResult,
    })

    const response = await model.invoke(formattedPrompt)
    const content = response.content as string

    const jsonMatch = content.match(/\{[\s\S]*\}/)
    if (!jsonMatch) {
        return { success: false, reason: "Failed to parse validation response", suggestions: [] }
    }

    const parsed = JSON.parse(jsonMatch[0])
    return ValidationSchema.parse(parsed)
}

/**
 * Generate a recovery action for a failed step
 */
export async function generateRecovery(options: {
    stepDescription: string
    error: string
    sceneState?: string
}): Promise<RecoveryAction> {
    const model = createGeminiModel({ temperature: 0.2 })

    const formattedPrompt = await recoveryPrompt.format({
        stepDescription: options.stepDescription,
        error: options.error,
        sceneState: options.sceneState ?? "Unknown",
    })

    const response = await model.invoke(formattedPrompt)
    const content = response.content as string

    const jsonMatch = content.match(/\{[\s\S]*\}/)
    if (!jsonMatch) {
        return { action: "skip", parameters: {}, rationale: "Failed to generate recovery" }
    }

    const parsed = JSON.parse(jsonMatch[0])
    return RecoverySchema.parse(parsed)
}

/**
 * Generate Blender Python code
 */
export async function generateCode(options: {
    request: string
    context?: string
    applyMaterials?: boolean
    namingPrefix?: string
    constraints?: string
}): Promise<string> {
    const model = createGeminiModel({
        temperature: 0.2,
        maxOutputTokens: 4096,
    })

    const formattedPrompt = await codeGenerationPrompt.format({
        request: options.request,
        context: options.context ?? "",
        applyMaterials: options.applyMaterials ?? true ? "Yes, apply appropriate materials" : "No materials needed",
        namingPrefix: options.namingPrefix ?? "ModelForge_",
        constraints: options.constraints ?? "None",
    })

    const response = await model.invoke(formattedPrompt)
    let code = response.content as string

    // Extract code from markdown code blocks if present
    const codeBlockMatch = code.match(/```python\n([\s\S]*?)```/)
    if (codeBlockMatch) {
        code = codeBlockMatch[1]
    }

    return code.trim()
}
