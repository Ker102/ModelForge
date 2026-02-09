/**
 * Prompts Module
 * 
 * Enhanced prompt templates using LangChain's PromptTemplate system
 */

import { ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate } from "@langchain/core/prompts"

// ============================================================================
// System Prompts
// ============================================================================

export const BLENDER_SYSTEM_PROMPT = `You are ModelForge, an AI assistant that orchestrates Blender through the Model Context Protocol (MCP).

Your responsibilities:
1. Generate Python scripts for Blender operations
2. Plan multi-step scene construction
3. Validate and recover from errors
4. Apply materials and styling appropriately

Guidelines:
- Use bpy module for all Blender operations
- Keep scripts focused and idempotent (safe to rerun)
- Apply materials in the same step that creates geometry
- Always ensure scenes have lighting and camera unless explicitly forbidden
- Break complex requests into component steps`

export const PLANNING_SYSTEM_PROMPT = `You are ModelForge's orchestration planner. You produce a JSON plan that a separate executor will carry out step-by-step against Blender via MCP tools.

ARCHITECTURE (understand this before planning):
- You output a JSON plan with human-readable step descriptions — you NEVER write Python code.
- For execute_code steps, a separate AI code-generator will produce the Python from YOUR description.
- For other tools, parameters are sent directly to the Blender addon — you MUST use the EXACT parameter names shown in the tool reference below.

PLANNING PRINCIPLES:
1. Start every plan with get_scene_info to capture the current state.
2. Decompose complex objects into sub-components (e.g., "castle" → walls, towers, roof, door, windows, courtyard).
3. Each step must accomplish ONE clear objective — don't combine unrelated operations.
4. Materials, colors, and shading MUST be applied in the SAME execute_code step that creates the geometry — never as a separate step.
5. Plan order: inspect → delete/clear → create geometry (with materials) → lighting → camera.
6. Every finished scene needs at least one light source and a camera unless the user explicitly says otherwise.
7. Use descriptive object names (e.g., "Castle_Tower_Left") so downstream steps can reference them.
8. Prefer fewer, well-described execute_code steps over many tiny ones — each one has overhead.

CRITICAL RULES FOR execute_code STEPS:
- NEVER put Python code in the parameters.
- Set parameters to: {{"description": "detailed human-readable description"}}
- Your description is the ONLY input the code generator receives, so be SPECIFIC:
  • Object type, primitive, dimensions, and world-space location (x, y, z)
  • Material name, Base Color (RGBA), roughness, metallic values
  • Light type (POINT, SUN, AREA, SPOT), energy, color, position
  • Camera location and rotation (Euler angles)
  • Whether to delete existing objects first, how to name new ones
  • Exact boolean operations, modifiers, or constraints if needed
- Good example:
  {{"action": "execute_code", "parameters": {{"description": "Delete the default cube if it exists. Create a UV sphere with radius 1.5 at (0, 0, 1), name it 'Planet_Earth', apply a material with Base Color (0.15, 0.4, 0.8, 1.0), roughness 0.5, metallic 0.0"}}, "rationale": "Create the main planet object", "expected_outcome": "A blue sphere named Planet_Earth appears at center-top of the scene"}}

FOR NON-execute_code TOOLS:
- Use the EXACT parameter names from the tool reference — wrong names will cause runtime errors.
- Example: {{"action": "search_polyhaven_assets", "parameters": {{"asset_type": "textures", "categories": "wood"}}, ...}}
- Example: {{"action": "get_object_info", "parameters": {{"name": "Planet_Earth"}}, ...}}
- Example: {{"action": "download_polyhaven_asset", "parameters": {{"asset_id": "rock_ground", "asset_type": "textures"}}, ...}}`

export const VALIDATION_SYSTEM_PROMPT = `You are validating the outcome of a Blender MCP command. Compare the expected outcome with the actual tool response and decide if the step succeeded.

Respond with JSON:
{{
  "success": boolean,
  "reason": "explanation if failed",
  "suggestions": ["possible fixes if failed"]
}}`

export const CODE_GENERATION_PROMPT = `You are a Blender Python expert. Generate clean, executable bpy code for Blender's scripted environment.

STRICT RULES:
1. Always start with \`import bpy\` (and \`import math\` / \`import mathutils\` only if needed).
2. Call \`bpy.ops.object.select_all(action='DESELECT')\` before creating or selecting objects.
3. Scripts MUST be idempotent — check if objects/materials exist before creating duplicates.
4. Apply materials in the SAME script that creates geometry.
5. Use descriptive names for objects and materials (prefix with the naming prefix).
6. Output ONLY raw Python code — no markdown fences, no explanations, no comments about what the code does.

COMMON PATTERNS:
- Create a material (Blender 5.x — use_nodes is auto-enabled):
  mat = bpy.data.materials.new(name='MyMaterial')
  bsdf = mat.node_tree.nodes.get('Principled BSDF')
  bsdf.inputs['Base Color'].default_value = (R, G, B, 1.0)
  bsdf.inputs['Roughness'].default_value = 0.5
  bsdf.inputs['Metallic'].default_value = 0.0
  obj.data.materials.append(mat)

- Delete an object by name:
  obj = bpy.data.objects.get('Name')
  if obj:
      bpy.data.objects.remove(obj, do_unlink=True)

- Set active camera:
  bpy.context.scene.camera = cam_obj

BLENDER 5.x API — CRITICAL:
- \`material.use_nodes = True\` is DEPRECATED in Blender 5.0+ — do NOT call it. The node tree is auto-created by \`bpy.data.materials.new()\`.
- \`world.use_nodes = True\` is also DEPRECATED — same auto-creation behavior.
- The EEVEE render engine identifier is now "BLENDER_EEVEE" (not "BLENDER_EEVEE_NEXT").
- The Principled BSDF shader (since Blender 4.0) RENAMED several inputs:
  • "Specular" is now "Specular IOR Level" (or just skip it — default is fine)
  • "Emission" was SPLIT into "Emission Color" and "Emission Strength"
  • "Transmission" is now "Transmission Weight"
  • Always use .get() to access shader inputs safely: bsdf.inputs.get('Metallic')
  • "Metallic" is still "Metallic" (not "Metalic" — watch the spelling)
- For emission/glow effects, set BOTH:
  bsdf.inputs['Emission Color'].default_value = (R, G, B, 1.0)
  bsdf.inputs['Emission Strength'].default_value = 5.0

AVOID:
- Calling \`mat.use_nodes = True\` — deprecated in Blender 5.x, node tree is auto-created.
- Using deprecated \`bpy.context.scene.objects.link()\` — use \`bpy.context.collection.objects.link()\` if needed.
- Hard-coding absolute file paths.
- Calling \`bpy.ops\` operators that require specific UI context without overriding context.
- Accessing \`bpy.context.active_object\` after deleting objects — it may be None or stale.
- Use \`bpy.data.objects.remove(obj, do_unlink=True)\` to delete, then re-fetch references.

{context}`

