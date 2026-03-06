"use client"

import Link from "next/link"
import { motion } from "framer-motion"

interface PricingProps {
  isAuthenticated: boolean
  currentTier?: string | null
}

const plans = [
  {
    name: "Free",
    price: "$0",
    description: "Get started with AI-powered modeling",
    features: ["10 daily requests", "basic RAG", "MCP connection"],
    cta: "Get Free",
    popular: false,
    href: "/signup",
  },
  {
    name: "Starter",
    price: "$12",
    description: "Professional modeling workflow",
    features: [
      "100 daily requests",
      "advanced RAG + CRAG",
      "visual feedback loop",
      "priority support",
    ],
    cta: "Get Started",
    popular: true,
    href: "/signup",
  },
  {
    name: "Pro",
    price: "$29",
    description: "Full AI pipeline access",
    features: [
      "Unlimited requests",
      "neural 3D generation (Hunyuan, TRELLIS)",
      "Studio mode",
      "workflow automation",
      "dedicated support",
    ],
    cta: "Get Plan",
    popular: false,
    href: "/signup",
  },
]

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const headingVariants: any = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1], delay: i * 0.1 },
  }),
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const cardVariants: any = {
  hidden: { opacity: 0, y: 30, scale: 0.97 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1], delay: i * 0.12 },
  }),
}

function CheckIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="shrink-0">
      <circle cx="12" cy="12" r="10" fill="hsl(var(--forge-accent))" />
      <path d="M8 12l2.5 2.5L16 9" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function Pricing({ isAuthenticated, currentTier }: PricingProps) {
  return (
    <section id="pricing" className="py-20 md:py-28">
      <div className="container mx-auto max-w-5xl">
        <div className="text-center space-y-4 mb-16">
          <motion.h2
            variants={headingVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-80px" }}
            custom={0}
            className="text-3xl md:text-5xl font-bold tracking-tight"
            style={{ color: "hsl(var(--forge-text))" }}
          >
            Simple, Transparent Pricing
          </motion.h2>
          <motion.p
            variants={headingVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-80px" }}
            custom={1}
            className="text-lg max-w-2xl mx-auto"
            style={{ color: "hsl(var(--forge-text-muted))" }}
          >
            Choose the plan that fits your workflow. Cancel anytime.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          {plans.map((plan, idx) => (
            <motion.div
              key={plan.name}
              variants={cardVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-60px" }}
              custom={idx}
              whileHover={{ y: -6, transition: { duration: 0.25 } }}
              className="relative rounded-2xl p-6 flex flex-col"
              style={{
                backgroundColor: "white",
                border: plan.popular
                  ? "2px solid hsl(var(--forge-accent))"
                  : "1px solid hsl(var(--forge-border))",
                boxShadow: plan.popular
                  ? "0 8px 32px hsl(168 75% 32% / 0.12)"
                  : "0 2px 8px rgba(0,0,0,0.04)",
              }}
            >
              {/* Popular badge */}
              {plan.popular && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                  <span
                    className="px-4 py-1.5 rounded-full text-xs font-semibold text-white"
                    style={{ backgroundColor: "hsl(var(--forge-accent))" }}
                  >
                    Popular
                  </span>
                </div>
              )}

              {/* Header */}
              <div className="mb-6">
                <h3
                  className="text-lg font-semibold mb-1"
                  style={{ color: "hsl(var(--forge-text))" }}
                >
                  {plan.name}
                </h3>
                <div className="flex items-baseline gap-1 mb-2">
                  <span
                    className="text-4xl font-bold"
                    style={{ color: "hsl(var(--forge-text))" }}
                  >
                    {plan.price}
                  </span>
                  <span
                    className="text-sm"
                    style={{ color: "hsl(var(--forge-text-muted))" }}
                  >
                    /month
                  </span>
                </div>
                <p
                  className="text-sm"
                  style={{ color: "hsl(var(--forge-text-muted))" }}
                >
                  {plan.description}
                </p>
              </div>

              {/* Features */}
              <ul className="space-y-3 mb-8 flex-1">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2.5">
                    <CheckIcon />
                    <span
                      className="text-sm"
                      style={{ color: "hsl(var(--forge-text))" }}
                    >
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <Link href={plan.href} className="block">
                <button
                  className="w-full py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 hover:shadow-md"
                  style={
                    plan.popular
                      ? {
                        backgroundColor: "hsl(var(--forge-accent))",
                        color: "white",
                        boxShadow: "0 2px 8px hsl(168 75% 32% / 0.25)",
                      }
                      : {
                        backgroundColor: "white",
                        color: "hsl(var(--forge-text))",
                        border: "1px solid hsl(var(--forge-border))",
                      }
                  }
                >
                  {plan.cta}
                </button>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
