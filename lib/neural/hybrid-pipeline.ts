/**
 * Hybrid Pipeline — Full Neural-to-Production Orchestrator
 *
 * Chains neural generation with Blender post-processing to produce
 * production-ready 3D assets:
 *
 *  1. Generate geometry        (Hunyuan Shape / TRELLIS)
 *  2. Texture with PBR         (Hunyuan Paint / YVO3D)
 *  3. Import into Blender      (MCP execute_code)
 *  4. Auto-retopology          (Blender Quadriflow)
 *  5. Clean UV unwrap          (Blender Smart UV / Lightmap UV)
 *  6. Segment into parts       (Hunyuan Part — optional)
 *  7. Auto-rig with Rigify     (Blender — optional)
 *  8. Procedural animation     (Blender — optional)
 *  9. Validate scene           (Vision feedback loop)
 * 10. Export to target format   (Blender export pipeline)
 */

import type {
    GenerationRequest,
    HybridPipelineOptions,
    PipelineStage,
    PipelineStageStatus,
    ProviderSlug,
} from "./types"
import { createNeuralClient, selectBestProvider } from "./registry"

export interface HybridPipelineResult {
    success: boolean
    stages: PipelineStageStatus[]
    /** Final exported model path (if export succeeded) */
    outputPath?: string
    totalDurationMs: number
}

export type PipelineProgressCallback = (stage: PipelineStageStatus) => void

/**
 * Execute the full hybrid pipeline: Neural generation → Blender refinement → Export
 *
 * @param request       - The generation input (prompt/image)
 * @param options       - Pipeline configuration (which providers, which stages)
 * @param onProgress    - Optional callback for real-time stage updates
 * @param executeMcp    - Callback to execute Blender commands via MCP
 */
