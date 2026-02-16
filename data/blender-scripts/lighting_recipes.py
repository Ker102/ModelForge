"""
{
  "title": "Professional Lighting Recipes for Blender",
  "category": "lighting",
  "tags": ["lighting", "three-point", "studio", "HDRI", "outdoor", "dramatic", "sunset", "rim", "fill", "key"],
  "description": "Professional lighting setups used in film, product visualization, and architectural rendering. Includes three-point lighting, studio setups, outdoor/sunset lighting, dramatic rim lighting, and HDRI environment lighting. Each recipe creates complete light rigs with correct energy, color temperature, and shadow settings.",
  "blender_version": "4.0+"
}
"""
import bpy
import math


# =============================================================================
# PROFESSIONAL LIGHTING RECIPES
# =============================================================================
#
# IMPORTANT PRINCIPLES:
# 1. Key light = main light source, strongest, casts primary shadows
# 2. Fill light = softer, opposite side from key, reduces harsh shadows
# 3. Rim/back light = behind subject, creates edge highlight/separation
# 4. Use color temperature to set mood: warm (orange/yellow) or cool (blue)
# 5. Energy values below are calibrated for Material Preview mode
# 6. For Cycles renders, multiply energy by ~10
#
# COLOR TEMPERATURE REFERENCE (RGB approximations):
#   Candle (1800K):        (1.0, 0.58, 0.16)
#   Warm tungsten (2700K): (1.0, 0.76, 0.46)
#   Warm white (3500K):    (1.0, 0.84, 0.66)
#   Neutral (4500K):       (1.0, 0.92, 0.82)
#   Daylight (5500K):      (1.0, 0.96, 0.92)
#   Overcast (6500K):      (0.87, 0.91, 1.0)
#   Blue sky (8000K):      (0.75, 0.83, 1.0)
# =============================================================================


def setup_three_point_lighting(
    target_location=(0, 0, 0),
    key_energy=800,
    fill_energy=300,
    rim_energy=500,
    key_color=(1.0, 0.95, 0.88),
    fill_color=(0.75, 0.83, 1.0),
    rim_color=(1.0, 1.0, 1.0),
    prefix="Light"
):
    """
    Classic three-point lighting setup used in film and photography.
    
    Creates:
    - Key light: Main light, 45° above and to the right
    - Fill light: Softer, opposite side, reduces shadows
    - Rim light: Behind subject, creates edge separation
    
    Args:
        target_location: Center point the lights aim at
        key_energy: Key light power (default 800 for EEVEE)
        fill_energy: Fill light power (typically 30-50% of key)
        rim_energy: Rim light power
        key_color: Key light color (warm daylight default)
        fill_color: Fill light color (cool blue default for contrast)
        rim_color: Rim light color
        prefix: Name prefix for light objects
    """
    tx, ty, tz = target_location
    
    # Key Light — 45° right, 45° above
    bpy.ops.object.light_add(type='AREA', location=(tx + 5, ty - 5, tz + 5))
    key = bpy.context.active_object
    key.name = f"{prefix}_Key"
    key.data.energy = key_energy
    key.data.color = key_color
    key.data.size = 2.0  # Soft shadows
    key.data.shadow_soft_size = 2.0
    # Point at target
    direction = (tx - key.location.x, ty - key.location.y, tz - key.location.z)
    key.rotation_euler = _look_at_rotation(key.location, target_location)
    
    # Fill Light — opposite side, lower, softer
    bpy.ops.object.light_add(type='AREA', location=(tx - 4, ty - 3, tz + 2))
    fill = bpy.context.active_object
    fill.name = f"{prefix}_Fill"
    fill.data.energy = fill_energy
    fill.data.color = fill_color
    fill.data.size = 4.0  # Very soft (larger = softer shadows)
    fill.rotation_euler = _look_at_rotation(fill.location, target_location)
    
    # Rim/Back Light — behind subject, high
    bpy.ops.object.light_add(type='SPOT', location=(tx + 1, ty + 6, tz + 4))
    rim = bpy.context.active_object
    rim.name = f"{prefix}_Rim"
    rim.data.energy = rim_energy
    rim.data.color = rim_color
    rim.data.spot_size = math.radians(60)
    rim.data.spot_blend = 0.5
    rim.rotation_euler = _look_at_rotation(rim.location, target_location)
    
    return key, fill, rim


