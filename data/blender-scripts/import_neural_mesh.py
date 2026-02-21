"""
Import Neural Mesh — Post-Processing Pipeline for AI-Generated 3D Models

Handles the critical step of importing GLB/OBJ meshes produced by neural
generators (Hunyuan 3D, TRELLIS 2, YVO3D) into Blender and preparing them
for production use.

Common issues with neural-generated meshes:
1. Non-manifold geometry (gaps, flipped normals, isolated vertices)
2. Excessive polygon count (100k-500k+ faces)
3. Missing or baked-in materials that need PBR conversion
4. No UV maps or auto-generated UVs with seam artifacts
5. Objects not centered at world origin
6. Scale inconsistencies (neural models have arbitrary units)

This script addresses ALL of these issues.

Categories: import, neural, mesh, cleanup, production
"""

import bpy
import os
import math


# =============================================================================
# 1. Import GLB/OBJ with Error Handling
# =============================================================================

def import_neural_mesh(filepath: str, name_prefix: str = "Neural") -> list:
    """Import a GLB or OBJ file and return the imported mesh objects.

    Args:
        filepath: Path to the .glb or .obj file
        name_prefix: Prefix for renaming imported objects

    Returns:
        List of imported mesh objects
    """
    ext = os.path.splitext(filepath)[1].lower()

    # Track existing objects
    existing = set(bpy.data.objects.keys())

    if ext in ('.glb', '.gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif ext in ('.obj',):
        bpy.ops.wm.obj_import(filepath=filepath)
    elif ext in ('.fbx',):
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext in ('.stl',):
        bpy.ops.wm.stl_import(filepath=filepath)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    # Identify newly imported objects
    imported = [
        bpy.data.objects[name]
        for name in bpy.data.objects.keys()
        if name not in existing
    ]

    # Filter to mesh objects and rename
    meshes = [obj for obj in imported if obj.type == 'MESH']
    for i, obj in enumerate(meshes):
        obj.name = f"{name_prefix}_{i:02d}" if len(meshes) > 1 else name_prefix

    print(f"Imported {len(meshes)} mesh objects from {os.path.basename(filepath)}")
    return meshes


# =============================================================================
# 2. Mesh Cleanup — Fix Common Neural Generation Artifacts
# =============================================================================

def cleanup_neural_mesh(
    obj,
    fix_normals: bool = True,
    remove_doubles: bool = True,
    merge_distance: float = 0.0001,
    fill_holes: bool = True
):
    """Clean up a neural-generated mesh.

    Neural models frequently produce:
    - Flipped normals
    - Duplicate vertices (near-zero distance apart)
    - Non-manifold edges
    - Loose vertices/edges
    """
    if obj.type != 'MESH':
        return

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    try:
        bpy.ops.mesh.select_all(action='SELECT')

        # Remove loose geometry
        bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=False)

        # Merge by distance (remove duplicate vertices)
        if remove_doubles:
            bpy.ops.mesh.remove_doubles(threshold=merge_distance)

        # Recalculate normals (neural meshes often have flipped faces)
        if fix_normals:
            bpy.ops.mesh.normals_make_consistent(inside=False)

        # Fill holes (non-manifold boundaries)
        if fill_holes:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            try:
                bpy.ops.mesh.fill()
            except RuntimeError:
                pass  # Some non-manifold edges can't be filled
    finally:
        bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Cleaned {obj.name}: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")


# =============================================================================
# 3. Center and Scale to Standard Size
# =============================================================================

def normalize_neural_mesh(
    obj,
    target_height: float = 2.0,
    ground_to_floor: bool = True
):
    """Center the object at world origin and scale to a standard size.

    Neural models come in arbitrary units — this normalizes them.
    """
    if obj.type != 'MESH':
        return

    bpy.context.view_layer.objects.active = obj

    # Set origin to geometry center
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Center at world origin
    obj.location = (0, 0, 0)

    # Scale to target height
    dims = obj.dimensions
    max_dim = max(dims)
    if max_dim > 0:
        scale_factor = target_height / max_dim
        obj.scale = (scale_factor, scale_factor, scale_factor)
        bpy.ops.object.transform_apply(scale=True)

    # Ground to floor (bottom of bounding box at z=0)
    if ground_to_floor:
        bbox_min_z = min(corner[2] for corner in obj.bound_box)
        obj.location.z -= bbox_min_z

    print(f"Normalized {obj.name}: height={obj.dimensions.z:.2f}m, grounded={ground_to_floor}")


# =============================================================================
# 4. Decimate for Target Poly Count
# =============================================================================

