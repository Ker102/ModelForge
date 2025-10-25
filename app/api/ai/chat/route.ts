import { randomUUID } from "crypto"
import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import {
  canConsumeAiRequest,
  getUsageSummary,
  logUsage,
} from "@/lib/usage"
import { streamGeminiResponse } from "@/lib/gemini"
import { createMcpClient } from "@/lib/mcp"
import { z } from "zod"

const MAX_HISTORY_MESSAGES = 12

type CommandStatus = "pending" | "ready" | "executed" | "failed"

interface CommandStub {
  id: string
  tool: string
  description: string
  status: CommandStatus
  confidence: number
  arguments: Record<string, unknown>
  notes?: string
}

interface ExecutedCommand extends CommandStub {
  status: "executed" | "failed"
  result?: unknown
  error?: string
}

function createStubId() {
  try {
    return randomUUID()
  } catch {
    return `stub-${Date.now()}`
  }
}

type ColorPreset = {
  rgba: [number, number, number, number]
  metallic?: number
  roughness?: number
}

const CODE_HELPERS = [
  "import bpy",
  "import math",
  "",
  "def ensure_collection(name):",
  "    collection = bpy.data.collections.get(name)",
  "    if collection is None:",
  "        collection = bpy.data.collections.new(name)",
  "        bpy.context.scene.collection.children.link(collection)",
  "    return collection",
  "",
  "def clear_collection(collection):",
  "    for obj in list(collection.objects):",
  "        bpy.data.objects.remove(obj, do_unlink=True)",
  "",
  "def link_object(obj, collection):",
  "    for existing in list(obj.users_collection):",
  "        if existing != collection:",
  "            existing.objects.unlink(obj)",
  "    if obj.name not in collection.objects:",
  "        collection.objects.link(obj)",
  "",
  "def ensure_material(name, rgba=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5):",
  "    mat = bpy.data.materials.get(name)",
  "    if mat is None:",
  "        mat = bpy.data.materials.new(name=name)",
  "        mat.use_nodes = True",
  "    nodes = mat.node_tree.nodes",
  "    bsdf = nodes.get('Principled BSDF')",
  "    if bsdf:",
  "        bsdf.inputs['Base Color'].default_value = (rgba[0], rgba[1], rgba[2], 1.0)",
  "        bsdf.inputs['Metallic'].default_value = metallic",
  "        bsdf.inputs['Roughness'].default_value = roughness",
  "    return mat",
  "",
  "def assign_material(target, material):",
  "    if not hasattr(target, 'data') or not hasattr(target.data, 'materials'):",
  "        return",
  "    if len(target.data.materials) == 0:",
  "        target.data.materials.append(material)",
  "    else:",
  "        target.data.materials[0] = material",
  "",
  "def ensure_camera():",
  "    camera = bpy.context.scene.camera",
  "    if camera is None:",
  "        bpy.ops.object.camera_add(location=(8, -8, 6))",
  "        camera = bpy.context.active_object",
  "        bpy.context.scene.camera = camera",
  "    return camera",
].join("\n")

const COLOR_PRESETS: Record<string, ColorPreset> = {
  red: { rgba: [0.85, 0.1, 0.1, 1], metallic: 0.1, roughness: 0.35 },
  blue: { rgba: [0.2, 0.35, 0.8, 1], metallic: 0.05, roughness: 0.4 },
  green: { rgba: [0.2, 0.6, 0.25, 1], metallic: 0.05, roughness: 0.45 },
  yellow: { rgba: [0.95, 0.85, 0.25, 1], metallic: 0.05, roughness: 0.3 },
  orange: { rgba: [0.95, 0.55, 0.15, 1], metallic: 0.05, roughness: 0.35 },
  purple: { rgba: [0.5, 0.25, 0.7, 1], metallic: 0.05, roughness: 0.4 },
  pink: { rgba: [0.95, 0.5, 0.7, 1], metallic: 0.03, roughness: 0.45 },
  white: { rgba: [0.95, 0.95, 0.95, 1], metallic: 0.0, roughness: 0.4 },
  black: { rgba: [0.05, 0.05, 0.05, 1], metallic: 0.2, roughness: 0.35 },
  gray: { rgba: [0.5, 0.5, 0.5, 1], metallic: 0.1, roughness: 0.45 },
  silver: { rgba: [0.75, 0.75, 0.78, 1], metallic: 0.85, roughness: 0.25 },
  gold: { rgba: [0.95, 0.72, 0.2, 1], metallic: 1.0, roughness: 0.2 },
  copper: { rgba: [0.83, 0.47, 0.24, 1], metallic: 0.85, roughness: 0.3 },
}

