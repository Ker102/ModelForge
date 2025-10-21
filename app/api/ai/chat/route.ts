import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import {
  canConsumeAiRequest,
  logUsage,
  UsageSummary,
} from "@/lib/usage"
import { z } from "zod"

const chatRequestSchema = z.object({
  projectId: z.string().uuid().optional(),
  message: z.string().min(1).max(2000),
  context: z
    .object({
      conversationId: z.string().uuid().optional(),
      previousMessages: z
        .array(
          z.object({
            role: z.enum(["user", "assistant", "system"]),
            content: z.string().max(4000),
          })
        )
        .optional(),
    })
    .optional(),
})

export async function POST(req: Request) {
  try {
    const session = await auth()

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await req.json()
    const { projectId, message } = chatRequestSchema.parse(body)

    if (projectId) {
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

    // Placeholder AI response. Replace with Gemini integration.
    const aiResponse = {
      role: "assistant",
      content: `ModelForge AI endpoint is not connected to an LLM yet. I received your prompt: “${message}”. This is a placeholder response.`,
    }

    await logUsage({
      userId: session.user.id,
      projectId,
      requestType: "ai_request",
    })

    const usage: UsageSummary = quotaCheck.allowed
      ? {
          daily: {
            used: quotaCheck.usage.daily.used + 1,
            limit: quotaCheck.usage.daily.limit,
          },
          monthly: {
            used: quotaCheck.usage.monthly.used + 1,
            limit: quotaCheck.usage.monthly.limit,
          },
        }
      : quotaCheck.usage

    return NextResponse.json({
      message: aiResponse,
      usage,
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
      { error: "Failed to process AI request" },
      { status: 500 }
    )
  }
}
