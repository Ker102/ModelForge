/**
 * MeshAnything V2 Auto-Retopology Provider Client
 *
 * MeshAnything V2 (ICCV 2025, Apache 2.0) — Autoregressive transformer
 * that converts messy neural mesh output into clean, artist-grade topology.
 * Uses Adjacent Mesh Tokenization (AMT) for efficient quad-dominant remeshing.
 *
 * Deployment: RunPod Serverless (A10G ~12GB VRAM)
 * Model: buaacyw/MeshAnythingV2 (GitHub / HuggingFace, Apache 2.0)
 * Input: GLB/OBJ mesh (high-poly neural output)
 * Output: Clean quad-dominant mesh (up to 1600 faces)
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
        /** URL to the retopologized mesh */
        model_url?: string
        /** Face count of the output mesh */
        face_count?: number
        /** Additional metadata */
        [key: string]: unknown
    }
    error?: string
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RUNPOD_API_BASE = "https://api.runpod.ai/v2"

/** Maximum face count supported by MeshAnything V2 (AMT tokenization limit) */
const MAX_TARGET_FACES = 1600

const META: Neural3DProviderMeta = {
    slug: "meshanything-v2",
    name: "MeshAnything V2 (Retopology)",
    stages: ["retopology"],
    modes: ["mesh_to_retopo"],
    selfHosted: true,
    outputFormats: ["glb", "obj"],
    estimatedTime: { min: 10, max: 45 },
    vramGb: 12,
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export class MeshAnythingV2Client extends Neural3DClient {
    readonly name = META.name
    readonly slug: ProviderSlug = "meshanything-v2"
    readonly meta = META

    private readonly apiKey: string
    private readonly endpointId: string

    constructor() {
        super()

        const apiKey = process.env.RUNPOD_API_KEY
        if (!apiKey) {
            throw new Error("RUNPOD_API_KEY environment variable is not set")
        }

        const endpointId = process.env.RUNPOD_ENDPOINT_MESHANYTHING
        if (!endpointId) {
            throw new Error(
                "RUNPOD_ENDPOINT_MESHANYTHING environment variable is not set. " +
                "Deploy MeshAnything V2 on RunPod Serverless and set this endpoint ID."
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

    // ── Generate (retopologize mesh) ──────────────────────────────────

    async generate(request: GenerationRequest): Promise<GenerationResult> {
        if (!request.meshUrl) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "retopology",
                error: "MeshAnything V2 requires a meshUrl — provide the mesh to retopologize.",
            }
        }

        const targetFaces = Math.min(
            request.targetFaces ?? 800,
            MAX_TARGET_FACES,
        )

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
                        mesh_url: request.meshUrl,
                        target_faces: targetFaces,
                        output_format: request.outputFormat ?? "glb",
                    },
                }),
            },
        )

        if (!submitRes.ok) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "retopology",
                error: `RunPod submit failed: ${submitRes.status} ${submitRes.statusText}`,
            }
        }

        const job: RunPodJobResponse = await submitRes.json()
        const startTime = Date.now()

        // Poll until done
        return this.pollUntilDone(
            () => this.checkJobStatus(job.id, startTime, request.outputFormat ?? "glb"),
            5_000,   // poll every 5s
            180_000, // timeout after 3min
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
                stage: "retopology",
                error: `RunPod status check failed: ${res.status}`,
            }
        }

        const data: RunPodStatusResponse = await res.json()

        if (data.status === "COMPLETED" && data.output?.model_url) {
            const ext = format === "obj" ? "obj" : "glb"
            const localPath = await this.downloadModel(
                data.output.model_url,
                `meshanything-retopo-${Date.now()}.${ext}`,
            )
            return {
                status: "completed",
                provider: this.slug,
                stage: "retopology",
                retopologyPath: localPath,
                modelPath: localPath,
                generationTimeMs: Date.now() - startTime,
            }
        }

        if (data.status === "FAILED" || data.status === "CANCELLED" || data.status === "TIMED_OUT") {
            return {
                status: "failed",
                provider: this.slug,
                stage: "retopology",
                error: data.error ?? `RunPod job ${data.status}`,
            }
        }

        // Still processing
        return {
            status: "processing",
            provider: this.slug,
            stage: "retopology",
        }
    }
}
