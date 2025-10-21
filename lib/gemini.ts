const GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"
const DEFAULT_MODEL = "gemini-1.5-flash"

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

const SYSTEM_PROMPT = `You are ModelForge, an AI assistant that helps users work with Blender through the Model Context Protocol (MCP).
Respond with clear, actionable instructions. When appropriate, reference Blender concepts such as objects, modifiers, materials,
lighting, cameras, and animations. Return concise answers; list steps or commands when useful. If you need more information,
ask clarifying questions.`

interface GenerateOptions {
  messages: GeminiMessage[]
  history?: GeminiMessage[]
  temperature?: number
  topP?: number
  topK?: number
  maxOutputTokens?: number
}

function mapMessageToGeminiContent(message: GeminiMessage) {
  return {
    role: message.role === "assistant" ? "model" : "user",
    parts: [{ text: message.content }],
  }
}

export async function generateGeminiResponse({
  messages,
  history = [],
  temperature = 0.4,
  topP = 0.8,
  topK = 32,
  maxOutputTokens = 512,
}: GenerateOptions): Promise<GeminiResult> {
  const apiKey = process.env.GEMINI_API_KEY
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is not configured")
  }

  const model = process.env.GEMINI_MODEL ?? DEFAULT_MODEL
  const url = `${GEMINI_API_ENDPOINT}/models/${model}:generateContent?key=${apiKey}`

  const contents = [...history, ...messages].map(mapMessageToGeminiContent)

  const body = {
    contents,
    systemInstruction: {
      role: "system",
      parts: [{ text: SYSTEM_PROMPT }],
    },
    generationConfig: {
      temperature,
      topP,
      topK,
      maxOutputTokens,
    },
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
    throw new Error(message)
  }

  const candidate = json?.candidates?.[0]
  const text =
    candidate?.content?.parts
      ?.map((part: { text?: string }) => part.text ?? "")
      .join("")
      .trim() ?? ""

  if (!text) {
    throw new Error("Gemini returned an empty response")
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
