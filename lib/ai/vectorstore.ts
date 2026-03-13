/**
 * Vector Store Module
 * 
 * Provides vector storage and retrieval using Neon PostgreSQL with pgvector.
 *
 * IMPORTANT: Prisma tagged template literals do NOT support type modifiers
 * like ::vector(768) because PostgreSQL rejects parameterized type modifiers.
 * We use Prisma.sql / Prisma.raw to inject the dimension as literal SQL.
 */

import { Prisma } from "@prisma/client"
import { prisma } from "@/lib/db"
import { embedText, embedTexts, EMBEDDING_DIMENSIONS } from "./embeddings"

export interface Document {
  content: string
  metadata?: Record<string, unknown>
  source?: string
}

export interface SearchResult {
  id: string
  content: string
  metadata: Record<string, unknown> | null
  source: string | null
  similarity: number
}

// Build the vector cast string as raw SQL (e.g. "::vector(768)")
// This MUST be Prisma.raw so it is injected as literal SQL, not a parameter.
const VECTOR_CAST = Prisma.raw(`::vector(${EMBEDDING_DIMENSIONS})`)

/**
 * Helper: format a number[] as a Prisma-safe SQL fragment "[1.0,2.0,...]::vector(768)"
 */
function vectorLiteral(embedding: number[]) {
  return Prisma.sql`${`[${embedding.join(",")}]`}${VECTOR_CAST}`
}

/**
 * Add a single document to the vector store
 */
export async function addDocument(doc: Document): Promise<string> {
  const embedding = await embedText(doc.content)

  const vec = vectorLiteral(embedding)
  const result = await prisma.$queryRaw<{ id: string }[]>`
    INSERT INTO document_embeddings (id, content, embedding, metadata, source, "createdAt")
    VALUES (
      gen_random_uuid(),
      ${doc.content},
      ${vec},
      ${JSON.stringify(doc.metadata ?? {})}::jsonb,
      ${doc.source ?? null},
      NOW()
    )
    RETURNING id::text
  `

  return result[0].id
}

/**
 * Add multiple documents to the vector store
 */
export async function addDocuments(docs: Document[]): Promise<string[]> {
  const embeddings = await embedTexts(docs.map((d) => d.content))

  // Wrap in a transaction so a mid-batch failure rolls back all inserts
  return prisma.$transaction(async (tx) => {
    const ids: string[] = []

    for (let i = 0; i < docs.length; i++) {
      const doc = docs[i]
      const embedding = embeddings[i].embedding

      const vec = vectorLiteral(embedding)
      const result = await tx.$queryRaw<{ id: string }[]>`
        INSERT INTO document_embeddings (id, content, embedding, metadata, source, "createdAt")
        VALUES (
          gen_random_uuid(),
          ${doc.content},
          ${vec},
          ${JSON.stringify(doc.metadata ?? {})}::jsonb,
          ${doc.source ?? null},
          NOW()
        )
        RETURNING id::text
      `

      ids.push(result[0].id)
    }

    return ids
  })
}

/**
 * Search for similar documents using cosine similarity
 */
export async function similaritySearch(
  query: string,
  options?: {
    limit?: number
    source?: string
    minSimilarity?: number
  }
): Promise<SearchResult[]> {
  const queryEmbedding = await embedText(query)
  const limit = options?.limit ?? 5
  const minSimilarity = options?.minSimilarity ?? 0.5
  const vec = vectorLiteral(queryEmbedding)

  let results: SearchResult[]

  if (options?.source) {
    results = await prisma.$queryRaw<SearchResult[]>`
      SELECT 
        id::text,
        content,
        metadata,
        source,
        1 - (embedding <=> ${vec}) as similarity
      FROM document_embeddings
      WHERE source = ${options.source}
        AND 1 - (embedding <=> ${vec}) >= ${minSimilarity}
      ORDER BY embedding <=> ${vec}
      LIMIT ${limit}
    `
  } else {
    results = await prisma.$queryRaw<SearchResult[]>`
      SELECT 
        id::text,
        content,
        metadata,
        source,
        1 - (embedding <=> ${vec}) as similarity
      FROM document_embeddings
      WHERE 1 - (embedding <=> ${vec}) >= ${minSimilarity}
      ORDER BY embedding <=> ${vec}
      LIMIT ${limit}
    `
  }

  return results
}

/**
 * Delete documents by source
 */
export async function deleteBySource(source: string): Promise<number> {
  const result = await prisma.$executeRaw`
    DELETE FROM document_embeddings WHERE source = ${source}
  `
  return result
}

/**
 * Get document count by source
 */
export async function getDocumentCount(source?: string): Promise<number> {
  if (source) {
    const result = await prisma.$queryRaw<{ count: bigint }[]>`
      SELECT COUNT(*) as count FROM document_embeddings WHERE source = ${source}
    `
    return Number(result[0].count)
  }

  const result = await prisma.$queryRaw<{ count: bigint }[]>`
    SELECT COUNT(*) as count FROM document_embeddings
  `
  return Number(result[0].count)
}
