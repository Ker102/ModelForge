"""
{
  "title": "Automated UV Unwrap Pipeline",
  "category": "uv",
  "tags": ["uv", "unwrap", "lightmap", "texel-density", "baking", "pipeline", "auto-uv"],
  "description": "High-level UV unwrapping pipeline that auto-detects the best projection method per object, creates lightmap UVs, checks texel density, and handles batch UV operations for production workflows.",
  "blender_version": "4.0+"
}
"""
import bpy
import bmesh
import math


def auto_uv_pipeline(
    obj: bpy.types.Object,
    island_margin: float = 0.02,
    normalize: bool = True,
    pack: bool = True
) -> dict:
    """
    Fully automated UV unwrap pipeline.
    Analyzes object shape to pick the best UV projection method,
    unwraps, packs islands, and normalizes texel density.

    Shape detection logic:
    - Flat / planar → Project From View
    - Box-like (roughly equal dims) → Cube Projection
    - Tall / long → Cylinder Projection
    - Spherical → Sphere Projection
    - Complex / organic → Smart UV Project with auto-seams

    Args:
        obj: Mesh object to unwrap
        island_margin: Space between UV islands
        normalize: Equalize texel density across all islands
        pack: Pack UV islands to fill 0-1 space

    Returns:
        Dict with 'method' used and 'island_count'

    Example:
        >>> result = auto_uv_pipeline(character_mesh)
        >>> print(f"Used {result['method']} — {result['island_count']} islands")
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Ensure UVs exist
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")

    # Analyze bounding box to pick method
    dims = obj.dimensions
    max_dim = max(dims)
    min_dim = min(dims) if min(dims) > 0 else 0.001

    aspect_ratio = max_dim / min_dim

    if aspect_ratio > 5:
        method = 'cylinder'
    elif aspect_ratio < 1.3 and abs(dims.x - dims.y) < 0.1 * max_dim and abs(dims.y - dims.z) < 0.1 * max_dim:
        method = 'sphere'
    elif aspect_ratio < 2.0 and min_dim / max_dim > 0.5:
        method = 'cube'
    else:
        method = 'smart'

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    if method == 'smart':
        bpy.ops.uv.smart_project(
            angle_limit=math.radians(66),
            island_margin=island_margin,
            scale_to_bounds=True
        )
    elif method == 'cube':
        bpy.ops.uv.cube_project(
            cube_size=max_dim,
            correct_aspect=True
        )
    elif method == 'cylinder':
        bpy.ops.uv.cylinder_project(
            direction='ALIGN_TO_OBJECT',
            radius=max_dim / 2
        )
    elif method == 'sphere':
        bpy.ops.uv.sphere_project(direction='ALIGN_TO_OBJECT')

    # Normalize texel density
    if normalize:
        bpy.ops.uv.average_islands_scale()

    # Pack islands
    if pack:
        bpy.ops.uv.pack_islands(margin=island_margin, rotate=True)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Count UV islands
    island_count = _count_uv_islands(obj)

    return {
        'method': method,
        'island_count': island_count,
        'object': obj.name
    }


def lightmap_uv(
    obj: bpy.types.Object,
    uv_name: str = "Lightmap",
    margin: float = 0.03
) -> None:
    """
    Create a second UV channel optimized for lightmap baking.
    Uses Smart UV Project with high margin for clean lightmap padding.

    Args:
        obj: Mesh object
        uv_name: Name for the lightmap UV layer
        margin: Island margin (higher than normal for lightmap bleeding)

    Example:
        >>> lightmap_uv(building_mesh, margin=0.05)
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Create new UV layer
    uv_layer = obj.data.uv_layers.new(name=uv_name)
    obj.data.uv_layers.active = uv_layer

    # Smart UV project is best for lightmaps (non-overlapping)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(66),
        island_margin=margin,
        scale_to_bounds=True
    )
    bpy.ops.uv.pack_islands(margin=margin, rotate=True)
    bpy.ops.object.mode_set(mode='OBJECT')


