"""
{
  "title": "3D Text Utilities",
  "category": "text",
  "tags": ["text", "3d", "font", "typography", "title", "extrude"],
  "description": "Functions for creating and styling 3D text objects.",
  "blender_version": "3.0+"
}
"""
import bpy


def create_3d_text(
    text: str = "Text",
    location: tuple = (0, 0, 0),
    size: float = 1.0,
    extrude: float = 0.1,
    font: str = None,
    name: str = "Text"
) -> bpy.types.Object:
    """
    Create a 3D text object.
    
    Args:
        text: Text content
        location: Position
        size: Text size
        extrude: 3D depth
        font: Path to font file (uses default if None)
        name: Object name
    
    Returns:
        The created text object
    """
    bpy.ops.object.text_add(location=location)
    text_obj = bpy.context.active_object
    text_obj.name = name
    
    text_obj.data.body = text
    text_obj.data.size = size
    text_obj.data.extrude = extrude
    
    if font and font.endswith(('.ttf', '.otf')):
        text_obj.data.font = bpy.data.fonts.load(font)
    
    return text_obj


def set_text_alignment(
    text_obj: bpy.types.Object,
    horizontal: str = 'CENTER',
    vertical: str = 'CENTER'
) -> None:
    """
    Set text alignment.
    
    Args:
        text_obj: Text object
        horizontal: 'LEFT', 'CENTER', 'RIGHT', 'JUSTIFY', 'FLUSH'
        vertical: 'TOP', 'CENTER', 'BOTTOM'
    """
    text_obj.data.align_x = horizontal
    text_obj.data.align_y = vertical


def set_text_bevel(
    text_obj: bpy.types.Object,
    depth: float = 0.02,
    resolution: int = 4
) -> None:
    """Add bevel to text edges."""
    text_obj.data.bevel_depth = depth
    text_obj.data.bevel_resolution = resolution


def set_text_spacing(
    text_obj: bpy.types.Object,
    character: float = 1.0,
    word: float = 1.0,
    line: float = 1.0
) -> None:
    """Set text spacing."""
    text_obj.data.space_character = character
    text_obj.data.space_word = word
    text_obj.data.space_line = line


def text_to_mesh(text_obj: bpy.types.Object) -> bpy.types.Object:
    """Convert text to mesh."""
    bpy.context.view_layer.objects.active = text_obj
    text_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return bpy.context.active_object


def text_to_curve(text_obj: bpy.types.Object) -> bpy.types.Object:
    """Convert text to curve."""
    bpy.context.view_layer.objects.active = text_obj
    text_obj.select_set(True)
    bpy.ops.object.convert(target='CURVE')
    return bpy.context.active_object


def create_title_text(
    text: str,
    style: str = 'BOLD',
    color: tuple = (1, 1, 1),
    location: tuple = (0, 0, 0)
) -> bpy.types.Object:
    """
    Create styled title text with material.
    
    Args:
        text: Title content
        style: 'BOLD', 'OUTLINE', 'SHADOW'
        color: RGB color
        location: Position
    
    Returns:
        Text object with material
    """
    if style == 'BOLD':
        extrude, bevel = 0.15, 0.02
    elif style == 'OUTLINE':
        extrude, bevel = 0.02, 0.01
    else:
        extrude, bevel = 0.1, 0.01
    
    text_obj = create_3d_text(
        text=text,
        location=location,
        extrude=extrude,
        name=f"Title_{text[:10]}"
    )
    
    set_text_bevel(text_obj, depth=bevel, resolution=3)
    set_text_alignment(text_obj, 'CENTER', 'CENTER')
    
    # Add material
    mat = bpy.data.materials.new(f"TitleMat_{text[:10]}")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.3
    bsdf.inputs['Roughness'].default_value = 0.4
    text_obj.data.materials.append(mat)
    
    return text_obj
