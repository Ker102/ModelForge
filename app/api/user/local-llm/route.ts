import { NextResponse } from "next/server"
import { z } from "zod"

import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"

const providerSchema = z.enum(["ollama", "lmstudio"])

const payloadSchema = z.object({
  provider: providerSchema.optional(),
  baseUrl: z.string().url().optional().nullable(),
  model: z.string().min(1).optional().nullable(),
  apiKey: z.string().optional().nullable(),
})

export async function GET() {
  const session = await auth()

  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    select: {
      subscriptionTier: true,
      localLlmProvider: true,
      localLlmUrl: true,
      localLlmModel: true,
      localLlmApiKey: true,
    },
  })

  if (!user) {
    return NextResponse.json({ error: "User not found" }, { status: 404 })
  }

  return NextResponse.json({
    subscriptionTier: user.subscriptionTier,
    provider: user.localLlmProvider,
    baseUrl: user.localLlmUrl,
    model: user.localLlmModel,
    apiKeyConfigured: Boolean(user.localLlmApiKey),
  })
}

export async function PATCH(req: Request) {
  const session = await auth()

  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const json = await req.json().catch(() => null)
  const parsed = payloadSchema.safeParse(json)

  if (!parsed.success) {
    return NextResponse.json(
      {
        error: "Invalid payload",
        details: parsed.error.flatten(),
      },
      { status: 400 }
    )
  }

  const { provider, baseUrl, model, apiKey } = parsed.data

  if (!provider) {
    await prisma.user.update({
      where: { id: session.user.id },
      data: {
        localLlmProvider: null,
        localLlmUrl: null,
        localLlmModel: null,
        localLlmApiKey: null,
      },
    })

    return NextResponse.json({ success: true })
  }

  if (!baseUrl || !model) {
    return NextResponse.json(
      {
        error: "baseUrl and model are required when provider is set",
      },
      { status: 400 }
    )
  }

  await prisma.user.update({
    where: { id: session.user.id },
    data: {
      localLlmProvider: provider,
      localLlmUrl: baseUrl,
      localLlmModel: model,
      localLlmApiKey: apiKey ?? null,
    },
  })

  return NextResponse.json({ success: true })
}
