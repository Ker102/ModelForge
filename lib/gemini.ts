import { buildSystemPrompt } from "@/lib/orchestration/prompts"

const GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1"
const DEFAULT_MODEL = "gemini-3.1-pro-preview"

export interface GeminiMessage {
  role: "user" | "assistant"
  content: string
}

export interface GeminiUsage {
  promptTokens?: number | null
  responseTokens?: number | null
  totalTokens?: number | null
}

export interface GeminiResult {
  text: string
  usage: GeminiUsage
}

export interface GeminiStreamChunk {
  textDelta?: string
  usage?: GeminiUsage
}

const SYSTEM_PROMPT = buildSystemPrompt()

interface GenerateOptions {
  messages: GeminiMessage[]
  history?: GeminiMessage[]
  temperature?: number
  topP?: number
  topK?: number
  maxOutputTokens?: number
  systemPrompt?: string
  responseMimeType?: string
}

function mapMessageToGeminiContent(message: GeminiMessage) {
  return {
    role: message.role === "assistant" ? "model" : "user",
    parts: [{ text: message.content }],
  }
}

function buildContents(
  history: GeminiMessage[],
  messages: GeminiMessage[],
  systemPrompt = SYSTEM_PROMPT
) {
  const systemContent = {
    role: "user",
    parts: [{ text: systemPrompt }],
  }

  return [
    systemContent,
    ...history.map(mapMessageToGeminiContent),
    ...messages.map(mapMessageToGeminiContent),
  ]
}

export async function generateGeminiResponse({
  messages,
  history = [],
  temperature = 0.4,
  topP = 0.8,
  topK = 32,
  maxOutputTokens = 512,
  systemPrompt,
  responseMimeType,
}: GenerateOptions): Promise<GeminiResult> {
  const apiKey = process.env.GEMINI_API_KEY
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is not configured")
  }

  const model = process.env.GEMINI_MODEL ?? DEFAULT_MODEL
  const url = `${GEMINI_API_ENDPOINT}/models/${model}:generateContent?key=${apiKey}`

  const contents = buildContents(history, messages, systemPrompt)

  const attempts = responseMimeType ? [true, false] : [false]
  let lastError: Error | null = null

  for (const includeMimeType of attempts) {
    const body = {
      contents,
      generationConfig: {
        temperature,
        topP,
        topK,
        maxOutputTokens,
      },
      ...(includeMimeType && responseMimeType ? { responseMimeType } : {}),
    }

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })

    const json = await response.json()

    if (!response.ok) {
      const message =
        json?.error?.message ??
        `Gemini API request failed with status ${response.status}`

      if (
        includeMimeType &&
        typeof message === "string" &&
        message.includes('responseMimeType')
      ) {
        lastError = new Error(message)
        continue
      }

      throw new Error(message)
    }

    const candidate = json?.candidates?.[0]
    const text =
      candidate?.content?.parts
        ?.map((part: { text?: string }) => part.text ?? "")
        .join("")
        .trim() ?? ""

    if (!text) {
      lastError = new Error("Gemini returned an empty response")
      continue
    }

    const usageMetadata = json?.usageMetadata ?? {}

    return {
      text,
      usage: {
        promptTokens: usageMetadata.promptTokenCount ?? null,
        responseTokens: usageMetadata.candidatesTokenCount ?? null,
        totalTokens: usageMetadata.totalTokenCount ?? null,
      },
    }
  }

  throw lastError ?? new Error("Gemini request failed without a specific error message")
}

export async function* streamGeminiResponse(
  options: GenerateOptions
): AsyncGenerator<GeminiStreamChunk> {
  const apiKey = process.env.GEMINI_API_KEY
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is not configured")
  }

  const model = process.env.GEMINI_MODEL ?? DEFAULT_MODEL
  const url = `${GEMINI_API_ENDPOINT}/models/${model}:streamGenerateContent?alt=sse&key=${apiKey}`

  const {
    messages,
    history = [],
    temperature = 0.4,
    topP = 0.8,
    topK = 32,
    maxOutputTokens = 512,
    systemPrompt,
  } = options

  const contents = buildContents(history, messages, systemPrompt)

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      contents,
      generationConfig: {
        temperature,
        topP,
        topK,
        maxOutputTokens,
      },
    }),
  })

  if (!response.ok || !response.body) {
    let message = `Gemini streaming request failed with status ${response.status}`
    try {
      const json = await response.json()
      message =
        json?.error?.message ??
        message
    } catch {
      // ignore parse error
    }
    throw new Error(message)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""
  let emittedText = ""

  while (true) {
    const { done, value } = await reader.read()
    buffer += decoder.decode(value ?? new Uint8Array(), {
      stream: !done,
    })

    let eventBoundary: number
    while ((eventBoundary = buffer.indexOf("\n\n")) !== -1) {
      const eventChunk = buffer.slice(0, eventBoundary)
      buffer = buffer.slice(eventBoundary + 2)

      const dataPayload = eventChunk
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => line.startsWith("data:"))
        .map((line) => line.slice(5).trim())
        .filter((payload) => payload && payload !== "[DONE]")
        .join("")

      if (!dataPayload) {
        continue
      }

      let parsed: Record<string, unknown> | null
      try {
        parsed = JSON.parse(dataPayload) as Record<string, unknown>
      } catch {
        continue
      }

      const candidate = (parsed as { candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }> }).candidates?.[0]
      if (candidate?.content?.parts) {
        const text =
          candidate.content.parts
            .map((part: { text?: string }) => part.text ?? "")
            .join("") ?? ""

        if (text.length > emittedText.length) {
          const delta = text.slice(emittedText.length)
          emittedText = text
          if (delta) {
            yield { textDelta: delta }
          }
        }
      }

      const usageMetadata = (parsed as { usageMetadata?: { promptTokenCount?: number; candidatesTokenCount?: number; totalTokenCount?: number } }).usageMetadata
      if (usageMetadata) {
        yield {
          usage: {
            promptTokens: usageMetadata.promptTokenCount ?? null,
            responseTokens: usageMetadata.candidatesTokenCount ?? null,
            totalTokens: usageMetadata.totalTokenCount ?? null,
          },
        }
      }
    }

    if (done) {
      // Attempt to flush any remaining partial event
      const trimmed = buffer.trim()
      if (trimmed && trimmed !== "[DONE]") {
        try {
          const parsed = JSON.parse(trimmed) as Record<string, unknown>
          const candidate = (parsed as { candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }> }).candidates?.[0]
          if (candidate?.content?.parts) {
            const text =
              candidate.content.parts
                .map((part: { text?: string }) => part.text ?? "")
                .join("") ?? ""
            if (text.length > emittedText.length) {
              const delta = text.slice(emittedText.length)
              emittedText = text
              if (delta) {
                yield { textDelta: delta }
              }
            }
          }
          const usageMetadata = (parsed as { usageMetadata?: { promptTokenCount?: number; candidatesTokenCount?: number; totalTokenCount?: number } }).usageMetadata
          if (usageMetadata) {
            yield {
              usage: {
                promptTokens: usageMetadata.promptTokenCount ?? null,
                responseTokens: usageMetadata.candidatesTokenCount ?? null,
                totalTokens: usageMetadata.totalTokenCount ?? null,
              },
            }
          }
        } catch {
          // ignore leftover parse errors
        }
      }
      break
    }
  }
}
