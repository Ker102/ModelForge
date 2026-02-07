export type SubscriptionTier = "free" | "starter" | "pro"

export const PROJECT_LIMITS: Record<SubscriptionTier, number> = {
  free: 3,
  starter: 10,
  pro: -1, // unlimited
}

export const USAGE_LIMITS: Record<
  SubscriptionTier,
  { daily?: number | null; monthly?: number | null }
> = {
  free: {
    daily: 5,
    monthly: null,
  },
  starter: {
    daily: null,
    monthly: 500,
  },
  pro: {
    daily: null,
    monthly: null,
  },
}