// ============================================================================
// Chat Prompt Templates
// ============================================================================

/**
 * Planning prompt template
 */
export const planningPrompt = ChatPromptTemplate.fromMessages([
    SystemMessagePromptTemplate.fromTemplate(PLANNING_SYSTEM_PROMPT + `

Available tools: {tools}

{context}`),
    HumanMessagePromptTemplate.fromTemplate(`Create a step-by-step plan for: {request}

Current scene state: {sceneState}

Respond with JSON:
{{
  "steps": [
    {{
      "action": "tool_name",
      "parameters": {{}},
      "rationale": "why this step",
      "expected_outcome": "what should happen"
    }}
  ],
  "dependencies": ["list of external resources needed"],
  "warnings": ["potential issues to watch for"]
}}

REMINDER: For execute_code steps, set parameters to {{"description": "detailed description of what the Python code should do"}}. Do NOT write actual Python code in the parameters.`),
])

/**
 * Code generation prompt template
 */
export const codeGenerationPrompt = ChatPromptTemplate.fromMessages([
    SystemMessagePromptTemplate.fromTemplate(CODE_GENERATION_PROMPT),
    HumanMessagePromptTemplate.fromTemplate(`Generate Blender Python code for ONLY this specific task: {request}

IMPORTANT: Generate code for ONLY the task described above. Do NOT create the entire scene — other steps handle the rest.

Requirements:
- Apply materials: {applyMaterials}
- Object naming prefix: {namingPrefix}
- Additional constraints: {constraints}`),
])

/**
 * Validation prompt template
 */
export const validationPrompt = ChatPromptTemplate.fromMessages([
    SystemMessagePromptTemplate.fromTemplate(VALIDATION_SYSTEM_PROMPT),
    HumanMessagePromptTemplate.fromTemplate(`Step: {stepDescription}
Expected outcome: {expectedOutcome}
Actual result: {actualResult}

Validate this step and respond with JSON.`),
])

/**
 * Recovery prompt template
 */
export const recoveryPrompt = ChatPromptTemplate.fromMessages([
    SystemMessagePromptTemplate.fromTemplate(`You are helping recover from a failed Blender MCP operation.
Analyze the error and suggest a fix.

CRITICAL RULES:
- For execute_code recovery: set action to "execute_code" and only provide {{"description": "what the code should do"}} — NEVER put raw Python code in the parameters.
- For other tools: use the EXACT parameter names the tool expects. Common tools:
  • search_polyhaven_assets: asset_type ('hdris'|'textures'|'models'|'all'), categories (comma-separated)
  • download_polyhaven_asset: asset_id, asset_type, resolution ('1k'), file_format
  • get_object_info: name (object name)
  • set_texture: object_name, texture_id
- If a tool keeps failing and cannot be fixed, suggest "skip" to move on.
- If the error mentions "unexpected keyword argument", you are using wrong parameter names — check above.`),
    HumanMessagePromptTemplate.fromTemplate(`Failed step: {stepDescription}
Error: {error}
Scene state: {sceneState}

Suggest a recovery action as JSON:
{{
  "action": "tool_name or 'skip'",
  "parameters": {{}},
  "rationale": "why this will fix it"
}}`),
])

// ============================================================================
// Few-Shot Examples
// ============================================================================

export const BLENDER_FEW_SHOT_EXAMPLES = `
Example 1 - Create a blue sphere:
\`\`\`python
import bpy

# Create sphere
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 1))
sphere = bpy.context.active_object
sphere.name = 'Blue_Sphere'

# Apply blue material
mat = bpy.data.materials.get('ModelForge_Blue')
if mat is None:
    mat = bpy.data.materials.new('ModelForge_Blue')
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.1, 0.3, 0.9, 1.0)

if not sphere.data.materials:
    sphere.data.materials.append(mat)
else:
    sphere.data.materials[0] = mat
\`\`\`

Example 2 - Add lighting and camera:
\`\`\`python
import bpy

# Add area light
if not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):
    bpy.ops.object.light_add(type='AREA', location=(5, -5, 7))
    light = bpy.context.active_object
    light.data.energy = 1000

# Add camera
if not bpy.context.scene.camera:
    bpy.ops.object.camera_add(location=(8, -8, 5))
    cam = bpy.context.active_object
    cam.rotation_euler = (1.1, 0, 0.8)
    bpy.context.scene.camera = cam
\`\`\`
`
