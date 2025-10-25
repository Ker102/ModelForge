import { ToolCategory, ToolMetadata } from "./types"

export const TOOL_REGISTRY: ToolMetadata[] = [
  {
    name: "get_scene_info",
    description:
      "Summarize the current Blender scene, including object names, counts, and basic transform data. Call this at the start of every plan to capture state.",
    category: "inspection",
  },
  {
    name: "get_object_info",
    description:
      "Inspect a specific object by name to retrieve type, transforms, materials, and bounding boxes. Use before modifying or reusing existing geometry.",
    category: "inspection",
  },
  {
    name: "get_viewport_screenshot",
    description:
      "Capture the active viewport for visual confirmation. Useful when the user requests a preview or validation of results.",
    category: "inspection",
  },
  {
    name: "execute_code",
    description:
      "Run custom Blender Python code to create or modify geometry, materials, lighting, or camera settings. Scripts should be concise and idempotent.",
    category: "advanced",
  },
  {
    name: "get_polyhaven_status",
    description:
      "Check whether PolyHaven integration is configured inside Blender and ready for asset downloads.",
    category: "assets",
  },
  {
    name: "search_polyhaven_assets",
    description:
      "Search the PolyHaven catalog for HDRIs, textures, or models using optional category filters.",
    category: "assets",
  },
  {
    name: "download_polyhaven_asset",
    description:
      "Download a PolyHaven asset by ID and import it into the Blender scene. Requires the status check to have succeeded.",
    category: "assets",
  },
  {
    name: "set_texture",
    description:
      "Apply a previously downloaded PolyHaven texture to a mesh object, creating material slots when needed.",
    category: "materials",
  },
  {
    name: "get_hyper3d_status",
    description:
      "Verify Hyper3D Rodin integration (mode and API keys) before attempting to generate assets.",
    category: "assets",
  },
  {
    name: "create_rodin_job",
    description:
      "Submit a Hyper3D Rodin generation job using text prompts or images. Returns identifiers for polling.",
    category: "assets",
  },
  {
    name: "poll_rodin_job_status",
    description:
      "Check the progress of a previously created Hyper3D job to determine whether assets are ready for import.",
    category: "assets",
  },
  {
    name: "import_generated_asset",
    description:
      "Download and import a generated Hyper3D asset into the scene, cleaning up temporary geometry.",
    category: "assets",
  },
  {
    name: "get_sketchfab_status",
    description:
      "Verify Sketchfab integration and credentials before searching the catalog.",
    category: "assets",
  },
  {
    name: "search_sketchfab_models",
    description:
      "Search Sketchfab for models that match user-provided keywords.",
    category: "assets",
  },
  {
    name: "download_sketchfab_model",
    description:
      "Download and import a Sketchfab model. Ensure usage rights are respected.",
    category: "assets",
  },
]

export function getToolMetadata(name: string): ToolMetadata | undefined {
  return TOOL_REGISTRY.find((tool) => tool.name === name)
}

export function toolsByCategory(category: ToolCategory): ToolMetadata[] {
  return TOOL_REGISTRY.filter((tool) => tool.category === category)
}
