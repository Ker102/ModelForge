import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"

export async function GET() {
  try {
    const session = await auth()
    
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const now = new Date()
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())

    // Get usage logs for the current month
    const monthlyUsage = await prisma.usageLog.count({
      where: {
        userId: session.user.id,
        requestType: "ai_request",
        createdAt: {
          gte: startOfMonth,
        },
      },
    })

    // Get usage logs for today
    const dailyUsage = await prisma.usageLog.count({
      where: {
        userId: session.user.id,
        requestType: "ai_request",
        createdAt: {
          gte: startOfDay,
        },
      },
    })

    return NextResponse.json({
      usage: {
        monthly: monthlyUsage,
        daily: dailyUsage,
      },
    })
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

    const { projectId, requestType, tokensUsed } = await req.json()

    await prisma.usageLog.create({
      data: {
        userId: session.user.id,
        projectId,
        requestType,
        tokensUsed,
      },
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

