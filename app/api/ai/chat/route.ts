import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import {
  canConsumeAiRequest,
  getUsageSummary,
  logUsage,
} from "@/lib/usage"
import { generateGeminiResponse } from "@/lib/gemini"
import { z } from "zod"

const MAX_HISTORY_MESSAGES = 12

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

    const { text: assistantText, usage: tokenUsage } =
      await generateGeminiResponse({
        history: trimmedHistory,
        messages: [
          {
            role: "user",
            content: message,
          },
        ],
        maxOutputTokens: 512,
      })

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
          mcpResults: tokenUsage.totalTokens
            ? {
                tokens: tokenUsage,
              }
            : undefined,
        },
        select: {
          id: true,
          role: true,
          content: true,
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
      tokensUsed: tokenUsage.totalTokens ?? undefined,
    })

    const usage = await getUsageSummary(
      session.user.id,
      session.user.subscriptionTier
    )

    return NextResponse.json({
      conversationId: resolvedConversationId,
      messages: [result.userMessageRecord, result.assistantMessageRecord],
      usage,
      tokenUsage,
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
