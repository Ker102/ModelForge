import type { GeminiMessage, GeminiResult, GeminiStreamChunk } from "@/lib/gemini"
import {
  generateGeminiResponse,
  streamGeminiResponse,
} from "@/lib/gemini"

export type LlmProviderSpec =
  | {
      type: "gemini"
    }
  | {
      type: "ollama"
      baseUrl: string
      model: string
    }
  | {
      type: "lmstudio"
      baseUrl: string
      model: string
      apiKey?: string | null
    }

export interface LlmGenerateOptions {
  messages: GeminiMessage[]
  history?: GeminiMessage[]
  temperature?: number
  topP?: number
  topK?: number
  maxOutputTokens?: number
  systemPrompt?: string
  responseMimeType?: string
}

export type LlmResult = GeminiResult
export type LlmStreamChunk = GeminiStreamChunk

function normalizeBaseUrl(url: string) {
  if (!url) return ""
  return url.endsWith("/") ? url.slice(0, -1) : url
}

function convertToPlainPrompt(
  options: LlmGenerateOptions,
  responseMimeType?: string
) {
  const { history = [], messages, systemPrompt } = options
  const parts: string[] = []

  if (systemPrompt) {
    parts.push(`System: ${systemPrompt}`.trim())
  }

  const allMessages = [...history, ...messages]
  for (const message of allMessages) {
    const roleLabel = message.role === "assistant" ? "Assistant" : "User"
    parts.push(`${roleLabel}: ${message.content}`)
  }

  if (responseMimeType === "application/json") {
    parts.push(
      "System: Respond with strict JSON. Do not include explanations or surrounding text."
    )
  }

  return parts.join("\n\n")
}

async function callOllama(
  provider: Extract<LlmProviderSpec, { type: "ollama" }>,
  options: LlmGenerateOptions
): Promise<LlmResult> {
  const url = `${normalizeBaseUrl(provider.baseUrl)}/api/generate`
  const prompt = convertToPlainPrompt(options, options.responseMimeType)

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: provider.model,
      prompt,
      stream: false,
      options: {
        temperature: options.temperature,
        top_p: options.topP,
      },
    }),
  })

  if (!response.ok) {
    const errorText = await response.text().catch(() => "")
    throw new Error(
      errorText || `Ollama request failed with status ${response.status}`
    )
  }

  const json = (await response.json()) as {
    response?: string
  }

  const text = json.response?.trim() ?? ""
  if (!text) {
    throw new Error("Ollama returned an empty response")
  }

  return {
    text,
    usage: {},
  }
}

async function callLmStudio(
  provider: Extract<LlmProviderSpec, { type: "lmstudio" }>,
  options: LlmGenerateOptions
): Promise<LlmResult> {
  const url = `${normalizeBaseUrl(provider.baseUrl)}/v1/chat/completions`
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  }
  if (provider.apiKey) {
    headers.Authorization = `Bearer ${provider.apiKey}`
  }

  const payload = {
    model: provider.model,
    temperature: options.temperature ?? 0.4,
    top_p: options.topP ?? 0.8,
    max_tokens: options.maxOutputTokens ?? 512,
    stream: false,
    messages: [
      ...(options.systemPrompt
        ? [{ role: "system", content: options.systemPrompt }]
        : []),
      ...(options.history ?? []).map((msg) => ({
        role: msg.role === "assistant" ? "assistant" : "user",
        content: msg.content,
      })),
      ...options.messages.map((msg) => ({
        role: msg.role === "assistant" ? "assistant" : "user",
        content: msg.content,
      })),
      ...(options.responseMimeType === "application/json"
        ? [{ role: "system", content: "Return only valid JSON." }]
        : []),
    ],
  }

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorText = await response.text().catch(() => "")
    throw new Error(
      errorText || `LM Studio request failed with status ${response.status}`
    )
  }

  const json = (await response.json()) as {
    choices?: Array<{ message?: { content?: string } }>
  }

  const choice = json.choices?.[0]
  const text = choice?.message?.content?.trim() ?? ""

  if (!text) {
    throw new Error("LM Studio returned an empty response")
  }

  return {
    text,
    usage: {},
  }
}

export async function generateLlmResponse(
  provider: LlmProviderSpec,
  options: LlmGenerateOptions
): Promise<LlmResult> {
  switch (provider.type) {
    case "gemini":
      return generateGeminiResponse(options)
    case "ollama":
      return callOllama(provider, options)
    case "lmstudio":
      return callLmStudio(provider, options)
    default:
      throw new Error(`Unsupported LLM provider: ${(provider as { type: string }).type}`)
  }
}

export async function* streamLlmResponse(
  provider: LlmProviderSpec,
  options: LlmGenerateOptions
): AsyncGenerator<LlmStreamChunk> {
  if (provider.type === "gemini") {
    yield* streamGeminiResponse(options)
    return
  }

  const result = await generateLlmResponse(provider, options)
  if (result.text) {
    yield { textDelta: result.text, usage: result.usage }
  }
}
