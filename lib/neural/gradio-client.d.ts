/**
 * Type declarations for @gradio/client (optional dependency).
 *
 * @gradio/client is only used by TRELLIS 2 and Hunyuan Part providers.
 * It is loaded via dynamic import so the dependency is optional.
 */
declare module "@gradio/client" {
    export interface PredictResult {
        data: unknown[]
    }

    export interface GradioClient {
        predict(endpoint: string, data: Record<string, unknown>): Promise<PredictResult>
    }

    export const Client: {
        connect(url: string): Promise<GradioClient>
    }
}
