"""
{
  "title": "Particle Explosion Effect",
  "category": "effects",
  "subcategory": "particles",
  "tags": ["explosion", "particles", "vfx", "debris", "smoke", "fire", "effect"],
  "difficulty": "intermediate",
  "description": "Creates an explosion particle effect with debris, smoke, and fire elements.",
  "blender_version": "3.0+"
}
"""
import bpy
import math
import random


def create_explosion_effect(
    location: tuple = (0, 0, 0),
    intensity: float = 1.0,
    duration: int = 60,
    start_frame: int = 1,
    include_debris: bool = True,
    include_smoke: bool = True,
    include_fire: bool = True,
    name: str = "Explosion"
) -> dict:
    """
    Create a complete explosion particle effect.
    
    Args:
        location: Explosion center
        intensity: Scale multiplier for the effect
        duration: Effect duration in frames
        start_frame: Frame when explosion begins
        include_debris: Add debris particles
        include_smoke: Add smoke simulation
        include_fire: Add fire/glow elements
        name: Prefix for created objects
    
    Returns:
        Dictionary with all created objects and systems
    
    Example:
        >>> explosion = create_explosion_effect((0, 0, 1), intensity=1.5)
    """
    result = {}
    
    # Create emitter sphere
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.5 * intensity, location=location)
    emitter = bpy.context.active_object
    emitter.name = f"{name}_Emitter"
    emitter.hide_render = True
    result['emitter'] = emitter
    
    if include_debris:
        # Create debris particle system
        debris_system = _create_debris_particles(emitter, intensity, duration, start_frame, name)
        result['debris'] = debris_system
    
    if include_smoke:
        # Create smoke domain and emitter
        smoke_result = _create_smoke_effect(location, intensity, duration, start_frame, name)
        result['smoke'] = smoke_result
    
    if include_fire:
        # Create fire/glow sphere
        fire_result = _create_fire_glow(location, intensity, duration, start_frame, name)
        result['fire'] = fire_result
    
    # Set frame range
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = start_frame + duration
    
    return result


def _create_debris_particles(
    emitter: bpy.types.Object,
    intensity: float,
    duration: int,
    start_frame: int,
    name: str
) -> bpy.types.ParticleSystem:
    """Create debris particle system."""
    # Create debris object
    bpy.ops.mesh.primitive_cube_add(size=0.1 * intensity)
    debris_obj = bpy.context.active_object
    debris_obj.name = f"{name}_DebrisObject"
    debris_obj.hide_viewport = True
    debris_obj.hide_render = True
    
    # Add material
    debris_mat = bpy.data.materials.new(name=f"{name}_DebrisMat")
    bsdf = debris_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.15, 0.12, 0.1, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    debris_obj.data.materials.append(debris_mat)
    
    # Add particle system to emitter
    bpy.context.view_layer.objects.active = emitter
    bpy.ops.object.particle_system_add()
    particle_sys = emitter.particle_systems[-1]
    particle_sys.name = f"{name}_Debris"
    settings = particle_sys.settings
    
    # Configure as emission particles
    settings.type = 'EMITTER'
    settings.count = int(100 * intensity)
    settings.frame_start = start_frame
    settings.frame_end = start_frame + 5  # Quick burst
    settings.lifetime = duration - 5
    settings.lifetime_random = 0.2
    
    # Physics
    settings.physics_type = 'NEWTON'
    settings.mass = 1.0
    settings.normal_factor = 10.0 * intensity
    settings.factor_random = 0.5
    settings.drag_factor = 0.1
    
    # Gravity
    settings.effector_weights.gravity = 1.0
    
    # Rotation
    settings.use_rotations = True
    settings.rotation_mode = 'VEL'
    settings.angular_velocity_mode = 'RAND'
    settings.angular_velocity_factor = 5.0
    
    # Render as object
    settings.render_type = 'OBJECT'
    settings.instance_object = debris_obj
    settings.particle_size = 1.0
    settings.size_random = 0.8
    
    return particle_sys


