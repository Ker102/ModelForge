
import Replicate from "replicate";

/**
 * Replicate Client Configuration
 * 
 * Used for interfacing with 3D generation models:
 * - Hunyuan3D-2: State-of-the-art for organic/characters
 * - Microsoft TRELLIS: State-of-the-art for hard-surface/geometric
 */

if (!process.env.REPLICATE_API_TOKEN) {
    console.warn("REPLICATE_API_TOKEN is not set. 3D generation features will fail.");
}

export const replicate = new Replicate({
    auth: process.env.REPLICATE_API_TOKEN,
});

// Model Identifiers on Replicate
export const MODELS = {
    HUNYUAN_3D_2: "tencent/hunyuan3d-2:3a364a66a6a2472d259c8491c6a28292882948685121b6d2e67df4844390748e", // Specific version hash might need update
    TRELLIS: "microsoft/trellis", // Using alias if available, or finding hash
    // Fallback/Latest versions (can be dynamic if needed)
} as const;

export interface GenerationRequest {
    prompt: string;
    image_url?: string;
    model_type: 'hunyuan' | 'trellis';
    quality?: 'fast' | 'high';
}

export interface GenerationResponse {
    id: string;
    status: 'starting' | 'processing' | 'succeeded' | 'failed' | 'canceled';
    output?: any; // Varies by model (GLB url, etc.)
    error?: string;
}
