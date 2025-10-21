import { randomUUID } from "crypto"
import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import {
  canConsumeAiRequest,
  getUsageSummary,
  logUsage,
} from "@/lib/usage"
import { streamGeminiResponse } from "@/lib/gemini"
import { z } from "zod"

const MAX_HISTORY_MESSAGES = 12

type CommandStatus = "pending" | "ready" | "executed"

interface CommandStub {
  id: string
  tool: string
  description: string
  status: CommandStatus
  confidence: number
  arguments: Record<string, unknown>
  notes?: string
}

function createStubId() {
  try {
    return randomUUID()
  } catch {
    return `stub-${Date.now()}`
  }
}

function buildCommandStubs(prompt: string, response: string): CommandStub[] {
  const lowerPrompt = prompt.toLowerCase()
  const promptSnippet = prompt.slice(0, 200)
  const responseSnippet = response.slice(0, 200)

  const patterns: Array<{
    tool: string
    description: string
    confidence: number
    arguments: Record<string, unknown>
  }> = []

  const objectMatch = /(create|add)\s+(?:a|an|the)?\s*(cube|sphere|plane|mesh|object)/i.exec(prompt)
  if (objectMatch) {
    patterns.push({
      tool: "create_object",
      description: `Create a ${objectMatch[2]} in Blender`,
      confidence: 0.6,
      arguments: {
        objectType: objectMatch[2].toLowerCase(),
        source: "prompt",
      },
    })
  }

  if (/material|texture/.test(lowerPrompt)) {
    patterns.push({
      tool: "assign_material",
      description: "Update or assign materials based on user request",
      confidence: 0.45,
      arguments: {
        promptSnippet,
      },
    })
  }

  if (/light|lighting|hdr/i.test(prompt)) {
    patterns.push({
      tool: "adjust_lighting",
      description: "Modify scene lighting parameters",
      confidence: 0.4,
      arguments: {
        promptSnippet,
      },
    })
  }

  if (/camera|render|shot/i.test(prompt)) {
    patterns.push({
      tool: "adjust_camera",
      description: "Update camera position or render settings",
      confidence: 0.35,
      arguments: {
        promptSnippet,
      },
    })
  }

  const stubs = patterns.map((pattern) => ({
    id: createStubId(),
    tool: pattern.tool,
    description: pattern.description,
    status: "pending" as CommandStatus,
    confidence: pattern.confidence,
    arguments: {
      ...pattern.arguments,
      assistantSummary: responseSnippet,
    },
    notes: "Auto-generated placeholder. Replace with precise MCP command once integration is ready.",
  }))

  if (stubs.length === 0) {
    stubs.push({
      id: createStubId(),
      tool: "context_summary",
      description: "Review user intent and map to MCP commands",
      status: "pending",
      confidence: 0.2,
      arguments: {
        promptSnippet,
        assistantSummary: responseSnippet,
      },
      notes: "Use this stub to draft actual MCP command sequence when the planner is available.",
    })
  }

  return stubs
}

const chatRequestSchema = z.object({
  projectId: z.string().uuid(),
  conversationId: z.string().uuid().optional(),
  startNew: z.boolean().optional(),
  message: z.string().min(1).max(2000),
})

async function ensureConversation({
  projectId,
  userId,
  conversationId,
  startNew,
}: {
  projectId: string
  userId: string
  conversationId?: string
  startNew?: boolean
}) {
  if (conversationId) {
    const conversation = await prisma.conversation.findFirst({
      where: {
        id: conversationId,
        project: {
          id: projectId,
          userId,
          isDeleted: false,
        },
      },
      select: { id: true },
    })

    if (!conversation) {
      throw new Error("Conversation not found")
    }

    return conversationId
  }

  if (!startNew) {
    const existing = await prisma.conversation.findFirst({
      where: {
        project: {
          id: projectId,
          userId,
          isDeleted: false,
        },
      },
      orderBy: {
        lastMessageAt: "desc",
      },
      select: { id: true },
    })

    if (existing) {
      return existing.id
    }
  }

  const conversation = await prisma.conversation.create({
    data: {
      projectId,
    },
    select: { id: true },
  })

  return conversation.id
}

