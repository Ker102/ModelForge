"""
{
  "title": "Particle System Utilities",
  "category": "particles",
  "tags": ["particles", "hair", "emitter", "scatter", "instance", "physics"],
  "description": "Functions for creating and configuring particle systems including hair and emitter types.",
  "blender_version": "3.0+"
}
"""
import bpy


def add_particle_system(
    obj: bpy.types.Object,
    name: str = "ParticleSystem",
    particle_type: str = 'EMITTER'
) -> tuple:
    """
    Add a particle system to an object.
    
    Args:
        obj: Object to add particles to
        name: Name for the particle system
        particle_type: 'EMITTER' or 'HAIR'
    
    Returns:
        Tuple of (particle_system, particle_settings)
    
    Example:
        >>> ps, settings = add_particle_system(plane, "Rain", "EMITTER")
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.particle_system_add()
    
    particle_sys = obj.particle_systems[-1]
    particle_sys.name = name
    settings = particle_sys.settings
    settings.name = f"{name}_Settings"
    settings.type = particle_type
    
    return particle_sys, settings


def configure_emitter(
    settings: bpy.types.ParticleSettings,
    count: int = 1000,
    lifetime: int = 50,
    frame_start: int = 1,
    frame_end: int = 200,
    emit_from: str = 'FACE',
    velocity_normal: float = 1.0,
    velocity_random: float = 0.0,
    size: float = 0.05,
    size_random: float = 0.0
) -> None:
    """
    Configure emitter particle settings.
    
    Args:
        settings: Particle settings object
        count: Number of particles
        lifetime: Particle lifetime in frames
        frame_start: Emission start frame
        frame_end: Emission end frame
        emit_from: 'VERT', 'FACE', 'VOLUME'
        velocity_normal: Velocity along normals
        velocity_random: Random velocity factor
        size: Particle size
        size_random: Random size variation (0-1)
    
    Example:
        >>> configure_emitter(settings, count=5000, lifetime=100)
    """
    settings.type = 'EMITTER'
    settings.count = count
    settings.lifetime = lifetime
    settings.frame_start = frame_start
    settings.frame_end = frame_end
    settings.emit_from = emit_from
    settings.normal_factor = velocity_normal
    settings.factor_random = velocity_random
    settings.particle_size = size
    settings.size_random = size_random


def configure_hair(
    settings: bpy.types.ParticleSettings,
    count: int = 1000,
    hair_length: float = 0.2,
    segments: int = 5,
    emit_from: str = 'FACE',
    use_advanced: bool = True
) -> None:
    """
    Configure hair particle settings.
    
    Args:
        settings: Particle settings object
        count: Number of hair strands
        hair_length: Length of each strand
        segments: Segments per strand
        emit_from: 'VERT', 'FACE'
        use_advanced: Enable advanced hair settings
    
    Example:
        >>> configure_hair(settings, count=10000, hair_length=0.5)
    """
    settings.type = 'HAIR'
    settings.count = count
    settings.hair_length = hair_length
    settings.hair_step = segments
    settings.emit_from = emit_from
    settings.use_advanced_hair = use_advanced


def set_particle_physics(
    settings: bpy.types.ParticleSettings,
    physics_type: str = 'NEWTON',
    gravity: float = 1.0,
    mass: float = 1.0,
    drag: float = 0.0,
    brownian: float = 0.0
) -> None:
    """
    Configure particle physics.
    
    Args:
        settings: Particle settings object
        physics_type: 'NO', 'NEWTON', 'KEYED', 'BOIDS', 'FLUID'
        gravity: Gravity influence (0-1)
        mass: Particle mass
        drag: Air resistance
        brownian: Random motion
    
    Example:
        >>> set_particle_physics(settings, gravity=0.5, drag=0.1)
    """
    settings.physics_type = physics_type
    settings.effector_weights.gravity = gravity
    settings.mass = mass
    settings.drag_factor = drag
    settings.brownian_factor = brownian


def render_as_object(
    settings: bpy.types.ParticleSettings,
    instance_object: bpy.types.Object,
    scale: float = 1.0,
    scale_random: float = 0.0,
    use_rotation: bool = True,
    rotation_random: float = 0.0
) -> None:
    """
    Render particles as instances of an object.
    
    Args:
        settings: Particle settings object
        instance_object: Object to instance at each particle
        scale: Instance scale
        scale_random: Random scale variation
        use_rotation: Use particle rotation
        rotation_random: Random rotation factor
    
    Example:
        >>> render_as_object(settings, leaf_mesh, scale=0.1, scale_random=0.3)
    """
    settings.render_type = 'OBJECT'
    settings.instance_object = instance_object
    settings.particle_size = scale
    settings.size_random = scale_random
    settings.use_rotation_instance = use_rotation
    settings.rotation_factor_random = rotation_random


def render_as_collection(
    settings: bpy.types.ParticleSettings,
    collection: bpy.types.Collection,
    scale: float = 1.0,
    use_whole_collection: bool = True,
    use_rotation: bool = True
) -> None:
    """
    Render particles as instances from a collection.
    
    Args:
        settings: Particle settings object
        collection: Collection containing instance objects
        scale: Instance scale
        use_whole_collection: Use all objects (False = pick random)
        use_rotation: Use particle rotation
    
    Example:
        >>> render_as_collection(settings, bpy.data.collections['Rocks'])
    """
    settings.render_type = 'COLLECTION'
    settings.instance_collection = collection
    settings.particle_size = scale
    settings.use_whole_collection = use_whole_collection
    settings.use_rotation_instance = use_rotation


def add_force_field(
    location: tuple = (0, 0, 0),
    field_type: str = 'FORCE',
    strength: float = 1.0,
    falloff_type: str = 'SPHERE',
    falloff_power: float = 2.0,
    name: str = "ForceField"
) -> bpy.types.Object:
    """
    Add a force field to affect particles.
    
    Args:
        location: Field position
        field_type: 'FORCE', 'WIND', 'VORTEX', 'MAGNETIC', 'HARMONIC',
                   'CHARGE', 'LENNARD_JONES', 'TEXTURE', 'GUIDE',
                   'BOID', 'TURBULENCE', 'DRAG'
        strength: Force strength
        falloff_type: 'SPHERE', 'TUBE', 'CONE'
        falloff_power: Distance falloff exponent
        name: Object name
    
    Returns:
        The created force field object
    
    Example:
        >>> wind = add_force_field((0, -5, 5), 'WIND', strength=10)
    """
    bpy.ops.object.effector_add(type=field_type, location=location)
    field = bpy.context.active_object
    field.name = name
    
    field.field.strength = strength
    field.field.shape = falloff_type
    field.field.falloff_power = falloff_power
    
    return field


def convert_particles_to_mesh(
    obj: bpy.types.Object,
    apply_modifiers: bool = True
) -> bpy.types.Object:
    """
    Convert particle instances to real mesh objects.
    
    Args:
        obj: Object with particle system
        apply_modifiers: Apply all modifiers
    
    Returns:
        The created mesh object
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)
    
    # The new objects are now selected
    return bpy.context.selected_objects


