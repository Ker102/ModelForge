/**
 * Anthropic Claude Integration
 *
 * Raw fetch-based integration (no SDK dependency) supporting:
 * - Direct Anthropic API (api.anthropic.com)
 * - Google Vertex AI (Claude on Vertex)
 *
 * Uses the Anthropic Messages API with SSE streaming.
 * Env vars:
 *   ANTHROPIC_API_KEY       — direct API key
 *   ANTHROPIC_MODEL         — model name (default: claude-opus-4-20250514)
 *   ANTHROPIC_BASE_URL      — optional custom base URL
 *   VERTEX_AI_PROJECT       — GCP project for Vertex AI
 *   VERTEX_AI_LOCATION      — GCP region (default: us-east5)
 *   VERTEX_AI_ACCESS_TOKEN  — OAuth2 token for Vertex
 */

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

const DEFAULT_ANTHROPIC_MODEL = "claude-opus-4-20250514"
const ANTHROPIC_API_VERSION = "2023-06-01"

interface ApiConfig {
  url: string
  headers: Record<string, string>
  bodyExtras: Record<string, unknown>
}

function getApiConfig(model: string): ApiConfig {
  // Check for Vertex AI first
  const vertexProject = process.env.VERTEX_AI_PROJECT
  const vertexLocation = process.env.VERTEX_AI_LOCATION ?? "us-east5"
  const vertexToken = process.env.VERTEX_AI_ACCESS_TOKEN

  if (vertexProject && vertexToken) {
    // Vertex AI endpoint for Claude
    // Format: https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/anthropic/models/{MODEL}:streamRawPredict
    const baseUrl = `https://${vertexLocation}-aiplatform.googleapis.com/v1/projects/${vertexProject}/locations/${vertexLocation}/publishers/anthropic/models/${model}`

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
      "ANTHROPIC_API_KEY is not configured (or set VERTEX_AI_PROJECT + VERTEX_AI_ACCESS_TOKEN for Vertex)"
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
  return !!(process.env.VERTEX_AI_PROJECT && process.env.VERTEX_AI_ACCESS_TOKEN)
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

  return {
    model,
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
