export type McpCommandType =
  | "create_object"
  | "delete_object"
  | "update_material"
  | "execute_python"
  | "adjust_lighting"
  | "adjust_camera"
  | "context_summary"
  | string

export interface McpCommand {
  id?: string
  type: McpCommandType
  params?: Record<string, unknown>
}

export interface McpResponse<T = unknown> {
  status: "ok" | "error"
  result?: T
  message?: string
  raw?: unknown
}

export interface McpClientConfig {
  host: string
  port: number
  timeoutMs: number
}
