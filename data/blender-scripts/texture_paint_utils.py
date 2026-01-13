"""
{
  "title": "Texture Paint Utilities",
  "category": "texturing",
  "tags": ["texture", "paint", "image", "brush", "UV", "baking"],
  "description": "Functions for texture painting and image editing.",
  "blender_version": "3.0+"
}
"""
import bpy


def enable_texture_paint_mode(obj: bpy.types.Object = None) -> None:
    """Enter texture paint mode."""
    if obj:
        bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='TEXTURE_PAINT')


def create_paint_slot(
    obj: bpy.types.Object,
    slot_type: str = 'DIFFUSE',
    width: int = 1024,
    height: int = 1024,
    color: tuple = (0.5, 0.5, 0.5, 1.0),
    name: str = "PaintTexture"
) -> bpy.types.Image:
    """
    Create texture paint slot.
    
    Args:
        obj: Target object
        slot_type: 'DIFFUSE', 'ROUGHNESS', 'NORMAL', 'BUMP'
        width: Image width
        height: Image height
        color: Fill color
        name: Texture name
    
    Returns:
        Created image
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
    
    bpy.ops.paint.add_texture_paint_slot(
        type=slot_type,
        width=width,
        height=height,
        color=color,
        name=name
    )
    
    return bpy.data.images.get(name)


def set_paint_brush(brush_name: str) -> None:
    """
    Set active paint brush.
    
    Args:
        brush_name: 'TexDraw', 'Soften', 'Smear', 'Clone', 'Fill', 'Mask'
    """
    brush = bpy.data.brushes.get(brush_name)
    if brush:
        bpy.context.tool_settings.image_paint.brush = brush


def set_brush_color(color: tuple = (1.0, 1.0, 1.0)) -> None:
    """Set brush primary color."""
    brush = bpy.context.tool_settings.image_paint.brush
    if brush:
        brush.color = color


def set_brush_secondary_color(color: tuple = (0.0, 0.0, 0.0)) -> None:
    """Set brush secondary color."""
    brush = bpy.context.tool_settings.image_paint.brush
    if brush:
        brush.secondary_color = color


def configure_paint_brush(
    strength: float = 1.0,
    radius: int = 50,
    blend_mode: str = 'MIX',
    use_pressure: bool = True
) -> None:
    """
    Configure paint brush settings.
    
    Args:
        strength: Brush strength
        radius: Brush size
        blend_mode: 'MIX', 'DARKEN', 'MULTIPLY', 'LIGHTEN', 'SCREEN', 'ADD', 'SUB'
        use_pressure: Enable pressure sensitivity
    """
    brush = bpy.context.tool_settings.image_paint.brush
    if brush:
        brush.strength = strength
        brush.size = radius
        brush.blend = blend_mode
        brush.use_pressure_strength = use_pressure


def enable_stencil_mapping(
    image_path: str,
    scale: float = 1.0
) -> None:
    """Enable stencil brush mapping."""
    img = bpy.data.images.load(image_path)
    brush = bpy.context.tool_settings.image_paint.brush
    if brush:
        brush.texture_slot.map_mode = 'STENCIL'
        tex = bpy.data.textures.new("StencilTex", 'IMAGE')
        tex.image = img
        brush.texture = tex


def save_painted_image(
    image: bpy.types.Image,
    filepath: str = None
) -> None:
    """
    Save painted image to file.
    
    Args:
        image: Image to save
        filepath: Path (uses image path if None)
    """
    if filepath:
        image.filepath_raw = filepath
    image.save()


def pack_painted_images() -> None:
    """Pack all painted images into blend file."""
    for img in bpy.data.images:
        if img.is_dirty:
            img.pack()


def bake_texture(
    obj: bpy.types.Object,
    bake_type: str = 'DIFFUSE',
    width: int = 1024,
    height: int = 1024,
    margin: int = 16,
    output_path: str = None
) -> bpy.types.Image:
    """
    Bake texture from materials.
    
    Args:
        obj: Target object
        bake_type: 'DIFFUSE', 'ROUGHNESS', 'NORMAL', 'AO', 'COMBINED'
        width: Output width
        height: Output height
        margin: UV margin pixels
        output_path: Save path
    
    Returns:
        Baked image
    """
    # Create target image
    img_name = f"{obj.name}_{bake_type}"
    img = bpy.data.images.new(img_name, width, height)
    
    # Set up material for baking
    for mat_slot in obj.material_slots:
        if mat_slot.material and mat_slot.material.use_nodes:
            nodes = mat_slot.material.node_tree.nodes
            
            # Add image texture node
            tex_node = nodes.new('ShaderNodeTexImage')
            tex_node.image = img
            tex_node.select = True
            nodes.active = tex_node
    
    # Configure bake settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.bake.margin = margin
    
    # Select object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Bake
    bpy.ops.object.bake(type=bake_type)
    
    if output_path:
        img.filepath_raw = output_path
        img.save()
    
    return img


def set_paint_canvas(image: bpy.types.Image) -> None:
    """Set active painting canvas."""
    ts = bpy.context.tool_settings.image_paint
    ts.canvas = image
    ts.mode = 'IMAGE'


def toggle_symmetry(
    x: bool = True,
    y: bool = False,
    z: bool = False
) -> None:
    """Toggle paint symmetry."""
    paint = bpy.context.tool_settings.image_paint
    paint.use_symmetry_x = x
    paint.use_symmetry_y = y
    paint.use_symmetry_z = z
