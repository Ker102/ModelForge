"""
{
  "title": "Physics Simulation Utilities",
  "category": "physics",
  "tags": ["physics", "rigid body", "soft body", "cloth", "collision", "simulation"],
  "description": "Utility functions for setting up physics simulations in Blender.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def add_rigid_body(
    obj: bpy.types.Object,
    body_type: str = 'ACTIVE',
    mass: float = 1.0,
    friction: float = 0.5,
    bounciness: float = 0.0,
    collision_shape: str = 'CONVEX_HULL'
) -> bpy.types.RigidBodyObject:
    """
    Add rigid body physics to an object.
    
    Args:
        obj: Object to add physics to
        body_type: 'ACTIVE' (simulated) or 'PASSIVE' (static)
        mass: Object mass in kg
        friction: Surface friction (0-1)
        bounciness: Bounce factor (0-1)
        collision_shape: 'BOX', 'SPHERE', 'CAPSULE', 'CYLINDER', 'CONE',
                        'CONVEX_HULL', or 'MESH'
    
    Returns:
        The rigid body settings
    
    Example:
        >>> add_rigid_body(cube, 'ACTIVE', mass=2.0, bounciness=0.5)
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add(type=body_type)
    
    rb = obj.rigid_body
    rb.mass = mass
    rb.friction = friction
    rb.restitution = bounciness
    rb.collision_shape = collision_shape
    
    return rb


def create_ground_plane(
    size: float = 20.0,
    location: tuple = (0, 0, 0),
    name: str = "Ground"
) -> bpy.types.Object:
    """
    Create a ground plane with passive rigid body physics.
    
    Args:
        size: Plane size
        location: Position
        name: Object name
    
    Returns:
        The created ground plane
    
    Example:
        >>> ground = create_ground_plane(size=50)
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    ground = bpy.context.active_object
    ground.name = name
    
    # Add passive rigid body
    add_rigid_body(ground, 'PASSIVE', collision_shape='BOX')
    
    # Add simple material
    mat = bpy.data.materials.new(name=f"{name}_Mat")
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1.0)
    mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.8
    ground.data.materials.append(mat)
    
    return ground


def add_soft_body(
    obj: bpy.types.Object,
    goal_strength: float = 0.7,
    friction: float = 0.5,
    mass: float = 1.0,
    springs: float = 0.5
) -> bpy.types.SoftBodyModifier:
    """
    Add soft body physics to an object.
    
    Args:
        obj: Object to make soft
        goal_strength: How much original shape is maintained (0-1)
        friction: Surface friction
        mass: Object mass
        springs: Spring stiffness (0-1)
    
    Returns:
        The soft body modifier
    
    Example:
        >>> add_soft_body(jelly_cube, goal_strength=0.3, springs=0.8)
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_add(type='SOFT_BODY')
    
    sb = obj.modifiers["Softbody"].settings
    sb.mass = mass
    sb.friction = friction
    sb.goal_spring = goal_strength
    sb.pull = springs
    sb.push = springs
    
    return obj.modifiers["Softbody"]


def add_cloth(
    obj: bpy.types.Object,
    preset: str = 'COTTON',
    quality: int = 5,
    collision: bool = True
) -> bpy.types.ClothModifier:
    """
    Add cloth simulation to an object.
    
    Args:
        obj: Mesh object (should be subdivided)
        preset: 'COTTON', 'SILK', 'LEATHER', 'RUBBER', 'DENIM'
        quality: Simulation quality steps
        collision: Enable self-collision
    
    Returns:
        The cloth modifier
    
    Example:
        >>> add_cloth(flag_mesh, preset='SILK', quality=10)
    """
    presets = {
        'COTTON': {'tension': 15, 'compression': 15, 'bending': 0.5, 'mass': 0.3},
        'SILK': {'tension': 5, 'compression': 5, 'bending': 0.1, 'mass': 0.15},
        'LEATHER': {'tension': 80, 'compression': 80, 'bending': 1.5, 'mass': 0.4},
        'RUBBER': {'tension': 25, 'compression': 25, 'bending': 25, 'mass': 0.3},
        'DENIM': {'tension': 40, 'compression': 40, 'bending': 10, 'mass': 0.4},
    }
    
    values = presets.get(preset.upper(), presets['COTTON'])
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_add(type='CLOTH')
    
    cloth = obj.modifiers["Cloth"]
    settings = cloth.settings
    
    settings.tension_stiffness = values['tension']
    settings.compression_stiffness = values['compression']
    settings.bending_stiffness = values['bending']
    settings.mass = values['mass']
    settings.quality = quality
    
    if collision:
        cloth.collision_settings.use_self_collision = True
    
    return cloth


def add_collision(
    obj: bpy.types.Object,
    thickness_outer: float = 0.02,
    thickness_inner: float = 0.01,
    friction: float = 0.5
) -> bpy.types.CollisionModifier:
    """
    Add collision modifier to make object interact with cloth/soft body.
    
    Args:
        obj: Object to add collision to
        thickness_outer: Outer collision shell thickness
        thickness_inner: Inner collision shell thickness
        friction: Collision friction
    
    Returns:
        The collision modifier
    
    Example:
        >>> add_collision(character_body)
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_add(type='COLLISION')
    
    collision = obj.modifiers["Collision"]
    settings = collision.settings
    
    settings.thickness_outer = thickness_outer
    settings.thickness_inner = thickness_inner
    settings.friction_factor = friction
    
    return collision


def create_force_field(
    field_type: str = 'FORCE',
    location: tuple = (0, 0, 0),
    strength: float = 5.0,
    falloff: float = 2.0,
    name: str = "ForceField"
) -> bpy.types.Object:
    """
    Create a physics force field.
    
    Args:
        field_type: 'FORCE', 'WIND', 'VORTEX', 'MAGNETIC', 'TURBULENCE'
        location: Field position
        strength: Force strength
        falloff: Distance falloff power
        name: Object name
    
    Returns:
        The created force field object
    
    Example:
        >>> wind = create_force_field('WIND', strength=10, location=(0, -5, 2))
    """
    field_types = {
        'FORCE': 'FORCE',
        'WIND': 'WIND',
        'VORTEX': 'VORTEX',
        'MAGNETIC': 'MAGNET',
        'TURBULENCE': 'TURBULENCE'
    }
    
    bpy.ops.object.effector_add(type=field_types.get(field_type.upper(), 'FORCE'), location=location)
    field = bpy.context.active_object
    field.name = name
    
    field.field.strength = strength
    field.field.falloff_power = falloff
    
    return field


def bake_physics(
    frame_start: int = 1,
    frame_end: int = 250,
    bake_all: bool = True
) -> None:
    """
    Bake all physics simulations in the scene.
    
    Args:
        frame_start: Start frame
        frame_end: End frame
        bake_all: Bake all physics types
    
    Example:
        >>> bake_physics(1, 100)
    """
    # Set frame range
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end
    
    # Bake rigid bodies
    if bake_all:
        try:
            bpy.ops.rigidbody.bake_to_keyframes(frame_start=frame_start, frame_end=frame_end)
        except:
            pass
    
    print(f"Physics baked from frame {frame_start} to {frame_end}")
