"""
{
  "title": "Weight Paint Utilities",
  "category": "rigging",
  "tags": ["weight", "paint", "vertex", "skinning", "rigging", "deform"],
  "description": "Functions for weight painting and vertex weight management.",
  "blender_version": "3.0+"
}
"""
import bpy


def enable_weight_paint_mode(obj: bpy.types.Object = None) -> None:
    """Enter weight paint mode."""
    if obj:
        bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')


def set_active_vertex_group(
    obj: bpy.types.Object,
    group_name: str
) -> int:
    """
    Set active vertex group for painting.
    
    Args:
        obj: Target object
        group_name: Vertex group name
    
    Returns:
        Index of the active group
    """
    index = obj.vertex_groups.find(group_name)
    if index >= 0:
        obj.vertex_groups.active_index = index
    return index


def set_weight(weight: float = 1.0) -> None:
    """Set brush weight value (0-1)."""
    ts = bpy.context.tool_settings
    ts.unified_paint_settings.weight = weight


def set_brush_strength(strength: float = 1.0) -> None:
    """Set brush strength."""
    brush = bpy.context.tool_settings.weight_paint.brush
    if brush:
        brush.strength = strength


def set_brush_radius(radius: int = 50) -> None:
    """Set brush radius in pixels."""
    brush = bpy.context.tool_settings.weight_paint.brush
    if brush:
        brush.size = radius


def set_weight_brush(brush_type: str = 'Draw') -> None:
    """
    Set weight paint brush.
    
    Args:
        brush_type: 'Draw', 'Blur', 'Average', 'Smear'
    """
    brush = bpy.data.brushes.get(brush_type)
    if brush:
        bpy.context.tool_settings.weight_paint.brush = brush


def normalize_all_weights(
    obj: bpy.types.Object,
    lock_active: bool = False
) -> None:
    """Normalize all vertex groups."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.vertex_group_normalize_all(lock_active=lock_active)


def clean_weights(
    obj: bpy.types.Object,
    threshold: float = 0.01
) -> None:
    """
    Remove weights below threshold.
    
    Args:
        obj: Target object
        threshold: Minimum weight to keep
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    
    for vg in obj.vertex_groups:
        obj.vertex_groups.active_index = vg.index
        bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=threshold)


def smooth_weights(
    obj: bpy.types.Object,
    factor: float = 0.5,
    iterations: int = 1
) -> None:
    """Smooth vertex weights."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    
    for _ in range(iterations):
        bpy.ops.object.vertex_group_smooth(
            factor=factor,
            repeat=1
        )


def limit_total_weights(
    obj: bpy.types.Object,
    limit: int = 4
) -> None:
    """Limit total influences per vertex."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.vertex_group_limit_total(limit=limit)


def quantize_weights(
    obj: bpy.types.Object,
    steps: int = 4
) -> None:
    """Quantize weights to discrete steps."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.vertex_group_quantize(group_select_mode='ALL', steps=steps)


def mirror_weights(
    obj: bpy.types.Object,
    direction: str = 'POSITIVE_X'
) -> None:
    """Mirror weights across axis."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.vertex_group_mirror(
        mirror_weights=True,
        use_topology=False
    )


def transfer_weights(
    source: bpy.types.Object,
    target: bpy.types.Object,
    method: str = 'NEAREST_FACE'
) -> None:
    """
    Transfer weights from source to target.
    
    Args:
        source: Source mesh with weights
        target: Target mesh
        method: 'NEAREST', 'NEAREST_FACE', 'PROJECTED'
    """
    bpy.context.view_layer.objects.active = target
    target.select_set(True)
    source.select_set(True)
    
    bpy.ops.object.data_transfer(
        use_reverse_transfer=False,
        data_type='VGROUP_WEIGHTS',
        vert_mapping=method,
        layers_select_src='ALL',
        layers_select_dst='NAME'
    )


def auto_weights_from_bones(
    mesh: bpy.types.Object,
    armature: bpy.types.Object
) -> None:
    """
    Auto-generate weights from armature bones.
    
    Args:
        mesh: Target mesh
        armature: Armature object
    """
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')


def show_weight_overlay(show: bool = True) -> None:
    """Toggle weight visualization overlay."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.show_weight = show
