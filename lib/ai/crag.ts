/**
 * CRAG (Corrective RAG) Module
 * 
 * Adds LLM-based relevance grading to RAG retrieval:
 * 1. Retrieve top-K documents via cosine similarity
 * 2. Grade each document's relevance to the query via Gemini
 * 3. Filter to only relevant/partially relevant docs
 * 4. If too few relevant docs, re-search with broader parameters
 */

import { createGeminiModel } from "./index"
import { similaritySearch, type SearchResult } from "./vectorstore"
import { HumanMessage, SystemMessage } from "@langchain/core/messages"
import type { MonitoringSession } from "@/lib/monitoring"

// ============================================================================
// Types
// ============================================================================

export type RelevanceGrade = "relevant" | "partially_relevant" | "not_relevant"

export interface GradedDocument extends SearchResult {
    grade: RelevanceGrade
    gradeReason: string
}

export interface CRAGResult {
    documents: GradedDocument[]
    totalRetrieved: number
    totalRelevant: number
    usedFallback: boolean
}

// ============================================================================
// Relevance Grading
// ============================================================================

const GRADING_PROMPT = `You are a relevance grader for Blender Python code retrieval.

Given a user query and a retrieved document, grade the document's relevance:
- "relevant": The document contains code patterns, API references, or techniques directly useful for the query.
- "partially_relevant": The document has some related content but doesn't directly address the query.
- "not_relevant": The document is unrelated to what the user needs.

Respond with ONLY valid JSON:
{"grade": "relevant"|"partially_relevant"|"not_relevant", "reason": "brief explanation"}

Be generous — if a document contains ANY useful Blender API patterns for the task, grade it as at least "partially_relevant".`

/**
 * Grade a single document's relevance to the query
 */
async function gradeDocument(
    query: string,
    doc: SearchResult,
    model: ReturnType<typeof createGeminiModel>
): Promise<GradedDocument> {
    try {
        const messages = [
            new SystemMessage(GRADING_PROMPT),
            new HumanMessage(
                `Query: "${query}"\n\nDocument (source: ${doc.source ?? "unknown"}, similarity: ${doc.similarity.toFixed(3)}):\n${doc.content.slice(0, 2000)}`
            ),
        ]

        const response = await model.invoke(messages)
        const text = (response.content as string).trim()

        // Parse JSON response — handle markdown code blocks
        const jsonStr = text.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim()
        const parsed = JSON.parse(jsonStr) as { grade: RelevanceGrade; reason: string }

        return {
            ...doc,
            grade: parsed.grade,
            gradeReason: parsed.reason,
        }
    } catch {
        // If grading fails, default to using similarity score as heuristic
        const grade: RelevanceGrade = doc.similarity >= 0.7 ? "relevant" : doc.similarity >= 0.5 ? "partially_relevant" : "not_relevant"
        return {
            ...doc,
            grade,
            gradeReason: "Grading failed, used similarity threshold fallback",
        }
    }
}

/**
 * Grade multiple documents in parallel
 */
async function gradeDocuments(
    query: string,
    docs: SearchResult[]
): Promise<GradedDocument[]> {
    if (docs.length === 0) return []

    const model = createGeminiModel({ temperature: 0.1, maxOutputTokens: 256 })

    // Grade all documents in parallel for speed
    const graded = await Promise.all(
        docs.map((doc) => gradeDocument(query, doc, model))
    )

    return graded
}

// ============================================================================
// Corrective Retrieval
// ============================================================================

/**
 * Corrective RAG retrieval: retrieve → grade → filter → fallback if needed
 * 
 * @param query - The user's natural language query
 * @param options - Retrieval options
 * @returns Graded and filtered documents with metadata
 */
export async function correctiveRetrieve(
    query: string,
    options: {
        topK?: number
        minSimilarity?: number
        source?: string
        /** Minimum number of relevant docs before triggering fallback */
        minRelevantDocs?: number
        /** Optional monitoring session for structured logging */
        monitor?: MonitoringSession
    } = {}
): Promise<CRAGResult> {
    const topK = options.topK ?? 8
    const minSimilarity = options.minSimilarity ?? 0.4
    const minRelevant = options.minRelevantDocs ?? 2
    const monitor = options.monitor

    monitor?.startTimer("crag_retrieval")

    // Step 1: Initial retrieval
    const initialDocs = await similaritySearch(query, {
        limit: topK,
        source: options.source ?? "blender-scripts",
        minSimilarity,
    })

    if (initialDocs.length === 0) {
        monitor?.warn("crag", "No documents retrieved from vector store", { query: query.slice(0, 100) })
        monitor?.endTimer("crag_retrieval")
        return {
            documents: [],
            totalRetrieved: 0,
            totalRelevant: 0,
            usedFallback: false,
        }
    }

    monitor?.info("crag", `Retrieved ${initialDocs.length} initial documents`, {
        topK,
        minSimilarity,
        docSources: initialDocs.map(d => d.source ?? "unknown"),
    })

    // Step 2: Grade relevance
    monitor?.startTimer("crag_grading")
    const graded = await gradeDocuments(query, initialDocs)
    monitor?.endTimer("crag_grading")

    // Log individual grades
    for (const doc of graded) {
        monitor?.debug("crag", `Grade: ${doc.grade} — ${doc.source ?? "unknown"}`, {
            grade: doc.grade,
            reason: doc.gradeReason,
            similarity: doc.similarity,
        })
    }

    // Step 3: Filter to relevant + partially relevant
    const relevant = graded.filter(
        (d) => d.grade === "relevant" || d.grade === "partially_relevant"
    )

    // Step 4: Fallback if not enough relevant docs
    if (relevant.length < minRelevant) {
        monitor?.warn("crag", `Only ${relevant.length}/${minRelevant} relevant docs — triggering broader search`, {
            relevantCount: relevant.length,
            minRequired: minRelevant,
        })

        // Retry with lower threshold and more results
        const fallbackDocs = await similaritySearch(query, {
            limit: topK * 2,
            source: options.source ?? "blender-scripts",
            minSimilarity: Math.max(0.2, minSimilarity - 0.15),
        })

        // Filter out docs we already graded
        const existingIds = new Set(graded.map((d) => d.id))
        const newDocs = fallbackDocs.filter((d) => !existingIds.has(d.id))

        if (newDocs.length > 0) {
            const newGraded = await gradeDocuments(query, newDocs)
            const newRelevant = newGraded.filter(
                (d) => d.grade === "relevant" || d.grade === "partially_relevant"
            )

            // Combine original relevant + new relevant, sort by grade then similarity
            const combined = [...relevant, ...newRelevant]
            combined.sort((a, b) => {
                const gradeOrder = { relevant: 0, partially_relevant: 1, not_relevant: 2 }
                const gradeDiff = gradeOrder[a.grade] - gradeOrder[b.grade]
                if (gradeDiff !== 0) return gradeDiff
                return b.similarity - a.similarity
            })

            return {
                documents: combined.slice(0, topK),
                totalRetrieved: initialDocs.length + newDocs.length,
                totalRelevant: combined.length,
                usedFallback: true,
            }
        }
    }

    // Sort: relevant first, then by similarity
    relevant.sort((a, b) => {
        if (a.grade === "relevant" && b.grade !== "relevant") return -1
        if (b.grade === "relevant" && a.grade !== "relevant") return 1
        return b.similarity - a.similarity
    })

    return {
        documents: relevant,
        totalRetrieved: initialDocs.length,
        totalRelevant: relevant.length,
        usedFallback: false,
    }
}
