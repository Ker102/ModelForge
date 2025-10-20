import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Check } from "lucide-react"

const plans = [
  {
    name: "Free",
    price: "$0",
    description: "Perfect for trying out ModelForge",
    features: [
      "5 AI requests per day",
      "1 active project",
      "Basic MCP commands",
      "Community support",
    ],
    cta: "Start Free",
    href: "/signup",
  },
  {
    name: "Starter",
    price: "$12",
    priceYearly: "$99",
    description: "For serious hobbyists and freelancers",
    features: [
      "500 AI requests per month",
      "10 active projects",
      "All MCP commands",
      "Viewport analysis",
      "Email support",
      "Export project history",
    ],
    cta: "Start Trial",
    href: "/signup",
    popular: true,
  },
  {
    name: "Pro",
    price: "$29",
    priceYearly: "$249",
    description: "For professional studios and teams",
    features: [
      "Unlimited AI requests",
      "Unlimited projects",
      "Priority model access",
      "Advanced viewport analysis",
      "Asset library integration",
      "Priority support",
      "API access",
      "Team collaboration (soon)",
    ],
    cta: "Start Trial",
    href: "/signup",
  },
]

export function Pricing() {
  return (
    <section id="pricing" className="container py-20 md:py-32">
      <div className="mx-auto max-w-6xl">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">Simple, Transparent Pricing</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Choose the plan that fits your workflow. Cancel anytime.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`relative ${plan.popular ? "border-primary shadow-lg" : ""}`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-0 right-0 flex justify-center">
                  <Badge className="px-3 py-1">Most Popular</Badge>
                </div>
              )}
              <CardHeader>
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <div className="pt-4">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  {plan.priceYearly && (
                    <span className="text-sm text-muted-foreground">
                      /month
                      <br />
                      <span className="text-xs">or {plan.priceYearly}/year</span>
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
                <Link href={plan.href} className="w-full">
                  <Button
                    className="w-full"
                    variant={plan.popular ? "default" : "outline"}
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

