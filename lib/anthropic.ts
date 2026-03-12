/**
 * Anthropic Claude Integration
 *
 * Raw fetch-based integration (no SDK dependency) supporting:
 * - Direct Anthropic API (api.anthropic.com)
 * - Google Vertex AI (Claude on Vertex) with auto-ADC token refresh
 *
 * Uses the Anthropic Messages API with SSE streaming.
 *
 * Env vars (Direct Anthropic):
 *   ANTHROPIC_API_KEY       — direct API key (sk-ant-...)
 *   ANTHROPIC_MODEL         — model name (default: claude-opus-4-6)
 *   ANTHROPIC_BASE_URL      — optional custom base URL
 *
 * Env vars (Vertex AI — preferred):
 *   VERTEX_AI_PROJECT       — GCP project ID (e.g. "modelsandtraining")
 *   VERTEX_AI_LOCATION      — GCP region (default: "global")
 *   VERTEX_AI_ACCESS_TOKEN  — optional static token (auto-fetched via gcloud if omitted)
 */

import { execSync } from "child_process"

export interface AnthropicMessage {
  role: "user" | "assistant"
  content: string
}

export interface AnthropicUsage {
  promptTokens?: number | null
  responseTokens?: number | null
  totalTokens?: number | null
}

export interface AnthropicResult {
  text: string
  usage: AnthropicUsage
}

export interface AnthropicStreamChunk {
  textDelta?: string
  usage?: AnthropicUsage
}

interface AnthropicGenerateOptions {
  messages: AnthropicMessage[]
  history?: AnthropicMessage[]
  temperature?: number
  topP?: number
  maxOutputTokens?: number
  systemPrompt?: string
  responseMimeType?: string
}

// ============================================================================
// Configuration helpers
// ============================================================================

const DEFAULT_ANTHROPIC_MODEL = "claude-opus-4-6"
const ANTHROPIC_API_VERSION = "2023-06-01"

// ADC token cache — Google OAuth2 tokens expire in 60 min, refresh at 50 min
let cachedAdcToken: string | null = null
let adcTokenExpiry = 0
const ADC_TOKEN_TTL_MS = 50 * 60 * 1000 // 50 minutes

/**
 * Fetch Application Default Credentials token via gcloud CLI.
 * Caches the token for 50 minutes to avoid shelling out on every request.
 */
function getAdcToken(): string {
  const now = Date.now()
  if (cachedAdcToken && now < adcTokenExpiry) {
    return cachedAdcToken
  }

  try {
    const token = execSync(
      "gcloud auth print-access-token",
      { encoding: "utf-8", timeout: 60_000 }
    ).trim()

    if (!token || !token.startsWith("ya29.")) {
      throw new Error(`Unexpected token format: ${token.slice(0, 10)}...`)
    }

    cachedAdcToken = token
    adcTokenExpiry = now + ADC_TOKEN_TTL_MS
    console.log("[Anthropic] ADC token refreshed (expires in 50 min)")
    return token
  } catch (error) {
    throw new Error(
      `Failed to fetch ADC token via gcloud. Run 'gcloud auth application-default login' first. ` +
      `Error: ${error instanceof Error ? error.message : String(error)}`
    )
  }
}

interface ApiConfig {
  url: string
  headers: Record<string, string>
  bodyExtras: Record<string, unknown>
}

