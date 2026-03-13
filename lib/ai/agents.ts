/**
 * Agents Module (v2 — LangChain v1 + LangGraph)
 *
 * Replaces the hand-rolled ReAct loop with LangChain 1.x `createAgent`
 * and middleware. The legacy implementation is preserved in agents.legacy.ts.
 *
 * Key improvements:
 *  - Built-in ReAct loop with hallucinated tool-call recovery
 *  - Middleware stack: viewport screenshots, context summarization
 *  - Session persistence via MemorySaver (thread_id = project ID)
 *  - LangSmith observability (auto-enabled via env vars)
 */

import { createAgent, createMiddleware, tool } from "langchain"
import { MemorySaver } from "@langchain/langgraph"
import { SystemMessage, isHumanMessage } from "@langchain/core/messages"
import { z } from "zod"

import { createMcpClient, getViewportScreenshot } from "@/lib/mcp"
import type { McpResponse } from "@/lib/mcp"
import { createGeminiModel, DEFAULT_MODEL } from "@/lib/ai"
import { similaritySearch } from "@/lib/ai/vectorstore"
import { formatContextFromSources } from "@/lib/ai/rag"
import type { AgentStreamEvent } from "@/lib/orchestration/types"
import { getAddonPromptHints } from "@/lib/ai/addon-registry"

import { readFileSync } from "fs"
import path from "path"

// ============================================================================
// System prompt (read from markdown file at module load time)
// ============================================================================

let SYSTEM_PROMPT: string
try {
  SYSTEM_PROMPT = readFileSync(
    path.join(process.cwd(), "lib/orchestration/prompts/blender-agent-system.md"),
    "utf-8"
  )
} catch {
  SYSTEM_PROMPT = "You are ModelForge, an expert Blender Python Developer."
}

// ============================================================================
// MCP Tool Wrappers
// ============================================================================

/**
 * Execute an MCP command and return a stringified result for the agent.
 */
async function executeMcpCommand(
  commandType: string,
  params: Record<string, unknown> = {}
): Promise<string> {
  const client = createMcpClient()
  try {
    const response: McpResponse = await client.execute({
      type: commandType,
      params,
    })
    if (response.status === "error") {
      return JSON.stringify({ error: response.message ?? "MCP command failed" })
    }
    return JSON.stringify(response.result ?? response.raw ?? { status: "ok" })
  } catch (error) {
    return JSON.stringify({
      error: error instanceof Error ? error.message : String(error),
    })
  } finally {
    await client.close().catch(() => undefined)
  }
}

// ---------- Core Tools ---------

const executeCode = tool(
  async ({ code }: { code: string }) => executeMcpCommand("execute_code", { code }),
  {
    name: "execute_code",
    description:
      "Execute a Blender Python script. Use this for geometry creation, material setup, " +
      "animation, lighting, camera, and any Blender Python API operation. " +
      "Break complex objects into SEPARATE calls — one component per call.",
    schema: z.object({
      code: z.string().describe("The Blender Python script to execute"),
    }),
  }
)

const getSceneInfo = tool(
  async () => executeMcpCommand("get_scene_info"),
  {
    name: "get_scene_info",
    description:
      "Get complete scene information including object list, materials, world settings. " +
      "ALWAYS call this first before making any changes.",
    schema: z.object({}),
  }
)

const getAllObjectInfo = tool(
  async ({ max_objects, start_index }: { max_objects?: number; start_index?: number }) =>
    executeMcpCommand("get_all_object_info", { max_objects, start_index }),
  {
    name: "get_all_object_info",
    description:
      "Get detailed info for all objects in the scene with transforms, materials, mesh stats, " +
      "modifiers, light/camera data. Supports pagination for large scenes.",
    schema: z.object({
      max_objects: z.number().optional().describe("Max objects to return (default 50)"),
      start_index: z.number().optional().describe("Start index for pagination (default 0)"),
    }),
  }
)

