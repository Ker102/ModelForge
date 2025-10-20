import Stripe from 'stripe'

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || 'sk_test_placeholder', {
  apiVersion: '2025-02-24.acacia',
  typescript: true,
})

export const PRICING_TIERS = {
  FREE: {
    name: 'Free',
    price: 0,
    features: [
      '5 AI requests per day',
      '1 active project',
      'Basic MCP commands',
      'Community support'
    ],
    limits: {
      maxProjects: 1,
      dailyRequests: 5,
      modelAccess: 'gemini-2.0-flash'
    }
  },
  STARTER: {
    name: 'Starter',
    priceMonthly: 12,
    priceYearly: 99,
    stripePriceIds: {
      monthly: process.env.STRIPE_STARTER_MONTHLY_PRICE_ID || '',
      yearly: process.env.STRIPE_STARTER_YEARLY_PRICE_ID || '',
    },
    features: [
      '500 AI requests per month',
      '10 active projects',
      'All MCP commands',
      'Viewport analysis',
      'Email support',
      'Export project history'
    ],
    limits: {
      maxProjects: 10,
      monthlyRequests: 500,
      modelAccess: 'gemini-pro'
    }
  },
  PRO: {
    name: 'Pro',
    priceMonthly: 29,
    priceYearly: 249,
    stripePriceIds: {
      monthly: process.env.STRIPE_PRO_MONTHLY_PRICE_ID || '',
      yearly: process.env.STRIPE_PRO_YEARLY_PRICE_ID || '',
    },
    features: [
      'Unlimited AI requests',
      'Unlimited projects',
      'Priority model access',
      'Advanced viewport analysis',
      'Asset library integration',
      'Priority support',
      'API access',
      'Team collaboration (coming soon)'
    ],
    limits: {
      maxProjects: -1,
      monthlyRequests: -1,
      modelAccess: 'gemini-ultra'
    }
  }
} as const

export type SubscriptionTier = keyof typeof PRICING_TIERS

