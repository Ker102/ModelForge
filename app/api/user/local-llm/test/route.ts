import { NextResponse } from "next/server"
import { z } from "zod"

import { auth } from "@/lib/auth"

const providerSchema = z.enum(["ollama", "lmstudio"])

const payloadSchema = z.object({
  provider: providerSchema,
  baseUrl: z.string().url(),
  model: z.string().min(1),
  apiKey: z.string().optional().nullable(),
})

function normalizeBaseUrl(url: string) {
  return url.endsWith("/") ? url.slice(0, -1) : url
}

async function fetchWithTimeout(
  input: string,
  init: RequestInit,
  timeoutMs = 5000
) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  try {
    return await fetch(input, { ...init, signal: controller.signal })
  } finally {
    clearTimeout(timer)
  }
}

async function testOllama(baseUrl: string) {
  const url = `${normalizeBaseUrl(baseUrl)}/api/tags`
  const response = await fetchWithTimeout(url, { method: "GET" })

  if (!response.ok) {
    const message = await response.text().catch(() => "")
    throw new Error(
      message || `Ollama responded with status ${response.status}`
    )
  }
}

async function testLmStudio(baseUrl: string, apiKey?: string | null) {
  const url = `${normalizeBaseUrl(baseUrl)}/v1/models`
  const headers: Record<string, string> = {}
  if (apiKey) {
    headers.Authorization = `Bearer ${apiKey}`
  }

  const response = await fetchWithTimeout(url, { method: "GET", headers })

  if (!response.ok) {
    const message = await response.text().catch(() => "")
    throw new Error(
      message || `LM Studio responded with status ${response.status}`
    )
  }
}

export async function POST(req: Request) {
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

  const { provider, baseUrl, apiKey } = parsed.data

  try {
    if (provider === "ollama") {
      await testOllama(baseUrl)
    } else {
      await testLmStudio(baseUrl, apiKey)
    }
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Connection test failed"
    return NextResponse.json({ error: message }, { status: 502 })
  }

  return NextResponse.json({ success: true })
}
