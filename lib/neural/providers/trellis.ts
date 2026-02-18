/**
 * TRELLIS 2 (Microsoft) — Geometry + PBR Texture Client
 *
 * 4B-parameter open-source model (MIT license).
 * Generates high-resolution 3D assets with PBR textures from images.
 * Supports resolutions up to 1536³.
 *
 * Connects to a self-hosted Gradio app or custom FastAPI wrapper.
 *
 * Env vars:
 *  - TRELLIS_API_URL  (e.g. http://localhost:7860 or Azure endpoint)
 */

import { Neural3DClient } from "../base-client"
import type {
    GenerationRequest,
    GenerationResult,
    Neural3DProviderMeta,
    ProviderSlug,
} from "../types"
import { PROVIDERS } from "../registry"
import fs from "fs/promises"

export class TrellisClient extends Neural3DClient {
    readonly name = "TRELLIS 2 (Microsoft)"
    readonly slug: ProviderSlug = "trellis"
    readonly meta: Neural3DProviderMeta = PROVIDERS["trellis"]

    private readonly baseUrl: string

    constructor() {
        super()
        this.baseUrl = process.env.TRELLIS_API_URL ?? "http://localhost:7860"
    }

    async healthCheck(): Promise<boolean> {
        try {
            const res = await fetch(this.baseUrl, {
                method: "GET",
                signal: AbortSignal.timeout(10_000),
            })
            return res.ok
        } catch {
            return false
        }
    }

    async generate(request: GenerationRequest): Promise<GenerationResult> {
        const startTime = Date.now()

        try {
            if (!request.imageUrl) {
                return {
                    status: "failed",
                    provider: this.slug,
                    stage: "geometry",
                    error: "TRELLIS 2 requires an imageUrl for image-to-3D generation.",
                }
            }

            // Use @gradio/client to submit to the TRELLIS 2 Gradio app
            const { Client } = await import("@gradio/client")
            const client = await Client.connect(this.baseUrl)

            // Prepare image input
            let imageBlob: Blob
            if (request.imageUrl.startsWith("data:")) {
                // Strip data URI prefix and decode
                const base64Data = request.imageUrl.split(",")[1]
                const buf = Buffer.from(base64Data, "base64")
                imageBlob = new Blob([new Uint8Array(buf)], { type: "image/png" })
            } else if (request.imageUrl.startsWith("http")) {
                const imgRes = await fetch(request.imageUrl)
                imageBlob = await imgRes.blob()
            } else {
                const buf = await fs.readFile(request.imageUrl)
                imageBlob = new Blob([new Uint8Array(buf)], { type: "image/png" })
            }

            // Submit generation — TRELLIS Gradio typically has /image_to_3d endpoint
            const result = await client.predict("/image_to_3d", {
                image: imageBlob,
                // Resolution defaults differ by target:
                //   512³ → ~3s on H100
                //   1024³ → ~15s
                //   1536³ → ~60s
            })

            // Parse the result — Gradio returns file references
            const data = result.data as Array<{ url?: string; path?: string }>
            if (data.length > 0 && (data[0].url || data[0].path)) {
                const outputUrl = data[0].url ?? data[0].path!
                const modelPath = await this.downloadModel(
                    outputUrl,
                    `trellis-${Date.now()}.glb`,
                )

                return {
                    status: "completed",
                    modelPath,
                    provider: this.slug,
                    stage: "geometry",
                    generationTimeMs: Date.now() - startTime,
                }
            }

            return {
                status: "failed",
                provider: this.slug,
                stage: "geometry",
                error: "TRELLIS 2 returned no output.",
                generationTimeMs: Date.now() - startTime,
            }
        } catch (err) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "geometry",
                error: `TRELLIS 2 generation failed: ${err instanceof Error ? err.message : String(err)}`,
                generationTimeMs: Date.now() - startTime,
            }
        }
    }
}
