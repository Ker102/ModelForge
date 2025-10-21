import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { getUsageSummary, logUsage, TrackedRequestType } from "@/lib/usage"
import { z } from "zod"

export async function GET() {
  try {
    const session = await auth()
    
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const usage = await getUsageSummary(
      session.user.id,
      session.user.subscriptionTier
    )

    return NextResponse.json({ usage })
  } catch (error) {
    console.error("Get usage error:", error)
    return NextResponse.json(
      { error: "Failed to fetch usage" },
      { status: 500 }
    )
  }
}

export async function POST(req: Request) {
  try {
    const session = await auth()
    
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const bodySchema = z.object({
      projectId: z.string().optional(),
      requestType: z.enum([
        "ai_request",
        "mcp_command",
        "project_action",
      ] as const satisfies readonly TrackedRequestType[]),
      tokensUsed: z.number().int().nonnegative().optional(),
    })

    const { projectId, requestType, tokensUsed } = bodySchema.parse(
      await req.json()
    )

    await logUsage({
      userId: session.user.id,
      projectId,
      requestType,
      tokensUsed,
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Log usage error:", error)
    return NextResponse.json(
      { error: "Failed to log usage" },
      { status: 500 }
    )
  }
}
