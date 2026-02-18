/**
 * Neural 3D Generation — Public API
 *
 * Barrel exports for lib/neural/*
 */

// Types
export type {
    ProviderSlug,
    PipelineStage,
    GenerationMode,
    Neural3DProviderMeta,
    GenerationRequest,
    GenerationResult,
    HybridPipelineOptions,
    PipelineStageStatus,
} from "./types"

// Base class
export { Neural3DClient } from "./base-client"

// Registry
export {
    PROVIDERS,
    getProvidersForStage,
    selectBestProvider,
    createNeuralClient,
} from "./registry"

// Hybrid Pipeline
export { runHybridPipeline } from "./hybrid-pipeline"
export type {
    HybridPipelineResult,
    PipelineProgressCallback,
} from "./hybrid-pipeline"
