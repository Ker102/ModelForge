import Link from "next/link"

import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { PRICING_TIERS } from "@/lib/stripe"
import { LocalLlmSettingsCard } from "@/components/dashboard/local-llm-settings-card"
import { PlanGrid } from "@/components/pricing/plan-grid"
import type { PlanKey } from "@/lib/plans"

export default async function SettingsPage({
  searchParams,
}: {
  searchParams?: Record<string, string | string[] | undefined>
}) {
  const session = await auth()
  
  if (!session?.user) {
    return null
  }

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    select: {
      email: true,
      name: true,
      subscriptionTier: true,
      subscriptionStatus: true,
      createdAt: true,
      localLlmProvider: true,
      localLlmUrl: true,
      localLlmModel: true,
      localLlmApiKey: true,
    },
  })

  if (!user) {
    return null
  }

  const currentTier = user.subscriptionTier as keyof typeof PRICING_TIERS
  const tierInfo = PRICING_TIERS[currentTier.toUpperCase() as keyof typeof PRICING_TIERS]
  const localConfig = {
    provider: (user.localLlmProvider as "ollama" | "lmstudio" | null) ?? "",
    baseUrl: user.localLlmUrl ?? "",
    model: user.localLlmModel ?? "",
    apiKeyConfigured: Boolean(user.localLlmApiKey),
  }

  const highlightPlanParam = typeof searchParams?.plan === "string" ? searchParams.plan.toLowerCase() : null
  const highlightPlan: PlanKey | null = highlightPlanParam === "starter" || highlightPlanParam === "pro"
    ? (highlightPlanParam as PlanKey)
    : null

  const focusPlans = typeof searchParams?.section === "string" && searchParams.section === "plans"

  const fromParam = typeof searchParams?.from === "string" ? decodeURIComponent(searchParams.from) : null
  const backUrl = fromParam && fromParam.startsWith("/") ? fromParam : "/dashboard"
  const backLabel = fromParam ? "Back" : "Back to dashboard"

  return (
    <div className="container py-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground mt-2">
            Manage your account and subscription
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Your account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium">Name</p>
              <p className="text-sm text-muted-foreground">{user.name}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Email</p>
              <p className="text-sm text-muted-foreground">{user.email}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Member since</p>
              <p className="text-sm text-muted-foreground">
                {new Date(user.createdAt).toLocaleDateString()}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Subscription</CardTitle>
            <CardDescription>Manage your subscription plan</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Current Plan</p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className="capitalize">{user.subscriptionTier}</Badge>
                  {user.subscriptionStatus && (
                    <Badge variant="outline" className="capitalize">
                      {user.subscriptionStatus}
                    </Badge>
                  )}
                </div>
              </div>
              {user.subscriptionTier !== "pro" && (
                <Link href="#plans">
                  <Button>Explore plans</Button>
                </Link>
              )}
            </div>

            <div className="rounded-lg border p-4 bg-muted/50">
              <p className="text-sm font-medium mb-2">Plan Features:</p>
              <ul className="space-y-1 text-sm text-muted-foreground">
                {tierInfo?.features.map((feature) => (
                  <li key={feature}>• {feature}</li>
                ))}
              </ul>
            </div>

            {user.subscriptionTier !== "free" && user.subscriptionStatus === "active" && (
              <Button variant="outline" className="w-full">
                Manage Billing
              </Button>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Choose your plan</CardTitle>
              <CardDescription>Upgrade instantly without leaving your account.</CardDescription>
            </div>
            <Button asChild variant="ghost" size="sm">
              <Link href={backUrl}>{backLabel}</Link>
            </Button>
          </CardHeader>
          <CardContent>
            <PlanGrid
              variant="settings"
              isAuthenticated
              currentTier={user.subscriptionTier}
              highlightPlan={highlightPlan}
              autoFocus={focusPlans}
              containerId="plans"
              returnPath="/dashboard/settings?section=plans"
            />
          </CardContent>
        </Card>

        <LocalLlmSettingsCard
          subscriptionTier={user.subscriptionTier}
          initialConfig={localConfig}
        />
      </div>
    </div>
  )
}
