"""
{
  "title": "Lighting Utilities",
  "category": "lighting",
  "tags": ["light", "area", "point", "sun", "spot", "hdri", "world"],
  "description": "Functions for creating and configuring different types of lights in Blender scenes.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def add_point_light(
    location: tuple = (0, 0, 3),
    energy: float = 1000,
    color: tuple = (1.0, 1.0, 1.0),
    radius: float = 0.25,
    name: str = "PointLight"
) -> bpy.types.Object:
    """
    Add a point light to the scene.
    
    Args:
        location: XYZ position tuple
        energy: Light intensity in watts
        color: RGB color tuple (0.0-1.0)
        radius: Shadow softness radius
        name: Object name
    
    Returns:
        The created light object
    
    Example:
        >>> warm_light = add_point_light((2, -2, 4), 800, (1.0, 0.9, 0.8))
    """
    bpy.ops.object.light_add(type='POINT', location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    light.data.color = color
    light.data.shadow_soft_size = radius
    return light


def add_area_light(
    location: tuple = (0, 0, 3),
    rotation: tuple = (0, 0, 0),
    energy: float = 500,
    color: tuple = (1.0, 1.0, 1.0),
    size: float = 2.0,
    shape: str = 'RECTANGLE',
    size_y: float = None,
    name: str = "AreaLight"
) -> bpy.types.Object:
    """
    Add an area light - ideal for soft shadows and studio lighting.
    
    Args:
        location: XYZ position tuple
        rotation: XYZ rotation in degrees
        energy: Light intensity in watts
        color: RGB color tuple
        size: Width of the light
        shape: 'SQUARE', 'RECTANGLE', 'DISK', or 'ELLIPSE'
        size_y: Height (for RECTANGLE/ELLIPSE), defaults to size
        name: Object name
    
    Example:
        >>> key_light = add_area_light((5, -5, 6), (45, 0, 45), 1200, size=4)
    """
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.active_object
    light.name = name
    light.rotation_euler = tuple(math.radians(r) for r in rotation)
    light.data.energy = energy
    light.data.color = color
    light.data.shape = shape
    light.data.size = size
    if size_y is not None:
        light.data.size_y = size_y
    elif shape in ('RECTANGLE', 'ELLIPSE'):
        light.data.size_y = size * 0.6
    return light


def add_sun_light(
    rotation: tuple = (45, 0, 30),
    energy: float = 5,
    color: tuple = (1.0, 0.98, 0.95),
    angle: float = 0.01,
    name: str = "Sun"
) -> bpy.types.Object:
    """
    Add a sun light for outdoor scenes with parallel rays.
    
    Args:
        rotation: XYZ rotation in degrees (controls sun direction)
        energy: Light intensity
        color: RGB color tuple
        angle: Angular diameter for soft shadows (radians)
        name: Object name
    
    Example:
        >>> sun = add_sun_light((60, 0, -30), energy=8)
    """
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    light = bpy.context.active_object
    light.name = name
    light.rotation_euler = tuple(math.radians(r) for r in rotation)
    light.data.energy = energy
    light.data.color = color
    light.data.angle = angle
    return light


def add_spot_light(
    location: tuple = (0, 0, 5),
    rotation: tuple = (0, 0, 0),
    energy: float = 1000,
    color: tuple = (1.0, 1.0, 1.0),
    spot_size: float = 45,
    spot_blend: float = 0.15,
    radius: float = 0.1,
    name: str = "SpotLight"
) -> bpy.types.Object:
    """
    Add a spot light with cone-shaped illumination.
    
    Args:
        location: XYZ position tuple
        rotation: XYZ rotation in degrees
        energy: Light intensity in watts
        color: RGB color tuple
        spot_size: Cone angle in degrees
        spot_blend: Edge softness (0-1)
        radius: Shadow softness
        name: Object name
    
    Example:
        >>> stage_spot = add_spot_light((0, -5, 8), (60, 0, 0), 2000, spot_size=30)
    """
    bpy.ops.object.light_add(type='SPOT', location=location)
    light = bpy.context.active_object
    light.name = name
    light.rotation_euler = tuple(math.radians(r) for r in rotation)
    light.data.energy = energy
    light.data.color = color
    light.data.spot_size = math.radians(spot_size)
    light.data.spot_blend = spot_blend
    light.data.shadow_soft_size = radius
    return light


def set_world_hdri(hdri_path: str, strength: float = 1.0, rotation_z: float = 0) -> None:
    """
    Set up world environment with an HDRI image for realistic lighting.
    
    Args:
        hdri_path: File path to .hdr or .exr file
        strength: Environment light intensity
        rotation_z: Rotate environment horizontally (degrees)
    
    Example:
        >>> set_world_hdri("/path/to/studio.hdr", strength=1.5, rotation_z=90)
    """
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    # Create nodes
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    env_tex = nodes.new('ShaderNodeTexEnvironment')
    background = nodes.new('ShaderNodeBackground')
    output = nodes.new('ShaderNodeOutputWorld')
    
    # Set values
    mapping.inputs['Rotation'].default_value[2] = math.radians(rotation_z)
    env_tex.image = bpy.data.images.load(hdri_path)
    background.inputs['Strength'].default_value = strength
    
    # Link nodes
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
    links.new(env_tex.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], output.inputs['Surface'])


def set_world_color(color: tuple = (0.05, 0.05, 0.05), strength: float = 1.0) -> None:
    """
    Set world background to a solid color.
    
    Args:
        color: RGB color tuple
        strength: Background intensity
    
    Example:
        >>> set_world_color((0.02, 0.02, 0.05))  # Dark blue background
    """
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    background = nodes.new('ShaderNodeBackground')
    output = nodes.new('ShaderNodeOutputWorld')
    
    background.inputs['Color'].default_value = (*color, 1.0)
    background.inputs['Strength'].default_value = strength
    
    links.new(background.outputs['Background'], output.inputs['Surface'])
