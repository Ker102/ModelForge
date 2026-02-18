/**
 * Workflow Advisor — Guided Human-in-the-Loop 3D Creation
 *
 * Generates per-step tool recommendations for complex 3D creation tasks.
 * Each step tells the user:
 *  - Which tool is best (neural model, Blender agent, or manual)
 *  - WHY that tool is the best choice
 *  - Alternative approaches they could use instead
 *
 * Only invoked when the strategy router classifies a request as "neural" or "hybrid".
 * Procedural requests bypass this entirely and use the existing auto-pilot planner.
 */

import type { Strategy } from "./strategy-types"
import type {
    WorkflowProposal,
    WorkflowStep,
    WorkflowTool,
    WorkflowCategory,
} from "./workflow-types"

// ---------------------------------------------------------------------------
// Tool recommendation knowledge base
// ---------------------------------------------------------------------------

interface ToolRecommendation {
    tool: WorkflowTool
    reasoning: string
    alternatives: WorkflowTool[]
    estimatedDuration: string
    neuralProvider?: string
    blenderAction?: string
}

/**
 * Static knowledge base mapping categories to their best tool.
 * Used as a fallback and to augment LLM proposals.
 */
const CATEGORY_DEFAULTS: Record<WorkflowCategory, ToolRecommendation> = {
    geometry: {
        tool: "neural",
        reasoning:
            "Neural models excel at generating complex organic shapes from text/image descriptions. Much faster than manual modeling for the initial base mesh.",
        alternatives: ["blender_agent", "manual"],
        estimatedDuration: "~1-3 min",
        neuralProvider: "hunyuan-shape",
    },
    topology: {
        tool: "blender_agent",
        reasoning:
            "Blender's built-in retopology tools (Voxel Remesh, Quadriflow) produce clean quad meshes efficiently. The agent uses proven RAG scripts.",
        alternatives: ["manual"],
        estimatedDuration: "~15-30s",
        blenderAction: "execute_code",
    },
    uv: {
        tool: "blender_agent",
        reasoning:
            "Auto UV unwrapping via Smart Project or Lightmap Pack produces good results for most models. Manual UV only needed for hero assets.",
        alternatives: ["manual"],
        estimatedDuration: "~10-20s",
        blenderAction: "execute_code",
    },
    texturing: {
        tool: "neural",
        reasoning:
            "Neural texture models (Hunyuan Paint, YVO3D) generate cohesive PBR textures across the entire model. Best for organic surfaces.",
        alternatives: ["blender_agent", "manual"],
        estimatedDuration: "~1-2 min",
        neuralProvider: "hunyuan-paint",
    },
    rigging: {
        tool: "blender_agent",
        reasoning:
            "Rigify auto-rigging in Blender is production-proven for bipeds and quadrupeds. The agent configures metarigs and applies automatic weights.",
        alternatives: ["manual"],
        estimatedDuration: "~20-40s",
        blenderAction: "execute_code",
    },
    animation: {
        tool: "blender_agent",
        reasoning:
            "Procedural animation (orbit, walk cycles, keyframe insertion) is fast and precise via Python. Manual keyframing for custom performances.",
        alternatives: ["manual"],
        estimatedDuration: "~15-30s",
        blenderAction: "execute_code",
    },
    lighting: {
        tool: "blender_agent",
        reasoning:
            "Lighting recipes (3-point, studio, HDRI) are handled via proven Python scripts. Always procedural.",
        alternatives: ["manual"],
        estimatedDuration: "~10s",
        blenderAction: "execute_code",
    },
    export: {
        tool: "blender_agent",
        reasoning:
            "Export with LOD generation and format presets (glTF, FBX, USD) is fully automated. The agent validates the output before exporting.",
        alternatives: ["manual"],
        estimatedDuration: "~10-20s",
        blenderAction: "execute_code",
    },
    composition: {
        tool: "blender_agent",
        reasoning:
            "Scene composition (layouts, pedestals, backdrops) is best handled by the Blender agent using procedural placement scripts.",
        alternatives: ["manual"],
        estimatedDuration: "~10-20s",
        blenderAction: "execute_code",
    },
    other: {
        tool: "manual",
        reasoning:
            "This step requires manual artistic judgment. Use Blender's tools directly for the best results.",
        alternatives: ["blender_agent"],
        estimatedDuration: "varies",
    },
}

// ---------------------------------------------------------------------------
// LLM-powered workflow generation
// ---------------------------------------------------------------------------

/**
 * Raw LLM response shape for workflow analysis.
 */