export async function POST(req: Request) {
  try {
    const session = await auth()

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await req.json()
    const { projectId, conversationId, startNew, message } =
      chatRequestSchema.parse(body)

    const project = await prisma.project.findFirst({
      where: {
        id: projectId,
        userId: session.user.id,
        isDeleted: false,
      },
      select: { id: true },
    })

    if (!project) {
      return NextResponse.json(
        { error: "Project not found" },
        { status: 404 }
      )
    }

    const quotaCheck = await canConsumeAiRequest(
      session.user.id,
      session.user.subscriptionTier
    )

    if (!quotaCheck.allowed) {
      const limitLabel =
        quotaCheck.limitType === "daily" ? "daily" : "monthly"
      return NextResponse.json(
        {
          error: `AI request limit reached for your ${limitLabel} allotment. Please upgrade your plan or try again later.`,
          usage: quotaCheck.usage,
        },
        { status: 429 }
      )
    }

    let resolvedConversationId: string
    try {
      resolvedConversationId = await ensureConversation({
        projectId,
        userId: session.user.id,
        conversationId,
        startNew,
      })
    } catch {
      return NextResponse.json(
        { error: "Conversation not found" },
        { status: 404 }
      )
    }

    const historyMessages = await prisma.message.findMany({
      where: { conversationId: resolvedConversationId },
      orderBy: { createdAt: "desc" },
      take: Math.max(0, MAX_HISTORY_MESSAGES - 1),
      select: {
        role: true,
        content: true,
      },
    })

    const trimmedHistory = historyMessages
      .reverse()
      .map((msg) => ({
        role: msg.role === "assistant" ? "assistant" : "user",
        content: msg.content,
      }))

    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      async start(controller) {
        const send = (data: unknown) => {
          controller.enqueue(
            encoder.encode(`${JSON.stringify(data)}\n`)
          )
        }

        send({ type: "init", conversationId: resolvedConversationId })

        let assistantText = ""
        let tokenUsage: { promptTokens?: number | null; responseTokens?: number | null; totalTokens?: number | null } | undefined

        try {
          for await (const chunk of streamGeminiResponse({
            history: trimmedHistory,
            messages: [
              {
                role: "user",
                content: message,
              },
            ],
            maxOutputTokens: 512,
          })) {
            if (chunk.textDelta) {
              assistantText += chunk.textDelta
              send({ type: "delta", delta: chunk.textDelta })
            }
            if (chunk.usage) {
              tokenUsage = chunk.usage
            }
          }

          const commandSuggestions = buildCommandStubs(message, assistantText)

          const result = await prisma.$transaction(async (tx) => {
            const userMessageRecord = await tx.message.create({
              data: {
                conversationId: resolvedConversationId,
                role: "user",
                content: message,
              },
              select: {
                id: true,
                role: true,
                content: true,
                createdAt: true,
              },
            })

            const assistantMessageRecord = await tx.message.create({
              data: {
                conversationId: resolvedConversationId,
                role: "assistant",
                content: assistantText,
                mcpCommands: commandSuggestions,
                mcpResults: tokenUsage?.totalTokens
                  ? {
                      tokens: tokenUsage,
                    }
                  : undefined,
              },
              select: {
                id: true,
                role: true,
                content: true,
                mcpCommands: true,
                createdAt: true,
              },
            })

            await tx.conversation.update({
              where: { id: resolvedConversationId },
              data: { lastMessageAt: assistantMessageRecord.createdAt },
            })

            return { userMessageRecord, assistantMessageRecord }
          })

          await logUsage({
            userId: session.user.id,
            projectId,
            requestType: "ai_request",
            tokensUsed: tokenUsage?.totalTokens ?? undefined,
          })

          const usage = await getUsageSummary(
            session.user.id,
            session.user.subscriptionTier
          )

          send({
            type: "complete",
            conversationId: resolvedConversationId,
            messages: [result.userMessageRecord, result.assistantMessageRecord],
            usage,
            tokenUsage,
            commandSuggestions,
          })
        } catch (error) {
          console.error("AI chat stream error:", error)
          send({
            type: "error",
            error:
              error instanceof Error
                ? error.message
                : "Failed to process AI request",
          })
        } finally {
          controller.close()
        }
      },
    })

    return new Response(stream, {
      headers: {
        "Content-Type": "application/x-ndjson",
        "Cache-Control": "no-cache",
      },
    })
  } catch (error) {
    console.error("AI chat error:", error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Invalid input data", details: error.flatten() },
        { status: 400 }
      )
    }

    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to process AI request" },
      { status: 500 }
    )
  }
}
