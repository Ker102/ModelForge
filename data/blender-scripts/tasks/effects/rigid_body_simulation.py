"""
{
  "title": "Rigid Body Simulation",
  "category": "effects",
  "subcategory": "physics",
  "tags": ["rigid body", "physics", "simulation", "collision", "gravity", "dynamic", "kinematic", "bake", "force field"],
  "difficulty": "intermediate",
  "description": "Set up rigid body simulations with active/passive objects, collision shapes, force fields, and simulation baking via Python.",
  "blender_version": "5.0+",
  "estimated_objects": 3
}
"""
import bpy
import math


def ensure_rigid_body_world(
    scene: bpy.types.Scene = None,
    substeps: int = 10,
    solver_iterations: int = 10,
    frame_start: int = 1,
    frame_end: int = 250
) -> bpy.types.RigidBodyWorld:
    """
    Ensure the scene has a rigid body world with proper settings.

    Args:
        scene: Target scene (defaults to current)
        substeps: Simulation substeps (higher = more accurate)
        solver_iterations: Constraint solver iterations
        frame_start: Simulation start frame
        frame_end: Simulation end frame

    Returns:
        The RigidBodyWorld object

    Example:
        >>> rbw = ensure_rigid_body_world(substeps=20, frame_end=300)
    """
    if scene is None:
        scene = bpy.context.scene

    if scene.rigidbody_world is None:
        bpy.ops.rigidbody.world_add()

    rbw = scene.rigidbody_world
    rbw.substeps_per_frame = substeps
    rbw.solver_iterations = solver_iterations

    # Set cache frame range
    rbw.point_cache.frame_start = frame_start
    rbw.point_cache.frame_end = frame_end

    return rbw


def add_rigid_body(
    obj: bpy.types.Object,
    body_type: str = 'ACTIVE',
    mass: float = 1.0,
    friction: float = 0.5,
    restitution: float = 0.5,
    collision_shape: str = 'CONVEX_HULL',
    linear_damping: float = 0.04,
    angular_damping: float = 0.1,
    use_margin: bool = False,
    collision_margin: float = 0.04
) -> bpy.types.RigidBodyObject:
    """
    Add rigid body physics to an object.

    Args:
        obj: Object to add rigid body physics to
        body_type: 'ACTIVE' (simulated) or 'PASSIVE' (static collider)
        mass: Mass in kg (only for ACTIVE)
        friction: Surface friction (0-1)
        restitution: Bounciness (0-1)
        collision_shape: 'BOX', 'SPHERE', 'CAPSULE', 'CYLINDER',
                        'CONE', 'CONVEX_HULL', or 'MESH'
        linear_damping: Linear velocity damping
        angular_damping: Rotational velocity damping
        use_margin: Enable collision margin
        collision_margin: Margin distance

    Returns:
        The RigidBodyObject settings

    Example:
        >>> add_rigid_body(cube, 'ACTIVE', mass=2.0, restitution=0.8)
    """
    # Select and make active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Add rigid body
    bpy.ops.rigidbody.object_add(type=body_type)

    rb = obj.rigid_body
    rb.mass = mass
    rb.friction = friction
    rb.restitution = restitution
    rb.collision_shape = collision_shape
    rb.linear_damping = linear_damping
    rb.angular_damping = angular_damping
    rb.use_margin = use_margin
    if use_margin:
        rb.collision_margin = collision_margin

    obj.select_set(False)
    return rb


