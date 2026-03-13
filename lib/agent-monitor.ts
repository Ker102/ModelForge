/**
 * Agent Monitor — Centralized Observability for the Blender Agent
 *
 * Captures ALL events from the Blender agent pipeline in one place:
 * - RAG retrieval (docs fetched, similarity scores)
 * - CRAG grading (relevant/not_relevant, fallback triggers)
 * - LLM calls (provider, model, prompt length, response length, latency)
 * - Plan generation (steps, actions)
 * - Code generation (lines, chars)
 * - MCP execution (command, result, latency)
 * - Errors and recoveries
 *
 * In dev mode, all events are stored in-memory and queryable via
 * GET /api/agent-monitor
 */

export type AgentEventType =
  | "rag:search"
  | "rag:results"
  | "crag:grade"
  | "crag:filter"
  | "crag:fallback"
  | "llm:call_start"
  | "llm:call_end"
  | "llm:error"
  | "plan:start"
  | "plan:steps"
  | "plan:complete"
  | "codegen:start"
  | "codegen:complete"
  | "mcp:connect"
  | "mcp:execute"
  | "mcp:result"
  | "mcp:error"
  | "pipeline:start"
  | "pipeline:complete"
  | "pipeline:error"
  | "validation:start"
  | "validation:result"
  | "recovery:attempt"

export interface AgentEvent {
  id: number
  type: AgentEventType
  timestamp: string
  sessionId: string
  data: Record<string, unknown>
  /** Duration in ms (for timed events like LLM calls) */
  durationMs?: number
}

export interface AgentSession {
  id: string
  startedAt: string
  prompt: string
  provider: string
  model: string
  events: AgentEvent[]
  status: "running" | "completed" | "failed"
}

// ────────────────────────────────────────────────────────────────
// Singleton Monitor
// ────────────────────────────────────────────────────────────────

class AgentMonitor {
  private sessions: Map<string, AgentSession> = new Map()
  private eventCounter = 0
  private maxSessions = 50 // Keep last 50 sessions in memory

  /**
   * Start a new monitoring session
   */
  startSession(sessionId: string, prompt: string, provider: string, model: string): void {
    // Prune old sessions if needed
    if (this.sessions.size >= this.maxSessions) {
      const oldest = [...this.sessions.keys()][0]
      this.sessions.delete(oldest)
    }

    this.sessions.set(sessionId, {
      id: sessionId,
      startedAt: new Date().toISOString(),
      prompt,
      provider,
      model,
      events: [],
      status: "running",
    })

    this.log(sessionId, "pipeline:start", { prompt, provider, model })
    console.log(`\n[MONITOR] ═══════════════════════════════════════════════════`)
    console.log(`[MONITOR] Session ${sessionId.slice(0, 8)} started`)
    console.log(`[MONITOR] Provider: ${provider} | Model: ${model}`)
    console.log(`[MONITOR] Prompt: "${prompt.slice(0, 100)}"`)
    console.log(`[MONITOR] ═══════════════════════════════════════════════════\n`)
  }

  /**
   * Log an event to the current session
   */
  log(sessionId: string, type: AgentEventType, data: Record<string, unknown>, durationMs?: number): void {
    const session = this.sessions.get(sessionId)
    if (!session) {
      console.warn(`[MONITOR] No session found for ${sessionId}`)
      return
    }

    const event: AgentEvent = {
      id: ++this.eventCounter,
      type,
      timestamp: new Date().toISOString(),
      sessionId,
      data,
      durationMs,
    }

    session.events.push(event)

    // Console logging with icons for dev visibility
    const icon = EVENT_ICONS[type] ?? "📋"
    const duration = durationMs ? ` (${durationMs}ms)` : ""
    const detail = this.formatEventDetail(type, data)
    console.log(`[MONITOR] ${icon} ${type}${duration} — ${detail}`)
  }