def uv_density_check(
    obj: bpy.types.Object,
    texture_size: int = 1024
) -> dict:
    """
    Check texel density across UV islands for quality assurance.
    Reports min/max/average texels per unit for identifying
    under-textured or over-textured areas.

    Args:
        obj: Mesh object with UVs to check
        texture_size: Expected texture resolution in pixels

    Returns:
        Dict with 'min_density', 'max_density', 'avg_density', 'variance'

    Example:
        >>> report = uv_density_check(game_asset, texture_size=2048)
        >>> if report['variance'] > 2.0:
        ...     print("Warning: uneven texel density")
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    mesh = obj.data
    if not mesh.uv_layers.active:
        return {'min_density': 0, 'max_density': 0, 'avg_density': 0, 'variance': 0}

    uv_layer = mesh.uv_layers.active.data
    densities = []

    for poly in mesh.polygons:
        # Calculate 3D face area
        face_area_3d = poly.area
        if face_area_3d < 1e-8:
            continue

        # Calculate UV face area
        uv_coords = []
        for loop_idx in poly.loop_indices:
            uv_coords.append(uv_layer[loop_idx].uv)

        if len(uv_coords) >= 3:
            uv_area = _polygon_area_2d(uv_coords)
            if uv_area > 1e-8:
                density = (uv_area * texture_size * texture_size) / face_area_3d
                densities.append(density)

    if not densities:
        return {'min_density': 0, 'max_density': 0, 'avg_density': 0, 'variance': 0}

    avg = sum(densities) / len(densities)
    variance = max(densities) / max(min(densities), 0.001)

    return {
        'min_density': min(densities),
        'max_density': max(densities),
        'avg_density': avg,
        'variance': variance
    }


def multi_object_uv(
    objects: list = None,
    method: str = 'smart',
    island_margin: float = 0.02
) -> list:
    """
    Batch UV unwrap multiple objects with consistent settings.
    If no objects are specified, uses all selected mesh objects.

    Args:
        objects: List of mesh objects (or None for selected)
        method: 'smart', 'cube', 'cylinder', 'sphere', or 'auto'
        island_margin: Space between islands

    Returns:
        List of dicts with results per object

    Example:
        >>> results = multi_object_uv(method='auto')
    """
    if objects is None:
        objects = [o for o in bpy.context.selected_objects if o.type == 'MESH']

    results = []
    for obj in objects:
        if obj.type != 'MESH':
            continue
        if method == 'auto':
            result = auto_uv_pipeline(obj, island_margin=island_margin)
        else:
            result = _unwrap_single(obj, method, island_margin)
        results.append(result)

    return results


def create_uv_for_texture_baking(
    obj: bpy.types.Object,
    uv_name: str = "BakeUV",
    margin: float = 0.04
) -> None:
    """
    Create UV layout optimized for texture baking.
    Non-overlapping, maximum space usage, higher margins to prevent bleeding.

    Args:
        obj: Mesh object
        uv_name: Name for the baking UV layer
        margin: Island margin (larger for bake bleed prevention)

    Example:
        >>> create_uv_for_texture_baking(high_poly_model)
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Create dedicated bake UV layer
    uv_layer = obj.data.uv_layers.new(name=uv_name)
    obj.data.uv_layers.active = uv_layer

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Use angle-based unwrap with auto-seams for best bake coverage
    bpy.ops.mesh.mark_seam(clear=True)
    bpy.ops.mesh.edges_select_sharp(sharpness=math.radians(40))
    bpy.ops.mesh.mark_seam()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=margin)

    # Normalize and pack
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(margin=margin, rotate=True)

    bpy.ops.object.mode_set(mode='OBJECT')


# --- Internal Helpers ---

def _count_uv_islands(obj: bpy.types.Object) -> int:
    """Count the number of UV islands in the active UV layer."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.active
    if not uv_layer:
        bm.free()
        return 0

    # Simple island counting via face connectivity in UV space
    visited = set()
    islands = 0
    for face in bm.faces:
        if face.index not in visited:
            # BFS through UV-connected faces
            queue = [face]
            while queue:
                f = queue.pop()
                if f.index in visited:
                    continue
                visited.add(f.index)
                for edge in f.edges:
                    for linked_face in edge.link_faces:
                        if linked_face.index not in visited:
                            queue.append(linked_face)
            islands += 1

    bm.free()
    return islands


def _polygon_area_2d(coords: list) -> float:
    """Calculate area of a 2D polygon using the shoelace formula."""
    n = len(coords)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0


def _unwrap_single(obj, method, margin):
    """Unwrap a single object with the specified method."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    if method == 'smart':
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margin)
    elif method == 'cube':
        bpy.ops.uv.cube_project(cube_size=max(obj.dimensions))
    elif method == 'cylinder':
        bpy.ops.uv.cylinder_project()
    elif method == 'sphere':
        bpy.ops.uv.sphere_project()

    bpy.ops.uv.pack_islands(margin=margin, rotate=True)
    bpy.ops.object.mode_set(mode='OBJECT')

    return {'method': method, 'object': obj.name, 'island_count': _count_uv_islands(obj)}
