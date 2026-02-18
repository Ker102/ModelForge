import type { ProviderSlug } from "@/lib/neural/types"

// ---------------------------------------------------------------------------
// Strategy Classification Types
// ---------------------------------------------------------------------------

/**
 * The three generation strategies available in ModelForge.
 *
 * - `procedural`  — Blender Python code-gen for geometric, architectural, parametric objects
 * - `neural`      — Neural 3D generation for organic, complex, photorealistic assets
 * - `hybrid`      — Neural geometry → Blender post-processing (retopo, rig, animate, export)
 */
export type Strategy = "procedural" | "neural" | "hybrid"

/**
 * Result of the strategy classification.
 */
export interface StrategyDecision {
    /** Which pipeline to invoke */
    strategy: Strategy
    /** 0.0–1.0 confidence in the classification */
    confidence: number
    /** Human-readable reasoning for the decision */
    reasoning: string
    /** Recommended providers when strategy is neural/hybrid */
    suggestedProviders?: ProviderSlug[]
    /** How the decision was made */
    classificationMethod: "keyword" | "llm" | "user_override"
}

/**
 * User-level override: lets users explicitly pick a strategy from the UI.
 * When set, the router skips classification entirely.
 */
export interface StrategyOverride {
    /** Force a specific strategy */
    strategy: Strategy
    /** Optional: force specific neural providers */
    providers?: ProviderSlug[]
}
