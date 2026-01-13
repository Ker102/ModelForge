"""
{
  "title": "Sculpt Utilities",
  "category": "sculpting",
  "tags": ["sculpt", "brush", "dyntopo", "remesh", "multires"],
  "description": "Functions for sculpting mode setup and operations.",
  "blender_version": "3.0+"
}
"""
import bpy


def enable_sculpt_mode(obj: bpy.types.Object = None) -> None:
    """Enter sculpt mode for object."""
    if obj:
        bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='SCULPT')


def enable_dyntopo(
    detail_size: float = 12,
    detail_type: str = 'RELATIVE',
    refine_method: str = 'SUBDIVIDE_COLLAPSE'
) -> None:
    """
    Enable dynamic topology sculpting.
    
    Args:
        detail_size: Detail level (lower = more detail)
        detail_type: 'RELATIVE', 'CONSTANT', 'BRUSH'
        refine_method: 'SUBDIVIDE', 'COLLAPSE', 'SUBDIVIDE_COLLAPSE'
    """
    if not bpy.context.sculpt_object.use_dynamic_topology_sculpting:
        bpy.ops.sculpt.dynamic_topology_toggle()
    
    ts = bpy.context.tool_settings.sculpt
    ts.detail_size = detail_size
    ts.detail_type_method = detail_type
    ts.detail_refine_method = refine_method


def disable_dyntopo() -> None:
    """Disable dynamic topology."""
    if bpy.context.sculpt_object.use_dynamic_topology_sculpting:
        bpy.ops.sculpt.dynamic_topology_toggle()


def add_multires_modifier(
    obj: bpy.types.Object,
    levels: int = 3
) -> bpy.types.Modifier:
    """
    Add multiresolution modifier for sculpting.
    
    Args:
        obj: Target object
        levels: Number of subdivision levels
    
    Returns:
        The multires modifier
    """
    mod = obj.modifiers.new("Multires", 'MULTIRES')
    
    bpy.context.view_layer.objects.active = obj
    for _ in range(levels):
        bpy.ops.object.multires_subdivide(modifier="Multires")
    
    return mod


def remesh_voxel(
    obj: bpy.types.Object,
    voxel_size: float = 0.01,
    smooth_normals: bool = True
) -> None:
    """
    Apply voxel remesh to object.
    
    Args:
        obj: Target object
        voxel_size: Voxel size (smaller = more detail)
        smooth_normals: Smooth resulting normals
    """
    bpy.context.view_layer.objects.active = obj
    obj.data.remesh_voxel_size = voxel_size
    obj.data.use_remesh_preserve_volume = True
    
    bpy.ops.object.voxel_remesh()
    
    if smooth_normals:
        bpy.ops.object.shade_smooth()


def remesh_quadriflow(
    obj: bpy.types.Object,
    target_faces: int = 5000,
    seed: int = 0
) -> None:
    """
    Apply QuadriFlow remesh for clean quad topology.
    
    Args:
        obj: Target object
        target_faces: Target face count
        seed: Random seed
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.quadriflow_remesh(
        target_faces=target_faces,
        seed=seed
    )


def set_sculpt_brush(brush_name: str) -> None:
    """
    Set active sculpt brush.
    
    Args:
        brush_name: 'Draw', 'Clay', 'Clay Strips', 'Grab', 'Smooth',
                   'Flatten', 'Crease', 'Inflate', 'Pinch', 'Mask'
    """
    brush = bpy.data.brushes.get(brush_name)
    if brush:
        bpy.context.tool_settings.sculpt.brush = brush


def configure_brush(
    strength: float = 0.5,
    radius: int = 50,
    auto_smooth: float = 0,
    use_frontface: bool = True
) -> None:
    """Configure active sculpt brush settings."""
    brush = bpy.context.tool_settings.sculpt.brush
    if brush:
        brush.strength = strength
        brush.size = radius
        brush.auto_smooth_factor = auto_smooth
        brush.use_frontface = use_frontface


def mask_by_normal(
    limit: float = 0.5,
    direction: str = 'VIEW'
) -> None:
    """Create mask based on normal direction."""
    bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
    bpy.ops.sculpt.mask_by_normal(limit=limit)


def expand_mask(iterations: int = 1) -> None:
    """Expand current mask."""
    for _ in range(iterations):
        bpy.ops.sculpt.mask_expand(
            use_smooth=True,
            smooth_iterations=2
        )


def invert_mask() -> None:
    """Invert mask."""
    bpy.ops.paint.mask_flood_fill(mode='INVERT')


def clear_mask() -> None:
    """Clear all masking."""
    bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)


def hide_masked() -> None:
    """Hide masked geometry."""
    bpy.ops.sculpt.face_sets_create(mode='MASKED')
    bpy.ops.sculpt.face_set_change_visibility(mode='HIDE_ACTIVE')


def show_all() -> None:
    """Show all hidden geometry."""
    bpy.ops.sculpt.reveal_all()


def symmetrize_mesh(direction: str = 'NEGATIVE_X') -> None:
    """
    Symmetrize mesh.
    
    Args:
        direction: 'NEGATIVE_X', 'POSITIVE_X', 'NEGATIVE_Y', etc.
    """
    bpy.ops.sculpt.symmetrize(direction=direction)
