/**
 * fal.ai Neural 3D Generation Client
 *
 * Unified client for all fal.ai hosted neural 3D models:
 *  - fal-ai/hunyuan3d-v21    (Hunyuan3D 2.1 — $0.05/gen geometry)
 *  - fal-ai/trellis-2        (TRELLIS 2 — $0.25-0.35/gen geometry + texture)
 *  - fal-ai/trellis-2/retexture (TRELLIS 2 retexture — mesh + reference image)
 *
 * Env vars:
 *  - FAL_KEY  (required — fal.ai API key)
 *
 * All models return GLB files via fal.ai's serverless infrastructure.
 * Zero cold start, scale-to-zero built-in, pay-per-call.
 */

import { fal } from "@fal-ai/client"
import { Neural3DClient } from "../base-client"
import type {
    GenerationRequest,
    GenerationResult,
    Neural3DProviderMeta,
    ProviderSlug,
} from "../types"
import { PROVIDERS } from "../registry"

// ---------------------------------------------------------------------------
// fal.ai model endpoint mapping
// ---------------------------------------------------------------------------

const FAL_ENDPOINTS: Record<string, string> = {
    "hunyuan-shape": "fal-ai/hunyuan3d-v21",
    trellis: "fal-ai/trellis-2",
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export class FalClient extends Neural3DClient {
    readonly name: string
    readonly slug: ProviderSlug
    readonly meta: Neural3DProviderMeta

    private readonly falEndpoint: string

    constructor(providerSlug: ProviderSlug = "hunyuan-shape") {
        super()
        this.slug = providerSlug
        this.name = `fal.ai ${PROVIDERS[providerSlug]?.name ?? providerSlug}`
        this.meta = PROVIDERS[providerSlug] ?? PROVIDERS["hunyuan-shape"]
        this.falEndpoint = FAL_ENDPOINTS[providerSlug] ?? FAL_ENDPOINTS["hunyuan-shape"]

        // Configure fal.ai credentials
        const falKey = process.env.FAL_KEY
        if (falKey) {
            fal.config({ credentials: falKey })
        }
    }

    // -------------------------------------------------------------------------
    // Health check — verify fal.ai is reachable and we have a key
    // -------------------------------------------------------------------------

    async healthCheck(): Promise<boolean> {
        if (!process.env.FAL_KEY) {
            console.warn("[fal.ai] FAL_KEY not set — cannot use fal.ai provider")
            return false
        }

        try {
            // fal.ai doesn't have an explicit health endpoint, but we can
            // check if the API key is valid by trying a minimal status call
            // We'll just verify the key exists — the actual failure will
            // surface during generation if the key is invalid
            return true
        } catch {
            return false
        }
    }

    // -------------------------------------------------------------------------
    // Generate — call fal.ai's queue-based API
    // -------------------------------------------------------------------------

    async generate(request: GenerationRequest): Promise<GenerationResult> {
        const startTime = Date.now()

        try {
            if (!process.env.FAL_KEY) {
                return {
                    status: "failed",
                    provider: this.slug,
                    stage: "geometry",
                    error: "FAL_KEY environment variable is not set",
                    generationTimeMs: Date.now() - startTime,
                }
            }

            // Build input payload based on provider
            const input: Record<string, unknown> = {}

            if (this.slug === "hunyuan-shape") {
                // Hunyuan3D 2.1 on fal.ai accepts image_url (required)
                // For text-to-3D, we'd need to generate an image first
                if (request.imageUrl) {
                    input.image_url = request.imageUrl
                } else if (request.prompt) {
                    // fal.ai Hunyuan requires an image — if we only have text,
                    // return an error suggesting using the self-hosted endpoint
                    return {
                        status: "failed",
                        provider: this.slug,
                        stage: "geometry",
                        error: "fal.ai Hunyuan3D requires an image_url input. For text-to-3D, use the self-hosted endpoint or generate a reference image first.",
                        generationTimeMs: Date.now() - startTime,
                    }
                }
            } else if (this.slug === "trellis") {
                // TRELLIS 2 on fal.ai — image-to-3D with texture
                if (request.imageUrl) {
                    input.image_url = request.imageUrl
                } else {
                    return {
                        status: "failed",
                        provider: this.slug,
                        stage: "geometry",
                        error: "fal.ai TRELLIS 2 requires an image_url input.",
                        generationTimeMs: Date.now() - startTime,
                    }
                }
                // TRELLIS 2 specific defaults
                input.resolution = 1024
                input.remesh = true
                input.texture_size = 2048
                input.decimation_target = 500000
            }

            // Call fal.ai with queue-based subscription
            console.log(`[fal.ai] Submitting ${this.falEndpoint} request...`)

            const result = await fal.subscribe(this.falEndpoint, {
                input,
                logs: true,
                onQueueUpdate: (update) => {
                    if (update.status === "IN_PROGRESS") {
                        const logs = (update as { logs?: Array<{ message: string }> }).logs
                        if (logs) {
                            logs.map((log) => log.message).forEach((msg) =>
                                console.log(`[fal.ai] ${msg}`)
                            )
                        }
                    }
                },
            })

            // Extract GLB URL from result
            const data = result.data as Record<string, unknown>
            const modelMesh = (data.model_mesh ?? data.model_glb) as { url?: string } | undefined
            const glbUrl = modelMesh?.url

            if (!glbUrl) {
                return {
                    status: "failed",
                    provider: this.slug,
                    stage: "geometry",
                    error: "fal.ai returned no model URL in response",
                    generationTimeMs: Date.now() - startTime,
                }
            }

            // Download the GLB file to local storage
            const modelPath = await this.downloadModel(
                glbUrl,
                `fal-${this.slug}-${Date.now()}.glb`,
            )

            console.log(`[fal.ai] Model saved to ${modelPath} (${this.slug})`)

            return {
                status: "completed",
                modelPath,
                provider: this.slug,
                stage: this.slug === "trellis" ? "texturing" : "geometry",
                generationTimeMs: Date.now() - startTime,
            }
        } catch (err) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "geometry",
                error: `fal.ai ${this.slug} generation failed: ${err instanceof Error ? err.message : String(err)}`,
                generationTimeMs: Date.now() - startTime,
            }
        }
    }
}
