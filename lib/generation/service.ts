
import { replicate, MODELS, GenerationRequest, GenerationResponse } from "./client";

export async function generate3D(request: GenerationRequest): Promise<GenerationResponse> {
    try {
        let modelId = "";
        let input: Record<string, unknown> = {};

        // Map request to specific model inputs
        if (request.model_type === 'hunyuan') {
            modelId = MODELS.HUNYUAN_3D_2;
            // Hunyuan specific inputs
            input = {
                prompt: request.prompt,
            };
            // Only include image if provided
            if (request.image_url) {
                input.image = request.image_url;
            }
        } else if (request.model_type === 'trellis') {
            modelId = MODELS.TRELLIS;

            // Trellis is primarily image-to-3D and requires an image
            if (!request.image_url) {
                // If no image but has prompt, we could implement text-to-image first
                // For now, return a clear validation error
                return {
                    id: "validation-" + Date.now(),
                    status: 'failed',
                    error: "TRELLIS model requires an image_url. Please provide an image or use Hunyuan3D for text-to-3D generation."
                };
            }

            input = {
                image: request.image_url,
            };
        }

        if (!modelId) {
            throw new Error("Invalid model type selected");
        }

        // Run the model
        console.log(`🚀 Starting generation with ${modelId}...`);
        const output = await replicate.run(modelId as `${string}/${string}`, { input });

        return {
            id: "generated-" + Date.now(),
            status: 'succeeded',
            output: output as string | string[]
        };

    } catch (error: unknown) {
        console.error("3D Generation Error:", error);
        return {
            id: "error-" + Date.now(),
            status: 'failed',
            error: error instanceof Error ? error.message : "Unknown error during generation"
        };
    }
}
