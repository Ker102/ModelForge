/**
 * MoMask Text-to-Motion Provider Client
 *
 * MoMask (CVPR 2024, MIT License) — Generative masked modeling for
 * text-driven 3D human motion generation. Uses a hierarchical quantization
 * scheme with masked transformer architecture.
 *
 * Deployment: RunPod Serverless (A10G ~8GB VRAM, can also run on CPU)
 * Model: EricGuo5513/momask-codes (GitHub, MIT)
 * Input: Text prompt + optional duration
 * Output: BVH motion capture file
 *
 * NOTE: MoMask outputs BVH data, not rigged animations. Users need to
 * manually import the BVH into Blender and apply it to an armature.
 */

import { Neural3DClient } from "../base-client"
import type {
    GenerationRequest,
    GenerationResult,
    Neural3DProviderMeta,
    ProviderSlug,
} from "../types"

// ---------------------------------------------------------------------------
// RunPod API types
// ---------------------------------------------------------------------------

interface RunPodJobResponse {
    id: string
    status: "IN_QUEUE" | "IN_PROGRESS" | "COMPLETED" | "FAILED" | "CANCELLED" | "TIMED_OUT"
}

interface RunPodStatusResponse extends RunPodJobResponse {
    delayTime?: number
    executionTime?: number
    output?: {
        /** URL to the generated BVH motion file */
        motion_url?: string
        /** Motion duration in seconds */
        duration?: number
        /** Number of frames generated */
        frame_count?: number
        /** Additional metadata */
        [key: string]: unknown
    }
    error?: string
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RUNPOD_API_BASE = "https://api.runpod.ai/v2"

const META: Neural3DProviderMeta = {
    slug: "momask",
    name: "MoMask (Text-to-Motion)",
    stages: ["animation"],
    modes: ["text_to_motion"],
    selfHosted: true,
    outputFormats: ["bvh", "fbx"],
    estimatedTime: { min: 5, max: 30 },
    vramGb: 8,
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export class MoMaskClient extends Neural3DClient {
    readonly name = META.name
    readonly slug: ProviderSlug = "momask"
    readonly meta = META

    private readonly apiKey: string
    private readonly endpointId: string

    constructor() {
        super()

        const apiKey = process.env.RUNPOD_API_KEY
        if (!apiKey) {
            throw new Error("RUNPOD_API_KEY environment variable is not set")
        }

        const endpointId = process.env.RUNPOD_ENDPOINT_MOMASK
        if (!endpointId) {
            throw new Error(
                "RUNPOD_ENDPOINT_MOMASK environment variable is not set. " +
                "Deploy the MoMask model on RunPod Serverless and set this endpoint ID."
            )
        }

        this.apiKey = apiKey
        this.endpointId = endpointId
    }

    // ── Health check ──────────────────────────────────────────────────

    async healthCheck(): Promise<boolean> {
        try {
            const res = await fetch(
                `${RUNPOD_API_BASE}/${this.endpointId}/health`,
                { headers: { Authorization: `Bearer ${this.apiKey}` } },
            )
            return res.ok
        } catch {
            return false
        }
    }

    // ── Generate (text to motion) ─────────────────────────────────────

    async generate(request: GenerationRequest): Promise<GenerationResult> {
        if (!request.prompt) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "animation",
                error: "MoMask requires a text prompt describing the motion.",
            }
        }

        // Submit job
        const submitRes = await fetch(
            `${RUNPOD_API_BASE}/${this.endpointId}/run`,
            {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${this.apiKey}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    input: {
                        prompt: request.prompt,
                        duration: request.motionDuration ?? 4.0,
                        format: request.motionFormat ?? "bvh",
                    },
                }),
            },
        )

        if (!submitRes.ok) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "animation",
                error: `RunPod submit failed: ${submitRes.status} ${submitRes.statusText}`,
            }
        }

        const job: RunPodJobResponse = await submitRes.json()
        const startTime = Date.now()

        // Poll until done
        return this.pollUntilDone(
            () => this.checkJobStatus(job.id, startTime, request.motionFormat ?? "bvh"),
            3_000,   // poll every 3s (MoMask is fast)
            120_000, // timeout after 2min
        )
    }

    // ── Poll job status ───────────────────────────────────────────────

    private async checkJobStatus(
        jobId: string,
        startTime: number,
        format: string,
    ): Promise<GenerationResult> {
        const res = await fetch(
            `${RUNPOD_API_BASE}/${this.endpointId}/status/${jobId}`,
            { headers: { Authorization: `Bearer ${this.apiKey}` } },
        )

        if (!res.ok) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "animation",
                error: `RunPod status check failed: ${res.status}`,
            }
        }

        const data: RunPodStatusResponse = await res.json()

        if (data.status === "COMPLETED" && data.output?.motion_url) {
            const ext = format === "fbx" ? "fbx" : "bvh"
            const localPath = await this.downloadModel(
                data.output.motion_url,
                `momask-motion-${Date.now()}.${ext}`,
            )
            return {
                status: "completed",
                provider: this.slug,
                stage: "animation",
                motionPath: localPath,
                modelPath: localPath,
                generationTimeMs: Date.now() - startTime,
            }
        }

        if (data.status === "FAILED" || data.status === "CANCELLED" || data.status === "TIMED_OUT") {
            return {
                status: "failed",
                provider: this.slug,
                stage: "animation",
                error: data.error ?? `RunPod job ${data.status}`,
            }
        }

        // Still processing
        return {
            status: "processing",
            provider: this.slug,
            stage: "animation",
        }
    }
}
