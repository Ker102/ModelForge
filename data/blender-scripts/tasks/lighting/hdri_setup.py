"""
{
  "title": "HDRI Lighting Setup",
  "category": "lighting",
  "subcategory": "environment",
  "tags": ["hdri", "environment", "lighting", "world", "background"],
  "difficulty": "beginner",
  "description": "Sets up HDRI environment lighting for realistic illumination.",
  "blender_version": "3.0+",
  "estimated_objects": 0
}
"""
import bpy
import math


def setup_hdri_lighting(
    hdri_path: str,
    strength: float = 1.0,
    rotation: float = 0,
    background_strength: float = None
) -> dict:
    """
    Set up HDRI environment lighting.
    
    Args:
        hdri_path: Path to HDRI image file
        strength: Light intensity
        rotation: Z rotation in degrees
        background_strength: Separate background strength (uses strength if None)
    
    Returns:
        Dictionary with world and nodes
    """
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    nodes.clear()
    
    # Environment texture
    env_tex = nodes.new('ShaderNodeTexEnvironment')
    env_tex.location = (-600, 300)
    env_tex.image = bpy.data.images.load(hdri_path)
    
    # Mapping for rotation
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-800, 300)
    mapping.inputs['Rotation'].default_value[2] = math.radians(rotation)
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1000, 300)
    
    # Background shader
    background = nodes.new('ShaderNodeBackground')
    background.location = (-200, 300)
    background.inputs['Strength'].default_value = strength
    
    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (0, 300)
    
    # Connect
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
    links.new(env_tex.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], output.inputs['Surface'])
    
    return {
        'world': world,
        'env_texture': env_tex,
        'mapping': mapping,
        'background': background
    }


def setup_gradient_sky(
    sky_color: tuple = (0.4, 0.6, 0.9),
    horizon_color: tuple = (0.8, 0.85, 0.9),
    ground_color: tuple = (0.2, 0.2, 0.15),
    strength: float = 1.0
) -> dict:
    """
    Set up gradient sky background.
    
    Args:
        sky_color: RGB color at top
        horizon_color: RGB color at horizon
        ground_color: RGB color below horizon
        strength: Light strength
    
    Returns:
        Dictionary with world and nodes
    """
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    nodes.clear()
    
    # Texture coordinate
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    # Separate Z
    separate = nodes.new('ShaderNodeSeparateXYZ')
    separate.location = (-600, 0)
    
    # Color ramp for sky gradient
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-400, 0)
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (*ground_color, 1.0)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (*horizon_color, 1.0)
    
    # Add sky color stop
    sky_stop = ramp.color_ramp.elements.new(0.7)
    sky_stop.color = (*sky_color, 1.0)
    
    # Background
    background = nodes.new('ShaderNodeBackground')
    background.location = (-100, 0)
    background.inputs['Strength'].default_value = strength
    
    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (100, 0)
    
    links.new(tex_coord.outputs['Generated'], separate.inputs['Vector'])
    links.new(separate.outputs['Z'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], output.inputs['Surface'])
    
    return {'world': world, 'color_ramp': ramp}


def setup_physical_sky(
    sun_elevation: float = 45,
    sun_rotation: float = 0,
    turbidity: float = 2.0,
    strength: float = 1.0
) -> dict:
    """
    Set up physical sky simulation.
    
    Args:
        sun_elevation: Sun angle above horizon (degrees)
        sun_rotation: Sun compass direction (degrees)
        turbidity: Atmosphere haze (1-10)
        strength: Light strength
    
    Returns:
        Dictionary with world and sky texture
    """
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    nodes.clear()
    
    # Sky texture
    sky = nodes.new('ShaderNodeTexSky')
    sky.location = (-300, 0)
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(sun_elevation)
    sky.sun_rotation = math.radians(sun_rotation)
    sky.air_density = 1.0
    sky.dust_density = turbidity / 10
    sky.ozone_density = 1.0
    
    # Background
    background = nodes.new('ShaderNodeBackground')
    background.location = (0, 0)
    background.inputs['Strength'].default_value = strength
    
    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)
    
    links.new(sky.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], output.inputs['Surface'])
    
    return {'world': world, 'sky_texture': sky}


def set_world_color(color: tuple, strength: float = 1.0) -> None:
    """Set solid color world background."""
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    nodes.clear()
    
    background = nodes.new('ShaderNodeBackground')
    background.inputs['Color'].default_value = (*color, 1.0)
    background.inputs['Strength'].default_value = strength
    
    output = nodes.new('ShaderNodeOutputWorld')
    
    links.new(background.outputs['Background'], output.inputs['Surface'])


if __name__ == "__main__":
    # Set up a physical sky
    setup_physical_sky(sun_elevation=30, sun_rotation=45)
    print("Set up physical sky lighting")
