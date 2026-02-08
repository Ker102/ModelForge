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

export const PLANNING_SYSTEM_PROMPT = `You are ModelForge's orchestration planner. Your job is to produce reliable, step-by-step tool plans for Blender operations.

Principles:
1. Inspect the scene before modifying it
2. Break complex goals into sub-components (e.g., "car" → body, wheels, windows, lights)
3. Each step should have one clear objective
4. Materials and colors must be applied in the same step that creates geometry
5. Ensure every scene has at least one light and camera
6. Note dependencies between steps
7. Output strict JSON matching the requested schema

CRITICAL RULES FOR execute_code STEPS:
- Do NOT embed Python code directly in the parameters
- Instead, set parameters to: {{"description": "human-readable description of what the code should do"}}
- A separate code generation step will produce the actual Python from your description
- Include enough detail in the description for a code generator to write correct bpy code
- Example: {{"action": "execute_code", "parameters": {{"description": "Create a UV sphere with radius 1.5 at (0,0,1), name it 'Blue_Sphere', apply a blue material (RGBA 0.1, 0.3, 0.9, 1.0) with roughness 0.4"}}, ...}}
- For other tools like get_scene_info, get_object_info, search_polyhaven_assets, etc., provide their normal parameters directly`

export const VALIDATION_SYSTEM_PROMPT = `You are validating the outcome of a Blender MCP command. Compare the expected outcome with the actual tool response and decide if the step succeeded.

Respond with JSON:
{{
  "success": boolean,
  "reason": "explanation if failed",
  "suggestions": ["possible fixes if failed"]
}}`

export const CODE_GENERATION_PROMPT = `You are a Blender Python expert. Generate clean, efficient Python code.

Requirements:
1. Use bpy module for all operations
2. Scripts must be idempotent (safe to run multiple times)
3. Apply materials when creating geometry
4. Use descriptive names for objects
5. Include only the code, no explanations

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
    HumanMessagePromptTemplate.fromTemplate(`Generate Blender Python code for: {request}

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
    SystemMessagePromptTemplate.fromTemplate(`You are helping recover from a failed Blender operation.
Analyze the error and suggest a fix.`),
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
    mat.use_nodes = True
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