const COLOR_KEYWORDS: Array<[RegExp, keyof typeof COLOR_PRESETS]> = [
  [/silver/, "silver"],
  [/gold/, "gold"],
  [/copper|bronze/, "copper"],
  [/red/, "red"],
  [/blue/, "blue"],
  [/green/, "green"],
  [/yellow/, "yellow"],
  [/orange/, "orange"],
  [/purple|violet/, "purple"],
  [/pink|magenta/, "pink"],
  [/white/, "white"],
  [/black|ebony|jet/, "black"],
  [/(grey|gray)/, "gray"],
]

const TARGET_KEYWORDS = [
  "car",
  "vehicle",
  "cube",
  "sphere",
  "house",
  "roof",
  "floor",
  "dragon",
  "gnome",
  "object",
  "model",
]

const METALLIC_KEYWORDS = ["metal", "metallic", "chrome", "polish"]

function formatPython(lines: string[]): string {
  return lines.join("\n")
}

function createCommand(
  tool: string,
  description: string,
  args: Record<string, unknown>,
  confidence: number,
  notes?: string
): CommandStub {
  return {
    id: createStubId(),
    tool,
    description,
    status: "pending",
    confidence,
    arguments: args,
    notes,
  }
}

function detectColor(lowerPrompt: string): keyof typeof COLOR_PRESETS | null {
  for (const [regex, key] of COLOR_KEYWORDS) {
    if (regex.test(lowerPrompt)) {
      return key
    }
  }
  return null
}

function detectTarget(lowerPrompt: string): string {
  for (const keyword of TARGET_KEYWORDS) {
    if (lowerPrompt.includes(keyword)) {
      return keyword
    }
  }
  return "object"
}

