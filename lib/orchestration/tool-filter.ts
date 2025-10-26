import { TOOL_REGISTRY } from "./tool-registry"

const CATEGORY_GROUPS: Record<string, string[]> = {
  inspection: ["get_scene_info", "get_object_info", "get_viewport_screenshot"],
  geometry: ["execute_code"],
  materials: ["execute_code", "set_texture"],
  lighting: ["execute_code"],
  camera: ["execute_code"],
  assets: [
    "get_polyhaven_status",
    "search_polyhaven_assets",
    "download_polyhaven_asset",
    "set_texture",
    "get_hyper3d_status",
    "create_rodin_job",
    "poll_rodin_job_status",
    "import_generated_asset",
    "get_sketchfab_status",
    "search_sketchfab_models",
    "download_sketchfab_model",
  ],
  advanced: ["execute_code"],
}

const KEYWORD_CATEGORY_MAP: Array<{ keywords: RegExp; categories: Array<keyof typeof CATEGORY_GROUPS> }> = [
  { keywords: /(create|add|generate|build)/i, categories: ["geometry"] },
  { keywords: /(color|material|texture|paint|shade|metallic)/i, categories: ["materials"] },
  { keywords: /(light|lighting|sun|shadow|illum|hdr)/i, categories: ["lighting", "assets"] },
  { keywords: /(camera|view|angle|isometric|shot)/i, categories: ["camera"] },
  { keywords: /(polyhaven|asset|hdri|texture|model|download)/i, categories: ["assets"] },
  { keywords: /(hyper3d|rodin|generate asset|ai model)/i, categories: ["assets"] },
  { keywords: /(sketchfab)/i, categories: ["assets"] },
  { keywords: /(complex|script|python|custom code)/i, categories: ["advanced"] },
  { keywords: /(modify|move|rotate|scale|adjust|change)/i, categories: ["geometry"] },
]

const BASELINE_TOOLS = new Set<string>(["get_scene_info"])

const HYPER3D_TOOLS = new Set([
  "get_hyper3d_status",
  "create_rodin_job",
  "poll_rodin_job_status",
  "import_generated_asset",
])

const SKETCHFAB_TOOLS = new Set([
  "get_sketchfab_status",
  "search_sketchfab_models",
  "download_sketchfab_model",
])

interface ToolFilterOptions {
  allowHyper3d?: boolean
  allowSketchfab?: boolean
}

export function filterRelevantTools(
  userRequest: string,
  planStepCount?: number,
  options: ToolFilterOptions = {}
): string[] {
  const normalized = userRequest.toLowerCase()
  const selected = new Set<string>(BASELINE_TOOLS)

  for (const { keywords, categories } of KEYWORD_CATEGORY_MAP) {
    if (keywords.test(normalized)) {
      categories.forEach((category) => {
        const tools = CATEGORY_GROUPS[category]
        tools?.forEach((tool) => selected.add(tool))
      })
    }
  }

  if ((planStepCount ?? 0) > 5) {
    CATEGORY_GROUPS.advanced.forEach((tool) => selected.add(tool))
  }

  if (options.allowHyper3d === false) {
    for (const tool of HYPER3D_TOOLS) {
      selected.delete(tool)
    }
  }

  if (options.allowSketchfab === false) {
    for (const tool of SKETCHFAB_TOOLS) {
      selected.delete(tool)
    }
  }

  return Array.from(selected)
}

export function formatToolListForPrompt(toolNames: string[]): string {
  const lines = toolNames
    .map((name) => {
      const metadata = TOOL_REGISTRY.find((tool) => tool.name === name)
      return metadata
        ? `- ${metadata.name}: ${metadata.description}`
        : `- ${name}`
    })
    .join("\n")

  return lines
}