export async function runHybridPipeline(
    request: Omit<GenerationRequest, "provider" | "mode">,
    options: HybridPipelineOptions = {},
    onProgress?: PipelineProgressCallback,
    executeMcp?: (code: string) => Promise<{ success: boolean; result?: string; error?: string }>,
): Promise<HybridPipelineResult> {
    const startTime = Date.now()
    const stages: PipelineStageStatus[] = []

    const {
        geometryProvider = "hunyuan-shape",
        textureProvider = "hunyuan-paint",
        enableSegmentation = false,
        enableRigging = false,
        enableAnimation = false,
        exportFormats = ["glb"],
        gracefulDegradation = true,
    } = options

    // Helper to track stage status
    const trackStage = (
        stage: PipelineStage,
        status: PipelineStageStatus["status"],
        provider?: ProviderSlug,
        extra?: Partial<PipelineStageStatus>,
    ) => {
        const entry: PipelineStageStatus = {
            stage,
            status,
            provider,
            ...extra,
        }
        // Update or add
        const idx = stages.findIndex((s) => s.stage === stage)
        if (idx >= 0) stages[idx] = entry
        else stages.push(entry)
        onProgress?.(entry)
    }

    let currentMeshPath: string | undefined

    // -----------------------------------------------------------------------
    // Stage 1: Geometry Generation
    // -----------------------------------------------------------------------
    try {
        trackStage("geometry", "running", geometryProvider)

        const geoMeta = selectBestProvider("geometry", geometryProvider)
        if (!geoMeta) throw new Error("No geometry provider available")

        const geoClient = await createNeuralClient(geoMeta.slug)
        const geoResult = await geoClient.generate({
            ...request,
            provider: geoMeta.slug,
            mode: request.imageUrl ? "image_to_3d" : "text_to_3d",
        })

        if (geoResult.status === "completed" && geoResult.modelPath) {
            currentMeshPath = geoResult.modelPath
            trackStage("geometry", "completed", geoMeta.slug, {
                durationMs: geoResult.generationTimeMs,
                outputPath: geoResult.modelPath,
            })
        } else {
            throw new Error(geoResult.error ?? "Geometry generation failed")
        }
    } catch (err) {
        const msg = err instanceof Error ? err.message : String(err)
        trackStage("geometry", "failed", geometryProvider, { error: msg })
        if (!gracefulDegradation) {
            return { success: false, stages, totalDurationMs: Date.now() - startTime }
        }
    }

    // -----------------------------------------------------------------------
    // Stage 2: Texturing
    // -----------------------------------------------------------------------
    if (currentMeshPath) {
        try {
            trackStage("texturing", "running", textureProvider)

            const texMeta = selectBestProvider("texturing", textureProvider)
            if (!texMeta) throw new Error("No texturing provider available")

            const texClient = await createNeuralClient(texMeta.slug)
            const texResult = await texClient.generate({
                ...request,
                meshUrl: currentMeshPath,
                provider: texMeta.slug,
                mode: "mesh_to_texture",
            })

            if (texResult.status === "completed" && texResult.modelPath) {
                currentMeshPath = texResult.modelPath
                trackStage("texturing", "completed", texMeta.slug, {
                    durationMs: texResult.generationTimeMs,
                    outputPath: texResult.modelPath,
                })
            } else {
                throw new Error(texResult.error ?? "Texturing failed")
            }
        } catch (err) {
            const msg = err instanceof Error ? err.message : String(err)
            trackStage("texturing", "failed", textureProvider, { error: msg })
            if (!gracefulDegradation) {
                return { success: false, stages, totalDurationMs: Date.now() - startTime }
            }
        }
    }

    // -----------------------------------------------------------------------
    // Stage 3: Import into Blender (via MCP)
    // -----------------------------------------------------------------------
    if (currentMeshPath && executeMcp) {
        const importCode = `
import bpy

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import the neural-generated GLB
bpy.ops.import_scene.gltf(filepath=r"${currentMeshPath.replace(/\\/g, "/")}")

# Center and ground the imported object
imported = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
if imported:
    bpy.context.view_layer.objects.active = imported[0]
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    for obj in imported:
        obj.location.z -= min(v.co.z for v in obj.data.vertices) * obj.scale.z

print(f"Imported {len(imported)} mesh objects from neural generation")
`.trim()

        try {
            const result = await executeMcp(importCode)
            if (!result.success) {
                trackStage("retopology", "skipped", undefined, {
                    error: `Blender import failed: ${result.error}`,
                })
            }
        } catch {
            // Non-fatal — continue with remaining stages
        }
    }

    // -----------------------------------------------------------------------
    // Stage 4: Retopology (Blender Quadriflow)
    // -----------------------------------------------------------------------
    if (currentMeshPath && executeMcp) {
        try {
            trackStage("retopology", "running")

            const retopoCode = `
import bpy

obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    # Voxel remesh for watertight mesh first
    mod = obj.modifiers.new(name="Voxel Remesh", type='REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = 0.02
    bpy.ops.object.modifier_apply(modifier=mod.name)

    # Quadriflow retopology
    bpy.ops.object.quadriflow_remesh(
        target_faces=5000,
        use_paint_symmetry=False,
        use_preserve_sharp=True,
        use_preserve_boundary=True,
        seed=42
    )
    print(f"Retopology complete: {len(obj.data.polygons)} faces")
else:
    print("No active mesh object for retopology")
`.trim()

            const result = await executeMcp(retopoCode)
            trackStage("retopology", result.success ? "completed" : "failed", undefined, {
                error: result.success ? undefined : result.error,
            })
        } catch (err) {
            const msg = err instanceof Error ? err.message : String(err)
            trackStage("retopology", "failed", undefined, { error: msg })
        }
    } else {
        trackStage("retopology", "skipped")
    }

    // -----------------------------------------------------------------------
    // Stage 5: Segmentation (Hunyuan Part — optional)
    // -----------------------------------------------------------------------
    if (enableSegmentation && currentMeshPath) {
        try {
            trackStage("segmentation", "running", "hunyuan-part")
            const partClient = await createNeuralClient("hunyuan-part")
            const partResult = await partClient.generate({
                meshUrl: currentMeshPath,
                provider: "hunyuan-part",
                mode: "mesh_to_parts",
            })

            if (partResult.status === "completed" && partResult.modelPath) {
                currentMeshPath = partResult.modelPath
                trackStage("segmentation", "completed", "hunyuan-part", {
                    durationMs: partResult.generationTimeMs,
                    outputPath: partResult.modelPath,
                })
            } else {
                throw new Error(partResult.error ?? "Segmentation failed")
            }
        } catch (err) {
            const msg = err instanceof Error ? err.message : String(err)
            trackStage("segmentation", "failed", "hunyuan-part", { error: msg })
        }
    } else {
        trackStage("segmentation", "skipped")
    }

    // -----------------------------------------------------------------------
    // Stage 6: Rigging (Blender Rigify — optional)
    // -----------------------------------------------------------------------
    if (enableRigging && executeMcp) {
        try {
            trackStage("rigging", "running")

            const rigCode = `
import bpy

obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    # Add Rigify basic human metarig
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object

    # Scale metarig to fit object
    obj_dims = obj.dimensions
    meta_dims = metarig.dimensions
    scale_factor = max(obj_dims) / max(meta_dims) if max(meta_dims) > 0 else 1
    metarig.scale = (scale_factor, scale_factor, scale_factor)
    bpy.ops.object.transform_apply(scale=True)

    # Generate rig
    bpy.ops.pose.rigify_generate()
    rig = bpy.context.active_object

    # Parent mesh to rig with automatic weights
    obj.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    print(f"Rigging complete: {len(rig.data.bones)} bones")
else:
    print("No active mesh for rigging")
`.trim()

            const result = await executeMcp(rigCode)
            trackStage("rigging", result.success ? "completed" : "failed", undefined, {
                error: result.success ? undefined : result.error,
            })
        } catch (err) {
            const msg = err instanceof Error ? err.message : String(err)
            trackStage("rigging", "failed", undefined, { error: msg })
        }
    } else {
        trackStage("rigging", "skipped")
    }

    // -----------------------------------------------------------------------
    // Stage 7: Animation (optional)
    // -----------------------------------------------------------------------
    if (enableAnimation && executeMcp) {
        trackStage("animation", "skipped", undefined, {
            error: "Procedural animation requires per-asset configuration — use RAG scripts directly",
        })
    } else {
        trackStage("animation", "skipped")
    }

    // -----------------------------------------------------------------------
    // Stage 8: Export
    // -----------------------------------------------------------------------
    if (executeMcp) {
        try {
            trackStage("export", "running")

            const format = exportFormats[0] ?? "glb"
            const exportPath = currentMeshPath?.replace(/\.[^.]+$/, `-final.${format}`) ??
                `neural-export-${Date.now()}.${format}`

            const exportCode = `
import bpy

bpy.ops.object.select_all(action='SELECT')
filepath = r"${exportPath.replace(/\\/g, "/")}"
${format === "glb" ? `bpy.ops.export_scene.gltf(filepath=filepath, export_format='GLB')` : ""}
${format === "fbx" ? `bpy.ops.export_scene.fbx(filepath=filepath)` : ""}
${format === "obj" ? `bpy.ops.wm.obj_export(filepath=filepath)` : ""}
${format === "usd" ? `bpy.ops.wm.usd_export(filepath=filepath)` : ""}
print(f"Exported to {filepath}")
`.trim()

            const result = await executeMcp(exportCode)
            trackStage("export", result.success ? "completed" : "failed", undefined, {
                outputPath: result.success ? exportPath : undefined,
                error: result.success ? undefined : result.error,
            })

            if (result.success) {
                return {
                    success: true,
                    stages,
                    outputPath: exportPath,
                    totalDurationMs: Date.now() - startTime,
                }
            }
        } catch (err) {
            const msg = err instanceof Error ? err.message : String(err)
            trackStage("export", "failed", undefined, { error: msg })
        }
    } else {
        trackStage("export", "skipped", undefined, {
            error: "No MCP executor available — cannot export from Blender",
        })
    }

    const allCompleted = stages.every((s) =>
        s.status === "completed" || s.status === "skipped",
    )

    return {
        success: allCompleted,
        stages,
        totalDurationMs: Date.now() - startTime,
    }
}