def decimate_to_target(obj, target_faces: int = 10000):
    """Reduce polygon count while preserving shape.

    Neural meshes often have 100k-500k+ faces. This uses the Decimate
    modifier to bring them to a usable count.
    """
    if obj.type != 'MESH':
        return

    current_faces = len(obj.data.polygons)
    if current_faces <= target_faces:
        print(f"{obj.name} already at {current_faces} faces (target: {target_faces})")
        return

    ratio = target_faces / current_faces

    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new(name="Neural_Decimate", type='DECIMATE')
    mod.decimate_type = 'COLLAPSE'
    mod.ratio = ratio
    bpy.ops.object.modifier_apply(modifier=mod.name)

    final_faces = len(obj.data.polygons)
    print(f"Decimated {obj.name}: {current_faces} → {final_faces} faces (target: {target_faces})")


# =============================================================================
# 5. Auto-UV for Neural Meshes
# =============================================================================

def auto_uv_neural_mesh(obj, method: str = 'SMART'):
    """Generate UV maps for neural meshes that lack them.

    Args:
        method: 'SMART' (Smart UV Project) or 'LIGHTMAP' (Lightmap Pack)
    """
    if obj.type != 'MESH':
        return

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    if method == 'SMART':
        bpy.ops.uv.smart_project(
            angle_limit=math.radians(66),
            island_margin=0.02,
            area_weight=0.0,
            scale_to_bounds=True
        )
    elif method == 'LIGHTMAP':
        bpy.ops.uv.lightmap_pack(
            PREF_CONTEXT='ALL_FACES',
            PREF_PACK_IN_ONE=True,
            PREF_BOX_DIV=12,
            PREF_MARGIN_DIV=0.2
        )

    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"UV unwrapped {obj.name} using {method}")


# =============================================================================
# 6. Convert Baked Textures to PBR Material
# =============================================================================

def ensure_pbr_material(obj, material_name: str = "Neural_PBR"):
    """Ensure the mesh has a proper PBR material setup.

    If the mesh came with vertex colors or baked textures, this preserves
    them as the Base Color input while setting up proper PBR channels.
    """
    if obj.type != 'MESH':
        return

    # Check for existing materials
    if len(obj.data.materials) > 0:
        # Mesh already has materials — check if they're PBR-ready
        mat = obj.data.materials[0]
        if mat and mat.node_tree:
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            if bsdf:
                print(f"{obj.name} already has a Principled BSDF material")
                return

    # Create new PBR material
    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')

    # If the mesh has vertex colors, connect them to Base Color
    if obj.data.color_attributes:
        attr_node = mat.node_tree.nodes.new('ShaderNodeVertexColor')
        attr_node.layer_name = obj.data.color_attributes[0].name
        mat.node_tree.links.new(
            attr_node.outputs['Color'],
            bsdf.inputs['Base Color']
        )

    # Default PBR values
    bsdf.inputs['Roughness'].default_value = 0.5
    bsdf.inputs['Metallic'].default_value = 0.0

    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

    print(f"Set up PBR material '{material_name}' on {obj.name}")


# =============================================================================
# 7. Full Import Pipeline
# =============================================================================

def full_neural_import_pipeline(
    filepath: str,
    name: str = "Neural",
    target_height: float = 2.0,
    target_faces: int = 10000,
    cleanup: bool = True,
    auto_uv: bool = True,
    setup_pbr: bool = True
) -> list:
    """Complete pipeline: import → cleanup → normalize → decimate → UV → PBR.

    Args:
        filepath: Path to mesh file (GLB/OBJ/FBX/STL)
        name: Name prefix for imported objects
        target_height: Desired height in meters
        target_faces: Target polygon count per object
        cleanup: Whether to fix normals, remove doubles, etc.
        auto_uv: Whether to generate UV maps
        setup_pbr: Whether to ensure PBR material setup

    Returns:
        List of processed mesh objects
    """
    meshes = import_neural_mesh(filepath, name)

    for obj in meshes:
        if cleanup:
            cleanup_neural_mesh(obj)
        normalize_neural_mesh(obj, target_height)
        decimate_to_target(obj, target_faces)
        if auto_uv:
            auto_uv_neural_mesh(obj, method='SMART')
        if setup_pbr:
            ensure_pbr_material(obj, f"{name}_PBR")

    print(f"\n=== Neural Import Complete ===")
    print(f"Objects: {len(meshes)}")
    for obj in meshes:
        print(f"  {obj.name}: {len(obj.data.polygons)} faces, "
              f"height={obj.dimensions.z:.2f}m")

    return meshes
