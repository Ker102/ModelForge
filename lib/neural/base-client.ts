/**
 * Neural 3D Generation — Abstract Base Client
 *
 * Every neural provider (Hunyuan Shape, Hunyuan Paint, TRELLIS, YVO3D, etc.)
 * extends this class. It provides shared utilities for downloading models,
 * preparing images, and polling async jobs.
 */

import fs from "fs/promises"
import path from "path"
import type {
    GenerationRequest,
    GenerationResult,
    Neural3DProviderMeta,
    ProviderSlug,
} from "./types"

/** Default output directory for downloaded neural models */
const DEFAULT_OUTPUT_DIR =
    process.env.NEURAL_3D_OUTPUT_DIR ?? path.join(process.cwd(), "tmp", "neural-output")

export abstract class Neural3DClient {
    /** Human-readable provider name (e.g. "Hunyuan Shape 2.1") */
    abstract readonly name: string

    /** Unique provider slug used in the registry / config */
    abstract readonly slug: ProviderSlug

    /** Static metadata about this provider's capabilities */
    abstract readonly meta: Neural3DProviderMeta

    // -------------------------------------------------------------------------
    // Abstract methods — every provider MUST implement these
    // -------------------------------------------------------------------------

    /** Run a generation request and return a result. */
    abstract generate(request: GenerationRequest): Promise<GenerationResult>

    /** Check whether the backing server / API is reachable. */
    abstract healthCheck(): Promise<boolean>

    // -------------------------------------------------------------------------
    // Shared utilities
    // -------------------------------------------------------------------------

    /**
     * Download a remote model file (GLB/OBJ) to a local directory.
     *
     * @returns The absolute local file path of the saved model.
     */
    protected async downloadModel(
        url: string,
        filename?: string,
        outDir: string = DEFAULT_OUTPUT_DIR,
    ): Promise<string> {
        await fs.mkdir(outDir, { recursive: true })

        const resolvedFilename =
            filename ?? `${this.slug}-${Date.now()}.glb`
        const destPath = path.join(outDir, resolvedFilename)

        const response = await fetch(url)
        if (!response.ok) {
            throw new Error(
                `Failed to download model from ${url}: ${response.status} ${response.statusText}`,
            )
        }

        const buffer = Buffer.from(await response.arrayBuffer())
        await fs.writeFile(destPath, buffer)

        return destPath
    }

    /**
     * Save raw binary data (e.g. from an API response body) to a local file.
     */
    protected async saveModelFromBuffer(
        data: Buffer,
        filename?: string,
        outDir: string = DEFAULT_OUTPUT_DIR,
    ): Promise<string> {
        await fs.mkdir(outDir, { recursive: true })

        const resolvedFilename =
            filename ?? `${this.slug}-${Date.now()}.glb`
        const destPath = path.join(outDir, resolvedFilename)
        await fs.writeFile(destPath, data)

        return destPath
    }

    /**
     * Read a local image file and return it as a base64 data URI string.
     */
    protected async imageToBase64(imagePath: string): Promise<string> {
        const buf = await fs.readFile(imagePath)
        const ext = path.extname(imagePath).replace(".", "").toLowerCase()
        const mime =
            ext === "png"
                ? "image/png"
                : ext === "webp"
                    ? "image/webp"
                    : "image/jpeg"
        return `data:${mime};base64,${buf.toString("base64")}`
    }

    /**
     * Generic async-job poll loop.
     *
     * Repeatedly calls `pollFn` at the given interval until it returns a
     * result with status "completed" or "failed", or until `maxWaitMs`
     * elapses.
     */
    protected async pollUntilDone(
        pollFn: () => Promise<GenerationResult>,
        intervalMs: number = 3_000,
        maxWaitMs: number = 300_000,
    ): Promise<GenerationResult> {
        const deadline = Date.now() + maxWaitMs

        while (Date.now() < deadline) {
            const result = await pollFn()
            if (result.status === "completed" || result.status === "failed") {
                return result
            }
            await new Promise((r) => setTimeout(r, intervalMs))
        }

        return {
            status: "failed",
            provider: this.slug,
            stage: "geometry",
            error: `Timed out after ${maxWaitMs / 1000}s waiting for generation to complete.`,
        }
    }
}