const getObjectInfo = tool(
  async ({ name }: { name: string }) =>
    executeMcpCommand("get_object_info", { name }),
  {
    name: "get_object_info",
    description: "Get detailed info about a specific Blender object by name.",
    schema: z.object({
      name: z.string().describe("Name of the Blender object to inspect"),
    }),
  }
)

const getViewportScreenshotTool = tool(
  async () => {
    try {
      const screenshot = await getViewportScreenshot()
      return JSON.stringify({
        status: "ok",
        width: screenshot.width,
        height: screenshot.height,
        format: screenshot.format,
        image_preview: `[Base64 image captured: ${screenshot.width}x${screenshot.height} ${screenshot.format}]`,
      })
    } catch (error) {
      return JSON.stringify({
        error: error instanceof Error ? error.message : "Failed to capture viewport",
      })
    }
  },
  {
    name: "get_viewport_screenshot",
    description:
      "Capture a screenshot of the current Blender viewport for visual verification. " +
      "Use after creating or modifying geometry to confirm the result looks correct.",
    schema: z.object({}),
  }
)

// ---------- Scene Management Tools ---------

const listMaterials = tool(
  async () => executeMcpCommand("list_materials"),
  {
    name: "list_materials",
    description:
      "List all materials in the .blend file with node counts and which objects they are assigned to. " +
      "Use this to inspect the material state before/after texture operations.",
    schema: z.object({}),
  }
)

const deleteObject = tool(
  async ({ name }: { name: string }) =>
    executeMcpCommand("delete_object", { name }),
  {
    name: "delete_object",
    description:
      "Safely delete an object from the Blender scene by name. " +
      "Also cleans up orphaned mesh/curve/light/camera data.",
    schema: z.object({
      name: z.string().describe("Name of the Blender object to delete"),
    }),
  }
)

// ---------- Phase 1A: Transform Tools ---------

const setObjectTransform = tool(
  async ({ name, location, rotation, scale }: { name: string; location?: number[]; rotation?: number[]; scale?: number[] }) =>
    executeMcpCommand("set_object_transform", { name, location, rotation, scale }),
  {
    name: "set_object_transform",
    description:
      "Set an object's location, rotation (in degrees), and/or scale. " +
      "Provide any combination of the three. Rotation uses Euler XYZ in degrees.",
    schema: z.object({
      name: z.string().describe("Name of the Blender object"),
      location: z.array(z.number()).length(3).optional().describe("[x, y, z] world location"),
      rotation: z.array(z.number()).length(3).optional().describe("[x, y, z] rotation in degrees"),
      scale: z.array(z.number()).length(3).optional().describe("[x, y, z] scale factors"),
    }),
  }
)

const renameObject = tool(
  async ({ name, new_name }: { name: string; new_name: string }) =>
    executeMcpCommand("rename_object", { name, new_name }),
  {
    name: "rename_object",
    description: "Rename a Blender object. Also renames its data block if it matches.",
    schema: z.object({
      name: z.string().describe("Current object name"),
      new_name: z.string().describe("New name to assign"),
    }),
  }
)

const duplicateObject = tool(
  async ({ name, new_name, linked }: { name: string; new_name?: string; linked?: boolean }) =>
    executeMcpCommand("duplicate_object", { name, new_name, linked }),
  {
    name: "duplicate_object",
    description:
      "Duplicate a Blender object. Use linked=true to share mesh data (instance). " +
      "Optionally provide new_name for the copy.",
    schema: z.object({
      name: z.string().describe("Name of the object to duplicate"),
      new_name: z.string().optional().describe("Name for the duplicate"),
      linked: z.boolean().optional().describe("If true, share mesh data (linked duplicate)"),
    }),
  }
)

