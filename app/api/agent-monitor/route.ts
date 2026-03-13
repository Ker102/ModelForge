/**
 * Agent Monitor API — DEV ONLY
 *
 * View all Blender agent pipeline events in one place.
 *
 * Usage:
 *   GET /api/agent-monitor              → All sessions (summary)
 *   GET /api/agent-monitor?id=<session> → Full session with events
 *   GET /api/agent-monitor?latest=true  → Latest session with events
 *   DELETE /api/agent-monitor           → Clear all sessions
 */

import { NextRequest, NextResponse } from "next/server"
import { agentMonitor } from "@/lib/agent-monitor"

export async function GET(req: NextRequest) {
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Monitor disabled in production" }, { status: 403 })
  }

  const sessionId = req.nextUrl.searchParams.get("id")
  const latest = req.nextUrl.searchParams.get("latest")

  if (sessionId) {
    const session = agentMonitor.getSession(sessionId)
    if (!session) {
      return NextResponse.json({ error: "Session not found" }, { status: 404 })
    }
    return NextResponse.json(session)
  }

  if (latest === "true") {
    const session = agentMonitor.getLatestSession()
    if (!session) {
      return NextResponse.json({ error: "No sessions recorded" }, { status: 404 })
    }
    return NextResponse.json(session)
  }

  // Return all sessions (summary only — no events for list view)
  const sessions = agentMonitor.getSessions().map(s => ({
    id: s.id,
    startedAt: s.startedAt,
    prompt: s.prompt.slice(0, 100),
    provider: s.provider,
    model: s.model,
    status: s.status,
    eventCount: s.events.length,
  }))

  return NextResponse.json({ sessions, count: sessions.length })
}

export async function DELETE() {
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Monitor disabled in production" }, { status: 403 })
  }

  agentMonitor.clear()
  return NextResponse.json({ cleared: true })
}
