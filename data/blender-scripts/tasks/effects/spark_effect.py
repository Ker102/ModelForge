"""
{
  "title": "Spark Effect Generator",
  "category": "effects",
  "subcategory": "particles",
  "tags": ["spark", "particles", "fire", "metal", "welding", "effect"],
  "difficulty": "intermediate",
  "description": "Generates spark particle effects for impacts and welding.",
  "blender_version": "3.0+",
  "estimated_objects": 2
}
"""
import bpy
import math


def create_spark_emitter(
    location: tuple = (0, 0, 0),
    direction: tuple = (0, 0, 1),
    spark_count: int = 200,
    lifetime: int = 30,
    velocity: float = 5.0,
    spread: float = 45,
    color: tuple = (1.0, 0.6, 0.1),
    name: str = "Sparks"
) -> dict:
    """
    Create spark particle emitter.
    
    Args:
        location: Emission point
        direction: Main direction of sparks
        spark_count: Number of particles
        lifetime: Particle lifetime in frames
        velocity: Initial velocity
        spread: Cone spread angle
        color: RGB spark color
        name: Object name
    
    Returns:
        Dictionary with emitter parts
    """
    result = {}
    
    # Emitter object
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.02,
        location=location
    )
    emitter = bpy.context.active_object
    emitter.name = name
    emitter.hide_render = True
    result['emitter'] = emitter
    
    # Particle system
    bpy.ops.object.particle_system_add()
    psys = emitter.particle_systems[0]
    psys.name = f"{name}_Particles"
    
    settings = psys.settings
    settings.name = f"{name}_Settings"
    settings.type = 'EMITTER'
    settings.count = spark_count
    settings.lifetime = lifetime
    settings.frame_start = 1
    settings.frame_end = 10
    
    # Velocity
    settings.normal_factor = velocity
    settings.factor_random = velocity * 0.5
    settings.tangent_factor = velocity * 0.3
    
    # Physics
    settings.effector_weights.gravity = 1.0
    settings.mass = 0.001
    settings.particle_size = 0.005
    settings.size_random = 0.5
    
    # Render as halo
    settings.render_type = 'HALO'
    
    result['particle_system'] = psys
    
    # Spark material
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 20.0
    emitter.data.materials.append(mat)
    
    result['material'] = mat
    
    # Point light for glow
    bpy.ops.object.light_add(type='POINT', location=location)
    light = bpy.context.active_object
    light.name = f"{name}_Light"
    light.data.energy = 50
    light.data.color = color
    light.data.shadow_soft_size = 0.1
    result['light'] = light
    
    return result


def create_impact_sparks(
    location: tuple = (0, 0, 0),
    surface_normal: tuple = (0, 0, 1),
    intensity: float = 1.0,
    name: str = "ImpactSparks"
) -> dict:
    """
    Create sparks from an impact point.
    
    Args:
        location: Impact location
        surface_normal: Surface normal direction
        intensity: Effect intensity multiplier
        name: Object name
    """
    return create_spark_emitter(
        location=location,
        direction=surface_normal,
        spark_count=int(150 * intensity),
        lifetime=20,
        velocity=8.0 * intensity,
        spread=60,
        color=(1.0, 0.7, 0.2),
        name=name
    )


def create_welding_sparks(
    location: tuple = (0, 0, 0),
    name: str = "WeldingSparks"
) -> dict:
    """Create continuous welding spark stream."""
    result = create_spark_emitter(
        location=location,
        spark_count=500,
        lifetime=15,
        velocity=3.0,
        spread=30,
        color=(1.0, 0.9, 0.5),
        name=name
    )
    
    # Make continuous
    settings = result['particle_system'].settings
    settings.frame_end = 250
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_spark_emitter(location=(0, 0, 0))
    create_impact_sparks(location=(1, 0, 0))
    
    print("Created spark effects")