def setup_studio_lighting(
    target_location=(0, 0, 0),
    energy_multiplier=1.0,
    warm=True,
    prefix="Studio"
):
    """
    Professional studio lighting for product visualization.
    
    Creates a 4-light setup:
    - Large key area light (top-right)
    - Large fill area light (top-left)
    - Ground bounce light (below, subtle)
    - Background light (behind, for backdrop illumination)
    
    Ideal for: product shots, character portraits, turntable renders
    """
    tx, ty, tz = target_location
    base_color = (1.0, 0.95, 0.88) if warm else (0.92, 0.95, 1.0)
    
    # Key — large overhead area
    bpy.ops.object.light_add(type='AREA', location=(tx + 4, ty - 3, tz + 6))
    key = bpy.context.active_object
    key.name = f"{prefix}_Key"
    key.data.energy = 600 * energy_multiplier
    key.data.color = base_color
    key.data.size = 5.0
    key.data.shape = 'RECTANGLE'
    key.data.size_y = 3.0
    key.rotation_euler = _look_at_rotation(key.location, target_location)
    
    # Fill — opposite side, very soft
    bpy.ops.object.light_add(type='AREA', location=(tx - 5, ty - 2, tz + 4))
    fill = bpy.context.active_object
    fill.name = f"{prefix}_Fill"
    fill.data.energy = 250 * energy_multiplier
    fill.data.color = base_color
    fill.data.size = 6.0
    fill.rotation_euler = _look_at_rotation(fill.location, target_location)
    
    # Ground bounce — subtle uplight
    bpy.ops.object.light_add(type='AREA', location=(tx, ty, tz - 1))
    bounce = bpy.context.active_object
    bounce.name = f"{prefix}_Bounce"
    bounce.data.energy = 100 * energy_multiplier
    bounce.data.color = (1.0, 1.0, 1.0)
    bounce.data.size = 8.0
    bounce.rotation_euler = (math.radians(180), 0, 0)
    
    # Background
    bpy.ops.object.light_add(type='AREA', location=(tx, ty + 5, tz + 2))
    bg = bpy.context.active_object
    bg.name = f"{prefix}_BG"
    bg.data.energy = 200 * energy_multiplier
    bg.data.color = base_color
    bg.data.size = 8.0
    bg.rotation_euler = _look_at_rotation(bg.location, (tx, ty, tz))
    
    return key, fill, bounce, bg


def setup_outdoor_sunlight(
    sun_direction=(0.5, -0.3, -0.8),
    sun_energy=3.0,
    sun_color=(1.0, 0.95, 0.85),
    sky_color=(0.3, 0.55, 0.9),
    prefix="Outdoor"
):
    """
    Outdoor daylight setup with sun and sky fill.
    
    Creates:
    - Sun light (directional, parallel rays)
    - Sky fill light (large area light from above, blue tint)
    
    Args:
        sun_direction: Direction vector for sunlight (negative Z = downward)
        sun_energy: Sun intensity (3–5 typical for EEVEE)
        sun_color: Sun color (warm for golden hour, neutral for midday)
        sky_color: Ambient sky color
    """
    # Sun light
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.active_object
    sun.name = f"{prefix}_Sun"
    sun.data.energy = sun_energy
    sun.data.color = sun_color
    sun.data.angle = math.radians(0.5)  # Small angle = sharp shadows
    
    # Aim the sun
    dx, dy, dz = sun_direction
    sun.rotation_euler = (
        math.atan2(math.sqrt(dx*dx + dy*dy), -dz),
        0,
        math.atan2(dx, -dy)
    )
    
    # Sky fill — large blue area light from above
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 15))
    sky = bpy.context.active_object
    sky.name = f"{prefix}_Sky"
    sky.data.energy = 100
    sky.data.color = sky_color
    sky.data.size = 20.0
    sky.rotation_euler = (math.radians(180), 0, 0)  # Point down
    
    return sun, sky