const joinObjects = tool(
  async ({ names }: { names: string[] }) =>
    executeMcpCommand("join_objects", { names }),
  {
    name: "join_objects",
    description:
      "Join multiple MESH objects into one. The first name becomes the target object. " +
      "All others are merged into it.",
    schema: z.object({
      names: z.array(z.string()).min(2).describe("Array of object names to join (first = target)"),
    }),
  }
)

// ---------- Phase 1B: Modifier & Mesh Tools ---------

const addModifier = tool(
  async ({ name, modifier_type, modifier_name, properties }: { name: string; modifier_type: string; modifier_name?: string; properties?: Record<string, unknown> }) =>
    executeMcpCommand("add_modifier", { name, modifier_type, modifier_name, properties }),
  {
    name: "add_modifier",
    description:
      "Add a modifier to an object. Common types: SUBSURF, MIRROR, BEVEL, BOOLEAN, ARRAY, " +
      "SOLIDIFY, DECIMATE, SMOOTH, EDGE_SPLIT, WIREFRAME. " +
      "Use properties dict to set modifier settings (e.g. {levels: 2} for SUBSURF).",
    schema: z.object({
      name: z.string().describe("Target object name"),
      modifier_type: z.string().describe("Modifier type enum (e.g. SUBSURF, MIRROR, BEVEL)"),
      modifier_name: z.string().optional().describe("Custom name for the modifier"),
      properties: z.record(z.unknown()).optional().describe("Modifier properties to set (e.g. {levels: 2})"),
    }),
  }
)

const applyModifier = tool(
  async ({ name, modifier }: { name: string; modifier: string }) =>
    executeMcpCommand("apply_modifier", { name, modifier }),
  {
    name: "apply_modifier",
    description:
      "Apply (bake) a modifier on an object, making its effect permanent and removing it from the stack.",
    schema: z.object({
      name: z.string().describe("Object name"),
      modifier: z.string().describe("Name of the modifier to apply"),
    }),
  }
)

const applyTransforms = tool(
  async ({ name, location, rotation, scale }: { name: string; location?: boolean; rotation?: boolean; scale?: boolean }) =>
    executeMcpCommand("apply_transforms", { name, location, rotation, scale }),
  {
    name: "apply_transforms",
    description:
      "Apply (freeze) an object's transforms to its mesh data. " +
      "Resets location/rotation/scale to identity while keeping visual appearance. " +
      "Essential before exporting models.",
    schema: z.object({
      name: z.string().describe("Object name"),
      location: z.boolean().optional().describe("Apply location (default true)"),
      rotation: z.boolean().optional().describe("Apply rotation (default true)"),
      scale: z.boolean().optional().describe("Apply scale (default true)"),
    }),
  }
)

const shadeSmooth = tool(
  async ({ name, smooth, angle }: { name: string; smooth?: boolean; angle?: number }) =>
    executeMcpCommand("shade_smooth", { name, smooth, angle }),
  {
    name: "shade_smooth",
    description:
      "Set smooth or flat shading on a mesh object. " +
      "Use angle (degrees) for auto-smooth by angle (e.g. 30 = edges sharper than 30° stay sharp).",
    schema: z.object({
      name: z.string().describe("Object name"),
      smooth: z.boolean().optional().describe("True for smooth, false for flat (default true)"),
      angle: z.number().optional().describe("Auto-smooth angle in degrees (e.g. 30)"),
    }),
  }
)

// ---------- Phase 2: Medium-Priority Tools ---------

const parentSet = tool(
  async ({ child_name, parent_name, parent_type }: { child_name: string; parent_name: string; parent_type?: string }) =>
    executeMcpCommand("parent_set", { child_name, parent_name, parent_type }),
  {
    name: "parent_set",
    description:
      "Set a parent-child relationship between two objects. " +
      "The child will follow the parent's transforms.",
    schema: z.object({
      child_name: z.string().describe("Name of the child object"),
      parent_name: z.string().describe("Name of the parent object"),
      parent_type: z.string().optional().describe("Parent type: OBJECT (default), ARMATURE, BONE, etc."),
    }),
  }
)