def create_rain_effect(
    emitter: bpy.types.Object,
    intensity: int = 1000,
    speed: float = 5.0,
    area_size: float = 10.0,
    name: str = "Rain"
) -> tuple:
    """
    Create a rain particle effect.
    
    Args:
        emitter: Surface to emit rain from (usually a plane above scene)
        intensity: Number of particles
        speed: Fall speed
        area_size: Emission area size
        name: System name
    
    Returns:
        Tuple of (particle_system, settings)
    
    Example:
        >>> rain_plane = bpy.data.objects['RainPlane']
        >>> ps, settings = create_rain_effect(rain_plane, intensity=5000)
    """
    ps, settings = add_particle_system(emitter, name, 'EMITTER')
    
    # Configure as rain
    settings.count = intensity
    settings.lifetime = 50
    settings.frame_start = 1
    settings.frame_end = 250
    settings.emit_from = 'FACE'
    
    # Physics
    settings.physics_type = 'NEWTON'
    settings.normal_factor = 0
    settings.object_align_factor = (0, 0, -speed)
    settings.effector_weights.gravity = 1.0
    
    # Appearance
    settings.render_type = 'LINE'
    settings.line_length_tail = 1.0
    
    return ps, settings


def create_dust_effect(
    emitter: bpy.types.Object,
    count: int = 500,
    size: float = 0.02,
    movement: float = 0.3,
    name: str = "Dust"
) -> tuple:
    """
    Create floating dust particles.
    
    Args:
        emitter: Volume or surface to emit from
        count: Number of particles
        size: Particle size
        movement: Brownian motion amount
        name: System name
    
    Returns:
        Tuple of (particle_system, settings)
    """
    ps, settings = add_particle_system(emitter, name, 'EMITTER')
    
    settings.count = count
    settings.lifetime = 500
    settings.frame_start = 1
    settings.frame_end = 1
    settings.emit_from = 'VOLUME'
    
    # Physics - floating motion
    settings.physics_type = 'NEWTON'
    settings.brownian_factor = movement
    settings.effector_weights.gravity = 0.0
    settings.drag_factor = 1.0
    
    # Appearance
    settings.render_type = 'HALO'
    settings.particle_size = size
    settings.size_random = 0.5
    
    return ps, settings