def _create_smoke_effect(
    location: tuple,
    intensity: float,
    duration: int,
    start_frame: int,
    name: str
) -> dict:
    """Create smoke simulation domain and flow."""
    result = {}
    
    # Create domain
    domain_size = 5.0 * intensity
    bpy.ops.mesh.primitive_cube_add(size=domain_size, location=(location[0], location[1], location[2] + domain_size / 2))
    domain = bpy.context.active_object
    domain.name = f"{name}_SmokeDomain"
    
    # Add fluid modifier (domain)
    bpy.ops.object.modifier_add(type='FLUID')
    domain.modifiers["Fluid"].fluid_type = 'DOMAIN'
    domain_settings = domain.modifiers["Fluid"].domain_settings
    domain_settings.domain_type = 'GAS'
    domain_settings.resolution_max = 64
    domain_settings.use_noise = True
    domain_settings.noise_scale = 2
    
    # Cache settings
    domain_settings.cache_frame_start = start_frame
    domain_settings.cache_frame_end = start_frame + duration
    
    result['domain'] = domain
    
    # Create flow emitter
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.3 * intensity, location=location)
    flow = bpy.context.active_object
    flow.name = f"{name}_SmokeFlow"
    
    # Add fluid modifier (flow)
    bpy.ops.object.modifier_add(type='FLUID')
    flow.modifiers["Fluid"].fluid_type = 'FLOW'
    flow_settings = flow.modifiers["Fluid"].flow_settings
    flow_settings.flow_type = 'SMOKE'
    flow_settings.flow_behavior = 'INFLOW'
    flow_settings.use_initial_velocity = True
    flow_settings.velocity_factor = 5.0 * intensity
    
    # Animate flow
    flow_settings.keyframe_insert('flow', frame=start_frame)
    flow_settings.flow = True
    flow_settings.keyframe_insert('flow', frame=start_frame)
    flow_settings.flow = False
    flow_settings.keyframe_insert('flow', frame=start_frame + 10)
    
    result['flow'] = flow
    
    return result


def _create_fire_glow(
    location: tuple,
    intensity: float,
    duration: int,
    start_frame: int,
    name: str
) -> dict:
    """Create expanding fire/glow sphere."""
    result = {}
    
    # Create sphere
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.1, location=location)
    glow = bpy.context.active_object
    glow.name = f"{name}_FireGlow"
    
    # Emission material
    glow_mat = bpy.data.materials.new(name=f"{name}_FireMat")
    nodes = glow_mat.node_tree.nodes
    links = glow_mat.node_tree.links
    nodes.clear()
    
    # Create emission shader
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 0.3, 0.05, 1.0)
    emission.inputs['Strength'].default_value = 50.0 * intensity
    
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    glow.data.materials.append(glow_mat)
    result['object'] = glow
    
    # Animate scale (expand and fade)
    bpy.context.scene.frame_set(start_frame)
    glow.scale = (0.1, 0.1, 0.1)
    glow.keyframe_insert('scale', frame=start_frame)
    emission.inputs['Strength'].keyframe_insert('default_value', frame=start_frame)
    
    bpy.context.scene.frame_set(start_frame + 10)
    glow.scale = (2.0 * intensity, 2.0 * intensity, 2.0 * intensity)
    glow.keyframe_insert('scale', frame=start_frame + 10)
    
    emission.inputs['Strength'].default_value = 0.0
    emission.inputs['Strength'].keyframe_insert('default_value', frame=start_frame + 30)
    
    result['material'] = glow_mat
    
    return result


def create_shatter_effect(
    target_object: bpy.types.Object,
    shards: int = 20,
    explosion_force: float = 5.0,
    start_frame: int = 1
) -> list:
    """
    Shatter an object into pieces with physics simulation.
    
    Args:
        target_object: Object to shatter
        shards: Number of pieces
        explosion_force: Initial explosion velocity
        start_frame: Frame when shatter begins
    
    Returns:
        List of shard objects
    
    Example:
        >>> shards = create_shatter_effect(glass_object, shards=30)
    """
    # Add cell fracture modifier (requires addon)
    try:
        bpy.ops.object.add_fracture_cell_objects(
            source={'PARTICLE_OWN'},
            source_limit=shards,
            source_noise=0.1,
            cell_scale=(1, 1, 1),
            recursion=0,
            recursion_chance=0.5
        )
    except:
        # Fallback: simple subdivision approach
        print("Cell Fracture addon not available, using basic approach")
        return []
    
    # Get created shards
    shards_list = [obj for obj in bpy.context.selected_objects if obj != target_object]
    
    # Add rigid body physics to each shard
    for shard in shards_list:
        bpy.context.view_layer.objects.active = shard
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        shard.rigid_body.mass = 1.0 / len(shards_list)
        
        # Add initial velocity (outward from center)
        center = target_object.location
        direction = (shard.location - center).normalized()
        # Note: Initial velocity would be set via force field or animation
    
    # Hide original
    target_object.hide_viewport = True
    target_object.hide_render = True
    
    return shards_list


# Standalone execution
if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create simple explosion
    explosion = create_explosion_effect(
        location=(0, 0, 1),
        intensity=1.0,
        duration=60,
        include_debris=True,
        include_smoke=False,  # Skip smoke for faster testing
        include_fire=True
    )
    
    print(f"Created explosion with {len(explosion)} components")
