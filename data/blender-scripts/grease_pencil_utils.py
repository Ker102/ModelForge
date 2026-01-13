"""
{
  "title": "Grease Pencil Utilities",
  "category": "drawing",
  "tags": ["grease pencil", "2d", "drawing", "stroke", "annotation"],
  "description": "Functions for Grease Pencil object creation and editing.",
  "blender_version": "3.0+"
}
"""
import bpy


def create_grease_pencil_object(
    name: str = "GPencil",
    location: tuple = (0, 0, 0)
) -> bpy.types.Object:
    """
    Create new Grease Pencil object.
    
    Args:
        name: Object name
        location: Position
    
    Returns:
        The Grease Pencil object
    """
    gpd = bpy.data.grease_pencils.new(name)
    gpo = bpy.data.objects.new(name, gpd)
    bpy.context.collection.objects.link(gpo)
    gpo.location = location
    
    # Add default layer
    layer = gpd.layers.new("Layer")
    layer.frames.new(1)
    
    return gpo


def add_gp_layer(
    gp_object: bpy.types.Object,
    name: str = "Layer",
    color: tuple = (0, 0, 0, 1)
) -> bpy.types.GPencilLayer:
    """
    Add layer to Grease Pencil object.
    
    Args:
        gp_object: Grease Pencil object
        name: Layer name
        color: RGBA layer tint
    
    Returns:
        The created layer
    """
    gpd = gp_object.data
    layer = gpd.layers.new(name)
    layer.tint_color = color[:3]
    layer.tint_factor = color[3] if len(color) > 3 else 1.0
    layer.frames.new(1)
    
    return layer


def add_gp_material(
    gp_object: bpy.types.Object,
    name: str = "GPMaterial",
    color: tuple = (0, 0, 0, 1),
    fill_color: tuple = None,
    stroke_style: str = 'SOLID'
) -> bpy.types.Material:
    """
    Add material to Grease Pencil object.
    
    Args:
        gp_object: Grease Pencil object
        name: Material name
        color: Stroke color (RGBA)
        fill_color: Fill color (None for no fill)
        stroke_style: 'SOLID', 'DOTS', 'SQUARES'
    
    Returns:
        The created material
    """
    mat = bpy.data.materials.new(name)
    bpy.data.materials.create_gpencil_data(mat)
    
    mat.grease_pencil.color = color
    mat.grease_pencil.stroke_style = stroke_style
    
    if fill_color:
        mat.grease_pencil.show_fill = True
        mat.grease_pencil.fill_color = fill_color
    else:
        mat.grease_pencil.show_fill = False
    
    gp_object.data.materials.append(mat)
    
    return mat


def set_gp_brush(brush_name: str) -> None:
    """
    Set Grease Pencil brush.
    
    Args:
        brush_name: Brush name (e.g., 'Pencil', 'Ink Pen', 'Marker')
    """
    brush = bpy.data.brushes.get(brush_name)
    if brush:
        bpy.context.tool_settings.gpencil_paint.brush = brush


def configure_gp_brush(
    size: int = 50,
    strength: float = 1.0,
    use_pressure: bool = True
) -> None:
    """Configure active Grease Pencil brush."""
    brush = bpy.context.tool_settings.gpencil_paint.brush
    if brush:
        brush.size = size
        brush.gpencil_settings.pen_strength = strength
        brush.gpencil_settings.use_pressure = use_pressure


def enable_gp_draw_mode(gp_object: bpy.types.Object) -> None:
    """Enter Grease Pencil draw mode."""
    bpy.context.view_layer.objects.active = gp_object
    bpy.ops.object.mode_set(mode='PAINT_GPENCIL')


def enable_gp_edit_mode(gp_object: bpy.types.Object) -> None:
    """Enter Grease Pencil edit mode."""
    bpy.context.view_layer.objects.active = gp_object
    bpy.ops.object.mode_set(mode='EDIT_GPENCIL')


def enable_gp_sculpt_mode(gp_object: bpy.types.Object) -> None:
    """Enter Grease Pencil sculpt mode."""
    bpy.context.view_layer.objects.active = gp_object
    bpy.ops.object.mode_set(mode='SCULPT_GPENCIL')


def add_gp_modifier(
    gp_object: bpy.types.Object,
    modifier_type: str,
    name: str = None
) -> bpy.types.GpencilModifier:
    """
    Add Grease Pencil modifier.
    
    Args:
        gp_object: Grease Pencil object
        modifier_type: 'GP_SMOOTH', 'GP_SUBDIV', 'GP_THICK', 'GP_TINT', etc.
        name: Optional modifier name
    
    Returns:
        The created modifier
    """
    mod_name = name or modifier_type
    mod = gp_object.grease_pencil_modifiers.new(mod_name, modifier_type)
    return mod


def add_gp_smooth(
    gp_object: bpy.types.Object,
    factor: float = 0.5,
    step: int = 1
) -> bpy.types.GpencilModifier:
    """Add smoothing modifier."""
    mod = add_gp_modifier(gp_object, 'GP_SMOOTH', 'Smooth')
    mod.factor = factor
    mod.step = step
    return mod


def add_gp_thickness(
    gp_object: bpy.types.Object,
    thickness: int = 10,
    normalize: bool = False
) -> bpy.types.GpencilModifier:
    """Add thickness modifier."""
    mod = add_gp_modifier(gp_object, 'GP_THICK', 'Thickness')
    mod.thickness = thickness
    mod.normalize_thickness = normalize
    return mod


def add_gp_tint(
    gp_object: bpy.types.Object,
    color: tuple = (1, 0, 0),
    factor: float = 0.5
) -> bpy.types.GpencilModifier:
    """Add tint modifier."""
    mod = add_gp_modifier(gp_object, 'GP_TINT', 'Tint')
    mod.color = color
    mod.factor = factor
    return mod


def add_gp_lineart(
    gp_object: bpy.types.Object,
    source_object: bpy.types.Object = None,
    source_collection: bpy.types.Collection = None
) -> bpy.types.GpencilModifier:
    """
    Add Line Art modifier for automatic line generation.
    
    Args:
        gp_object: Target Grease Pencil object
        source_object: Single source object
        source_collection: Collection of source objects
    
    Returns:
        The Line Art modifier
    """
    mod = add_gp_modifier(gp_object, 'GP_LINEART', 'LineArt')
    
    if source_object:
        mod.source_type = 'OBJECT'
        mod.source_object = source_object
    elif source_collection:
        mod.source_type = 'COLLECTION'
        mod.source_collection = source_collection
    else:
        mod.source_type = 'SCENE'
    
    return mod


def convert_gp_to_curves(gp_object: bpy.types.Object) -> bpy.types.Object:
    """Convert Grease Pencil strokes to curves."""
    bpy.context.view_layer.objects.active = gp_object
    gp_object.select_set(True)
    
    bpy.ops.gpencil.convert(type='CURVE')
    
    return bpy.context.active_object


def set_gp_onion_skin(
    gp_object: bpy.types.Object,
    enabled: bool = True,
    frames_before: int = 1,
    frames_after: int = 1
) -> None:
    """Configure onion skinning."""
    gpd = gp_object.data
    gpd.use_onion_skinning = enabled
    gpd.onion_factor = 0.5
    
    if enabled:
        gpd.ghost_before_range = frames_before
        gpd.ghost_after_range = frames_after
