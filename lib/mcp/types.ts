export type McpCommandType =
  | "execute_code"
  | "get_scene_info"
  | "get_object_info"
  | "get_viewport_screenshot"
  | "get_polyhaven_categories"
  | "search_polyhaven_assets"
  | "download_polyhaven_asset"
  | "set_texture"
  | "create_rodin_job"
  | "poll_rodin_job_status"
  | "import_generated_asset"
  | "search_sketchfab_models"
  | "download_sketchfab_model"
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