def setup_sunset_lighting(
    target_location=(0, 0, 0),
    prefix="Sunset"
):
    """
    Golden hour / sunset lighting with warm orange key and cool blue fill.
    
    Creates dramatic warm-cool contrast typical of sunset scenes.
    """
    tx, ty, tz = target_location
    
    # Low sun — warm orange, from the side
    bpy.ops.object.light_add(type='SUN', location=(10, -5, 2))
    sun = bpy.context.active_object
    sun.name = f"{prefix}_Sun"
    sun.data.energy = 4.0
    sun.data.color = (1.0, 0.6, 0.2)  # Warm orange
    sun.data.angle = math.radians(2.0)  # Slightly soft
    sun.rotation_euler = _look_at_rotation(sun.location, target_location)
    
    # Cool sky fill from above
    bpy.ops.object.light_add(type='AREA', location=(tx, ty, tz + 12))
    sky = bpy.context.active_object
    sky.name = f"{prefix}_Sky"
    sky.data.energy = 80
    sky.data.color = (0.5, 0.6, 1.0)  # Cool blue
    sky.data.size = 15.0
    sky.rotation_euler = (math.radians(180), 0, 0)
    
    return sun, sky


def setup_dramatic_lighting(
    target_location=(0, 0, 0),
    prefix="Dramatic"
):
    """
    High-contrast dramatic lighting for moody/cinematic scenes.
    
    Features: strong key from one side, almost no fill,
    strong colored rim light for edge separation.
    """
    tx, ty, tz = target_location
    
    # Key — harsh, single side
    bpy.ops.object.light_add(type='SPOT', location=(tx + 5, ty - 2, tz + 4))
    key = bpy.context.active_object
    key.name = f"{prefix}_Key"
    key.data.energy = 1200
    key.data.color = (1.0, 0.9, 0.75)
    key.data.spot_size = math.radians(45)
    key.data.spot_blend = 0.3
    key.rotation_euler = _look_at_rotation(key.location, target_location)
    
    # Rim — colored, strong
    bpy.ops.object.light_add(type='SPOT', location=(tx - 2, ty + 5, tz + 3))
    rim = bpy.context.active_object
    rim.name = f"{prefix}_Rim"
    rim.data.energy = 800
    rim.data.color = (0.3, 0.5, 1.0)  # Blue rim
    rim.data.spot_size = math.radians(50)
    rim.data.spot_blend = 0.4
    rim.rotation_euler = _look_at_rotation(rim.location, target_location)
    
    return key, rim


def set_world_hdri(hdri_path: str, strength: float = 1.0):
    """
    Set up an HDRI environment map for realistic lighting.
    
    Args:
        hdri_path: File path to .hdr or .exr file
        strength: Light intensity multiplier
    """
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    # Background node
    bg = nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = strength
    
    # Environment texture
    env_tex = nodes.new('ShaderNodeTexEnvironment')
    env_tex.image = bpy.data.images.load(hdri_path)
    
    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    
    # Optional: Texture coordinate for rotation
    coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    
    links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
    links.new(env_tex.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])
    
    return world


def set_world_color(color=(0.05, 0.05, 0.1), strength=1.0):
    """
    Set a solid-color world background.
    
    Common backgrounds:
        Dark studio:  (0.02, 0.02, 0.02)
        Space/night:  (0.002, 0.002, 0.01)
        Light studio: (0.8, 0.8, 0.82)
        Overcast sky:  (0.5, 0.55, 0.6)
        Navy blue:    (0.02, 0.03, 0.08)
    """
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    bg = nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (*color, 1.0)
    bg.inputs['Strength'].default_value = strength
    
    output = nodes.new('ShaderNodeOutputWorld')
    links.new(bg.outputs['Background'], output.inputs['Surface'])
    
    return world


# =============================================================================
# HELPER
# =============================================================================

def _look_at_rotation(source_location, target_location):
    """Calculate rotation euler for an object to look at a target point."""
    from mathutils import Vector, Matrix
    direction = Vector(target_location) - Vector(source_location)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    return rot_quat.to_euler()
