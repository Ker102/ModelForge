import { prisma } from "@/lib/db"
import { SubscriptionTier, USAGE_LIMITS } from "@/lib/subscription"

export type TrackedRequestType = "ai_request" | "mcp_command" | "project_action"

export interface UsageBucket {
  used: number
  limit: number | null
}

export interface UsageSummary {
  daily: UsageBucket
  monthly: UsageBucket
}

function resolveTier(tier?: string | null): SubscriptionTier {
  if (tier === "starter" || tier === "pro") {
    return tier
  }
  return "free"
}

export async function logUsage({
  userId,
  requestType,
  projectId,
  tokensUsed,
}: {
  userId: string
  requestType: TrackedRequestType
  projectId?: string
  tokensUsed?: number | null
}) {
  await prisma.usageLog.create({
    data: {
      userId,
      projectId,
      requestType,
      tokensUsed,
    },
  })
}

export async function getUsageSummary(
  userId: string,
  tier?: string | null
): Promise<UsageSummary> {
  const subscriptionTier = resolveTier(tier)
  const limits = USAGE_LIMITS[subscriptionTier]

  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  const [monthlyUsage, dailyUsage] = await Promise.all([
    prisma.usageLog.count({
      where: {
        userId,
        requestType: "ai_request",
        createdAt: {
          gte: startOfMonth,
        },
      },
    }),
    prisma.usageLog.count({
      where: {
        userId,
        requestType: "ai_request",
        createdAt: {
          gte: startOfDay,
        },
      },
    }),
  ])

  return {
    daily: {
      used: dailyUsage,
      limit: limits.daily ?? null,
    },
    monthly: {
      used: monthlyUsage,
      limit: limits.monthly ?? null,
    },
  }
}
