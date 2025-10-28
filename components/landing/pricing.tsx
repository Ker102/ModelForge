import { PlanGrid } from "@/components/pricing/plan-grid"

interface PricingProps {
  isAuthenticated: boolean
  currentTier?: string | null
}

export function Pricing({ isAuthenticated, currentTier }: PricingProps) {
  return (
    <section id="pricing" className="container py-20 md:py-32">
      <div className="mx-auto max-w-6xl">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">Simple, Transparent Pricing</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Choose the plan that fits your workflow. Cancel anytime.
          </p>
        </div>
        <PlanGrid
          variant="landing"
          isAuthenticated={isAuthenticated}
          currentTier={currentTier}
          redirectAfterLogin="/dashboard/settings?section=plans"
          returnPath="/dashboard/settings?section=plans"
        />
      </div>
    </section>
  )
}
