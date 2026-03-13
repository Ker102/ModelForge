/**
 * Addon Registry — Known Blender Addon Profiles
 *
 * Maps addon module names to their capabilities and prompt hints.
 * When the agent detects a known addon is installed, it can inject
 * the prompt hint into its system prompt for smarter interactions.
 */

export interface AddonProfile {
  /** Human-readable addon name */
  name: string
  /** Short description of what it does */
  description: string
  /** Category (matches Blender's addon categories) */
  category: string
  /** Key operators the agent can call via execute_code */
  operators: string[]
  /** Prompt hint injected into the system prompt when detected */
  promptHint: string
}

/**
 * Registry of known Blender addons with agent-compatible profiles.
 * Keys are the addon module names as returned by `bpy.context.preferences.addons.keys()`.
 */
export const ADDON_REGISTRY: Record<string, AddonProfile> = {
  // ---- Built-in Addons ----

  "node_wrangler": {
    name: "Node Wrangler",
    description: "Shader node workflow shortcuts and automation",
    category: "Node",
    operators: [
      "node.nw_add_principled_setup",
      "node.nw_link_viewer",
      "node.nw_reset_bg_color",
    ],
    promptHint:
      "Node Wrangler is enabled. You can use Ctrl+Shift+Click to add viewer nodes, " +
      "and use bpy.ops.node.nw_add_principled_setup() to auto-connect PBR texture sets.",
  },

  "rigify": {
    name: "Rigify",
    description: "Professional auto-rigging toolkit with meta-rig generation",
    category: "Rigging",
    operators: [
      "pose.rigify_generate",
      "object.rigify_add_bone_groups",
    ],
    promptHint:
      "Rigify is available. You can add a meta-rig (bpy.ops.object.armature_human_metarig_add()), " +
      "customize it, then generate the full rig with bpy.ops.pose.rigify_generate().",
  },

  "mesh_looptools": {
    name: "LoopTools",
    description: "Advanced mesh editing tools (Circle, Relax, Bridge, Flatten, etc.)",
    category: "Mesh",
    operators: [
      "mesh.looptools_circle",
      "mesh.looptools_relax",
      "mesh.looptools_bridge",
      "mesh.looptools_flatten",
      "mesh.looptools_space",
    ],
    promptHint:
      "LoopTools is enabled. You can use bpy.ops.mesh.looptools_relax() to smooth vertex distribution, " +
      "bpy.ops.mesh.looptools_circle() to circularize edge loops, and bridge/flatten for mesh editing.",
  },

  "bool_tool": {
    name: "Bool Tool",
    description: "Quick boolean operations between objects",
    category: "Object",
    operators: [
      "object.booltool_auto_union",
      "object.booltool_auto_difference",
      "object.booltool_auto_intersect",
    ],
    promptHint:
      "Bool Tool is enabled for quick boolean operations. Use bpy.ops.object.booltool_auto_difference() " +
      "for subtractive booleans, auto_union() for additive, auto_intersect() for intersections.",
  },

  "io_import_images_as_planes": {
    name: "Images as Planes",
    description: "Import images as textured planes",
    category: "Import-Export",
    operators: [
      "import_image.to_plane",
    ],
    promptHint:
      "Images as Planes is enabled. Use bpy.ops.import_image.to_plane(filepath=...) to import " +
      "reference images or textures as textured plane objects.",
  },

  "add_mesh_extra_objects": {
    name: "Extra Mesh Objects",
    description: "Additional mesh primitives (gears, gems, rocks, etc.)",
    category: "Add Mesh",
    operators: [
      "mesh.primitive_gear",
      "mesh.primitive_diamond_add",
      "mesh.primitive_star_add",
    ],
    promptHint:
      "Extra Mesh Objects is enabled. You can add procedural gears, gems, stars, and other shapes " +
      "using operators like bpy.ops.mesh.primitive_gear().",
  },

  "add_curve_extra_objects": {
    name: "Extra Curve Objects",
    description: "Additional curve primitives (spirals, knots, profiles)",
    category: "Add Curve",
    operators: [
      "curve.spirals",
      "curve.torus_knot_plus",
    ],
    promptHint:
      "Extra Curve Objects is enabled. You can create spirals with bpy.ops.curve.spirals() " +
      "and torus knots with bpy.ops.curve.torus_knot_plus().",
  },

  "mesh_f2": {
    name: "F2",
    description: "Extended face-filling capabilities",
    category: "Mesh",
    operators: [],
    promptHint:
      "F2 addon is enabled. The F key in edit mode has extended face-filling capabilities — " +
      "it can fill faces from a single vertex or edge intelligently.",
  },

  "object_print3d_utils": {
    name: "3D-Print Toolbox",
    description: "Mesh analysis for 3D printing (non-manifold, overhangs, etc.)",
    category: "Mesh",
    operators: [
      "mesh.print3d_check_all",
      "mesh.print3d_clean_non_manifold",
    ],
    promptHint:
      "3D-Print Toolbox is available. Use bpy.ops.mesh.print3d_check_all() to run all print " +
      "quality checks, and print3d_clean_non_manifold() to fix topology issues.",
  },

  // ---- Popular Community Addons ----

  "animation_nodes": {
    name: "Animation Nodes",
    description: "Visual programming for procedural animation",
    category: "Animation",
    operators: [],
    promptHint:
      "Animation Nodes is installed for procedural animation. " +
      "Node trees can be manipulated via bpy.data.node_groups of type 'an_AnimationNodeTree'.",
  },

  "blenderkit": {
    name: "BlenderKit",
    description: "Online library of materials, models, and assets",
    category: "Import-Export",
    operators: [
      "scene.blenderkit_download",
    ],
    promptHint:
      "BlenderKit is installed for asset downloading. The user can browse and download " +
      "models, materials, and HDRIs directly from the BlenderKit library.",
  },
}

/**
 * Match installed addon modules against the registry.
 * Returns prompt hints for all recognized addons.
 */
export function getAddonPromptHints(
  installedModules: string[]
): { matched: AddonProfile[]; promptBlock: string } {
  const matched: AddonProfile[] = []

  for (const modName of installedModules) {
    const profile = ADDON_REGISTRY[modName]
    if (profile) {
      matched.push(profile)
    }
  }

  if (matched.length === 0) {
    return { matched, promptBlock: "" }
  }

  const lines = [
    "\\n## Detected Blender Addons",
    "The following third-party addons are installed and available for use via execute_code:\\n",
  ]

  for (const addon of matched) {
    lines.push(`### ${addon.name} (${addon.category})`)
    lines.push(addon.promptHint)
    lines.push("")
  }

  return { matched, promptBlock: lines.join("\\n") }
}