function getApiConfig(model: string): ApiConfig {
  // Check for Vertex AI first (project ID is the trigger)
  const vertexProject = process.env.VERTEX_AI_PROJECT
  const vertexLocation = process.env.VERTEX_AI_LOCATION ?? "global"

  if (vertexProject) {
    // Get token: prefer static env var, fallback to ADC auto-fetch
    const vertexToken = process.env.VERTEX_AI_ACCESS_TOKEN || getAdcToken()

    // Vertex AI endpoint for Claude
    // 'global' region uses aiplatform.googleapis.com (no prefix)
    // Regional endpoints use {region}-aiplatform.googleapis.com
    const host = vertexLocation === "global"
      ? "aiplatform.googleapis.com"
      : `${vertexLocation}-aiplatform.googleapis.com`
    const baseUrl = `https://${host}/v1/projects/${vertexProject}/locations/${vertexLocation}/publishers/anthropic/models/${model}`

    return {
      url: baseUrl, // :rawPredict or :streamRawPredict appended below
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${vertexToken}`,
      },
      bodyExtras: {
        anthropic_version: "vertex-2023-10-16",
      },
    }
  }

  // Direct Anthropic API
  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) {
    throw new Error(
      "ANTHROPIC_API_KEY is not configured (or set VERTEX_AI_PROJECT for Vertex AI with gcloud ADC)"
    )
  }

  const baseUrl = process.env.ANTHROPIC_BASE_URL ?? "https://api.anthropic.com"

  return {
    url: `${baseUrl}/v1/messages`,
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": ANTHROPIC_API_VERSION,
    },
    bodyExtras: {},
  }
}

function isVertexMode(): boolean {
  return !!process.env.VERTEX_AI_PROJECT
}

// ============================================================================
// Build request body
// ============================================================================

function buildMessages(
  history: AnthropicMessage[],
  messages: AnthropicMessage[]
): Array<{ role: string; content: string }> {
  const all = [...history, ...messages]

  // Anthropic requires alternating user/assistant turns starting with user
  const result: Array<{ role: string; content: string }> = []
  for (const msg of all) {
    const last = result[result.length - 1]
    if (last && last.role === msg.role) {
      // Merge consecutive same-role messages
      last.content += "\n\n" + msg.content
    } else {
      result.push({ role: msg.role, content: msg.content })
    }
  }

  // Must start with 'user' role
  if (result.length > 0 && result[0].role !== "user") {
    result.unshift({ role: "user", content: "Continue." })
  }

  return result
}

function buildRequestBody(
  options: AnthropicGenerateOptions,
  model: string,
  stream: boolean,
  extras: Record<string, unknown>
) {
  const messages = buildMessages(options.history ?? [], options.messages)
  const vertex = isVertexMode()

  return {
    // Vertex AI: model is in the URL, not the body
    ...(vertex ? {} : { model }),
    max_tokens: options.maxOutputTokens ?? 4096,
    temperature: options.temperature ?? 0.4,
    ...(options.topP !== undefined ? { top_p: options.topP } : {}),
    ...(options.systemPrompt ? { system: options.systemPrompt } : {}),
    messages,
    stream,
    ...extras,
  }
}

// ============================================================================
// Non-streaming generate
// ============================================================================

export async function generateAnthropicResponse(
  options: AnthropicGenerateOptions
): Promise<AnthropicResult> {
  const model = process.env.ANTHROPIC_MODEL ?? DEFAULT_ANTHROPIC_MODEL
  const config = getApiConfig(model)

  const url = isVertexMode() ? `${config.url}:rawPredict` : config.url
  const body = buildRequestBody(options, model, false, config.bodyExtras)

  const response = await fetch(url, {
    method: "POST",
    headers: config.headers,
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const errorBody = await response.text().catch(() => "")
    throw new Error(
      `Anthropic API error ${response.status}: ${errorBody.slice(0, 500)}`
    )
  }

  const json = (await response.json()) as {
    content?: Array<{ type: string; text?: string }>
    usage?: { input_tokens?: number; output_tokens?: number }
  }

  const text =
    json.content
      ?.filter((block) => block.type === "text")
      .map((block) => block.text ?? "")
      .join("")
      .trim() ?? ""

  if (!text) {
    throw new Error("Anthropic returned an empty response")
  }

  const usage = json.usage
  return {
    text,
    usage: {
      promptTokens: usage?.input_tokens ?? null,
      responseTokens: usage?.output_tokens ?? null,
      totalTokens:
        usage?.input_tokens && usage?.output_tokens
          ? usage.input_tokens + usage.output_tokens
          : null,
    },
  }
}

// ============================================================================
// SSE Streaming
// ============================================================================

export async function* streamAnthropicResponse(
  options: AnthropicGenerateOptions
): AsyncGenerator<AnthropicStreamChunk> {
  const model = process.env.ANTHROPIC_MODEL ?? DEFAULT_ANTHROPIC_MODEL
  const config = getApiConfig(model)

  const url = isVertexMode() ? `${config.url}:streamRawPredict` : config.url
  const body = buildRequestBody(options, model, true, config.bodyExtras)

  const response = await fetch(url, {
    method: "POST",
    headers: config.headers,
    body: JSON.stringify(body),
  })

  if (!response.ok || !response.body) {
    const errorBody = await response.text().catch(() => "")
    throw new Error(
      `Anthropic streaming error ${response.status}: ${errorBody.slice(0, 500)}`
    )
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    buffer += decoder.decode(value ?? new Uint8Array(), { stream: !done })

    // Parse SSE events separated by double newlines
    let boundary: number
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const eventBlock = buffer.slice(0, boundary)
      buffer = buffer.slice(boundary + 2)

      // Extract event type and data
      let eventType = ""
      let dataPayload = ""

      for (const line of eventBlock.split("\n")) {
        if (line.startsWith("event: ")) {
          eventType = line.slice(7).trim()
        } else if (line.startsWith("data: ")) {
          dataPayload += line.slice(6)
        }
      }

      if (!dataPayload) continue

      let parsed: Record<string, unknown>
      try {
        parsed = JSON.parse(dataPayload) as Record<string, unknown>
      } catch {
        continue
      }

      // Handle different event types
      switch (eventType) {
        case "content_block_delta": {
          const delta = parsed.delta as { type?: string; text?: string } | undefined
          if (delta?.type === "text_delta" && delta.text) {
            yield { textDelta: delta.text }
          }
          break
        }

        case "message_delta": {
          // Final usage info
          const usage = parsed.usage as { output_tokens?: number } | undefined
          if (usage?.output_tokens) {
            yield {
              usage: {
                responseTokens: usage.output_tokens,
              },
            }
          }
          break
        }

        case "message_start": {
          // Initial message with input token count
          const message = parsed.message as {
            usage?: { input_tokens?: number }
          } | undefined
          if (message?.usage?.input_tokens) {
            yield {
              usage: {
                promptTokens: message.usage.input_tokens,
              },
            }
          }
          break
        }

        case "message_stop":
          // Stream complete
          break

        case "ping":
        case "content_block_start":
        case "content_block_stop":
          // No action needed
          break

        case "error": {
          const error = parsed.error as { message?: string } | undefined
          throw new Error(
            `Anthropic stream error: ${error?.message ?? "Unknown error"}`
          )
        }
      }
    }

    if (done) break
  }
}
