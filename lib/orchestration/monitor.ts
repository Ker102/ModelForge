import { appendFile, mkdir } from "fs/promises"
import path from "path"

import type { ExecutionLogEntry } from "./types"

const LOG_DIR = path.join(process.cwd(), "logs")
const LOG_FILE = path.join(LOG_DIR, "orchestration.ndjson")

let directoryEnsured = false

async function ensureDirectory() {
  if (directoryEnsured) return
  await mkdir(LOG_DIR, { recursive: true })
  directoryEnsured = true
}

const replacer = (_key: string, value: unknown) => {
  if (value instanceof Error) {
    return { message: value.message, stack: value.stack }
  }
  if (typeof value === "bigint") {
    return value.toString()
  }
  if (typeof Buffer !== "undefined" && Buffer.isBuffer(value)) {
    return { type: "Buffer", data: value.toString("base64") }
  }
  return value
}

export interface ExecutionMonitorRecord {
  timestamp: string
  conversationId: string
  userId: string
  projectId: string
  request: string
  planSummary: string
  planSteps: number
  success: boolean
  fallbackUsed: boolean
  planRetries: number
  failedCommands: Array<{ id: string; tool: string; error?: string }>
  commandCount: number
  planErrors?: string[]
  tokenUsage?: { promptTokens?: number | null; responseTokens?: number | null; totalTokens?: number | null }
  executionLog?: ExecutionLogEntry[]
  sceneSummary?: string | null
}

export async function recordExecutionLog(record: ExecutionMonitorRecord) {
  try {
    await ensureDirectory()
    const line = `${JSON.stringify(record, replacer)}\n`
    await appendFile(LOG_FILE, line, { encoding: "utf8" })
  } catch (error) {
    console.error("Failed to write orchestration log:", error)
  }
}
