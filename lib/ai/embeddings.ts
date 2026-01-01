/**
 * Embeddings Module
 * 
 * Provides embedding generation using Together.ai M2-BERT-Retrieval-32k
 * - 768-dimensional vectors
 * - 32k token context window
 * - Optimized for retrieval tasks
 */

import OpenAI from "openai"

const EMBEDDING_MODEL = "togethercomputer/m2-bert-80M-32k-retrieval"
const EMBEDDING_DIMENSIONS = 768
const MAX_BATCH_SIZE = 32

let client: OpenAI | null = null

function getClient(): OpenAI {
    if (client) return client

    const apiKey = process.env.TOGETHER_API_KEY
    if (!apiKey) {
        throw new Error("TOGETHER_API_KEY is not configured")
    }

    client = new OpenAI({
        apiKey,
        baseURL: "https://api.together.xyz/v1",
    })

    return client
}

export interface EmbeddingResult {
    embedding: number[]
    index: number
}

/**
 * Generate embeddings for a batch of texts
 */
export async function embedTexts(texts: string[]): Promise<EmbeddingResult[]> {
    const client = getClient()

    // Process in batches
    const results: EmbeddingResult[] = []

    for (let i = 0; i < texts.length; i += MAX_BATCH_SIZE) {
        const batch = texts.slice(i, i + MAX_BATCH_SIZE)

        const response = await client.embeddings.create({
            model: EMBEDDING_MODEL,
            input: batch,
        })

        for (const item of response.data) {
            results.push({
                embedding: item.embedding,
                index: i + item.index,
            })
        }
    }

    return results
}

/**
 * Generate a single embedding
 */
export async function embedText(text: string): Promise<number[]> {
    const results = await embedTexts([text])
    return results[0].embedding
}

/**
 * Compute cosine similarity between two vectors
 */
export function cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) {
        throw new Error("Vectors must have the same dimension")
    }

    let dotProduct = 0
    let normA = 0
    let normB = 0

    for (let i = 0; i < a.length; i++) {
        dotProduct += a[i] * b[i]
        normA += a[i] * a[i]
        normB += b[i] * b[i]
    }

    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB))
}

export { EMBEDDING_MODEL, EMBEDDING_DIMENSIONS }
