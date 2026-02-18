import type { Strategy, StrategyDecision, StrategyOverride } from "./strategy-types"
import type { ProviderSlug } from "@/lib/neural/types"

// ---------------------------------------------------------------------------
// Keyword-based classification patterns
// ---------------------------------------------------------------------------

/** Signals that strongly indicate procedural (Blender Python) generation. */
const PROCEDURAL_PATTERNS: RegExp[] = [
    // Architectural & structural
    /\b(building|house|room|wall|floor|ceiling|door|window|staircase|stair|arch|column|bridge|tower|castle|temple|cabin|shed|warehouse)\b/i,
    // Geometric primitives & parametric
    /\b(cube|sphere|cylinder|cone|torus|plane|grid|prism|pyramid|helix|spiral|polygon|vertex|edge|mesh|parametric|boolean|extrude|bevel)\b/i,
    // Furniture & interior
    /\b(table|chair|desk|shelf|bookcase|lamp|sofa|bed|cabinet|drawer|mirror|frame|rug|carpet|curtain)\b/i,
    // Mechanical & precision
    /\b(gear|screw|bolt|pipe|duct|rail|track|frame|mount|bracket|hinge|axle|piston|wheel|engine)\b/i,
    // Scene-level edits (these always use Blender Python)
    /\b(move|rotate|scale|delete|duplicate|array|modify|adjust|position|layout|arrange|align)\b/i,
    // Lighting & camera (always procedural)
    /\b(light|lighting|camera|render|hdri|sun|spot|area|point light)\b/i,
    // Materials & textures (always procedural via Blender nodes)
    /\b(material|shader|texture|color|roughness|metallic|emission|glass|glossy|pbr|uv map)\b/i,
]

/** Signals that strongly indicate neural 3D generation. */
const NEURAL_PATTERNS: RegExp[] = [
    // Organic / characters
    /\b(character|person|human|man|woman|child|face|portrait|head|body|figure|figurine|bust|statue)\b/i,
    // Animals & creatures
    /\b(animal|dog|cat|horse|bird|fish|dragon|creature|monster|dinosaur|insect|snake|wolf|bear|lion)\b/i,
    // Nature & organic shapes
    /\b(tree|plant|flower|leaf|branch|coral|mushroom|rock formation|terrain|mountain|cliff)\b/i,
    // Sculpted / artistic
    /\b(sculpture|sculpt|organic|freeform|natural shape|realistic model|photorealistic|lifelike)\b/i,
    // Food & complex objects
    /\b(food|fruit|vegetable|bread|cake|skull|shoe|clothing|garment|hat|bag|backpack)\b/i,
]

/** Signals that suggest hybrid pipeline (neural + Blender post-processing). */
const HYBRID_PATTERNS: RegExp[] = [
    // Character + rigging/animation
    /\b(character|creature|person|human).{0,40}(rig|rigged|animate|animated|pose|posed|walk|run|dance)\b/i,
    /\b(rig|animate|pose).{0,40}(character|creature|person|human|animal)\b/i,
    // Realistic + game/production ready
    /\b(realistic|organic|character|creature).{0,40}(game.?ready|production|export|fbx|gltf|usd)\b/i,
    // Neural + specific Blender ops
    /\b(generate|create|make).{0,40}(then|and).{0,40}(rig|texture|animate|retopolog)/i,
]

// ---------------------------------------------------------------------------
// Keyword scoring
// ---------------------------------------------------------------------------

interface KeywordScore {
    procedural: number
    neural: number
    hybrid: number
}

function scoreKeywords(request: string): KeywordScore {
    const score: KeywordScore = { procedural: 0, neural: 0, hybrid: 0 }

    // Hybrid checked first — it's context-dependent combinations
    for (const pattern of HYBRID_PATTERNS) {
        if (pattern.test(request)) score.hybrid += 2
    }

    for (const pattern of PROCEDURAL_PATTERNS) {
        if (pattern.test(request)) score.procedural += 1
    }

    for (const pattern of NEURAL_PATTERNS) {
        if (pattern.test(request)) score.neural += 1
    }

    return score
}

function decideFromKeywords(score: KeywordScore): StrategyDecision | null {
    const total = score.procedural + score.neural + score.hybrid
    if (total === 0) return null // ambiguous — need LLM

    // Hybrid wins if it has ANY matches (it's more specific)
    if (score.hybrid >= 2) {
        return {
            strategy: "hybrid",
            confidence: Math.min(0.85, 0.6 + score.hybrid * 0.1),
            reasoning: "Request combines neural generation with Blender post-processing (rigging, animation, export).",
            classificationMethod: "keyword",
        }
    }

    // Clear procedural winner
    if (score.procedural > 0 && score.neural === 0) {
        return {
            strategy: "procedural",
            confidence: Math.min(0.95, 0.7 + score.procedural * 0.05),
            reasoning: "Request involves geometric, architectural, or scene-editing operations best handled by Blender Python.",
            classificationMethod: "keyword",
        }
    }

    // Clear neural winner
    if (score.neural > 0 && score.procedural === 0) {
        return {
            strategy: "neural",
            confidence: Math.min(0.9, 0.65 + score.neural * 0.08),
            reasoning: "Request involves organic shapes, characters, or photorealistic assets best suited for neural 3D generation.",
            suggestedProviders: ["hunyuan-shape", "trellis"],
            classificationMethod: "keyword",
        }
    }

    // Mixed signals — if procedural dominates, favor procedural (cheaper, faster)
    if (score.procedural >= score.neural * 2) {
        return {
            strategy: "procedural",
            confidence: 0.6,
            reasoning: "Request has mixed signals but leans procedural. Blender Python is preferred for precision.",
            classificationMethod: "keyword",
        }
    }

    // Mixed but neural leans stronger
    if (score.neural >= score.procedural * 2) {
        return {
            strategy: "neural",
            confidence: 0.6,
            reasoning: "Request has mixed signals but leans toward organic/complex shapes suited for neural generation.",
            suggestedProviders: ["hunyuan-shape"],
            classificationMethod: "keyword",
        }
    }

    // Truly ambiguous — fall through to LLM
    return null
}

