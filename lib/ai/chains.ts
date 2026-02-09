/**
 * Chains Module
 * 
 * LangChain chains for orchestrating AI operations
 */

import { createGeminiModel } from "./index"
import { planningPrompt, validationPrompt, recoveryPrompt, codeGenerationPrompt } from "./prompts"
import { formatToolListForPrompt } from "@/lib/orchestration/tool-filter"
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

/** Extended result types that preserve LLM reasoning */
export interface PlanWithReasoning {
    plan: Plan
    reasoning: string
    rawResponse: string
}

export interface ValidationWithReasoning {
    result: ValidationResult
    reasoning: string
}

export interface RecoveryWithReasoning {
    recovery: RecoveryAction
    reasoning: string
}

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
}): Promise<PlanWithReasoning> {
    const model = createGeminiModel({ temperature: 0.3, maxOutputTokens: 65536 })

    const formattedPrompt = await planningPrompt.format({
        request: options.request,
        sceneState: options.sceneState ?? "Unknown",
        tools: formatToolListForPrompt(options.tools),
        context: options.context ?? "",
    })

    const response = await model.invoke(formattedPrompt)
    const content = response.content as string

    // Extract reasoning (everything before the JSON block)
    // Find the outermost JSON object by matching braces
    const jsonStart = content.indexOf('{')
    if (jsonStart === -1) {
        throw new Error("Failed to extract JSON plan from response")
    }

    // Find matching closing brace by counting (string-aware)
    let braceCount = 0
    let jsonEnd = -1
    let inString = false
    for (let i = jsonStart; i < content.length; i++) {
        const ch = content[i]
        if (inString) {
            if (ch === '\\') {
                i++ // skip escaped character
            } else if (ch === '"') {
                inString = false
            }
        } else {
            if (ch === '"') {
                inString = true
            } else if (ch === '{') {
                braceCount++
            } else if (ch === '}') {
                braceCount--
                if (braceCount === 0) {
                    jsonEnd = i + 1
                    break
                }
            }
        }
    }

    if (jsonEnd === -1) {
        throw new Error("Failed to find complete JSON object in response (possible truncation)")
    }

    const reasoning = content.substring(0, jsonStart).trim()
    const jsonStr = content.substring(jsonStart, jsonEnd)

    try {
        const parsed = JSON.parse(jsonStr)
        const plan = PlanSchema.parse(parsed)
        return { plan, reasoning, rawResponse: content }
    } catch (parseError) {
        const errMsg = parseError instanceof Error ? parseError.message : String(parseError)
        throw new Error(`Failed to parse plan from LLM output: ${errMsg}\n\nRaw JSON (first 800 chars):\n${jsonStr.substring(0, 800)}`)
    }
}

/**
 * Validate a step execution result
 */
export async function validateStep(options: {
    stepDescription: string
    expectedOutcome: string
    actualResult: string
}): Promise<ValidationWithReasoning> {
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
        return {
            result: { success: false, reason: "Failed to parse validation response", suggestions: [] },
            reasoning: content,
        }
    }

    const jsonStart = content.indexOf(jsonMatch[0])
    const reasoning = content.substring(0, jsonStart).trim()

    try {
        const parsed = JSON.parse(jsonMatch[0])
        return { result: ValidationSchema.parse(parsed), reasoning }
    } catch {
        return {
            result: { success: false, reason: "Failed to parse validation response", suggestions: [] },
            reasoning,
        }
    }
}

/**
 * Generate a recovery action for a failed step
 */
export async function generateRecovery(options: {
    stepDescription: string
    error: string
    sceneState?: string
}): Promise<RecoveryWithReasoning> {
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
        return {
            recovery: { action: "skip", parameters: {}, rationale: "Failed to generate recovery" },
            reasoning: content,
        }
    }

    const jsonStart = content.indexOf(jsonMatch[0])
    const reasoning = content.substring(0, jsonStart).trim()

    try {
        const parsed = JSON.parse(jsonMatch[0])
        return { recovery: RecoverySchema.parse(parsed), reasoning }
    } catch {
        return {
            recovery: { action: "skip", parameters: {}, rationale: "Failed to parse recovery response" },
            reasoning,
        }
    }
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
        maxOutputTokens: 16384,
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
