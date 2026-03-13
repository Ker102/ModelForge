/**
 * Viewport Screenshot Module
 * 
 * Retrieves screenshots from Blender's viewport via MCP for visual analysis.
 * The Blender MCP server requires a filepath param and saves the screenshot there.
 */

import { tmpdir } from "os"
import path from "path"
import { readFile, unlink } from "fs/promises"
import { createMcpClient } from "./client"
import type { McpResponse, ViewportScreenshotResponse } from "./types"

/**
 * Capture a screenshot of the current Blender viewport.
 * Returns base64-encoded image data.
 * 
 * @param options - Screenshot options
 * @returns Base64-encoded PNG image data
 */
export async function getViewportScreenshot(options: {
    maxSize?: number
    format?: "png" | "jpeg"
} = {}): Promise<ViewportScreenshotResponse> {
    const client = createMcpClient()
    const filepath = path.join(tmpdir(), `modelforge_viewport_${Date.now()}.png`)

    try {
        const response = await client.execute<ViewportScreenshotResponse>({
            type: "get_viewport_screenshot",
            params: {
                filepath,
                ...(options.maxSize && { max_size: options.maxSize }),
                ...(options.format && { format: options.format }),
            },
        })

        if (response.status === "error") {
            throw new Error(response.message ?? "Failed to capture viewport screenshot")
        }

        // Check for nested error in result
        const result = response.result as Record<string, unknown> | undefined
        if (result?.error) {
            throw new Error(String(result.error))
        }

        // Try to get image from response first (some servers return inline base64)
        let imageBase64 = result?.image as string | undefined

        // If not inline, read from the saved filepath
        if (!imageBase64) {
            try {
                const buffer = await readFile(filepath)
                imageBase64 = buffer.toString("base64")
            } catch {
                throw new Error("Screenshot file not found - Blender MCP may not have saved it")
            }
        }

        return {
            image: imageBase64,
            width: (result?.width as number) ?? options.maxSize ?? 800,
            height: (result?.height as number) ?? options.maxSize ?? 800,
            format: ((result?.format as string) ?? options.format ?? "png") as "png" | "jpeg",
            timestamp: new Date().toISOString(),
        }
    } finally {
        // Always clean up temp file and close client
        await unlink(filepath).catch(() => { })
        await client.close()
    }
}

/**
 * Convert a viewport screenshot to a data URL for embedding.
 * 
 * @param screenshot - The screenshot response
 * @returns Data URL string (e.g., "data:image/png;base64,...")
 */
export function screenshotToDataUrl(screenshot: ViewportScreenshotResponse): string {
    const mimeType = screenshot.format === "jpeg" ? "image/jpeg" : "image/png"
    return `data:${mimeType};base64,${screenshot.image}`
}

/**
 * Estimate the size of a screenshot in bytes.
 * Useful for monitoring API payload sizes.
 * 
 * @param screenshot - The screenshot response
 * @returns Approximate size in bytes
 */
export function estimateScreenshotSize(screenshot: ViewportScreenshotResponse): number {
    // Base64 encoding increases size by ~33%
    return Math.ceil(screenshot.image.length * 0.75)
}
