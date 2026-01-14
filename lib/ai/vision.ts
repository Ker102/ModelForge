/**
 * Vision Module
 * 
 * LangChain-based Gemini multimodal integration for analyzing Blender viewport screenshots.
 * Enables dynamic feedback loop: see what changed → analyze → suggest improvements.
 */

import { HumanMessage } from "@langchain/core/messages"
import { createGeminiModel } from "./index"

// ============================================================================
// Types
// ============================================================================

export interface VisionAnalysisResult {
    /** Natural language description of what's visible */
    description: string
    /** List of detected objects/elements */
    objects: string[]
    /** Overall assessment */
    assessment: "complete" | "partial" | "needs_work" | "error"
    /** Specific issues or missing elements */
    issues: string[]
    /** Suggested next actions */
    suggestions: string[]
    /** Confidence score 0-1 */
    confidence: number
}

export interface SceneComparisonResult {
    /** Whether the scene matches the expected outcome */
    matches: boolean
    /** What was expected */
    expected: string
    /** What was observed */
    observed: string
    /** Specific differences */
    differences: string[]
    /** Confidence in the comparison */
    confidence: number
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Create a multimodal message with text and image for LangChain
 */
function createVisionMessage(prompt: string, imageBase64: string, mimeType: string = "image/png") {
    // Remove data URL prefix if present
    const cleanBase64 = imageBase64.replace(/^data:image\/\w+;base64,/, "")

    return new HumanMessage({
        content: [
            { type: "text", text: prompt },
            {
                type: "image_url",
                image_url: {
                    url: `data:${mimeType};base64,${cleanBase64}`,
                },
            },
        ],
    })
}

/**
 * Parse JSON from LLM response (handles markdown code blocks)
 */
function parseJsonResponse<T>(response: string): T {
    const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/) ||
        response.match(/\{[\s\S]*\}/)

    if (!jsonMatch) {
        throw new Error("Failed to parse JSON from response")
    }

    const jsonStr = jsonMatch[1] || jsonMatch[0]
    return JSON.parse(jsonStr) as T
}

// ============================================================================
// Vision Functions
// ============================================================================

/**
 * Analyze a viewport screenshot and describe what's visible.
 * 
 * @param imageBase64 - Base64-encoded image data
 * @param context - Optional context about what was requested
 * @returns Analysis result with description, objects, and suggestions
 */
export async function analyzeViewport(
    imageBase64: string,
    context?: string
): Promise<VisionAnalysisResult> {
    const model = createGeminiModel({ temperature: 0.2 })

    const prompt = `You are analyzing a Blender 3D viewport screenshot. 

${context ? `Context: The user requested: "${context}"` : ""}

Analyze this viewport image and provide:
1. A brief description of what you see in the scene
2. List of visible objects/elements
3. Assessment: "complete" (request fulfilled), "partial" (some work done), "needs_work" (issues found), or "error" (major problems)
4. Any issues or missing elements
5. Suggested next actions to improve the scene

Respond in this exact JSON format:
{
  "description": "Brief description of the scene",
  "objects": ["object1", "object2"],
  "assessment": "complete|partial|needs_work|error",
  "issues": ["issue1", "issue2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "confidence": 0.85
}`

    try {
        const message = createVisionMessage(prompt, imageBase64)
        const response = await model.invoke([message])
        const content = typeof response.content === "string"
            ? response.content
            : JSON.stringify(response.content)

        return parseJsonResponse<VisionAnalysisResult>(content)
    } catch (error) {
        return {
            description: "Failed to analyze viewport",
            objects: [],
            assessment: "error",
            issues: [error instanceof Error ? error.message : String(error)],
            suggestions: ["Retry the analysis"],
            confidence: 0,
        }
    }
}

/**
 * Generate a natural language description of the scene.
 * Useful for logging and debugging.
 * 
 * @param imageBase64 - Base64-encoded image data
 * @returns Short description of the scene
 */
export async function describeScene(imageBase64: string): Promise<string> {
    const model = createGeminiModel({ temperature: 0.3 })

    const prompt = `Describe this Blender 3D viewport screenshot in 1-2 sentences. 
Focus on: what objects are visible, their arrangement, materials/colors, and lighting.
Be concise and technical.`

    try {
        const message = createVisionMessage(prompt, imageBase64)
        const response = await model.invoke([message])
        const content = typeof response.content === "string"
            ? response.content
            : JSON.stringify(response.content)

        return content.trim()
    } catch (error) {
        return `[Vision Error: ${error instanceof Error ? error.message : String(error)}]`
    }
}