// ---------------------------------------------------------------------------
// LLM-based classification (fallback for ambiguous requests)
// ---------------------------------------------------------------------------

async function classifyWithLLM(
    userRequest: string,
    sceneContext?: string
): Promise<StrategyDecision> {
    // Dynamic import to avoid circular dependencies
    const { generateGeminiResponse } = await import("@/lib/gemini")

    const systemPrompt = `You are a 3D generation strategy classifier for ModelForge.
Classify the user's request into exactly ONE strategy:

- "procedural": For geometric shapes, architecture, furniture, mechanical parts, scene edits, lighting, camera, materials. Generated via Blender Python scripting.
- "neural": For organic characters, animals, sculptures, plants, photorealistic assets. Generated by neural 3D models (Hunyuan, TRELLIS).
- "hybrid": When the request needs neural generation PLUS Blender post-processing like rigging, animation, retopology, or game-ready export.

When in doubt, prefer "procedural" — it's faster, cheaper, and more controllable.

Respond with ONLY a JSON object:
{"strategy": "procedural"|"neural"|"hybrid", "confidence": 0.0-1.0, "reasoning": "one sentence", "suggestedProviders": ["hunyuan-shape"|"hunyuan-paint"|"trellis"|"yvo3d"]}

suggestedProviders should be empty [] for procedural strategy.`

    const userPrompt = sceneContext
        ? `Scene context: ${sceneContext}\n\nUser request: ${userRequest}`
        : `User request: ${userRequest}`

    try {
        const result = await generateGeminiResponse({
            messages: [{ role: "user", content: userPrompt }],
            systemPrompt,
            temperature: 0,
            maxOutputTokens: 256,
            responseMimeType: "application/json",
        })

        const parsed = JSON.parse(result.text) as {
            strategy: Strategy
            confidence: number
            reasoning: string
            suggestedProviders?: ProviderSlug[]
        }

        // Validate
        const validStrategies: Strategy[] = ["procedural", "neural", "hybrid"]
        if (!validStrategies.includes(parsed.strategy)) {
            parsed.strategy = "procedural"
        }
        parsed.confidence = Math.max(0, Math.min(1, parsed.confidence ?? 0.5))

        return {
            strategy: parsed.strategy,
            confidence: parsed.confidence,
            reasoning: parsed.reasoning || "Classified by LLM.",
            suggestedProviders: parsed.suggestedProviders,
            classificationMethod: "llm",
        }
    } catch (error) {
        console.warn("LLM strategy classification failed, defaulting to procedural:", error)
        return {
            strategy: "procedural",
            confidence: 0.5,
            reasoning: "LLM classification failed; defaulting to procedural (safest option).",
            classificationMethod: "llm",
        }
    }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export interface ClassifyOptions {
    /** User's manual override — skips all classification */
    override?: StrategyOverride
    /** Current scene context for LLM classification */
    sceneContext?: string
    /** Skip LLM fallback — only use keyword classification (default: false) */
    keywordOnly?: boolean
}

/**
 * Classify a user request into the best generation strategy.
 *
 * Classification pipeline:
 * 1. If user override is set → return immediately
 * 2. Keyword pattern matching (fast, covers ~80% of requests)
 * 3. LLM classification fallback (for ambiguous requests)
 *
 * @param userRequest - The user's natural language request
 * @param options - Classification options
 * @returns StrategyDecision with strategy, confidence, and reasoning
 */
export async function classifyStrategy(
    userRequest: string,
    options: ClassifyOptions = {}
): Promise<StrategyDecision> {
    // 1. User override — always wins
    if (options.override) {
        return {
            strategy: options.override.strategy,
            confidence: 1.0,
            reasoning: `User manually selected "${options.override.strategy}" strategy.`,
            suggestedProviders: options.override.providers,
            classificationMethod: "user_override",
        }
    }

    // 2. Keyword-based classification
    const score = scoreKeywords(userRequest)
    const keywordResult = decideFromKeywords(score)

    if (keywordResult && keywordResult.confidence >= 0.6) {
        return keywordResult
    }

    // 3. LLM fallback (unless disabled)
    if (!options.keywordOnly) {
        return classifyWithLLM(userRequest, options.sceneContext)
    }

    // 4. Keyword-only mode with low confidence — default to procedural
    return keywordResult ?? {
        strategy: "procedural",
        confidence: 0.4,
        reasoning: "Could not confidently classify; defaulting to procedural generation.",
        classificationMethod: "keyword",
    }
}
