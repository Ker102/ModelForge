"""
{
  "title": "World Settings Utilities",
  "category": "environment",
  "tags": ["world", "sky", "environment", "background", "atmosphere"],
  "description": "Functions for configuring world/environment settings.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def set_background_color(color: tuple = (0.05, 0.05, 0.05)) -> None:
    """Set solid background color."""
    world = _ensure_world()
    world.use_nodes = True
    nodes = world.node_tree.nodes
    
    bg = nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (*color, 1.0)
        bg.inputs['Strength'].default_value = 1.0


def set_hdri_background(
    hdri_path: str,
    strength: float = 1.0,
    rotation: float = 0
) -> None:
    """
    Set HDRI environment map.
    
    Args:
        hdri_path: Path to HDRI image
        strength: Environment strength
        rotation: Z rotation in degrees
    """
    world = _ensure_world()
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    nodes.clear()
    
    # Texture coordinate
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    # Mapping for rotation
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-400, 0)
    mapping.inputs['Rotation'].default_value[2] = math.radians(rotation)
    
    # Environment texture
    env_tex = nodes.new('ShaderNodeTexEnvironment')
    env_tex.location = (-200, 0)
    env_tex.image = bpy.data.images.load(hdri_path)
    
    # Background
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Strength'].default_value = strength
    
    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)
    
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
    links.new(env_tex.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])


def set_sky_texture(
    sun_elevation: float = 45,
    sun_rotation: float = 0,
    turbidity: float = 2.2,
    strength: float = 1.0
) -> None:
    """
    Set procedural sky texture.
    
    Args:
        sun_elevation: Sun angle above horizon
        sun_rotation: Sun horizontal rotation
        turbidity: Atmospheric haze
        strength: Sky brightness
    """
    world = _ensure_world()
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    nodes.clear()
    
    # Sky texture
    sky = nodes.new('ShaderNodeTexSky')
    sky.location = (-200, 0)
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(sun_elevation)
    sky.sun_rotation = math.radians(sun_rotation)
    sky.air_density = turbidity
    
    # Background
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Strength'].default_value = strength
    
    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)
    
    links.new(sky.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])


def set_gradient_background(
    top_color: tuple = (0.05, 0.1, 0.2),
    bottom_color: tuple = (0.4, 0.35, 0.3),
    blend_type: str = 'LINEAR'
) -> None:
    """
    Set gradient background.
    
    Args:
        top_color: RGB color at top
        bottom_color: RGB color at bottom
        blend_type: 'LINEAR', 'QUADRATIC', 'EASING'
    """
    world = _ensure_world()
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    nodes.clear()
    
    # Texture coordinate
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-400, 0)
    
    # Separate XYZ to get Z
    separate = nodes.new('ShaderNodeSeparateXYZ')
    separate.location = (-200, 0)
    
    # Color ramp
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 0)
    ramp.color_ramp.elements[0].color = (*bottom_color, 1.0)
    ramp.color_ramp.elements[1].color = (*top_color, 1.0)
    
    if blend_type == 'QUADRATIC':
        ramp.color_ramp.interpolation = 'EASE'
    
    # Background
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (200, 0)
    
    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (400, 0)
    
    links.new(tex_coord.outputs['Generated'], separate.inputs['Vector'])
    links.new(separate.outputs['Z'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])


def _ensure_world() -> bpy.types.World:
    """Ensure scene has a world."""
    if not bpy.context.scene.world:
        bpy.context.scene.world = bpy.data.worlds.new("World")
    return bpy.context.scene.world


def set_ambient_occlusion(
    enabled: bool = True,
    distance: float = 1.0,
    factor: float = 1.0
) -> None:
    """Configure world ambient occlusion."""
    world = _ensure_world()
    world.light_settings.use_ambient_occlusion = enabled
    world.light_settings.ao_factor = factor
    world.light_settings.distance = distance


if __name__ == "__main__":
    set_sky_texture(sun_elevation=30)
    print("Set sky texture")