def create_collision_ground(
    size: float = 20.0,
    location: tuple = (0, 0, 0),
    friction: float = 0.8,
    name: str = "RB_Ground"
) -> bpy.types.Object:
    """
    Create a passive rigid body ground plane for collisions.

    Args:
        size: Ground plane size
        location: World position
        friction: Surface friction
        name: Object name

    Returns:
        The ground plane object

    Example:
        >>> ground = create_collision_ground(size=30, friction=0.9)
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    ground = bpy.context.active_object
    ground.name = name

    add_rigid_body(
        ground,
        body_type='PASSIVE',
        friction=friction,
        restitution=0.3,
        collision_shape='BOX'
    )

    return ground


def add_force_field(
    location: tuple = (0, 0, 0),
    field_type: str = 'FORCE',
    strength: float = -5.0,
    flow: float = 0.0,
    name: str = "ForceField"
) -> bpy.types.Object:
    """
    Add a force field to the scene.

    Args:
        location: Force field position
        field_type: 'FORCE', 'WIND', 'VORTEX', 'TURBULENCE',
                   'DRAG', 'HARMONIC', 'CHARGE', 'MAGNETIC'
        strength: Force strength (negative = attraction)
        flow: Flow amount for fluid-like forces
        name: Object name

    Returns:
        The force field empty object

    Example:
        >>> wind = add_force_field((0, 0, 5), 'WIND', strength=10.0)
    """
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    field_obj = bpy.context.active_object
    field_obj.name = name

    # Add force field
    bpy.ops.object.forcefield_toggle()
    field_obj.field.type = field_type
    field_obj.field.strength = strength
    field_obj.field.flow = flow

    return field_obj


def keyframe_kinematic_switch(
    obj: bpy.types.Object,
    switch_frame: int,
    animated_before: bool = True
) -> None:
    """
    Switch an object from kinematic (animated) to dynamic (simulated) at a specific frame.
    Useful for throwing objects, dropping things, etc.

    Args:
        obj: Object with rigid body
        switch_frame: Frame at which to switch
        animated_before: If True, object is kinematic before switch_frame

    Example:
        >>> keyframe_kinematic_switch(ball, switch_frame=30)
    """
    if not obj.rigid_body:
        raise ValueError(f"Object '{obj.name}' has no rigid body")

    rb = obj.rigid_body

    if animated_before:
        # Before switch: kinematic (follows animation)
        rb.kinematic = True
        rb.keyframe_insert(data_path="kinematic", frame=switch_frame - 1)

        # At switch: dynamic (falls/collides)
        rb.kinematic = False
        rb.keyframe_insert(data_path="kinematic", frame=switch_frame)
    else:
        # Before switch: dynamic
        rb.kinematic = False
        rb.keyframe_insert(data_path="kinematic", frame=switch_frame - 1)

        # At switch: kinematic (freezes in place)
        rb.kinematic = True
        rb.keyframe_insert(data_path="kinematic", frame=switch_frame)


def bake_rigid_body_simulation(
    scene: bpy.types.Scene = None,
    frame_start: int = 1,
    frame_end: int = 250
) -> bool:
    """
    Bake the rigid body simulation cache.
    Must be called before rendering for deterministic results.

    Args:
        scene: Target scene
        frame_start: Start frame
        frame_end: End frame

    Returns:
        True if successful

    Example:
        >>> bake_rigid_body_simulation(frame_end=300)
    """
    if scene is None:
        scene = bpy.context.scene

    if not scene.rigidbody_world:
        print("No rigid body world to bake")
        return False

    # Set cache range
    cache = scene.rigidbody_world.point_cache
    cache.frame_start = frame_start
    cache.frame_end = frame_end

    # Free existing bake, then rebake
    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all(bake=True)

    return True


def create_domino_chain(
    count: int = 10,
    spacing: float = 0.3,
    domino_size: tuple = (0.1, 0.02, 0.2),
    start_location: tuple = (0, 0, 0),
    direction: tuple = (1, 0, 0),
    mass: float = 0.5,
    initial_push_force: float = 200
) -> list:
    """
    Create a chain of dominoes with rigid body physics.
    The first domino gets an initial rotation impulse to start the chain reaction.

    Args:
        count: Number of dominoes
        spacing: Distance between dominoes
        domino_size: (width, depth, height) of each domino
        start_location: Starting position
        direction: Direction vector for the chain
        mass: Mass of each domino
        initial_push_force: Impulse force on first domino

    Returns:
        List of domino objects

    Example:
        >>> dominoes = create_domino_chain(count=20, spacing=0.25)
    """
    ensure_rigid_body_world()

    # Normalize direction
    mag = math.sqrt(sum(d * d for d in direction))
    dir_n = tuple(d / mag for d in direction)

    dominoes = []
    for i in range(count):
        loc = (
            start_location[0] + dir_n[0] * spacing * i,
            start_location[1] + dir_n[1] * spacing * i,
            start_location[2] + domino_size[2] / 2  # stand upright
        )

        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=loc,
            scale=domino_size
        )
        domino = bpy.context.active_object
        domino.name = f"Domino_{i:03d}"

        # Add material
        mat = bpy.data.materials.new(f"Domino_Mat_{i:03d}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            # Alternate colors
            if i % 2 == 0:
                bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.8, 1.0)
            else:
                bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1.0)
        domino.data.materials.append(mat)

        add_rigid_body(domino, 'ACTIVE', mass=mass, collision_shape='BOX')
        dominoes.append(domino)

    # Tilt first domino slightly to trigger the chain
    if dominoes:
        angle = math.radians(15)
        dominoes[0].rotation_euler.y = angle

    return dominoes


# Standalone execution
if __name__ == "__main__":
    # Create ground and domino chain
    ground = create_collision_ground()
    dominoes = create_domino_chain(count=15, spacing=0.3)
    print(f"Created {len(dominoes)} dominoes with rigid body simulation")
