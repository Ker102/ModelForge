import { PRICING_TIERS } from "@/lib/stripe"

export type PlanKey = "free" | "starter" | "pro"

interface PlanConfig {
  key: PlanKey
  name: string
  description: string
  monthlyLabel: string
  yearlyLabel?: string
  features: string[]
  popular?: boolean
  cta?: string
  stripePriceIdMonthly?: string | null
}

export const PLAN_ORDER: PlanKey[] = ["free", "starter", "pro"]

export const PLAN_CONFIG: Record<PlanKey, PlanConfig> = {
  free: {
    key: "free",
    name: "Free",
    description: "Perfect for trying out ModelForge",
    monthlyLabel: "$0",
    features: PRICING_TIERS.FREE.features,
    cta: "Start Free",
    stripePriceIdMonthly: null,
  },
  starter: {
    key: "starter",
    name: "Starter",
    description: "For serious hobbyists and freelancers",
    monthlyLabel: `$${PRICING_TIERS.STARTER.priceMonthly}`,
    yearlyLabel: `$${PRICING_TIERS.STARTER.priceYearly}`,
    features: PRICING_TIERS.STARTER.features,
    popular: true,
    cta: "Start Trial",
    stripePriceIdMonthly: PRICING_TIERS.STARTER.stripePriceIds.monthly,
  },
  pro: {
    key: "pro",
    name: "Pro",
    description: "For professional studios and teams",
    monthlyLabel: `$${PRICING_TIERS.PRO.priceMonthly}`,
    yearlyLabel: `$${PRICING_TIERS.PRO.priceYearly}`,
    features: PRICING_TIERS.PRO.features,
    cta: "Start Trial",
    stripePriceIdMonthly: PRICING_TIERS.PRO.stripePriceIds.monthly,
  },
}

export function getPlanList(): PlanConfig[] {
  return PLAN_ORDER.map((key) => PLAN_CONFIG[key])
}