  /**
   * Complete a session
   */
  completeSession(sessionId: string, success: boolean): void {
    const session = this.sessions.get(sessionId)
    if (!session) return

    session.status = success ? "completed" : "failed"
    this.log(sessionId, success ? "pipeline:complete" : "pipeline:error", {
      totalEvents: session.events.length,
      duration: Date.now() - new Date(session.startedAt).getTime(),
    })

    const totalMs = Date.now() - new Date(session.startedAt).getTime()
    const status = success ? "✅ COMPLETED" : "❌ FAILED"
    console.log(`[MONITOR] ───────────────────────────────────────────────────`)
    console.log(`[MONITOR] Session ${sessionId.slice(0, 8)} ${status} (${totalMs}ms, ${session.events.length} events)`)
    console.log(`[MONITOR] ═══════════════════════════════════════════════════\n`)
  }

  /**
   * Get all sessions (for the monitor API)
   */
  getSessions(): AgentSession[] {
    return [...this.sessions.values()].reverse() // newest first
  }

  /**
   * Get a specific session
   */
  getSession(sessionId: string): AgentSession | undefined {
    return this.sessions.get(sessionId)
  }

  /**
   * Get the latest session
   */
  getLatestSession(): AgentSession | undefined {
    const sessions = [...this.sessions.values()]
    return sessions[sessions.length - 1]
  }

  /**
   * Clear all sessions
   */
  clear(): void {
    this.sessions.clear()
    this.eventCounter = 0
  }

  /**
   * Format event detail for console logging
   */
  private formatEventDetail(type: AgentEventType, data: Record<string, unknown>): string {
    switch (type) {
      case "rag:search":
        return `query="${String(data.query ?? "").slice(0, 60)}" limit=${data.limit} source=${data.source}`
      case "rag:results":
        return `${data.count} docs found, top: ${String(data.topTitle ?? "none")} (${data.topSimilarity})`
      case "crag:grade":
        return `"${String(data.title ?? "").slice(0, 40)}" → ${data.grade} (${data.reason})`
      case "crag:filter":
        return `${data.relevant}/${data.total} docs relevant`
      case "crag:fallback":
        return `Triggered — only ${data.relevantCount} found, need ${data.minRequired}`
      case "llm:call_start":
        return `${data.provider}/${data.model} for ${data.purpose} (${data.promptChars} chars)`
      case "llm:call_end":
        return `${data.responseChars} chars response`
      case "llm:error":
        return `ERROR: ${String(data.error ?? "").slice(0, 100)}`
      case "plan:steps":
        return `${data.stepCount} steps: ${String(data.summary ?? "").slice(0, 100)}`
      case "codegen:complete":
        return `${data.lines} lines, ${data.chars} chars`
      case "mcp:execute":
        return `${data.command} ${JSON.stringify(data.params ?? {}).slice(0, 80)}`
      case "mcp:result":
        return `${data.status} ${JSON.stringify(data.result ?? {}).slice(0, 100)}`
      case "mcp:error":
        return `ERROR: ${String(data.error ?? "").slice(0, 100)}`
      case "pipeline:complete":
        return `${data.totalEvents} events, ${data.duration}ms total`
      case "pipeline:error":
        return `FAILED after ${data.totalEvents} events`
      default:
        return JSON.stringify(data).slice(0, 120)
    }
  }
}

const EVENT_ICONS: Partial<Record<AgentEventType, string>> = {
  "rag:search": "🔍",
  "rag:results": "📚",
  "crag:grade": "📝",
  "crag:filter": "🧹",
  "crag:fallback": "🔄",
  "llm:call_start": "🤖",
  "llm:call_end": "✨",
  "llm:error": "💥",
  "plan:start": "📐",
  "plan:steps": "📋",
  "plan:complete": "✅",
  "codegen:start": "⚙️",
  "codegen:complete": "💻",
  "mcp:connect": "🔌",
  "mcp:execute": "▶️",
  "mcp:result": "📦",
  "mcp:error": "🔥",
  "pipeline:start": "🚀",
  "pipeline:complete": "🏁",
  "pipeline:error": "❌",
  "validation:start": "🔬",
  "validation:result": "📊",
  "recovery:attempt": "🔧",
}

// Export singleton instance
export const agentMonitor = new AgentMonitor()