/**
 * Compare a viewport screenshot against an expected outcome.
 * 
 * @param imageBase64 - Base64-encoded image data
 * @param expectedOutcome - Description of what should be visible
 * @returns Comparison result indicating if the scene matches expectations
 */
export async function compareWithExpectation(
    imageBase64: string,
    expectedOutcome: string
): Promise<SceneComparisonResult> {
    const model = createGeminiModel({ temperature: 0.2 })

    const prompt = `You are comparing a Blender 3D viewport screenshot against an expected outcome.

EXPECTED: "${expectedOutcome}"

Analyze the image and determine if it matches the expected outcome.

Respond in this exact JSON format:
{
  "matches": true/false,
  "expected": "What was expected",
  "observed": "What you actually see",
  "differences": ["difference1", "difference2"],
  "confidence": 0.85
}`

    try {
        const message = createVisionMessage(prompt, imageBase64)
        const response = await model.invoke([message])
        const content = typeof response.content === "string"
            ? response.content
            : JSON.stringify(response.content)

        return parseJsonResponse<SceneComparisonResult>(content)
    } catch (error) {
        return {
            matches: false,
            expected: expectedOutcome,
            observed: "Failed to analyze",
            differences: [error instanceof Error ? error.message : String(error)],
            confidence: 0,
        }
    }
}

/**
 * Analyze a viewport and suggest improvements based on the user's request.
 * 
 * @param imageBase64 - Base64-encoded image data
 * @param userRequest - Original user request
 * @returns Detailed suggestions for improvements
 */
export async function suggestImprovements(
    imageBase64: string,
    userRequest: string
): Promise<{
    currentState: string
    missingElements: string[]
    improvements: Array<{
        priority: "high" | "medium" | "low"
        action: string
        rationale: string
    }>
}> {
    const model = createGeminiModel({ temperature: 0.3 })

    const prompt = `You are an expert 3D artist reviewing a Blender scene.

USER REQUEST: "${userRequest}"

Analyze this viewport screenshot and suggest improvements to better fulfill the user's request.

Respond in this exact JSON format:
{
  "currentState": "Brief description of current scene",
  "missingElements": ["element1", "element2"],
  "improvements": [
    {
      "priority": "high|medium|low",
      "action": "specific action to take",
      "rationale": "why this improves the scene"
    }
  ]
}`

    try {
        const message = createVisionMessage(prompt, imageBase64)
        const response = await model.invoke([message])
        const content = typeof response.content === "string"
            ? response.content
            : JSON.stringify(response.content)

        return parseJsonResponse(content)
    } catch (error) {
        return {
            currentState: "Failed to analyze",
            missingElements: [],
            improvements: [{
                priority: "high",
                action: "Retry analysis",
                rationale: error instanceof Error ? error.message : String(error),
            }],
        }
    }
}

/**
 * Quick validation: check if a scene contains specific elements.
 * 
 * @param imageBase64 - Base64-encoded image data
 * @param requiredElements - List of elements that should be present
 * @returns Object indicating which elements were found
 */
export async function validateSceneElements(
    imageBase64: string,
    requiredElements: string[]
): Promise<{
    allPresent: boolean
    found: string[]
    missing: string[]
}> {
    const model = createGeminiModel({ temperature: 0.1 })

    const prompt = `Analyze this Blender 3D viewport screenshot.

Check if these elements are visible:
${requiredElements.map((e, i) => `${i + 1}. ${e}`).join("\n")}

Respond in this exact JSON format:
{
  "allPresent": true/false,
  "found": ["element1", "element2"],
  "missing": ["element3"]
}`

    try {
        const message = createVisionMessage(prompt, imageBase64)
        const response = await model.invoke([message])
        const content = typeof response.content === "string"
            ? response.content
            : JSON.stringify(response.content)

        return parseJsonResponse(content)
    } catch (error) {
        return {
            allPresent: false,
            found: [],
            missing: requiredElements,
        }
    }
}
