"""
{
  "title": "Automated Retopology Pipeline",
  "category": "topology",
  "tags": ["retopology", "remesh", "quadriflow", "voxel", "cleanup", "topology", "mesh-repair"],
  "description": "Production retopology pipeline for cleaning up sculpted or neural-generated meshes. Includes voxel remesh, Quadriflow quad-based remesh, decimation, mesh repair, and a full automated pipeline.",
  "blender_version": "4.0+"
}
"""
import bpy
import bmesh


def voxel_remesh(
    obj: bpy.types.Object,
    voxel_size: float = 0.03,
    adaptivity: float = 0.0
) -> bpy.types.Object:
    """
    Voxel remesh an object to create a unified, watertight mesh.
    Ideal first step before Quadriflow — merges intersecting geometry and
    removes internal faces.

    Args:
        obj: Mesh object to remesh
        voxel_size: Resolution (smaller = more detail). 0.003 for characters, 0.03 for environments
        adaptivity: Reduce faces in flat areas (0.0 = uniform, 1.0 = maximum adaptive)

    Returns:
        The remeshed object (same reference, modified in-place)

    Example:
        >>> voxel_remesh(sculpted_head, voxel_size=0.005)
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    obj.data.remesh_voxel_size = voxel_size
    obj.data.remesh_voxel_adaptivity = adaptivity

    bpy.ops.object.voxel_remesh()

    return obj


def quadriflow_remesh(
    obj: bpy.types.Object,
    target_faces: int = 5000,
    use_symmetry: bool = True,
    preserve_sharp: bool = True,
    preserve_boundary: bool = True
) -> bpy.types.Object:
    """
    Quadriflow remesh for clean quad-based topology.
    Essential for animation deformation — produces all-quad meshes
    with proper edge flow for subdivision and rigging.

    Args:
        obj: Mesh object to remesh
        target_faces: Desired number of faces in output mesh
        use_symmetry: Enable X-axis symmetry detection
        preserve_sharp: Keep sharp edges from original mesh
        preserve_boundary: Keep boundary edges (open meshes)

    Returns:
        The remeshed object (modified in-place)

    Example:
        >>> quadriflow_remesh(character_body, target_faces=8000, use_symmetry=True)
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.quadriflow_remesh(
        target_faces=target_faces,
        use_mesh_symmetry=use_symmetry,
        preserve_sharp=preserve_sharp,
        preserve_boundary=preserve_boundary
    )

    return obj


def decimate_mesh(
    obj: bpy.types.Object,
    ratio: float = None,
    target_faces: int = None,
    method: str = 'COLLAPSE'
) -> int:
    """
    Reduce mesh density using the Decimate modifier.

    Args:
        obj: Mesh object to decimate
        ratio: Decimation ratio (0.0 to 1.0). Mutually exclusive with target_faces
        target_faces: Target face count (calculates ratio automatically)
        method: 'COLLAPSE' (edge collapse), 'UNSUBDIV' (un-subdivide), 'DISSOLVE' (planar dissolve)

    Returns:
        Final face count after decimation

    Example:
        >>> decimate_mesh(dense_mesh, ratio=0.5)
        >>> decimate_mesh(dense_mesh, target_faces=2000)
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    current_faces = len(obj.data.polygons)

    if target_faces is not None:
        ratio = min(1.0, max(0.01, target_faces / current_faces))
    elif ratio is None:
        ratio = 0.5

    mod = obj.modifiers.new(name="Decimate_Auto", type='DECIMATE')
    mod.decimate_type = method
    if method == 'COLLAPSE':
        mod.ratio = ratio
    elif method == 'UNSUBDIV':
        mod.iterations = max(1, int(-1 * (ratio - 1) * 6))

    bpy.ops.object.modifier_apply(modifier=mod.name)

    return len(obj.data.polygons)


def fix_mesh_issues(
    obj: bpy.types.Object,
    merge_distance: float = 0.0001,
    fix_normals: bool = True,
    remove_doubles: bool = True,
    fill_holes: bool = True,
    remove_loose: bool = True
) -> dict:
    """
    Repair common mesh problems. Run this before retopology or export.

    Args:
        obj: Mesh object to repair
        merge_distance: Threshold for merging duplicate vertices
        fix_normals: Recalculate normals to face outward
        remove_doubles: Merge overlapping vertices
        fill_holes: Fill small boundary holes
        remove_loose: Remove disconnected vertices and edges

    Returns:
        Dict with counts of issues fixed

    Example:
        >>> report = fix_mesh_issues(imported_mesh)
        >>> print(f"Fixed {report['doubles_removed']} doubles")
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    report = {
        'doubles_removed': 0,
        'normals_fixed': False,
        'holes_filled': 0,
        'loose_removed': 0
    }

    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)

    # Remove doubles (merge by distance)
    if remove_doubles:
        initial_verts = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge_distance)
        report['doubles_removed'] = initial_verts - len(bm.verts)

    bmesh.update_edit_mesh(obj.data)

    # Remove loose geometry
    if remove_loose:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_loose()
        count = obj.data.total_vert_sel
        if count > 0:
            bpy.ops.mesh.delete(type='VERT')
            report['loose_removed'] = count

    # Fill holes
    if fill_holes:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold(extend=False)
        count = obj.data.total_edge_sel
        if count > 0:
            try:
                bpy.ops.mesh.fill()
                report['holes_filled'] = count
            except RuntimeError:
                pass  # Fill can fail on complex boundaries

    # Fix normals
    if fix_normals:
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        report['normals_fixed'] = True

    bpy.ops.object.mode_set(mode='OBJECT')

    return report


