"""
{
  "title": "Fluid Simulation (Mantaflow)",
  "category": "effects",
  "subcategory": "physics",
  "tags": ["fluid", "mantaflow", "liquid", "smoke", "fire", "simulation", "domain", "inflow", "effector", "bake"],
  "difficulty": "advanced",
  "description": "Set up fluid simulations (liquid, smoke, fire) using Mantaflow via Python. Covers domain configuration, flow objects, effectors, and baking.",
  "blender_version": "5.0+",
  "estimated_objects": 3
}
"""
import bpy
import math


def create_fluid_domain(
    size: tuple = (4, 4, 4),
    location: tuple = (0, 0, 2),
    domain_type: str = 'LIQUID',
    resolution: int = 64,
    frame_end: int = 250,
    name: str = "FluidDomain"
) -> bpy.types.Object:
    """
    Create a fluid simulation domain.

    Args:
        size: Domain bounding box size (x, y, z)
        location: World position
        domain_type: 'LIQUID' or 'GAS' (smoke/fire)
        resolution: Simulation resolution (32-256, higher=slower)
        frame_end: Simulation end frame
        name: Object name

    Returns:
        The domain object

    Example:
        >>> domain = create_fluid_domain(size=(6, 6, 6), domain_type='LIQUID', resolution=128)
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, scale=size)
    domain = bpy.context.active_object
    domain.name = name

    # Add fluid modifier as domain
    bpy.ops.object.modifier_add(type='FLUID')
    fluid = domain.modifiers[-1]
    fluid.fluid_type = 'DOMAIN'

    settings = fluid.domain_settings
    settings.domain_type = domain_type
    settings.resolution_max = resolution
    settings.cache_frame_end = frame_end

    # Set time scale for realistic speed
    settings.time_scale = 1.0

    if domain_type == 'LIQUID':
        # Liquid-specific settings
        settings.use_flip_particles = True
        settings.use_mesh = True  # Generate mesh surface
        settings.mesh_generator = 'IMPROVED'
    elif domain_type == 'GAS':
        # Gas-specific settings
        settings.use_noise = True
        settings.noise_scale = 2

    # Make domain wireframe for visibility
    domain.display_type = 'WIRE'

    return domain


def create_fluid_flow(
    location: tuple = (0, 0, 3),
    flow_type: str = 'LIQUID',
    flow_behavior: str = 'INFLOW',
    velocity: tuple = (0, 0, -2),
    use_initial_velocity: bool = True,
    name: str = "FluidFlow"
) -> bpy.types.Object:
    """
    Create a fluid flow object (inflow, outflow, or geometry source).

    Args:
        location: World position
        flow_type: 'LIQUID', 'SMOKE', 'FIRE', or 'BOTH' (smoke+fire)
        flow_behavior: 'INFLOW' (continuous), 'OUTFLOW' (drain), or 'GEOMETRY' (one-time)
        velocity: Initial velocity (x, y, z)
        use_initial_velocity: Apply velocity to emitted fluid
        name: Object name

    Returns:
        The flow object

    Example:
        >>> inflow = create_fluid_flow((0, 0, 4), 'LIQUID', 'INFLOW', velocity=(0, 0, -3))
        >>> fire = create_fluid_flow((0, 0, 0), 'FIRE', 'INFLOW')
    """
    # Use a sphere for the flow source
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=location, segments=16, ring_count=8)
    flow_obj = bpy.context.active_object
    flow_obj.name = name

    # Add fluid modifier as flow
    bpy.ops.object.modifier_add(type='FLUID')
    fluid = flow_obj.modifiers[-1]
    fluid.fluid_type = 'FLOW'

    settings = fluid.flow_settings
    settings.flow_type = flow_type
    settings.flow_behavior = flow_behavior

    if use_initial_velocity:
        settings.use_initial_velocity = True
        settings.velocity_coord = velocity

    # Set flow source to mesh surface
    settings.flow_source = 'MESH'

    return flow_obj


def create_fluid_effector(
    obj: bpy.types.Object = None,
    effector_type: str = 'COLLISION',
    location: tuple = (0, 0, 0),
    name: str = "FluidEffector"
) -> bpy.types.Object:
    """
    Create or convert an object into a fluid effector (collision/guide).

    Args:
        obj: Existing object to convert (creates a plane if None)
        effector_type: 'COLLISION' or 'GUIDE'
        location: Position if creating new object
        name: Object name

    Returns:
        The effector object

    Example:
        >>> wall = create_fluid_effector(effector_type='COLLISION')
        >>> create_fluid_effector(existing_mesh, 'COLLISION')
    """
    if obj is None:
        bpy.ops.mesh.primitive_plane_add(size=4, location=location)
        obj = bpy.context.active_object
        obj.name = name

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.modifier_add(type='FLUID')
    fluid = obj.modifiers[-1]
    fluid.fluid_type = 'EFFECTOR'
    fluid.effector_settings.effector_type = effector_type

    return obj


def setup_smoke_domain_material(
    domain: bpy.types.Object,
    smoke_color: tuple = (0.8, 0.8, 0.8),
    density: float = 5.0,
    fire_color: tuple = (1.0, 0.4, 0.05),
    fire_intensity: float = 3.0
) -> bpy.types.Material:
    """
    Create a volumetric material for smoke/fire domain rendering.

    Args:
        domain: The fluid domain object
        smoke_color: Smoke color (RGB)
        density: Volume density multiplier
        fire_color: Fire emission color (RGB)
        fire_intensity: Fire emission strength

    Returns:
        The volume material

    Example:
        >>> setup_smoke_domain_material(domain, smoke_color=(0.3, 0.3, 0.3))
    """
    mat = bpy.data.materials.new(f"{domain.name}_Volume")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)

    # Principled Volume
    volume = nodes.new('ShaderNodeVolumePrincipled')
    volume.location = (0, 0)
    volume.inputs['Color'].default_value = (*smoke_color, 1.0)
    volume.inputs['Density'].default_value = density

    # Fire settings
    volume.inputs['Blackbody Intensity'].default_value = fire_intensity
    volume.inputs['Emission Color'].default_value = (*fire_color, 1.0)

    # Connect volume to output
    links.new(volume.outputs['Volume'], output.inputs['Volume'])

    domain.data.materials.clear()
    domain.data.materials.append(mat)

    return mat


def bake_fluid_simulation(
    domain: bpy.types.Object,
    bake_type: str = 'ALL'
) -> bool:
    """
    Bake a fluid simulation on the domain object.

    Args:
        domain: The fluid domain object
        bake_type: 'ALL' (data + mesh), 'DATA' (simulation only), or 'MESH' (mesh only)

    Returns:
        True if successful

    Example:
        >>> bake_fluid_simulation(domain, 'ALL')
    """
    bpy.context.view_layer.objects.active = domain
    domain.select_set(True)

    try:
        if bake_type in ('ALL', 'DATA'):
            bpy.ops.fluid.bake_all()
        if bake_type == 'MESH':
            bpy.ops.fluid.bake_mesh()
        return True
    except RuntimeError as e:
        print(f"Bake failed: {e}")
        return False


def create_campfire_smoke(
    location: tuple = (0, 0, 0),
    domain_size: tuple = (3, 3, 5),
    resolution: int = 64,
    frame_end: int = 200
) -> dict:
    """
    Create a complete campfire smoke/fire simulation setup.

    Args:
        location: Base position for the fire
        domain_size: Size of the simulation domain
        resolution: Simulation resolution
        frame_end: End frame

    Returns:
        Dict with domain, flow, and effector objects

    Example:
        >>> scene = create_campfire_smoke(location=(0, 0, 0))
    """
    domain_loc = (location[0], location[1], location[2] + domain_size[2] / 2)

    # Create domain
    domain = create_fluid_domain(
        size=domain_size,
        location=domain_loc,
        domain_type='GAS',
        resolution=resolution,
        frame_end=frame_end,
        name="Campfire_Domain"
    )

    # Configure domain for fire + smoke
    settings = domain.modifiers[-1].domain_settings
    settings.use_noise = True
    settings.noise_scale = 2
    settings.vorticity = 0.3

    # Create fire source
    fire_flow = create_fluid_flow(
        location=location,
        flow_type='BOTH',
        flow_behavior='INFLOW',
        velocity=(0, 0, 1),
        name="Campfire_Fire"
    )

    # Configure fire flow
    flow_settings = fire_flow.modifiers[-1].flow_settings
    flow_settings.fuel_amount = 1.0
    flow_settings.temperature = 2.0

    # Add volume material
    setup_smoke_domain_material(
        domain,
        smoke_color=(0.3, 0.3, 0.35),
        density=3.0,
        fire_color=(1.0, 0.4, 0.05),
        fire_intensity=5.0
    )

    # Create ground effector
    ground = create_fluid_effector(
        effector_type='COLLISION',
        location=(location[0], location[1], location[2] - 0.1),
        name="Campfire_Ground"
    )

    return {
        'domain': domain,
        'fire_flow': fire_flow,
        'ground': ground,
    }


# Standalone execution
if __name__ == "__main__":
    result = create_campfire_smoke(location=(0, 0, 0))
    print(f"Created campfire: domain='{result['domain'].name}', "
          f"fire='{result['fire_flow'].name}'")
    print("Bake the simulation before rendering: bake_fluid_simulation(domain)")
