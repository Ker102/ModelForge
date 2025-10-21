import { SubscriptionTier } from "@/lib/subscription"
import { UsageSummary } from "@/lib/usage"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface UsageSummaryCardProps {
  tier: SubscriptionTier
  usage: UsageSummary
}

function formatLimit(limit: number | null) {
  if (limit === null || limit === undefined || limit < 0) {
    return "Unlimited"
  }
  return limit.toLocaleString()
}

function formatUsageText(used: number, limit: number | null) {
  if (limit === null || limit < 0) {
    return `${used.toLocaleString()} used`
  }

  return `${used.toLocaleString()} / ${limit.toLocaleString()} used`
}

export function UsageSummaryCard({ tier, usage }: UsageSummaryCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div>
          <CardTitle className="text-xl font-semibold">Usage overview</CardTitle>
          <CardDescription>Your current AI request usage and limits</CardDescription>
        </div>
        <Badge variant="secondary" className="capitalize">
          {tier} plan
        </Badge>
      </CardHeader>
      <CardContent className="grid gap-6 md:grid-cols-2">
        <div className="space-y-1">
          <p className="text-sm font-medium text-muted-foreground">Daily AI requests</p>
          <p className="text-2xl font-semibold">
            {formatUsageText(usage.daily.used, usage.daily.limit)}
          </p>
          <p className="text-xs text-muted-foreground">
            Limit: {formatLimit(usage.daily.limit)}
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-sm font-medium text-muted-foreground">Monthly AI requests</p>
          <p className="text-2xl font-semibold">
            {formatUsageText(usage.monthly.used, usage.monthly.limit)}
          </p>
          <p className="text-xs text-muted-foreground">
            Limit: {formatLimit(usage.monthly.limit)}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
