"""
{
  "title": "Create Outdoor Sun Lighting",
  "category": "lighting",
  "subcategory": "outdoor",
  "tags": ["sun", "outdoor", "daylight", "sky", "shadows", "atmosphere"],
  "difficulty": "beginner",
  "description": "Creates realistic outdoor lighting with sun, sky, and optional HDRI environment.",
  "blender_version": "3.0+",
  "estimated_objects": 2
}
"""
import bpy
import math


def create_outdoor_sun_lighting(
    sun_angle: float = 45,
    sun_rotation: float = 30,
    sun_energy: float = 5.0,
    sun_color: tuple = (1.0, 0.98, 0.95),
    sky_type: str = 'NISHITA',
    time_of_day: str = 'NOON',
    name_prefix: str = "Outdoor"
) -> dict:
    """
    Create realistic outdoor sun lighting.
    
    Args:
        sun_angle: Sun elevation angle in degrees (0 = horizon, 90 = overhead)
        sun_rotation: Sun horizontal rotation in degrees
        sun_energy: Sun intensity
        sun_color: RGB sun color
        sky_type: 'NISHITA' (physical sky), 'PREETHAM', 'HOSEK_WILKIE', 'COLOR'
        time_of_day: 'DAWN', 'MORNING', 'NOON', 'AFTERNOON', 'SUNSET', 'CUSTOM'
        name_prefix: Prefix for created objects
    
    Returns:
        Dictionary with 'sun' and 'world' keys
    
    Example:
        >>> lights = create_outdoor_sun_lighting(time_of_day='SUNSET')
    """
    result = {}
    
    # Time of day presets
    presets = {
        'DAWN': {'angle': 5, 'energy': 2.0, 'color': (1.0, 0.7, 0.5)},
        'MORNING': {'angle': 25, 'energy': 4.0, 'color': (1.0, 0.95, 0.9)},
        'NOON': {'angle': 70, 'energy': 6.0, 'color': (1.0, 1.0, 1.0)},
        'AFTERNOON': {'angle': 45, 'energy': 5.0, 'color': (1.0, 0.98, 0.95)},
        'SUNSET': {'angle': 10, 'energy': 3.0, 'color': (1.0, 0.6, 0.3)},
    }
    
    if time_of_day in presets:
        preset = presets[time_of_day]
        sun_angle = preset['angle']
        sun_energy = preset['energy']
        sun_color = preset['color']
    
    # === CREATE SUN ===
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.active_object
    sun.name = f"{name_prefix}_Sun"
    
    # Calculate sun direction from angles
    elevation_rad = math.radians(sun_angle)
    rotation_rad = math.radians(sun_rotation)
    
    sun.rotation_euler = (
        math.pi/2 - elevation_rad,  # X: pitch (elevation)
        0,                           # Y
        rotation_rad                 # Z: horizontal rotation
    )
    
    sun.data.energy = sun_energy
    sun.data.color = sun_color
    sun.data.angle = 0.009  # Soft shadows (angular diameter of sun)
    
    result['sun'] = sun
    
    # === CREATE SKY ===
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new(f"{name_prefix}_World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    if sky_type == 'NISHITA':
        # Physical sky simulation
        sky_texture = nodes.new('ShaderNodeTexSky')
        sky_texture.sky_type = 'NISHITA'
        sky_texture.sun_elevation = math.radians(sun_angle)
        sky_texture.sun_rotation = math.radians(sun_rotation)
        sky_texture.altitude = 0
        sky_texture.air_density = 1.0
        sky_texture.dust_density = 1.0
        sky_texture.ozone_density = 1.0
        
        # Adjust for time of day
        if time_of_day == 'SUNSET' or time_of_day == 'DAWN':
            sky_texture.air_density = 1.5
            sky_texture.dust_density = 2.0
        
        background = nodes.new('ShaderNodeBackground')
        background.inputs['Strength'].default_value = 1.0
        
        output = nodes.new('ShaderNodeOutputWorld')
        
        links.new(sky_texture.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
    elif sky_type == 'COLOR':
        # Simple gradient sky
        background = nodes.new('ShaderNodeBackground')
        
        if time_of_day == 'SUNSET':
            background.inputs['Color'].default_value = (0.8, 0.4, 0.3, 1.0)
        elif time_of_day == 'DAWN':
            background.inputs['Color'].default_value = (0.6, 0.3, 0.4, 1.0)
        else:
            background.inputs['Color'].default_value = (0.4, 0.6, 0.9, 1.0)
        
        background.inputs['Strength'].default_value = 0.5
        
        output = nodes.new('ShaderNodeOutputWorld')
        links.new(background.outputs['Background'], output.inputs['Surface'])
    
    result['world'] = world
    
    return result


def create_golden_hour_lighting(
    direction: float = 180,
    name_prefix: str = "GoldenHour"
) -> dict:
    """
    Create golden hour (sunset/sunrise) lighting.
    
    Args:
        direction: Sun direction (180 = behind camera)
        name_prefix: Prefix for objects
    
    Returns:
        Dictionary with lighting objects
    """
    return create_outdoor_sun_lighting(
        sun_angle=15,
        sun_rotation=direction,
        sun_energy=3.5,
        sun_color=(1.0, 0.65, 0.35),
        sky_type='NISHITA',
        time_of_day='SUNSET',
        name_prefix=name_prefix
    )


def create_overcast_lighting(
    brightness: float = 3.0,
    name_prefix: str = "Overcast"
) -> dict:
    """
    Create overcast/cloudy day lighting.
    
    Args:
        brightness: Overall scene brightness
        name_prefix: Prefix for objects
    
    Returns:
        Dictionary with lighting objects
    """
    result = {}
    
    # Large soft area light from above (simulating diffused sky)
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 20))
    sky_light = bpy.context.active_object
    sky_light.name = f"{name_prefix}_SkyLight"
    sky_light.data.shape = 'DISK'
    sky_light.data.size = 50
    sky_light.data.energy = brightness * 5000
    sky_light.data.color = (0.9, 0.95, 1.0)
    sky_light.rotation_euler = (0, 0, 0)
    
    result['sky_light'] = sky_light
    
    # Soft fill from horizon
    bpy.ops.object.light_add(type='AREA', location=(0, -20, 5))
    fill = bpy.context.active_object
    fill.name = f"{name_prefix}_Fill"
    fill.data.shape = 'RECTANGLE'
    fill.data.size = 30
    fill.data.size_y = 10
    fill.data.energy = brightness * 1000
    fill.data.color = (0.8, 0.85, 0.9)
    fill.rotation_euler = (math.radians(80), 0, 0)
    
    result['fill'] = fill
    
    # Gray sky
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new(f"{name_prefix}_World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    background = nodes.new('ShaderNodeBackground')
    background.inputs['Color'].default_value = (0.6, 0.65, 0.7, 1.0)
    background.inputs['Strength'].default_value = 0.3
    
    output = nodes.new('ShaderNodeOutputWorld')
    links.new(background.outputs['Background'], output.inputs['Surface'])
    
    result['world'] = world
    
    return result


# Standalone execution
if __name__ == "__main__":
    # Create noon lighting
    lighting = create_outdoor_sun_lighting(time_of_day='NOON')
    print(f"Created outdoor lighting: {list(lighting.keys())}")
