
import { replicate, MODELS, GenerationRequest, GenerationResponse } from "./client";

export async function generate3D(request: GenerationRequest): Promise<GenerationResponse> {
    try {
        let modelId = "";
        let input: any = {};

        // Map request to specific model inputs
        if (request.model_type === 'hunyuan') {
            modelId = MODELS.HUNYUAN_3D_2;
            // Hunyuan specific inputs
            input = {
                prompt: request.prompt,
                image: request.image_url,
                // add other parameters as needed
            };
        } else if (request.model_type === 'trellis') {
            modelId = MODELS.TRELLIS;
            // Trellis specific inputs
            input = {
                image: request.image_url,
                // Trellis is primarily image-to-3d, might need text-to-image step if only prompt provided
                // For now assuming image_url is present or we fetch a temporary image driven by prompt
            };

            if (!request.image_url && request.prompt) {
                // TODO: Implement Text-to-Image step here if Trellis doesn't support text directly
                // For now, throw if no image
                // actually Trellis often takes image. 
            }
        }

        if (!modelId) {
            throw new Error("Invalid model type selected");
        }

        // Run the model
        // Note: Replicate.run waits for completion, .predictions.create is async
        console.log(`🚀 Starting generation with ${modelId}...`);
        const output = await replicate.run(modelId as any, { input });

        return {
            id: "generated-" + Date.now(), // Replicate run ID would be better if using predictions.create
            status: 'succeeded',
            output: output
        };

    } catch (error: any) {
        console.error("3D Generation Error:", error);
        return {
            id: "error-" + Date.now(),
            status: 'failed',
            error: error.message || "Unknown error during generation"
        };
    }
}