const parentClear = tool(
  async ({ name, keep_transform }: { name: string; keep_transform?: boolean }) =>
    executeMcpCommand("parent_clear", { name, keep_transform }),
  {
    name: "parent_clear",
    description: "Remove the parent from an object. By default keeps the object's world transform.",
    schema: z.object({
      name: z.string().describe("Object to unparent"),
      keep_transform: z.boolean().optional().describe("Keep world transform after unparenting (default true)"),
    }),
  }
)

const setOrigin = tool(
  async ({ name, origin_type, center }: { name: string; origin_type?: string; center?: string }) =>
    executeMcpCommand("set_origin", { name, origin_type, center }),
  {
    name: "set_origin",
    description:
      "Set the origin (pivot point) of an object. Common types: " +
      "ORIGIN_GEOMETRY (origin to geometry center), ORIGIN_CURSOR (origin to 3D cursor), " +
      "GEOMETRY_ORIGIN (geometry to origin), ORIGIN_CENTER_OF_VOLUME.",
    schema: z.object({
      name: z.string().describe("Object name"),
      origin_type: z.string().optional().describe("Origin type (default ORIGIN_GEOMETRY)"),
      center: z.string().optional().describe("Center calculation: MEDIAN or BOUNDS (default MEDIAN)"),
    }),
  }
)

const moveToCollection = tool(
  async ({ name, collection_name, create_new }: { name: string; collection_name: string; create_new?: boolean }) =>
    executeMcpCommand("move_to_collection", { name, collection_name, create_new }),
  {
    name: "move_to_collection",
    description:
      "Move an object to a Blender collection for organization. " +
      "Set create_new=true to create the collection if it doesn't exist.",
    schema: z.object({
      name: z.string().describe("Object name"),
      collection_name: z.string().describe("Target collection name"),
      create_new: z.boolean().optional().describe("Create collection if it doesn't exist (default false)"),
    }),
  }
)

const setVisibility = tool(
  async ({ name, hide_viewport, hide_render }: { name: string; hide_viewport?: boolean; hide_render?: boolean }) =>
    executeMcpCommand("set_visibility", { name, hide_viewport, hide_render }),
  {
    name: "set_visibility",
    description:
      "Control an object's visibility in the viewport and/or render. " +
      "Set hide_viewport=true to hide in viewport, hide_render=true to hide in renders.",
    schema: z.object({
      name: z.string().describe("Object name"),
      hide_viewport: z.boolean().optional().describe("Hide in viewport"),
      hide_render: z.boolean().optional().describe("Hide in render"),
    }),
  }
)

const exportObject = tool(
  async ({ names, filepath, file_format }: { names: string[]; filepath: string; file_format?: string }) =>
    executeMcpCommand("export_object", { names, filepath, file_format }),
  {
    name: "export_object",
    description:
      "Export one or more objects to a file. Supported formats: GLB (default), GLTF, FBX, OBJ, STL. " +
      "Provide the full filepath including extension.",
    schema: z.object({
      names: z.array(z.string()).describe("Object name(s) to export"),
      filepath: z.string().describe("Full output file path (e.g. /tmp/model.glb)"),
      file_format: z.string().optional().describe("Format: GLB, GLTF, FBX, OBJ, or STL (default GLB)"),
    }),
  }
)

const listInstalledAddons = tool(
  async () => executeMcpCommand("list_installed_addons"),
  {
    name: "list_installed_addons",
    description:
      "List all enabled Blender addons with metadata. Use this to discover what " +
      "additional capabilities are available (e.g. Node Wrangler, Rigify, LoopTools). " +
      "Call this early to adapt your approach based on installed addons.",
    schema: z.object({}),
  }
)

// ---------- PolyHaven Tools ---------

