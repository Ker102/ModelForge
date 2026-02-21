/**
 * Viewport Screenshot Module
 * 
 * Retrieves screenshots from Blender's viewport via MCP for visual analysis.
 */

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
    width?: number
    height?: number
    format?: "png" | "jpeg"
} = {}): Promise<ViewportScreenshotResponse> {
    const client = createMcpClient()

    try {
        const response = await client.execute<ViewportScreenshotResponse>({
            type: "get_viewport_screenshot",
            params: {
                ...(options.width && { width: options.width }),
                ...(options.height && { height: options.height }),
                ...(options.format && { format: options.format }),
            },
        })

        if (response.status === "error") {
            throw new Error(response.message ?? "Failed to capture viewport screenshot")
        }

        // The MCP server returns the screenshot in the result field
        const result = response.result

        if (!result?.image) {
            throw new Error("No image data received from Blender MCP")
        }

        return {
            image: result.image,
            width: result.width ?? options.width ?? 1920,
            height: result.height ?? options.height ?? 1080,
            format: result.format ?? options.format ?? "png",
            timestamp: new Date().toISOString(),
        }
    } finally {
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
