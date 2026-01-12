"""
{
  "title": "Rain Effect Generator",
  "category": "effects",
  "subcategory": "weather",
  "tags": ["rain", "weather", "particles", "droplets", "environment"],
  "difficulty": "intermediate",
  "description": "Creates rain particle effect with optional splashes.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math


def create_rain_effect(
    area_size: tuple = (10, 10),
    height: float = 10,
    density: int = 2000,
    speed: float = 1.0,
    angle: float = 0,
    with_splashes: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Rain"
) -> dict:
    """
    Create a rain particle effect.
    
    Args:
        area_size: XY area covered by rain
        height: Rain fall height
        density: Number of rain particles
        speed: Fall speed multiplier
        angle: Wind angle in degrees
        with_splashes: Add splash particles on ground
        location: Center position
        name: Effect name
    
    Returns:
        Dictionary with rain components
    """
    result = {}
    
    # === RAIN EMITTER ===
    bpy.ops.mesh.primitive_plane_add(
        size=1,
        location=(location[0], location[1], location[2] + height)
    )
    emitter = bpy.context.active_object
    emitter.name = f"{name}_Emitter"
    emitter.scale = (area_size[0]/2, area_size[1]/2, 1)
    bpy.ops.object.transform_apply(scale=True)
    emitter.hide_render = True
    
    # Add particle system
    bpy.ops.object.particle_system_add()
    ps = emitter.particle_systems[-1]
    ps.name = f"{name}_Particles"
    settings = ps.settings
    settings.name = f"{name}_Settings"
    
    # Rain settings
    settings.count = density
    settings.lifetime = int(height / (10 * speed) * 24)  # Frames to fall
    settings.emit_from = 'FACE'
    settings.use_emit_random = True
    
    # Physics
    settings.normal_factor = 0
    settings.object_align_factor = (
        math.sin(math.radians(angle)) * 0.2,  # Wind
        0,
        -10 * speed  # Downward
    )
    settings.factor_random = 0.1
    
    # Render as lines (streaks)
    settings.render_type = 'LINE'
    settings.line_length_tail = 2.0
    settings.line_length_head = 0.0
    
    # Material for rain
    rain_mat = bpy.data.materials.new(f"{name}_Mat")
    rain_mat.use_nodes = True
    bsdf = rain_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.8, 0.85, 0.9, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.1
    bsdf.inputs['Transmission Weight'].default_value = 0.5
    
    settings.material = 1
    if not emitter.data.materials:
        emitter.data.materials.append(rain_mat)
    
    result['emitter'] = emitter
    result['particle_system'] = ps
    
    # === SPLASH PARTICLES ===
    if with_splashes:
        splash = _create_rain_splashes(area_size, density // 4, location, name)
        result['splashes'] = splash
    
    return result


def _create_rain_splashes(
    area_size: tuple,
    count: int,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create rain splash particles on ground."""
    # Ground plane emitter
    bpy.ops.mesh.primitive_plane_add(
        size=1,
        location=(location[0], location[1], location[2] + 0.01)
    )
    splash_emitter = bpy.context.active_object
    splash_emitter.name = f"{name}_SplashEmitter"
    splash_emitter.scale = (area_size[0]/2, area_size[1]/2, 1)
    bpy.ops.object.transform_apply(scale=True)
    splash_emitter.hide_render = True
    
    bpy.ops.object.particle_system_add()
    ps = splash_emitter.particle_systems[-1]
    settings = ps.settings
    
    settings.count = count
    settings.lifetime = 5
    settings.emit_from = 'FACE'
    settings.use_emit_random = True
    
    # Splash upward
    settings.normal_factor = 2.0
    settings.factor_random = 0.5
    
    settings.render_type = 'HALO'
    settings.particle_size = 0.01
    
    return splash_emitter


def create_snow_effect(
    area_size: tuple = (10, 10),
    height: float = 8,
    density: int = 1000,
    flake_size: float = 0.02,
    location: tuple = (0, 0, 0),
    name: str = "Snow"
) -> dict:
    """
    Create a snow particle effect.
    
    Args:
        area_size: XY area covered
        height: Fall height
        density: Number of snowflakes
        flake_size: Size of flakes
        location: Center position
        name: Effect name
    
    Returns:
        Dictionary with snow components
    """
    result = {}
    
    bpy.ops.mesh.primitive_plane_add(
        size=1,
        location=(location[0], location[1], location[2] + height)
    )
    emitter = bpy.context.active_object
    emitter.name = f"{name}_Emitter"
    emitter.scale = (area_size[0]/2, area_size[1]/2, 1)
    bpy.ops.object.transform_apply(scale=True)
    emitter.hide_render = True
    
    bpy.ops.object.particle_system_add()
    ps = emitter.particle_systems[-1]
    settings = ps.settings
    
    # Snow falls slower, drifts more
    settings.count = density
    settings.lifetime = int(height / 2 * 24)  # Slower fall
    settings.emit_from = 'FACE'
    
    settings.normal_factor = 0
    settings.object_align_factor = (0, 0, -2)  # Slow fall
    settings.brownian_factor = 0.3  # Drift
    settings.factor_random = 0.5
    
    # Render as spheres
    settings.render_type = 'HALO'
    settings.particle_size = flake_size
    settings.size_random = 0.5
    
    result['emitter'] = emitter
    result['particle_system'] = ps
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_rain_effect(area_size=(8, 8), density=1500)
    create_snow_effect(area_size=(8, 8), location=(12, 0, 0), density=800)
    
    print("Created rain and snow effects")