const getPolyhavenCategories = tool(
  async ({ asset_type }: { asset_type: string }) =>
    executeMcpCommand("get_polyhaven_categories", { asset_type }),
  {
    name: "get_polyhaven_categories",
    description: "List available PolyHaven asset categories for a given type.",
    schema: z.object({
      asset_type: z.string().describe("Asset type: hdris, textures, models, or all"),
    }),
  }
)

const searchPolyhavenAssets = tool(
  async ({ asset_type, categories }: { asset_type?: string; categories?: string }) =>
    executeMcpCommand("search_polyhaven_assets", { asset_type, categories }),
  {
    name: "search_polyhaven_assets",
    description:
      "Search PolyHaven for textures, HDRIs, and 3D models. " +
      "Filter by asset_type (hdris, textures, models, all) and/or categories.",
    schema: z.object({
      asset_type: z.string().optional().describe("Asset type filter: hdris, textures, models, or all"),
      categories: z.string().optional().describe("Category filter string"),
    }),
  }
)

const downloadPolyhavenAsset = tool(
  async ({ asset_id, asset_type, resolution, file_format }: { asset_id: string; asset_type: string; resolution?: string; file_format?: string }) =>
    executeMcpCommand("download_polyhaven_asset", { asset_id, asset_type, resolution, file_format }),
  {
    name: "download_polyhaven_asset",
    description: "Download a PolyHaven asset by ID and import it into the scene.",
    schema: z.object({
      asset_id: z.string().describe("PolyHaven asset ID (slug)"),
      asset_type: z.string().describe("Asset type: hdris, textures, or models"),
      resolution: z.string().optional().describe("Resolution (default: 1k)"),
      file_format: z.string().optional().describe("File format (hdr/exr for HDRIs, jpg/png for textures, gltf/fbx for models)"),
    }),
  }
)

const setTexture = tool(
  async ({ object_name, texture_id }: { object_name: string; texture_id: string }) =>
    executeMcpCommand("set_texture", { object_name, texture_id }),
  {
    name: "set_texture",
    description:
      "Apply a previously downloaded PolyHaven texture to an object. " +
      "The texture must be downloaded first via download_polyhaven_asset.",
    schema: z.object({
      object_name: z.string().describe("Target Blender object name"),
      texture_id: z.string().describe("PolyHaven texture asset ID (the same ID used for download)"),
    }),
  }
)

// ---------- Sketchfab Tools ---------

const searchSketchfabModels = tool(
  async ({ query, downloadable }: { query: string; downloadable?: boolean }) =>
    executeMcpCommand("search_sketchfab_models", { query, downloadable }),
  {
    name: "search_sketchfab_models",
    description: "Search Sketchfab for 3D models.",
    schema: z.object({
      query: z.string().describe("Search query"),
      downloadable: z.boolean().optional().describe("Only show downloadable models"),
    }),
  }
)

const downloadSketchfabModel = tool(
  async ({ uid }: { uid: string }) => executeMcpCommand("download_sketchfab_model", { uid }),
  {
    name: "download_sketchfab_model",
    description: "Download a Sketchfab model by UID.",
    schema: z.object({
      uid: z.string().describe("Sketchfab model UID"),
    }),
  }
)

// ---------- Hyper3D / Neural Tools ---------

const getHyper3dStatus = tool(
  async () => executeMcpCommand("get_hyper3d_status"),
  {
    name: "get_hyper3d_status",
    description: "Check if Hyper3D neural generation is available.",
    schema: z.object({}),
  }
)

const createRodinJob = tool(
  async ({ text_prompt, images }: { text_prompt?: string; images?: string[] }) =>
    executeMcpCommand("create_rodin_job", { text_prompt, images }),
  {
    name: "create_rodin_job",
    description:
      "Create a Hyper3D Rodin neural 3D generation job. " +
      "Provide either a text prompt or reference images (not both).",
    schema: z.object({
      text_prompt: z.string().optional().describe("Text description of the 3D model to generate"),
      images: z.array(z.string()).optional().describe("Optional reference image URLs for image-to-3D"),
    }),
  }
)