function buildCommandStubs(prompt: string): CommandStub[] {
  const lowerPrompt = prompt.toLowerCase()
  const promptSnippet = prompt.slice(0, 200)
  const stubs: CommandStub[] = []
  const alreadyHandled = new Set<string>()

  const addStub = (stub: CommandStub, key?: string) => {
    if (key) {
      if (alreadyHandled.has(key)) return
      alreadyHandled.add(key)
    }
    stubs.push(stub)
  }

  const addStubs = (newStubs: CommandStub[], key?: string) => {
    if (key && alreadyHandled.has(key)) {
      return
    }
    if (key) {
      alreadyHandled.add(key)
    }
    stubs.push(...newStubs)
  }

  const wantsDungeonScene =
    /(dungeon|dragon|pot of gold|torch|castle)/.test(lowerPrompt) &&
    /house/.test(lowerPrompt) === false

  if (wantsDungeonScene) {
    const dungeonCode = formatPython([
      CODE_HELPERS,
      "",
      "collection = ensure_collection('ModelForge_Dungeon')",
      "clear_collection(collection)",
      "",
      "bpy.ops.mesh.primitive_plane_add(size=18, location=(0, 0, 0))",
      "floor = bpy.context.active_object",
      "floor.name = 'Dungeon_Floor'",
      "assign_material(floor, ensure_material('Dungeon_Stone', (0.18, 0.18, 0.2, 1.0), metallic=0.05, roughness=0.85))",
      "link_object(floor, collection)",
      "",
      "wall_specs = [",
      "    {'location': (0, 9, 2), 'scale': (9, 0.6, 2)},",
      "    {'location': (0, -9, 2), 'scale': (9, 0.6, 2)},",
      "    {'location': (9, 0, 2), 'scale': (0.6, 9, 2)},",
      "    {'location': (-9, 0, 2), 'scale': (0.6, 9, 2)},",
      "]",
      "for spec in wall_specs:",
      "    bpy.ops.mesh.primitive_cube_add(size=1, location=spec['location'])",
      "    wall = bpy.context.active_object",
      "    wall.scale = spec['scale']",
      "    wall.name = 'Dungeon_Wall'",
      "    assign_material(wall, ensure_material('Dungeon_Wall', (0.15, 0.15, 0.16, 1.0), roughness=0.75))",
      "    link_object(wall, collection)",
      "",
      "bpy.ops.mesh.primitive_circle_add(vertices=6, radius=3, location=(0, 0, 0.05))",
      "pit = bpy.context.active_object",
      "pit.name = 'Dungeon_Center'",
      "assign_material(pit, ensure_material('Dungeon_Center', (0.12, 0.1, 0.14, 1.0), roughness=0.8))",
      "link_object(pit, collection)",
      "",
      "bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.2, location=(2.5, 0, 1.2))",
      "dragon = bpy.context.active_object",
      "dragon.name = 'Dungeon_Dragon'",
      "assign_material(dragon, ensure_material('Dungeon_Dragon', (0.22, 0.55, 0.2, 1.0), metallic=0.15, roughness=0.35))",
      "link_object(dragon, collection)",
      "",
      "bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.5, location=(-2.3, 0, 0.25))",
      "pot = bpy.context.active_object",
      "pot.name = 'Dungeon_Pot'",
      "assign_material(pot, ensure_material('Dungeon_Pot', (0.15, 0.12, 0.08, 1.0), metallic=0.2, roughness=0.4))",
      "link_object(pot, collection)",
      "",
      "bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(-2.3, 0, 0.75))",
      "gold = bpy.context.active_object",
      "gold.name = 'Dungeon_Gold'",
      "assign_material(gold, ensure_material('Dungeon_Gold', (0.95, 0.78, 0.18, 1.0), metallic=1.0, roughness=0.18))",
      "link_object(gold, collection)",
      "",
      "for angle in (-3.5, 3.5, 30, -30):",
      "    bpy.ops.object.light_add(type='POINT', location=(angle, 6 if angle in (-3.5, 3.5) else 0, 3.5))",
      "    light = bpy.context.active_object",
      "    light.data.energy = 450",
      "    light.name = 'Dungeon_Torch'",
      "    link_object(light, collection)",
      "",
      "print('ModelForge: Generated low poly dungeon block-in with guardian dragon and treasure.')",
    ])

    addStub(
      createCommand(
        "execute_code",
        "Block in a low-poly dungeon scene with a dragon and treasure",
        { code: dungeonCode },
        0.68,
        "Generated automatically for dungeon-style requests."
      ),
      "dungeon"
    )
  }

  const wantsHouse = /house|building|home|structure/.test(lowerPrompt)
  if (wantsHouse && !alreadyHandled.has("dungeon")) {
    const houseCode = formatPython([
      CODE_HELPERS,
      "",
      "collection = ensure_collection('ModelForge_House')",
      "clear_collection(collection)",
      "",
      "bpy.ops.mesh.primitive_cube_add(size=4, location=(0, 0, 1))",
      "base = bpy.context.active_object",
      "base.name = 'House_Base'",
      "base.scale[2] = 0.6",
      "assign_material(base, ensure_material('House_Walls', (0.86, 0.86, 0.86, 1.0), roughness=0.55))",
      "link_object(base, collection)",
      "",
      "bpy.ops.mesh.primitive_cone_add(radius1=3.4, radius2=0.2, depth=2.8, location=(0, 0, 2.8))",
      "roof = bpy.context.active_object",
      "roof.name = 'House_Roof'",
      "assign_material(roof, ensure_material('House_Roof', (0.6, 0.18, 0.12, 1.0), roughness=0.4))",
      "link_object(roof, collection)",
      "",
      "bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0, 1.9, 0.5))",
      "door = bpy.context.active_object",
      "door.scale[2] = 1.5",
      "assign_material(door, ensure_material('House_Door', (0.25, 0.16, 0.1, 1.0), roughness=0.5))",
      "link_object(door, collection)",
      "",
      "print('ModelForge: simple house block-in created')",
    ])

    addStub(
      createCommand(
        "execute_code",
        "Create a simple house with base, roof, and doorway",
        { code: houseCode },
        0.62,
        "ModelForge heuristic house scaffold."
      ),
      "house"
    )
  }

  const primitiveMatch = /(cube|sphere|plane|cone|cylinder|torus)/.exec(lowerPrompt)
  if (primitiveMatch && !alreadyHandled.has("primitive")) {
    const primitive = primitiveMatch[1]
    const primitiveMap: Record<string, string> = {
      cube: "bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))",
      sphere: "bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0))",
      plane: "bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0))",
      cone: "bpy.ops.mesh.primitive_cone_add(location=(0, 0, 0))",
      cylinder: "bpy.ops.mesh.primitive_cylinder_add(location=(0, 0, 0))",
      torus: "bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0))",
    }

    const primitiveCode = formatPython([
      CODE_HELPERS,
      "",
      "collection = ensure_collection('ModelForge_Primitives')",
      "",
      primitiveMap[primitive] ?? primitiveMap.cube,
      "obj = bpy.context.active_object",
      `obj.name = 'Primitive_${primitive.charAt(0).toUpperCase() + primitive.slice(1)}'`,
      "link_object(obj, collection)",
      "assign_material(obj, ensure_material('Primitive_Default'))",
      "",
      `print('ModelForge: ${primitive} created')`,
    ])

    addStub(
      createCommand(
        "execute_code",
        `Create a ${primitive} primitive`,
        { code: primitiveCode },
        0.45,
        "Generated automatically from primitive keyword detection."
      ),
      "primitive"
    )
  }

  const wantsSphereAboveCube =
    /sphere/.test(lowerPrompt) && /above/.test(lowerPrompt) && /cube/.test(lowerPrompt)
  if (wantsSphereAboveCube) {
    const sphereAboveCubeCode = formatPython([
      CODE_HELPERS,
      "",
      "collection = ensure_collection('ModelForge_Primitives')",
      "clear_collection(collection)",
      "",
      "bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))",
      "cube = bpy.context.active_object",
      "cube.name = 'Reference_Cube'",
      "assign_material(cube, ensure_material('Reference_Cube_Mat', (0.75, 0.75, 0.8, 1.0), roughness=0.55))",
      "link_object(cube, collection)",
      "",
      "bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(0, 0, 3))",
      "sphere = bpy.context.active_object",
      "sphere.name = 'Reference_Sphere'",
      "assign_material(sphere, ensure_material('Reference_Sphere_Mat', (0.2, 0.55, 0.9, 1.0), roughness=0.25))",
      "link_object(sphere, collection)",
      "",
      "print('ModelForge: created cube with sphere positioned above it at 2m offset.')",
    ])

    addStub(
      createCommand(
        "execute_code",
        "Create a reference cube with a sphere positioned above it",
        { code: sphereAboveCubeCode },
        0.58,
        "ModelForge primitive arrangement heuristic."
      ),
      "sphereAboveCube"
    )
  }

  const wantsStudioLighting = /(studio lighting|three[-\s]?point)/.test(lowerPrompt)
  if (wantsStudioLighting) {
    const studioLightingCode = formatPython([
      CODE_HELPERS,
      "",
      "collection = ensure_collection('ModelForge_Lighting')",
      "clear_collection(collection)",
      "",
      "# Key light",
      "bpy.ops.object.light_add(type='AREA', location=(6, -4, 4))",
      "key = bpy.context.active_object",
      "key.data.energy = 1200",
      "key.data.shape = 'RECTANGLE'",
      "key.data.size = 4",
      "key.data.size_y = 3",
      "key.name = 'Studio_Key'",
      "link_object(key, collection)",
      "",
      "# Fill light",
      "bpy.ops.object.light_add(type='AREA', location=(-5, -3, 3))",
      "fill = bpy.context.active_object",
      "fill.data.energy = 600",
      "fill.data.size = 3.5",
      "fill.data.size_y = 2.5",
      "fill.name = 'Studio_Fill'",
      "link_object(fill, collection)",
      "",
      "# Rim light",
      "bpy.ops.object.light_add(type='AREA', location=(0, 5, 4))",
      "rim = bpy.context.active_object",
      "rim.data.energy = 900",
      "rim.data.size = 4",
      "rim.data.size_y = 1.5",
      "rim.rotation_euler[0] = math.radians(-120)",
      "rim.name = 'Studio_Rim'",
      "link_object(rim, collection)",
      "",
      "print('ModelForge: studio three-point lighting setup created')",
    ])

    addStub(
      createCommand(
        "execute_code",
        "Add a three-point studio lighting setup",
        { code: studioLightingCode },
        0.52,
        "Automated lighting heuristic using AREA lights."
      ),
      "studioLighting"
    )
  }

  const wantsIsometricCamera =
    /isometric/.test(lowerPrompt) || /point the camera/.test(lowerPrompt) || /aim the camera/.test(lowerPrompt)
  if (wantsIsometricCamera) {
    const cameraCode = formatPython([
      CODE_HELPERS,
      "",
      "camera = ensure_camera()",
      "camera.location = (8, -8, 8)",
      "camera.rotation_euler = (math.radians(60), 0, math.radians(45))",
      "bpy.context.scene.camera = camera",
      "",
      "for obj in bpy.context.scene.objects:",
      "    if obj.type == 'LIGHT' and obj.name.startswith('Studio_Key'):",
      "        obj.rotation_euler.z = math.radians(25)",
      "",
      "print('ModelForge: camera set to an isometric-style view looking at the origin.')",
    ])

    addStub(
      createCommand(
        "execute_code",
        "Position the active camera to an isometric view toward the origin",
        { code: cameraCode },
        0.5,
        "Camera utility heuristic."
      ),
      "isometricCamera"
    )
  }

  const detectedColor = detectColor(lowerPrompt)
  if (detectedColor) {
    const preset = COLOR_PRESETS[detectedColor]
    const wantsMetallic = METALLIC_KEYWORDS.some((word) => lowerPrompt.includes(word)) || ["silver", "gold", "copper"].includes(detectedColor)
    const metallicValue = wantsMetallic ? Math.max(preset.metallic ?? 0.8, 0.75) : preset.metallic ?? 0.15
    const roughnessValue = wantsMetallic ? Math.min(preset.roughness ?? 0.3, 0.35) : preset.roughness ?? 0.45
    const targetKeyword = detectTarget(lowerPrompt)
    const materialName = `ModelForge_${detectedColor.replace(/\s+/g, '_').toUpperCase()}`
    const colorTuple = preset.rgba

    const colorCode = formatPython([
      CODE_HELPERS,
      "",
      `target_keyword = '${targetKeyword}'`,
      "candidates = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']",
      "if not candidates:",
      "    for obj in bpy.data.objects:",
      "        if obj.type == 'MESH' and target_keyword in obj.name.lower():",
      "            candidates.append(obj)",
      "",
      "if not candidates:",
      "    candidates = [obj for obj in bpy.data.objects if obj.type == 'MESH'][:8]",
      "",
      `material = ensure_material('${materialName}', (${colorTuple[0]}, ${colorTuple[1]}, ${colorTuple[2]}, 1.0), metallic=${metallicValue}, roughness=${roughnessValue})`,
      "for mesh in candidates:",
      "    assign_material(mesh, material)",
      "",
      `print('ModelForge: applied ${detectedColor} material to', [mesh.name for mesh in candidates])`,
    ])

    addStub(
      createCommand(
        "execute_code",
        `Apply a ${detectedColor}${wantsMetallic ? ' metallic' : ''} material to the targeted meshes`,
        { code: colorCode },
        0.48,
        `Color heuristic matched the "${detectedColor}" keyword${wantsMetallic ? " with metallic emphasis" : ""}.`
      ),
      `color-${detectedColor}`
    )
  }

  const wantsSceneInfo =
    /scene info/.test(lowerPrompt) ||
    /get information about the current scene/.test(lowerPrompt) ||
    /threejs|three\.js/.test(lowerPrompt)
  if (wantsSceneInfo) {
    addStub(
      createCommand(
        "get_scene_info",
        "Fetch summary information about the current scene",
        {},
        0.55,
        "Provides object counts, names, and key transforms."
      ),
      "scene-info"
    )

    const sketchCode = formatPython([
      "import bpy",
      "import json",
      "",
      "summary = []",
      "for obj in bpy.context.scene.objects:",
      "    if obj.type == 'MESH':",
      "        summary.append({",
      "            'name': obj.name,",
      "            'location': [round(coord, 3) for coord in obj.location],",
      "            'rotation': [round(angle, 3) for angle in obj.rotation_euler],",
      "            'scale': [round(scale, 3) for scale in obj.scale],",
      "        })",
      "",
      "print(json.dumps({'objects': summary}))",
    ])

    addStub(
      createCommand(
        "execute_code",
        "Serialize mesh transforms as JSON for a Three.js sketch",
        { code: sketchCode },
        0.42,
        "Use the JSON output to scaffold a Three.js representation."
      ),
      "scene-sketch"
    )
  }

  const wantsHyper3d =
    /hyper3d/.test(lowerPrompt) ||
    /rodin/.test(lowerPrompt) ||
    /garden gnome/.test(lowerPrompt)
  if (wantsHyper3d) {
    addStub(
      createCommand(
        "get_hyper3d_status",
        "Check whether Hyper3D integration is ready",
        {},
        0.4,
        "Ensures the add-on is configured before launching a job."
      ),
      "hyper3d-status"
    )

    const textPrompt = prompt.trim()
    addStub(
      createCommand(
        "create_rodin_job",
        "Kick off a Hyper3D Rodin generation job",
        { text_prompt: textPrompt },
        0.42,
        "Uses the full user prompt so Hyper3D can interpret intent."
      ),
      "hyper3d-job"
    )
  }

  const mentionsPolyHaven = /poly ?haven/.test(lowerPrompt)
  const mentionsBeach = /beach|coast|shore/.test(lowerPrompt)

  if (mentionsBeach) {
    const beachCode = formatPython([
      CODE_HELPERS,
      "",
      "collection = ensure_collection('ModelForge_Beach')",
      "clear_collection(collection)",
      "",
      "bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))",
      "sand = bpy.context.active_object",
      "sand.name = 'Beach_Sand'",
      "assign_material(sand, ensure_material('Beach_Sand', (0.92, 0.85, 0.62, 1.0), roughness=0.6))",
      "link_object(sand, collection)",
      "",
      "bpy.ops.mesh.primitive_plane_add(size=44, location=(0, -14, -0.35))",
      "water = bpy.context.active_object",
      "water.name = 'Beach_Water'",
      "assign_material(water, ensure_material('Beach_Water', (0.08, 0.25, 0.45, 1.0), metallic=0.25, roughness=0.12))",
      "link_object(water, collection)",
      "wave = water.modifiers.new(name='ModelForge_Waves', type='WAVE')",
      "wave.height = 0.35",
      "wave.width = 2.6",
      "",
      "bpy.ops.object.light_add(type='SUN', location=(12, -8, 14))",
      "sun = bpy.context.active_object",
      "sun.data.energy = 5.5",
      "sun.rotation_euler = (math.radians(35), math.radians(-25), math.radians(-15))",
      "sun.name = 'Beach_Sun'",
      "link_object(sun, collection)",
      "",
      "world = bpy.context.scene.world or bpy.data.worlds.new('ModelForge_World')",
      "world.use_nodes = True",
      "bg = world.node_tree.nodes.get('Background')",
      "if bg:",
      "    bg.inputs['Color'].default_value = (0.48, 0.72, 0.85, 1.0)",
      "    bg.inputs['Strength'].default_value = 1.3",
      "",
      "print('ModelForge: Beach scene scaffold created (sand plane, ocean plane, sun light).')",
    ])

    addStub(
      createCommand(
        "execute_code",
        "Lay out a beach base with sand, water, and sun lighting",
        { code: beachCode },
        0.6,
        "Provides a starting point before applying PolyHaven assets."
      ),
      "beach-base"
    )

    addStub(
      createCommand(
        "get_polyhaven_status",
        "Confirm PolyHaven integration is active",
        {},
        0.35,
        "PolyHaven assets require the integration to be enabled inside Blender."
      ),
      "polyhaven-status"
    )

    addStubs(
      [
        createCommand(
          "search_polyhaven_assets",
          "Search PolyHaven HDRIs for beach lighting",
          { asset_type: "hdris", categories: "outdoor,coast,beach" },
          0.32,
          "Review HDRI results and download your preferred sky texture."
        ),
        createCommand(
          "search_polyhaven_assets",
          "Search PolyHaven textures for sand materials",
          { asset_type: "textures", categories: "sand,ground" },
          0.32,
          "Use downloaded texture IDs with the set_texture command."
        ),
        createCommand(
          "search_polyhaven_assets",
          "Search PolyHaven models for rocks or vegetation",
          { asset_type: "models", categories: "rocks,plants" },
          0.32,
          "Download models that complement the beach environment."
        ),
      ],
      "polyhaven-search"
    )
  } else if (mentionsPolyHaven) {
    addStub(
      createCommand(
        "get_polyhaven_status",
        "Check PolyHaven integration status",
        {},
        0.35,
        "Verifies the user has enabled PolyHaven in the Blender sidebar."
      ),
      "polyhaven-status"
    )

    const assetType =
      /hdri/.test(lowerPrompt) ? "hdris" : /texture/.test(lowerPrompt) ? "textures" : "models"
    const categories: string[] = []
    if (/rock|stone/.test(lowerPrompt)) categories.push("rocks")
    if (/vegetation|plant|tree/.test(lowerPrompt)) categories.push("plants")
    if (/urban|city/.test(lowerPrompt)) categories.push("urban")
    if (/interior|indoor/.test(lowerPrompt)) categories.push("interior")
    if (categories.length === 0) categories.push("all")

    addStub(
      createCommand(
        "search_polyhaven_assets",
        "Search PolyHaven for matching assets",
        { asset_type: assetType, categories: categories.join(",") },
        0.3,
        "Review the search results and choose assets to download."
      ),
      "polyhaven-generic-search"
    )
  }

  if (stubs.length === 0) {
    const placeholderMessage = promptSnippet.replace(/[\n\r]+/g, " ").replace(/'/g, "")
    const placeholderCode = formatPython([
      `print('ModelForge placeholder: ${placeholderMessage}')`,
    ])

    stubs.push(
      createCommand(
        "execute_code",
        "Log prompt for manual planning",
        { code: placeholderCode },
        0.08,
        "No direct automation rule matched. Logged prompt for review."
      )
    )
  }

  return stubs
}

const chatRequestSchema = z.object({
  projectId: z.string().uuid(),
  conversationId: z.string().uuid().optional(),
  startNew: z.boolean().optional(),
  message: z.string().min(1).max(2000),
})

async function ensureConversation({
  projectId,
  userId,
  conversationId,
  startNew,
}: {
  projectId: string
  userId: string
  conversationId?: string
  startNew?: boolean
}) {
  if (conversationId) {
    const conversation = await prisma.conversation.findFirst({
      where: {
        id: conversationId,
        project: {
          id: projectId,
          userId,
          isDeleted: false,
        },
      },
      select: { id: true },
    })

    if (!conversation) {
      throw new Error("Conversation not found")
    }

    return conversationId
  }

  if (!startNew) {
    const existing = await prisma.conversation.findFirst({
      where: {
        project: {
          id: projectId,
          userId,
          isDeleted: false,
        },
      },
      orderBy: {
        lastMessageAt: "desc",
      },
      select: { id: true },
    })

    if (existing) {
      return existing.id
    }
  }

  const conversation = await prisma.conversation.create({
    data: {
      projectId,
    },
    select: { id: true },
  })

  return conversation.id
}

async function executeCommandPlan(commands: CommandStub[]): Promise<ExecutedCommand[]> {
  if (commands.length === 0) {
    return []
  }

  const client = createMcpClient()
  const executed: ExecutedCommand[] = []

  try {
    for (const command of commands) {
      try {
        const response = await client.execute({
          type: command.tool,
          params: command.arguments,
        })

        const normalizedStatus = response.status?.toLowerCase()
        const isSuccess = normalizedStatus === "ok" || normalizedStatus === "success"

        if (isSuccess) {
          executed.push({
            ...command,
            status: "executed",
            result: response.result ?? response.message ?? response.raw,
            error: undefined,
          })
        } else {
          executed.push({
            ...command,
            status: "failed",
            result: response.result ?? response.raw,
            error: response.message ?? "Command returned an error",
          })
        }
      } catch (error) {
        executed.push({
          ...command,
          status: "failed",
          result: undefined,
          error: error instanceof Error ? error.message : "Failed to execute MCP command",
        })
      }
    }
  } finally {
    await client.close().catch(() => {
      // ignore close errors
    })
  }

  return executed
}

export async function POST(req: Request) {
  try {
    const session = await auth()

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await req.json()
    const { projectId, conversationId, startNew, message } =
      chatRequestSchema.parse(body)

    const project = await prisma.project.findFirst({
      where: {
        id: projectId,
        userId: session.user.id,
        isDeleted: false,
      },
      select: { id: true },
    })

    if (!project) {
      return NextResponse.json(
        { error: "Project not found" },
        { status: 404 }
      )
    }

    const quotaCheck = await canConsumeAiRequest(
      session.user.id,
      session.user.subscriptionTier
    )

    if (!quotaCheck.allowed) {
      const limitLabel =
        quotaCheck.limitType === "daily" ? "daily" : "monthly"
      return NextResponse.json(
        {
          error: `AI request limit reached for your ${limitLabel} allotment. Please upgrade your plan or try again later.`,
          usage: quotaCheck.usage,
        },
        { status: 429 }
      )
    }

    let resolvedConversationId: string
    try {
      resolvedConversationId = await ensureConversation({
        projectId,
        userId: session.user.id,
        conversationId,
        startNew,
      })
    } catch {
      return NextResponse.json(
        { error: "Conversation not found" },
        { status: 404 }
      )
    }

    const historyMessages = await prisma.message.findMany({
      where: { conversationId: resolvedConversationId },
      orderBy: { createdAt: "desc" },
      take: Math.max(0, MAX_HISTORY_MESSAGES - 1),
      select: {
        role: true,
        content: true,
      },
    })

    const trimmedHistory = historyMessages
      .reverse()
      .map((msg) => ({
        role: msg.role === "assistant" ? "assistant" : "user",
        content: msg.content,
      }))

    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      async start(controller) {
        const send = (data: unknown) => {
          controller.enqueue(
            encoder.encode(`${JSON.stringify(data)}\n`)
          )
        }

        send({ type: "init", conversationId: resolvedConversationId })

        let assistantText = ""
        let tokenUsage: { promptTokens?: number | null; responseTokens?: number | null; totalTokens?: number | null } | undefined

        try {
          for await (const chunk of streamGeminiResponse({
            history: trimmedHistory,
            messages: [
              {
                role: "user",
                content: message,
              },
            ],
            maxOutputTokens: 512,
          })) {
            if (chunk.textDelta) {
              assistantText += chunk.textDelta
              send({ type: "delta", delta: chunk.textDelta })
            }
            if (chunk.usage) {
              tokenUsage = chunk.usage
            }
          }

          const commandSuggestions = buildCommandStubs(message)
          const executedCommands = await executeCommandPlan(commandSuggestions)

          const result = await prisma.$transaction(async (tx) => {
            const userMessageRecord = await tx.message.create({
              data: {
                conversationId: resolvedConversationId,
                role: "user",
                content: message,
              },
              select: {
                id: true,
                role: true,
                content: true,
                createdAt: true,
              },
            })

            const assistantMessageRecord = await tx.message.create({
              data: {
                conversationId: resolvedConversationId,
                role: "assistant",
                content: assistantText,
                mcpCommands: executedCommands,
                mcpResults: {
                  tokens: tokenUsage,
                  commands: executedCommands.map((command) => ({
                    id: command.id,
                    tool: command.tool,
                    status: command.status,
                    result: command.result,
                    error: command.error,
                  })),
                },
              },
              select: {
                id: true,
                role: true,
                content: true,
                mcpCommands: true,
                createdAt: true,
              },
            })

            await tx.conversation.update({
              where: { id: resolvedConversationId },
              data: { lastMessageAt: assistantMessageRecord.createdAt },
            })

            return { userMessageRecord, assistantMessageRecord }
          })

          await logUsage({
            userId: session.user.id,
            projectId,
            requestType: "ai_request",
            tokensUsed: tokenUsage?.totalTokens ?? undefined,
          })

          const usage = await getUsageSummary(
            session.user.id,
            session.user.subscriptionTier
          )

          send({
            type: "complete",
            conversationId: resolvedConversationId,
            messages: [result.userMessageRecord, result.assistantMessageRecord],
            usage,
            tokenUsage,
            commandSuggestions: executedCommands,
          })
        } catch (error) {
          console.error("AI chat stream error:", error)
          send({
            type: "error",
            error:
              error instanceof Error
                ? error.message
                : "Failed to process AI request",
          })
        } finally {
          controller.close()
        }
      },
    })

    return new Response(stream, {
      headers: {
        "Content-Type": "application/x-ndjson",
        "Cache-Control": "no-cache",
      },
    })
  } catch (error) {
    console.error("AI chat error:", error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Invalid input data", details: error.flatten() },
        { status: 400 }
      )
    }

    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to process AI request" },
      { status: 500 }
    )
  }
}
