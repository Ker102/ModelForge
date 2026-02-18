/**
 * Neural 3D Generation — Provider Registry
 *
 * Central catalogue of all available neural providers, with helper functions
 * to look up providers by pipeline stage, select the best one, and
 * instantiate client instances via a factory.
 */

import type { Neural3DProviderMeta, PipelineStage, ProviderSlug } from "./types"
import type { Neural3DClient } from "./base-client"

// ---------------------------------------------------------------------------
// Provider metadata catalogue
// ---------------------------------------------------------------------------

export const PROVIDERS: Record<ProviderSlug, Neural3DProviderMeta> = {
    "hunyuan-shape": {
        slug: "hunyuan-shape",
        name: "Hunyuan3D Shape 2.1",
        stages: ["geometry"],
        modes: ["image_to_3d", "text_to_3d"],
        selfHosted: true,
        outputFormats: ["glb", "obj"],
        estimatedTime: { min: 10, max: 60 },
        vramGb: 10,
    },
    "hunyuan-paint": {
        slug: "hunyuan-paint",
        name: "Hunyuan3D Paint 2.1",
        stages: ["texturing"],
        modes: ["mesh_to_texture"],
        selfHosted: true,
        outputFormats: ["glb"],
        estimatedTime: { min: 15, max: 90 },
        vramGb: 21,
    },
    "hunyuan-part": {
        slug: "hunyuan-part",
        name: "Hunyuan3D Part",
        stages: ["segmentation"],
        modes: ["mesh_to_parts"],
        selfHosted: true,
        outputFormats: ["glb", "obj"],
        estimatedTime: { min: 5, max: 30 },
    },
    trellis: {
        slug: "trellis",
        name: "TRELLIS 2 (Microsoft)",
        stages: ["geometry", "texturing"],
        modes: ["image_to_3d"],
        selfHosted: true,
        outputFormats: ["glb"],
        estimatedTime: { min: 3, max: 60 },
        vramGb: 24,
    },
    yvo3d: {
        slug: "yvo3d",
        name: "YVO3D",
        stages: ["texturing"],
        modes: ["mesh_to_texture", "image_to_3d"],
        selfHosted: false,
        outputFormats: ["glb", "obj"],
        estimatedTime: { min: 10, max: 120 },
    },
}

// ---------------------------------------------------------------------------
// Lookup helpers
// ---------------------------------------------------------------------------

/** Return all providers that can handle the given pipeline stage. */
export function getProvidersForStage(stage: PipelineStage): Neural3DProviderMeta[] {
    return Object.values(PROVIDERS).filter((p) => p.stages.includes(stage))
}

/**
 * Pick the best provider for a given pipeline stage.
 *
 * Strategy:
 *  1. Prefer self-hosted providers (lower cost, full control).
 *  2. Among self-hosted, pick the one with lower VRAM (more accessible).
 *  3. Fall back to third-party APIs if no self-hosted option exists.
 *  4. If `preferredSlug` is provided and valid for the stage, use it.
 */
export function selectBestProvider(
    stage: PipelineStage,
    preferredSlug?: ProviderSlug,
): Neural3DProviderMeta | null {
    const candidates = getProvidersForStage(stage)
    if (candidates.length === 0) return null

    // If the caller has a preference and it supports this stage, use it.
    if (preferredSlug) {
        const preferred = candidates.find((p) => p.slug === preferredSlug)
        if (preferred) return preferred
    }

    // Sort: self-hosted first, then by lower VRAM
    const sorted = [...candidates].sort((a, b) => {
        if (a.selfHosted !== b.selfHosted) return a.selfHosted ? -1 : 1
        return (a.vramGb ?? 999) - (b.vramGb ?? 999)
    })

    return sorted[0]
}

// ---------------------------------------------------------------------------
// Client factory
// ---------------------------------------------------------------------------

/**
 * Create a concrete Neural3DClient for the given provider slug.
 *
 * Uses dynamic imports to avoid loading every provider's dependencies
 * upfront (they may have heavy optional packages like @gradio/client).
 */
export async function createNeuralClient(slug: ProviderSlug): Promise<Neural3DClient> {
    switch (slug) {
        case "hunyuan-shape": {
            const { HunyuanShapeClient } = await import("./providers/hunyuan-shape")
            return new HunyuanShapeClient()
        }
        case "hunyuan-paint": {
            const { HunyuanPaintClient } = await import("./providers/hunyuan-paint")
            return new HunyuanPaintClient()
        }
        case "hunyuan-part": {
            const { HunyuanPartClient } = await import("./providers/hunyuan-part")
            return new HunyuanPartClient()
        }
        case "trellis": {
            const { TrellisClient } = await import("./providers/trellis")
            return new TrellisClient()
        }
        case "yvo3d": {
            const { Yvo3dClient } = await import("./providers/yvo3d")
            return new Yvo3dClient()
        }
        default:
            throw new Error(`Unknown neural provider slug: ${slug}`)
    }
}
