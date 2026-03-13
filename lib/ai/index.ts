/**
 * ModelForge AI Module
 * 
 * Core AI infrastructure using:
 * - Gemini 3.1 Pro (customtools variant) for LLM generation
 * - Together.ai GTE-ModernBERT-base for embeddings
 * - LangChain.js for chains and agents
 * - Neon pgvector for RAG storage
 */

import { ChatGoogleGenerativeAI } from "@langchain/google-genai"
import OpenAI from "openai"

// ============================================================================
// Configuration
// ============================================================================

const DEFAULT_MODEL = process.env.GEMINI_MODEL ?? "gemini-2.5-pro"
const EMBEDDING_MODEL = "Alibaba-NLP/gte-modernbert-base"
const EMBEDDING_DIMENSIONS = 768

// ============================================================================
// LLM Client (Gemini)
// ============================================================================

/**
 * Create a LangChain-compatible Gemini chat model
 */
export function createGeminiModel(options?: {
    temperature?: number
    maxOutputTokens?: number
    model?: string
}) {
    const apiKey = process.env.GEMINI_API_KEY
    if (!apiKey) {
        throw new Error("GEMINI_API_KEY is not configured")
    }

    return new ChatGoogleGenerativeAI({
        apiKey,
        model: options?.model ?? DEFAULT_MODEL,
        temperature: options?.temperature ?? 0.4,
        maxOutputTokens: options?.maxOutputTokens ?? 65536,
    })
}

// ============================================================================
// Embeddings Client (Together.ai GTE-ModernBERT)
// ============================================================================

let togetherClient: OpenAI | null = null

/**
 * Get the Together.ai client (OpenAI-compatible)
 */
function getTogetherClient(): OpenAI {
    if (togetherClient) return togetherClient

    const apiKey = process.env.TOGETHER_API_KEY
    if (!apiKey) {
        throw new Error("TOGETHER_API_KEY is not configured")
    }

    togetherClient = new OpenAI({
        apiKey,
        baseURL: "https://api.together.xyz/v1",
    })

    return togetherClient
}

/**
 * Generate embeddings using Together.ai GTE-ModernBERT-base
 * @param input Single text or array of texts to embed
 * @returns Array of embedding vectors (768 dimensions each)
 */
export async function generateEmbeddings(
    input: string | string[]
): Promise<number[][]> {
    const client = getTogetherClient()

    const response = await client.embeddings.create({
        model: EMBEDDING_MODEL,
        input: Array.isArray(input) ? input : [input],
    })

    return response.data.map((item) => item.embedding)
}

/**
 * Generate a single embedding vector
 */
export async function generateEmbedding(text: string): Promise<number[]> {
    const embeddings = await generateEmbeddings(text)
    return embeddings[0]
}

// ============================================================================
// Exports
// ============================================================================

export { EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, DEFAULT_MODEL }

// Re-export types
export type { ChatGoogleGenerativeAI }
