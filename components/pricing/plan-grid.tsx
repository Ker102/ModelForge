'use client'

import { useEffect, useMemo, useState, useTransition } from "react"
import { useRouter } from "next/navigation"

import { getPlanList, type PlanKey } from "@/lib/plans"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Check, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

type PlanGridVariant = "landing" | "settings"

interface PlanGridProps {
  variant?: PlanGridVariant
  isAuthenticated: boolean
  currentTier?: string | null
  redirectAfterLogin?: string
  returnPath?: string
  highlightPlan?: PlanKey | null
  autoFocus?: boolean
  containerId?: string
}

const DEFAULT_RETURN = "/dashboard/settings?section=plans"

const buildPlanPath = (basePath: string, plan: PlanKey): string => {
  try {
    const [pathPart, hashPart] = basePath.split("#")
    const url = new URL(pathPart || "/", "https://placeholder.local")
    const params = new URLSearchParams(url.search)
    if (!params.has("section")) {
      params.set("section", "plans")
    }
    params.set("plan", plan)
    const query = params.toString()
    const rebuilt = `${url.pathname}${query ? `?${query}` : ""}`
    return hashPart ? `${rebuilt}#${hashPart}` : rebuilt
  } catch {
    return basePath
  }
}

export function PlanGrid({
  variant = "landing",
  isAuthenticated,
  currentTier,
  redirectAfterLogin = DEFAULT_RETURN,
  returnPath = DEFAULT_RETURN,
  highlightPlan,
  autoFocus = false,
  containerId,
}: PlanGridProps) {
  const plans = useMemo(() => getPlanList(), [])
  const router = useRouter()
  const normalizedTier = currentTier?.toLowerCase() ?? null
  const [pendingPlan, setPendingPlan] = useState<PlanKey | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  const handleSelect = (planKey: PlanKey) => {
    const plan = plans.find((item) => item.key === planKey)
    if (!plan) return
    setError(null)

    if (plan.key === "free") {
      if (!isAuthenticated) {
        router.push("/signup")
      } else {
        router.push(returnPath)
      }
      return
    }

    if (!isAuthenticated) {
      const targetPath = buildPlanPath(redirectAfterLogin, plan.key)
      const loginTarget = `/login?callbackUrl=${encodeURIComponent(targetPath)}`
      router.push(loginTarget)
      return
    }

    if (normalizedTier === plan.key) {
      return
    }

    if (!plan.stripePriceIdMonthly) {
      setError("Missing Stripe price configuration for this plan.")
      return
    }

    const cancelPath = buildPlanPath(returnPath, plan.key)
    const successPath = buildPlanPath(returnPath, plan.key)

    startTransition(async () => {
      setPendingPlan(plan.key)
      setError(null)
      try {
        const origin = window.location.origin
        const response = await fetch("/api/user/subscription", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            priceId: plan.stripePriceIdMonthly,
            cancelUrl: `${origin}${cancelPath}`,
            successUrl: `${origin}${successPath}`,
          }),
        })

        const data = (await response.json().catch(() => null)) as
          | { url?: string; error?: string }
          | null

        if (!response.ok || !data?.url) {
          throw new Error(data?.error ?? "Failed to start checkout session.")
        }

        window.location.href = data.url
      } catch (checkoutError) {
        const message =
          checkoutError instanceof Error
            ? checkoutError.message
            : "Unexpected error starting checkout."
        setError(message)
      } finally {
        setPendingPlan(null)
      }
    })
  }

  useEffect(() => {
    if (!autoFocus || !containerId) {
      return
    }
    const element = document.getElementById(containerId)
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }, [autoFocus, containerId])

  return (
    <div
      className={cn("space-y-4", autoFocus ? "scroll-mt-24" : undefined)}
      id={containerId}
    >
      {error && (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}
      <div className={cn("grid gap-8", "md:grid-cols-3")}>
        {plans.map((plan) => {
          const isCurrent = normalizedTier === plan.key
          const isLoading = pendingPlan === plan.key && isPending
          const highlight = plan.key === highlightPlan || plan.popular
          const isPaidPlan = plan.key !== "free"

          let buttonLabel = plan.cta ?? "Select"
          if (plan.key === "free") {
            if (isAuthenticated && isCurrent) {
              buttonLabel = "Current plan"
            } else {
              buttonLabel = plan.cta ?? "Start Free"
            }
          } else if (variant === "settings" && isPaidPlan) {
            buttonLabel = isCurrent ? "Current plan" : `Upgrade to ${plan.name}`
          } else if (isAuthenticated && isPaidPlan) {
            buttonLabel = isCurrent ? "Current plan" : `Upgrade to ${plan.name}`
          }

          const disabled = isCurrent || (plan.key !== "free" && isLoading)

          return (
            <Card
              key={plan.key}
              className={cn(
                "relative transition",
                highlight ? "border-primary shadow-lg" : ""
              )}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-0 right-0 flex justify-center">
                  <Badge className="px-3 py-1">Most Popular</Badge>
                </div>
              )}
              {highlightPlan === plan.key && !plan.popular && (
                <div className="absolute -top-4 left-0 right-0 flex justify-center">
                  <Badge variant="outline" className="px-3 py-1">
                    Selected
                  </Badge>
                </div>
              )}
              <CardHeader>
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <div className="pt-4">
                  <span className="text-4xl font-bold">{plan.monthlyLabel}</span>
                  {plan.yearlyLabel && (
                    <span className="text-sm text-muted-foreground">
                      /month
                      <br />
                      <span className="text-xs">or {plan.yearlyLabel}/year</span>
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button
                  className="w-full"
                  variant={plan.popular ? "default" : "outline"}
                  onClick={() => handleSelect(plan.key)}
                  disabled={disabled}
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Redirecting…
                    </span>
                  ) : (
                    buttonLabel
                  )}
                </Button>
              </CardFooter>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
