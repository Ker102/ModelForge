"""
{
  "title": "NPR/Toon Rendering Setup",
  "category": "rendering",
  "subcategory": "stylized",
  "tags": ["npr", "toon", "cartoon", "stylized", "outline", "freestyle"],
  "difficulty": "intermediate",
  "description": "Sets up non-photorealistic/toon rendering with outlines.",
  "blender_version": "3.0+",
  "estimated_objects": 0
}
"""
import bpy


def setup_toon_shading(
    obj: bpy.types.Object,
    base_color: tuple = (1, 0.5, 0.3),
    shadow_color: tuple = (0.4, 0.2, 0.1),
    steps: int = 3,
    name: str = "ToonMat"
) -> bpy.types.Material:
    """
    Apply toon shading material to object.
    
    Args:
        obj: Target object
        base_color: RGB main color
        shadow_color: RGB shadow color
        steps: Cell shading steps
        name: Material name
    
    Returns:
        The created material
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    # Shader to RGB for Eevee toon effect
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.location = (-400, 0)
    diffuse.inputs['Color'].default_value = (*base_color, 1.0)
    
    shader_to_rgb = nodes.new('ShaderNodeShaderToRGB')
    shader_to_rgb.location = (-200, 0)
    
    # Color ramp for cel shading
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 0)
    ramp.color_ramp.interpolation = 'CONSTANT'
    
    # Configure steps
    ramp.color_ramp.elements[0].position = 0
    ramp.color_ramp.elements[0].color = (*shadow_color, 1.0)
    
    if steps >= 2:
        ramp.color_ramp.elements[1].position = 0.5
        ramp.color_ramp.elements[1].color = (*base_color, 1.0)
    
    if steps >= 3:
        elem = ramp.color_ramp.elements.new(0.8)
        highlight = tuple(min(1, c * 1.3) for c in base_color)
        elem.color = (*highlight, 1.0)
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    links.new(diffuse.outputs['BSDF'], shader_to_rgb.inputs['Shader'])
    links.new(shader_to_rgb.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], output.inputs['Surface'])
    
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    
    return mat


def enable_freestyle_outlines(
    line_thickness: float = 2.0,
    line_color: tuple = (0, 0, 0)
) -> None:
    """
    Enable Freestyle for outline rendering.
    
    Args:
        line_thickness: Line thickness in pixels
        line_color: RGB line color
    """
    bpy.context.scene.render.use_freestyle = True
    
    view_layer = bpy.context.view_layer
    view_layer.freestyle_settings.as_render_pass = True
    
    # Configure line set
    if not view_layer.freestyle_settings.linesets:
        view_layer.freestyle_settings.linesets.new("OutlineSet")
    
    lineset = view_layer.freestyle_settings.linesets[0]
    lineset.select_silhouette = True
    lineset.select_border = True
    lineset.select_crease = True
    lineset.select_edge_mark = False
    
    # Line style
    linestyle = lineset.linestyle
    linestyle.color = line_color
    linestyle.thickness = line_thickness


def setup_grease_pencil_outline(
    obj: bpy.types.Object,
    thickness: float = 50,
    color: tuple = (0, 0, 0),
    name: str = "GPOutline"
) -> bpy.types.Object:
    """
    Add Grease Pencil outline to object.
    
    Args:
        obj: Target object
        thickness: Outline thickness
        color: RGB outline color
        name: GP object name
    
    Returns:
        The Grease Pencil object
    """
    # Create GP object
    gp_data = bpy.data.grease_pencils.new(name)
    gp_obj = bpy.data.objects.new(name, gp_data)
    bpy.context.collection.objects.link(gp_obj)
    
    # Add layer
    layer = gp_data.layers.new("Outline")
    frame = layer.frames.new(1)
    
    # Line art modifier on GP
    mod = gp_obj.grease_pencil_modifiers.new("LineArt", 'GP_LINEART')
    mod.source_type = 'OBJECT'
    mod.source_object = obj
    mod.thickness = int(thickness)
    
    # Create material for outline
    gp_mat = bpy.data.materials.new(f"{name}_Mat")
    bpy.data.materials.create_gpencil_data(gp_mat)
    gp_mat.grease_pencil.color = (*color, 1.0)
    gp_data.materials.append(gp_mat)
    
    return gp_obj


def setup_eevee_for_toon() -> None:
    """Configure Eevee settings for toon rendering."""
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
    
    eevee = bpy.context.scene.eevee
    eevee.taa_render_samples = 32
    
    # Disable reflections/refractions for flat look
    eevee.use_ssr = False
    
    # Simple shadows
    eevee.shadow_cascade_size = '1024'


def create_toon_scene(
    target: bpy.types.Object = None,
    outline_thickness: float = 2.0
) -> None:
    """
    Set up complete toon rendering scene.
    
    Args:
        target: Object to apply toon shading
        outline_thickness: Outline size
    """
    setup_eevee_for_toon()
    enable_freestyle_outlines(line_thickness=outline_thickness)
    
    if target:
        setup_toon_shading(target)


if __name__ == "__main__":
    # Apply toon shading to active object
    obj = bpy.context.active_object
    if obj and obj.type == 'MESH':
        setup_toon_shading(obj, base_color=(0.9, 0.5, 0.2))
        enable_freestyle_outlines()
        print("Applied toon shading")
    else:
        print("Select a mesh object first")