interface LLMWorkflowResponse {
    title: string
    steps: Array<{
        title: string
        description: string
        category: WorkflowCategory
        recommendedTool: WorkflowTool
        toolReasoning: string
        alternativeTools: WorkflowTool[]
        estimatedDuration: string
        requiresPreviousStep: boolean
        tips?: string
        neuralProvider?: string
    }>
    overallTips: string[]
}

const WORKFLOW_SYSTEM_PROMPT = `You are a 3D workflow advisor for ModelForge. Given a user's creation request, generate a step-by-step workflow where each step recommends the BEST tool.

Available tools:
- "neural": AI model generation (best for organic geometry, complex textures). Providers: hunyuan-shape (geometry), hunyuan-paint (PBR textures), trellis (geometry+texture)
- "blender_agent": Automated Blender Python scripts (best for retopology, UV, rigging, animation, lighting, scene edits, export)
- "manual": User does it themselves in Blender (best for artistic fine-tuning, custom sculpting, precise adjustments)

Category values: geometry, topology, uv, texturing, rigging, animation, lighting, export, composition, other

Rules:
1. Keep steps between 3-8 depending on complexity
2. For geometry of organic/creature/character shapes → recommend "neural"
3. For geometry of architectural/mechanical shapes → recommend "blender_agent"  
4. Retopology, UV unwrap, rigging, animation, lighting, export → always "blender_agent"
5. Texturing of organic models → "neural", texturing with specific PBR materials → "blender_agent"
6. Only recommend "manual" for steps requiring artistic judgment (fine detail sculpting, weight paint adjustments)
7. Set requiresPreviousStep=true when a step depends on the output of the prior step
8. Include practical tips for each step
9. neuralProvider is required when recommendedTool is "neural"

Respond with ONLY a JSON object matching this schema:
{
  "title": "string — workflow title",
  "steps": [
    {
      "title": "string",
      "description": "string — what this step does",
      "category": "geometry|topology|uv|texturing|rigging|animation|lighting|export|composition|other",
      "recommendedTool": "neural|blender_agent|manual",
      "toolReasoning": "string — WHY this tool is best",
      "alternativeTools": ["neural"|"blender_agent"|"manual"],
      "estimatedDuration": "~Xs or ~Xmin",
      "requiresPreviousStep": true|false,
      "tips": "optional string",
      "neuralProvider": "hunyuan-shape|hunyuan-paint|trellis|yvo3d — required when tool is neural"
    }
  ],
  "overallTips": ["string"]
}`

/**
 * Generate a workflow proposal using LLM analysis of the user's request.
 */
async function generateWithLLM(
    userRequest: string,
    strategy: Strategy,
    sceneContext?: string
): Promise<LLMWorkflowResponse> {
    const { generateGeminiResponse } = await import("@/lib/gemini")

    const userPrompt = [
        `Strategy classification: ${strategy}`,
        sceneContext ? `Current scene: ${sceneContext}` : null,
        `User request: ${userRequest}`,
    ]
        .filter(Boolean)
        .join("\n\n")

    const result = await generateGeminiResponse({
        messages: [{ role: "user", content: userPrompt }],
        systemPrompt: WORKFLOW_SYSTEM_PROMPT,
        temperature: 0.1,
        maxOutputTokens: 2048,
        responseMimeType: "application/json",
    })

    const parsed = JSON.parse(result.text) as LLMWorkflowResponse

    // Validate categories and tools
    const validTools: WorkflowTool[] = ["blender_agent", "neural", "manual"]
    const validCategories: WorkflowCategory[] = [
        "geometry", "topology", "uv", "texturing", "rigging",
        "animation", "lighting", "export", "composition", "other",
    ]

    for (const step of parsed.steps) {
        if (!validTools.includes(step.recommendedTool)) {
            step.recommendedTool = "blender_agent"
        }
        if (!validCategories.includes(step.category)) {
            step.category = "other"
        }
        // Ensure alternatives don't include the recommended tool
        step.alternativeTools = (step.alternativeTools ?? []).filter(
            (t) => validTools.includes(t) && t !== step.recommendedTool
        )
    }

    return parsed
}

// ---------------------------------------------------------------------------
// Fallback: deterministic workflow template
// ---------------------------------------------------------------------------

/**
 * Generates a reasonable workflow without LLM, based on the strategy.
 * Used when the LLM call fails.
 */
