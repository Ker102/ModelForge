/**
 * YVO3D — Premium Texture Generation Client (Third-Party API)
 *
 * YVO3D specializes in ultra-high-quality texture generation (up to ULTIMA 8K).
 * Supports:
 *  - image_to_3d:    Image → geometry-only model
 *  - mesh_to_texture: Existing mesh → retextured with PBR materials
 *
 * REST API docs: https://api.yvo3d.com/docs/generation
 *
 * Env vars:
 *  - YVO3D_API_KEY  (Bearer token for the YVO3D API)
 */

import { Neural3DClient } from "../base-client"
import type {
    GenerationRequest,
    GenerationResult,
    Neural3DProviderMeta,
    ProviderSlug,
} from "../types"
import { PROVIDERS } from "../registry"

const YVO3D_BASE = "https://api.yvo3d.com/v1"

export class Yvo3dClient extends Neural3DClient {
    readonly name = "YVO3D"
    readonly slug: ProviderSlug = "yvo3d"
    readonly meta: Neural3DProviderMeta = PROVIDERS["yvo3d"]

    private readonly apiKey: string

    constructor() {
        super()
        this.apiKey = process.env.YVO3D_API_KEY ?? ""
    }

    private get headers() {
        return {
            "Content-Type": "application/json",
            Authorization: `Bearer ${this.apiKey}`,
        }
    }

    async healthCheck(): Promise<boolean> {
        if (!this.apiKey) return false
        try {
            const res = await fetch(`${YVO3D_BASE}/status`, {
                method: "GET",
                headers: this.headers,
                signal: AbortSignal.timeout(5_000),
            })
            return res.ok
        } catch {
            return false
        }
    }

    async generate(request: GenerationRequest): Promise<GenerationResult> {
        const startTime = Date.now()

        if (!this.apiKey) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "texturing",
                error: "YVO3D_API_KEY is not configured.",
            }
        }

        try {
            let payload: Record<string, unknown>

            if (request.mode === "mesh_to_texture" && request.meshUrl) {
                // ---------------------------------------------------------------
                // Model-to-Model: Retexture an existing mesh with PBR
                // ---------------------------------------------------------------
                payload = {
                    type: "model_to_model",
                    inputModelUrl: request.meshUrl,
                    textureResolution: request.textureResolution ?? "2K",
                    realismLevel: 0.9,
                    creativity: 3,
                    insideOut: "OFF",
                    unlit: "OFF",
                    generateUVs: "OFF",
                    hyperMode: request.turbo ? "ON" : "OFF",
                    textureSharpness: 0.7,
                    textureAdherence: "OFF",
                    roughness: 1.3,
                }

                // If a reference image is provided, enable retexturing
                if (request.imageUrl) {
                    // YVO3D requires uploading the image first via /v1/upload,
                    // but for now we pass the imageId directly if available
                    payload.retexture = "ON"
                }
            } else if (request.imageUrl) {
                // ---------------------------------------------------------------
                // Image-to-Texture-Model: Full generation from image
                // ---------------------------------------------------------------
                payload = {
                    type: "image_to_texture_model",
                    modelGenerator: request.turbo ? "FAST_CREATIVE" : "ULTIMA_PRIME",
                    textureResolution: request.textureResolution ?? "2K",
                    realismLevel: 0.9,
                    creativity: 3,
                    insideOut: "OFF",
                    unlit: "OFF",
                    generateUVs: "OFF",
                    hyperMode: request.turbo ? "ON" : "OFF",
                    textureSharpness: 0.7,
                    textureAdherence: "OFF",
                    roughness: 1.3,
                }
            } else {
                return {
                    status: "failed",
                    provider: this.slug,
                    stage: "texturing",
                    error: "YVO3D requires either imageUrl or meshUrl.",
                }
            }

            // Submit generation job
            const genRes = await fetch(`${YVO3D_BASE}/generate`, {
                method: "POST",
                headers: this.headers,
                body: JSON.stringify(payload),
            })

            if (!genRes.ok) {
                const errText = await genRes.text()
                return {
                    status: "failed",
                    provider: this.slug,
                    stage: "texturing",
                    error: `YVO3D API error ${genRes.status}: ${errText}`,
                    generationTimeMs: Date.now() - startTime,
                }
            }

            const genData = (await genRes.json()) as { data?: { id?: string } }
            const jobId = genData?.data?.id
            if (!jobId) {
                return {
                    status: "failed",
                    provider: this.slug,
                    stage: "texturing",
                    error: "YVO3D returned no job ID.",
                    generationTimeMs: Date.now() - startTime,
                }
            }

            // Poll for completion
            return await this.pollUntilDone(
                async (): Promise<GenerationResult> => {
                    const statusRes = await fetch(`${YVO3D_BASE}/status/${jobId}`, {
                        headers: this.headers,
                    })

                    if (!statusRes.ok) {
                        return {
                            status: "processing",
                            provider: this.slug,
                            stage: "texturing",
                        }
                    }

                    const statusData = (await statusRes.json()) as {
                        data?: {
                            status?: string
                            progress?: number
                            result?: { model_url?: string }
                        }
                    }

                    const jobStatus = statusData?.data?.status

                    if (jobStatus === "completed" && statusData?.data?.result?.model_url) {
                        const modelPath = await this.downloadModel(
                            statusData.data.result.model_url,
                            `yvo3d-${Date.now()}.glb`,
                        )

                        return {
                            status: "completed",
                            modelPath,
                            provider: this.slug,
                            stage: "texturing",
                            progress: 100,
                            generationTimeMs: Date.now() - startTime,
                        }
                    }

                    if (jobStatus === "failed") {
                        return {
                            status: "failed",
                            provider: this.slug,
                            stage: "texturing",
                            error: "YVO3D job failed.",
                            generationTimeMs: Date.now() - startTime,
                        }
                    }

                    return {
                        status: "processing",
                        provider: this.slug,
                        stage: "texturing",
                        progress: statusData?.data?.progress,
                    }
                },
                5_000, // poll every 5s
                180_000, // max 3 minutes
            )
        } catch (err) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "texturing",
                error: `YVO3D generation failed: ${err instanceof Error ? err.message : String(err)}`,
                generationTimeMs: Date.now() - startTime,
            }
        }
    }
}
