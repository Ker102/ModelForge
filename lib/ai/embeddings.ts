// Embeddings Module
//
// Provides embedding generation using Google Gemini gemini-embedding-001
// - Configurable dimensions via output_dimensionality (768 default here)
// - Default model output is 3072 but we use 768 to match pgvector column
// - Uses Matryoshka Representation Learning (MRL) for dimension truncation
//
// Previously used Together.ai GTE-ModernBERT-base, but that model
// was deprecated as a serverless model (400 error).

const EMBEDDING_MODEL = "gemini-embedding-001"
const EMBEDDING_DIMENSIONS = 768
const MAX_BATCH_SIZE = 32

function getApiKey(): string {
    const apiKey = process.env.GEMINI_API_KEY
    if (!apiKey) {
        throw new Error("GEMINI_API_KEY is not configured")
    }
    return apiKey
}

export interface EmbeddingResult {
    embedding: number[]
    index: number
}

/**
 * Generate embeddings for a batch of texts using Gemini batchEmbedContents
 */
export async function embedTexts(texts: string[]): Promise<EmbeddingResult[]> {
    const apiKey = getApiKey()
    const results: EmbeddingResult[] = []

    // Process in batches
    for (let i = 0; i < texts.length; i += MAX_BATCH_SIZE) {
        const batch = texts.slice(i, i + MAX_BATCH_SIZE)

        const url = `https://generativelanguage.googleapis.com/v1beta/models/${EMBEDDING_MODEL}:batchEmbedContents`
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-goog-api-key": apiKey,
            },
            body: JSON.stringify({
                requests: batch.map((text) => ({
                    model: `models/${EMBEDDING_MODEL}`,
                    content: { parts: [{ text }] },
                    output_dimensionality: EMBEDDING_DIMENSIONS,
                })),
            }),
        })

        if (!response.ok) {
            const errorText = await response.text()
            throw new Error(`Gemini Embedding API error ${response.status}: ${errorText}`)
        }

        const data = (await response.json()) as {
            embeddings: Array<{ values: number[] }>
        }

        for (let j = 0; j < data.embeddings.length; j++) {
            results.push({
                embedding: data.embeddings[j].values,
                index: i + j,
            })
        }
    }

    return results
}

/**
 * Generate a single embedding
 */
export async function embedText(text: string): Promise<number[]> {
    const apiKey = getApiKey()

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${EMBEDDING_MODEL}:embedContent`
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-goog-api-key": apiKey,
        },
        body: JSON.stringify({
            content: { parts: [{ text }] },
            output_dimensionality: EMBEDDING_DIMENSIONS,
        }),
    })

    if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Gemini Embedding API error ${response.status}: ${errorText}`)
    }

    const data = (await response.json()) as {
        embedding: { values: number[] }
    }
    return data.embedding.values
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