const pollRodinJobStatus = tool(
  async ({ subscription_key }: { subscription_key: string }) =>
    executeMcpCommand("poll_rodin_job_status", { subscription_key }),
  {
    name: "poll_rodin_job_status",
    description: "Poll the status of a Rodin generation job using the subscription key from create_rodin_job.",
    schema: z.object({
      subscription_key: z.string().describe("Subscription key returned by create_rodin_job"),
    }),
  }
)

const importGeneratedAsset = tool(
  async ({ task_uuid, name }: { task_uuid: string; name: string }) =>
    executeMcpCommand("import_generated_asset", { task_uuid, name }),
  {
    name: "import_generated_asset",
    description:
      "Import a completed Hyper3D Rodin generated asset into the Blender scene. " +
      "Requires the task UUID from the generation job.",
    schema: z.object({
      task_uuid: z.string().describe("Task UUID from the Rodin generation job"),
      name: z.string().describe("Name to assign to the imported object in Blender"),
    }),
  }
)

// ============================================================================
// Tool Sets (filtered by config)
// ============================================================================

const SKETCHFAB_TOOL_NAMES = new Set(["search_sketchfab_models", "download_sketchfab_model"])
const POLYHAVEN_TOOL_NAMES = new Set([
  "get_polyhaven_categories",
  "search_polyhaven_assets",
  "download_polyhaven_asset",
  "set_texture",
])
const HYPER3D_TOOL_NAMES = new Set([
  "get_hyper3d_status",
  "create_rodin_job",
  "poll_rodin_job_status",
  "import_generated_asset",
])

const ALL_TOOLS = [
  executeCode,
  getSceneInfo,
  getAllObjectInfo,
  getObjectInfo,
  getViewportScreenshotTool,
  listMaterials,
  deleteObject,
  setObjectTransform,
  renameObject,
  duplicateObject,
  joinObjects,
  addModifier,
  applyModifier,
  applyTransforms,
  shadeSmooth,
  parentSet,
  parentClear,
  setOrigin,
  moveToCollection,
  setVisibility,
  exportObject,
  listInstalledAddons,
  getPolyhavenCategories,
  searchPolyhavenAssets,
  downloadPolyhavenAsset,
  setTexture,
  searchSketchfabModels,
  downloadSketchfabModel,
  getHyper3dStatus,
  createRodinJob,
  pollRodinJobStatus,
  importGeneratedAsset,
]

// ============================================================================
// Middleware
// ============================================================================

/**
 * Viewport Screenshot Middleware
 *
 * Auto-captures a screenshot after every `execute_code` call and logs it
 * as a vision event. Replaces the manual hack in the old executor.ts.
 */
function createViewportMiddleware(onStreamEvent?: (event: AgentStreamEvent) => void) {
  return createMiddleware({
    name: "ViewportScreenshotMiddleware",
    wrapToolCall: async (request, handler) => {
      const result = await handler(request)

      // After execute_code, auto-capture viewport
      if (request.toolCall.name === "execute_code") {
        try {
          const screenshot = await getViewportScreenshot()
          const event: AgentStreamEvent = {
            type: "agent:vision",
            timestamp: new Date().toISOString(),
            assessment: `Viewport captured: ${screenshot.width}x${screenshot.height}`,
            issues: [],
          }
          onStreamEvent?.(event)
        } catch (error) {
          const event: AgentStreamEvent = {
            type: "agent:vision",
            timestamp: new Date().toISOString(),
            assessment: `WARNING: Viewport capture failed — ${error instanceof Error ? error.message : String(error)}`,
            issues: ["screenshot_failed"],
          }
          onStreamEvent?.(event)
        }
      }

      return result
    },
  })
}

/**
 * RAG Context Middleware
 *
 * Before each model call, searches for relevant scripts and injects them
 * into the conversation context. This is the CRAG pipeline integration.
 */
