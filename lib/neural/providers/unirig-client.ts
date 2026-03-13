/**
 * UniRig Auto-Rigging Provider Client
 *
 * UniRig (SIGGRAPH 2025, MIT License) — GPT-like autoregressive transformer
 * for automatic skeleton prediction and skinning weight assignment.
 * Works on any 3D asset (humanoids, animals, objects).
 *
 * Deployment: RunPod Serverless (A10G / A5000 ~16GB VRAM)
 * Model: VAST-AI-Research/UniRig (HuggingFace, MIT)
 * Input: GLB/OBJ mesh URL
 * Output: GLB with embedded armature + skinning weights
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
        /** URL to the rigged GLB model */
        model_url?: string
        /** Skeleton bone count */
        bone_count?: number
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
    slug: "unirig",
    name: "UniRig (Auto-Rigging)",
    stages: ["rigging"],
    modes: ["mesh_to_rig"],
    selfHosted: true,
    outputFormats: ["glb"],
    estimatedTime: { min: 15, max: 60 },
    vramGb: 16,
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export class UniRigClient extends Neural3DClient {
    readonly name = META.name
    readonly slug: ProviderSlug = "unirig"
    readonly meta = META

    private readonly apiKey: string
    private readonly endpointId: string

    constructor() {
        super()

        const apiKey = process.env.RUNPOD_API_KEY
        if (!apiKey) {
            throw new Error("RUNPOD_API_KEY environment variable is not set")
        }

        const endpointId = process.env.RUNPOD_ENDPOINT_UNIRIG
        if (!endpointId) {
            throw new Error(
                "RUNPOD_ENDPOINT_UNIRIG environment variable is not set. " +
                "Deploy the UniRig model on RunPod Serverless and set this endpoint ID."
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

    // ── Generate (rig a mesh) ─────────────────────────────────────────

    async generate(request: GenerationRequest): Promise<GenerationResult> {
        if (!request.meshUrl) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "rigging",
                error: "UniRig requires a meshUrl — provide the GLB/OBJ to rig.",
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
                        mesh_url: request.meshUrl,
                    },
                }),
            },
        )

        if (!submitRes.ok) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "rigging",
                error: `RunPod submit failed: ${submitRes.status} ${submitRes.statusText}`,
            }
        }

        const job: RunPodJobResponse = await submitRes.json()
        const startTime = Date.now()

        // Poll until done
        return this.pollUntilDone(
            () => this.checkJobStatus(job.id, startTime),
            5_000,   // poll every 5s
            300_000, // timeout after 5min
        )
    }

    // ── Poll job status ───────────────────────────────────────────────

    private async checkJobStatus(
        jobId: string,
        startTime: number,
    ): Promise<GenerationResult> {
        const res = await fetch(
            `${RUNPOD_API_BASE}/${this.endpointId}/status/${jobId}`,
            { headers: { Authorization: `Bearer ${this.apiKey}` } },
        )

        if (!res.ok) {
            return {
                status: "failed",
                provider: this.slug,
                stage: "rigging",
                error: `RunPod status check failed: ${res.status}`,
            }
        }

        const data: RunPodStatusResponse = await res.json()

        if (data.status === "COMPLETED" && data.output?.model_url) {
            const localPath = await this.downloadModel(
                data.output.model_url,
                `unirig-rigged-${Date.now()}.glb`,
            )
            return {
                status: "completed",
                provider: this.slug,
                stage: "rigging",
                riggedModelPath: localPath,
                modelPath: localPath,
                generationTimeMs: Date.now() - startTime,
            }
        }

        if (data.status === "FAILED" || data.status === "CANCELLED" || data.status === "TIMED_OUT") {
            return {
                status: "failed",
                provider: this.slug,
                stage: "rigging",
                error: data.error ?? `RunPod job ${data.status}`,
            }
        }

        // Still processing
        return {
            status: "processing",
            provider: this.slug,
            stage: "rigging",
        }
    }
}