function generateFallbackWorkflow(
    userRequest: string,
    strategy: Strategy
): LLMWorkflowResponse {
    const steps: LLMWorkflowResponse["steps"] = []

    if (strategy === "neural" || strategy === "hybrid") {
        steps.push({
            title: "Generate Base Mesh",
            description: `Use a neural 3D model to generate the initial geometry for: "${userRequest}"`,
            category: "geometry",
            recommendedTool: "neural",
            toolReasoning: CATEGORY_DEFAULTS.geometry.reasoning,
            alternativeTools: ["manual"],
            estimatedDuration: CATEGORY_DEFAULTS.geometry.estimatedDuration,
            requiresPreviousStep: false,
            tips: "You can also upload a reference image for image-to-3D generation.",
            neuralProvider: "hunyuan-shape",
        })
    }

    if (strategy === "hybrid") {
        steps.push(
            {
                title: "Clean Up Topology",
                description: "Apply automatic retopology to create clean quad-based geometry suitable for deformation and export.",
                category: "topology",
                recommendedTool: "blender_agent",
                toolReasoning: CATEGORY_DEFAULTS.topology.reasoning,
                alternativeTools: ["manual"],
                estimatedDuration: CATEGORY_DEFAULTS.topology.estimatedDuration,
                requiresPreviousStep: true,
            },
            {
                title: "UV Unwrap",
                description: "Automatically generate UV maps for texturing.",
                category: "uv",
                recommendedTool: "blender_agent",
                toolReasoning: CATEGORY_DEFAULTS.uv.reasoning,
                alternativeTools: ["manual"],
                estimatedDuration: CATEGORY_DEFAULTS.uv.estimatedDuration,
                requiresPreviousStep: true,
            },
            {
                title: "Apply Textures",
                description: "Generate PBR textures using a neural texture model, or apply materials using the Blender agent.",
                category: "texturing",
                recommendedTool: "neural",
                toolReasoning: CATEGORY_DEFAULTS.texturing.reasoning,
                alternativeTools: ["blender_agent", "manual"],
                estimatedDuration: CATEGORY_DEFAULTS.texturing.estimatedDuration,
                requiresPreviousStep: true,
                neuralProvider: "hunyuan-paint",
            },
            {
                title: "Export",
                description: "Export the final model in glTF/FBX format with validation.",
                category: "export",
                recommendedTool: "blender_agent",
                toolReasoning: CATEGORY_DEFAULTS.export.reasoning,
                alternativeTools: ["manual"],
                estimatedDuration: CATEGORY_DEFAULTS.export.estimatedDuration,
                requiresPreviousStep: true,
            }
        )
    }

    return {
        title: `Workflow: ${userRequest.slice(0, 60)}`,
        steps,
        overallTips: [
            "You can skip any step and do it manually in Blender.",
            "Neural generation works best with descriptive, detailed prompts.",
            "The Blender agent uses battle-tested RAG scripts for post-processing.",
        ],
    }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export interface WorkflowAdvisorOptions {
    /** Current scene context for better recommendations */
    sceneContext?: string
}

/**
 * Generate a workflow proposal for a user's creation request.
 *
 * @param userRequest - The user's natural language request
 * @param strategy - The classified strategy (should be "neural" or "hybrid")
 * @param options - Additional options (scene context, etc.)
 * @returns A WorkflowProposal with per-step tool recommendations
 */
export async function generateWorkflowProposal(
    userRequest: string,
    strategy: Strategy,
    options: WorkflowAdvisorOptions = {}
): Promise<WorkflowProposal> {
    let llmResponse: LLMWorkflowResponse

    try {
        llmResponse = await generateWithLLM(userRequest, strategy, options.sceneContext)
    } catch (error) {
        console.warn("Workflow LLM generation failed, using fallback:", error)
        llmResponse = generateFallbackWorkflow(userRequest, strategy)
    }

    // Convert LLM response to WorkflowStep[] with status tracking
    const steps: WorkflowStep[] = llmResponse.steps.map((step, index) => {
        const categoryDefault = CATEGORY_DEFAULTS[step.category] ?? CATEGORY_DEFAULTS.other

        return {
            id: `step-${index + 1}-${step.category}`,
            stepNumber: index + 1,
            title: step.title,
            description: step.description,
            recommendedTool: step.recommendedTool,
            toolReasoning: step.toolReasoning || categoryDefault.reasoning,
            alternativeTools: step.alternativeTools.length > 0
                ? step.alternativeTools
                : categoryDefault.alternatives,
            category: step.category,
            estimatedDuration: step.estimatedDuration || categoryDefault.estimatedDuration,
            requiresPreviousStep: step.requiresPreviousStep,
            tips: step.tips,
            status: "pending",
            neuralProvider: step.neuralProvider ?? categoryDefault.neuralProvider,
            blenderAction: categoryDefault.blenderAction,
        }
    })

    const proposal: WorkflowProposal = {
        id: `workflow-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        title: llmResponse.title,
        strategy,
        steps,
        overallTips: llmResponse.overallTips ?? [],
        userRequest,
        createdAt: new Date().toISOString(),
    }

    return proposal
}