def retopology_pipeline(
    obj: bpy.types.Object,
    target_faces: int = 5000,
    voxel_size: float = 0.02,
    use_symmetry: bool = True,
    cleanup_first: bool = True
) -> dict:
    """
    Full automated retopology pipeline.
    Cleans mesh → voxel unify → optional decimate → Quadriflow.

    This is the recommended way to retopologize neural-generated or sculpted meshes
    for animation and game-dev use.

    Args:
        obj: Mesh object to retopologize
        target_faces: Desired final face count
        voxel_size: Voxel remesh resolution (smaller = more detail preserved)
        use_symmetry: Enable symmetry detection in Quadriflow
        cleanup_first: Run mesh repair before retopology

    Returns:
        Dict with pipeline results (face counts at each stage)

    Example:
        >>> result = retopology_pipeline(neural_mesh, target_faces=8000)
        >>> print(f"Reduced from {result['initial_faces']} to {result['final_faces']}")
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    result = {
        'initial_faces': len(obj.data.polygons),
        'after_cleanup': 0,
        'after_voxel': 0,
        'final_faces': 0
    }

    # Step 1: Cleanup
    if cleanup_first:
        fix_mesh_issues(obj)
    result['after_cleanup'] = len(obj.data.polygons)

    # Step 2: Apply all transforms (required for consistent results)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Step 3: Voxel remesh to unify geometry
    voxel_remesh(obj, voxel_size=voxel_size)
    result['after_voxel'] = len(obj.data.polygons)

    # Step 4: If voxel result is much denser than target, pre-decimate
    if len(obj.data.polygons) > target_faces * 3:
        decimate_mesh(obj, target_faces=target_faces * 2)

    # Step 5: Quadriflow for clean quad topology
    quadriflow_remesh(
        obj,
        target_faces=target_faces,
        use_symmetry=use_symmetry,
        preserve_sharp=True
    )
    result['final_faces'] = len(obj.data.polygons)

    # Step 6: Smooth shading on final mesh
    bpy.ops.object.shade_smooth()

    return result


def smooth_mesh(
    obj: bpy.types.Object,
    iterations: int = 2,
    factor: float = 0.5
) -> None:
    """
    Apply Laplacian smooth to reduce noise while preserving shape.

    Args:
        obj: Mesh object
        iterations: Number of smoothing passes
        factor: Smoothing strength (0.0 to 1.0)

    Example:
        >>> smooth_mesh(retopoed_mesh, iterations=3, factor=0.3)
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    mod = obj.modifiers.new(name="Smooth_Auto", type='LAPLACIANSMOOTH')
    mod.iterations = iterations
    mod.lambda_factor = factor

    bpy.ops.object.modifier_apply(modifier=mod.name)
