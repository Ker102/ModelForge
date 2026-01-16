/**
 * Conversation Memory Service
 * 
 * Stores conversation history as vector embeddings for context-aware responses.
 * Uses the existing pgvector infrastructure and Together.ai M2-BERT embeddings.
 */

import { prisma } from "@/lib/db"
import { generateEmbedding } from "@/lib/ai"
import { Prisma } from "@prisma/client"

// ============================================================================
// Types
// ============================================================================

export interface MemoryMessage {
    id: string
    role: "user" | "assistant" | "system"
    content: string
    similarity?: number
    createdAt: Date
}

export interface MemorySearchOptions {
    limit?: number
    minSimilarity?: number
    roles?: ("user" | "assistant" | "system")[]
}

// ============================================================================
// ConversationMemory Class
// ============================================================================

/**
 * Manages conversation memory with vector embeddings for semantic search.
 */
export class ConversationMemory {
    private projectId: string
    private conversationId: string | null = null

    constructor(projectId: string, conversationId?: string) {
        this.projectId = projectId
        this.conversationId = conversationId ?? null
    }

    /**
     * Set the active conversation
     */
    setConversation(conversationId: string) {
        this.conversationId = conversationId
    }

    /**
     * Store a message with its embedding
     */
    async storeMessage(
        role: "user" | "assistant" | "system",
        content: string,
        metadata?: { mcpCommands?: unknown; mcpResults?: unknown }
    ): Promise<string> {
        // Ensure conversation exists
        if (!this.conversationId) {
            const conversation = await prisma.conversation.create({
                data: {
                    projectId: this.projectId,
                },
            })
            this.conversationId = conversation.id
        }

        // Generate embedding for semantic search
        const embedding = await generateEmbedding(content)

        // Store message with embedding using raw SQL (Prisma doesn't support vector type directly)
        const result = await prisma.$queryRaw<{ id: string }[]>`
      INSERT INTO messages (id, conversation_id, role, content, mcp_commands, mcp_results, embedding, created_at)
      VALUES (
        gen_random_uuid(),
        ${this.conversationId}::uuid,
        ${role},
        ${content},
        ${metadata?.mcpCommands ? JSON.stringify(metadata.mcpCommands) : null}::jsonb,
        ${metadata?.mcpResults ? JSON.stringify(metadata.mcpResults) : null}::jsonb,
        ${embedding}::vector(768),
        NOW()
      )
      RETURNING id::text
    `

        return result[0]?.id ?? ""
    }

    /**
     * Retrieve relevant context from past messages using semantic search
     */
    async retrieveContext(
        query: string,
        options: MemorySearchOptions = {}
    ): Promise<MemoryMessage[]> {
        const { limit = 5, minSimilarity = 0.5, roles } = options

        // Generate embedding for the query
        const queryEmbedding = await generateEmbedding(query)

        // Build role filter
        const roleFilter = roles?.length
            ? Prisma.sql`AND m.role = ANY(${roles}::text[])`
            : Prisma.sql``

        // Semantic search using cosine similarity
        const results = await prisma.$queryRaw<Array<{
            id: string
            role: string
            content: string
            similarity: number
            created_at: Date
        }>>`
      SELECT 
        m.id::text,
        m.role,
        m.content,
        1 - (m.embedding <=> ${queryEmbedding}::vector(768)) AS similarity,
        m.created_at
      FROM messages m
      JOIN conversations c ON m.conversation_id = c.id
      WHERE c.project_id = ${this.projectId}::uuid
        AND m.embedding IS NOT NULL
        ${roleFilter}
      ORDER BY m.embedding <=> ${queryEmbedding}::vector(768)
      LIMIT ${limit}
    `

        return results
            .filter(r => r.similarity >= minSimilarity)
            .map(r => ({
                id: r.id,
                role: r.role as "user" | "assistant" | "system",
                content: r.content,
                similarity: r.similarity,
                createdAt: r.created_at,
            }))
    }

    /**
     * Get recent messages from the current conversation (no embedding search)
     */
    async getRecentMessages(limit: number = 10): Promise<MemoryMessage[]> {
        if (!this.conversationId) {
            return []
        }

        const messages = await prisma.message.findMany({
            where: { conversationId: this.conversationId },
            orderBy: { createdAt: "desc" },
            take: limit,
            select: {
                id: true,
                role: true,
                content: true,
                createdAt: true,
            },
        })

        return messages.reverse().map(m => ({
            id: m.id,
            role: m.role as "user" | "assistant" | "system",
            content: m.content,
            createdAt: m.createdAt,
        }))
    }

    /**
     * Clear all messages for the current conversation
     */
    async clearConversation(): Promise<void> {
        if (!this.conversationId) return

        await prisma.message.deleteMany({
            where: { conversationId: this.conversationId },
        })
    }

    /**
     * Clear all conversation memory for the project
     */
    async clearAllMemory(): Promise<void> {
        // Delete all messages via conversations
        await prisma.conversation.deleteMany({
            where: { projectId: this.projectId },
        })
    }

    /**
     * Format retrieved context for injection into prompts
     */
    formatContextForPrompt(messages: MemoryMessage[]): string {
        if (messages.length === 0) {
            return ""
        }

        const formatted = messages
            .map(m => `[${m.role.toUpperCase()}]: ${m.content}`)
            .join("\n\n")

        return `## Relevant Past Conversations\n\n${formatted}`
    }
}

/**
 * Create a new ConversationMemory instance
 */
export function createConversationMemory(
    projectId: string,
    conversationId?: string
): ConversationMemory {
    return new ConversationMemory(projectId, conversationId)
}