function createRAGMiddleware() {
  return createMiddleware({
    name: "RAGContextMiddleware",
    wrapModelCall: async (request, handler) => {
      // Extract the latest user message to use as search query
      const messages = request.messages ?? []
      const lastUserMsg = [...messages]
        .reverse()
        .find((m) => isHumanMessage(m))

      if (lastUserMsg) {
        const msg = lastUserMsg as unknown as Record<string, unknown>
        const content = typeof msg.content === "string"
          ? msg.content
          : ""

        if (content) {
          try {
            const results = await similaritySearch(content, { limit: 3 })
            if (results.length > 0) {
              const context = formatContextFromSources(results)
              // Inject RAG context as a system message hint
              const ragMessage = new SystemMessage(
                `\n<rag_context>\nRelevant Blender script references:\n${context}\n</rag_context>`
              )
              return handler({
                ...request,
                messages: [ragMessage, ...messages],
              })
            }
          } catch {
            // RAG failure is non-fatal — continue without context
          }
        }
      }

      return handler(request)
    },
  })
}

// ============================================================================
// Agent Factory
// ============================================================================

export interface BlenderAgentV2Options {
  /** Allow PolyHaven assets */
  allowPolyHaven?: boolean
  /** Allow Sketchfab assets */
  allowSketchfab?: boolean
  /** Allow Hyper3D neural generation */
  allowHyper3d?: boolean
  /** Use RAG for context enrichment */
  useRAG?: boolean
  /** Enable dynamic addon detection — detects installed addons and adapts system prompt */
  enableAddonDetection?: boolean
  /** Pre-fetched addon modules for prompt injection (skips runtime detection) */
  detectedAddonModules?: string[]
  /** Callback for streaming agent events to UI */
  onStreamEvent?: (event: AgentStreamEvent) => void
}

/** Shared checkpointer for session persistence */
const checkpointer = new MemorySaver()

/**
 * Create a new LangChain v1 Blender agent.
 *
 * Usage:
 *   const agent = createBlenderAgentV2(options)
 *   const result = await agent.invoke(
 *     { messages: [{ role: "user", content: "Create a cube" }] },
 *     { configurable: { thread_id: projectId } }
 *   )
 */
export function createBlenderAgentV2(options: BlenderAgentV2Options = {}) {
  const {
    allowPolyHaven = true,
    allowSketchfab = false,
    allowHyper3d = false,
    useRAG = true,
    enableAddonDetection = true,
    detectedAddonModules,
    onStreamEvent,
  } = options

  // Filter tools based on config
  const tools = ALL_TOOLS.filter((t) => {
    if (!allowSketchfab && SKETCHFAB_TOOL_NAMES.has(t.name)) return false
    if (!allowPolyHaven && POLYHAVEN_TOOL_NAMES.has(t.name)) return false
    if (!allowHyper3d && HYPER3D_TOOL_NAMES.has(t.name)) return false
    return true
  })

  // Build dynamic system prompt with addon detection
  let dynamicPrompt = SYSTEM_PROMPT
  if (enableAddonDetection && detectedAddonModules) {
    const { promptBlock } = getAddonPromptHints(detectedAddonModules)
    if (promptBlock) {
      dynamicPrompt = SYSTEM_PROMPT + "\n" + promptBlock
    }
  }

  // Build middleware stack
  const middleware = [
    createViewportMiddleware(onStreamEvent),
  ]

  if (useRAG) {
    middleware.push(createRAGMiddleware())
  }

  // Create the LangChain v1 agent
  const model = createGeminiModel({ temperature: 0.4 })

  const agent = createAgent({
    model,
    tools,
    systemPrompt: dynamicPrompt,
    middleware,
    checkpointer,
  })

  return agent
}

// ============================================================================
// Convenience re-exports
// ============================================================================

export type { AgentStreamEvent }
export { checkpointer }
