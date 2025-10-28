import NextAuth, { DefaultSession } from "next-auth"
import { PrismaAdapter } from "@auth/prisma-adapter"
import Credentials from "next-auth/providers/credentials"
import Google from "next-auth/providers/google"
import { prisma } from "@/lib/db"
import { stripe } from "@/lib/stripe"
import bcrypt from "bcryptjs"
import { z } from "zod"

declare module "next-auth" {
  interface Session {
    user: {
      id: string
      subscriptionTier: string
      subscriptionStatus: string | null
      stripeCustomerId?: string
      localLlmProvider?: string | null
      localLlmUrl?: string | null
      localLlmModel?: string | null
      localLlmApiKey?: string | null
    } & DefaultSession["user"]
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id?: string
    subscriptionTier?: string
    subscriptionStatus?: string | null
    stripeCustomerId?: string | null
    localLlmProvider?: string | null
    localLlmUrl?: string | null
    localLlmModel?: string | null
    localLlmApiKey?: string | null
  }
}

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
})

async function ensureStripeCustomer(userId: string) {
  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: {
      email: true,
      name: true,
      stripeCustomerId: true,
    },
  })

  if (!user?.email) {
    return
  }

  // Update metadata if already linked
  if (user.stripeCustomerId) {
    try {
      await stripe.customers.update(user.stripeCustomerId, {
        email: user.email,
        name: user.name ?? undefined,
        metadata: {
          userId,
        },
      })
    } catch (error) {
      console.error("Stripe customer update failed:", error)
    }
    return
  }

  let resolvedCustomerId: string | null = null

  try {
    const existing = await stripe.customers.list({
      email: user.email,
      limit: 1,
    })
    if (existing.data.length > 0) {
      resolvedCustomerId = existing.data[0].id
    }
  } catch (error) {
    console.error("Stripe customer lookup failed:", error)
  }

  if (resolvedCustomerId) {
    // Ensure no one else is linked to this customer
    const conflictingUser = await prisma.user.findFirst({
      where: {
        stripeCustomerId: resolvedCustomerId,
        NOT: { id: userId },
      },
      select: { id: true },
    })

    if (conflictingUser) {
      console.warn(
        `Stripe customer ${resolvedCustomerId} already associated with user ${conflictingUser.id}; skipping relink for ${userId}`
      )
      return
    }

    await prisma.user.update({
      where: { id: userId },
      data: { stripeCustomerId: resolvedCustomerId },
    })

    try {
      await stripe.customers.update(resolvedCustomerId, {
        email: user.email,
        name: user.name ?? undefined,
        metadata: { userId },
      })
    } catch (error) {
      console.error("Stripe customer metadata sync failed:", error)
    }

    return
  }

  try {
    const created = await stripe.customers.create({
      email: user.email,
      name: user.name ?? undefined,
      metadata: { userId },
    })

    await prisma.user.update({
      where: { id: userId },
      data: { stripeCustomerId: created.id },
    })
  } catch (error) {
    console.error("Stripe customer creation failed:", error)
  }
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  session: { strategy: "jwt" },
  pages: {
    signIn: "/login",
    error: "/login",
  },
  providers: [
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        try {
          const { email, password } = loginSchema.parse(credentials)

          const user = await prisma.user.findUnique({
            where: { email: email.toLowerCase() },
          })

          if (!user || !user.password) {
            return null
          }

          const isValidPassword = await bcrypt.compare(password, user.password)

          if (!isValidPassword) {
            return null
          }

          return {
            id: user.id,
            email: user.email,
            name: user.name,
            image: user.image,
          }
        } catch {
          return null
        }
      },
    }),
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? "",
      allowDangerousEmailAccountLinking: true,
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      
      if (token.id) {
        const dbUser = await prisma.user.findUnique({
          where: { id: token.id as string },
          select: {
            subscriptionTier: true,
            subscriptionStatus: true,
            stripeCustomerId: true,
            localLlmProvider: true,
            localLlmUrl: true,
            localLlmModel: true,
            localLlmApiKey: true,
          },
        })
        
        if (dbUser) {
          token.subscriptionTier = dbUser.subscriptionTier
          token.subscriptionStatus = dbUser.subscriptionStatus
          token.stripeCustomerId = dbUser.stripeCustomerId
          token.localLlmProvider = dbUser.localLlmProvider
          token.localLlmUrl = dbUser.localLlmUrl
          token.localLlmModel = dbUser.localLlmModel
          token.localLlmApiKey = dbUser.localLlmApiKey
        }
      }
      
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
        session.user.subscriptionTier = token.subscriptionTier as string
        session.user.subscriptionStatus = token.subscriptionStatus as string | null
        session.user.stripeCustomerId = (token as Record<string, unknown>).stripeCustomerId as string | undefined
        session.user.localLlmProvider = token.localLlmProvider ?? null
        session.user.localLlmUrl = token.localLlmUrl ?? null
        session.user.localLlmModel = token.localLlmModel ?? null
        session.user.localLlmApiKey = token.localLlmApiKey ?? null
      }
      return session
    },
  },
  events: {
    async signIn({ user }) {
      if (user?.id) {
        await ensureStripeCustomer(user.id)
      }
    },
  },
})
