"""
{
  "title": "Volumetric Effects",
  "category": "rendering",
  "subcategory": "volume",
  "tags": ["volumetric", "fog", "mist", "god rays", "volume scatter", "atmosphere", "haze", "light shaft"],
  "difficulty": "intermediate",
  "description": "Create volumetric fog, mist, god rays, and atmospheric haze using Volume Scatter/Absorption nodes and mist passes.",
  "blender_version": "5.0+",
  "estimated_objects": 1
}
"""
import bpy
import math


def setup_world_volume_fog(
    density: float = 0.01,
    color: tuple = (0.8, 0.85, 0.9),
    anisotropy: float = 0.3,
    absorption_color: tuple = None
) -> bpy.types.Material:
    """
    Add volumetric fog to the entire world using Volume Scatter.
    Creates atmospheric haze and god ray effects with directional lights.

    Args:
        density: Fog density (0.001=subtle haze, 0.05=thick fog)
        color: Scatter color (RGB)
        anisotropy: Light scattering direction (-1 to 1, 0=uniform, positive=forward scatter)
        absorption_color: Optional volume absorption color for tinted fog

    Returns:
        The world material

    Example:
        >>> setup_world_volume_fog(density=0.02, anisotropy=0.5)
    """
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Find output node
    output = None
    for node in nodes:
        if node.type == 'OUTPUT_WORLD':
            output = node
            break

    if not output:
        output = nodes.new('ShaderNodeOutputWorld')
        output.location = (600, 0)

    # Create Volume Scatter
    scatter = nodes.new('ShaderNodeVolumeScatter')
    scatter.inputs['Color'].default_value = (*color, 1.0)
    scatter.inputs['Density'].default_value = density
    scatter.inputs['Anisotropy'].default_value = anisotropy
    scatter.location = (200, -200)

    if absorption_color:
        # Add absorption for colored fog
        absorb = nodes.new('ShaderNodeVolumeAbsorption')
        absorb.inputs['Color'].default_value = (*absorption_color, 1.0)
        absorb.inputs['Density'].default_value = density * 0.3
        absorb.location = (200, -400)

        # Mix volumes
        add_shader = nodes.new('ShaderNodeAddShader')
        add_shader.location = (400, -300)

        links.new(scatter.outputs['Volume'], add_shader.inputs[0])
        links.new(absorb.outputs['Volume'], add_shader.inputs[1])
        links.new(add_shader.outputs['Shader'], output.inputs['Volume'])
    else:
        links.new(scatter.outputs['Volume'], output.inputs['Volume'])

    return world


def create_volume_cube(
    location: tuple = (0, 0, 0),
    size: tuple = (10, 10, 4),
    density: float = 0.1,
    color: tuple = (0.9, 0.9, 0.95),
    anisotropy: float = 0.3,
    name: str = "VolumeFog"
) -> bpy.types.Object:
    """
    Create a localized fog volume (cube with Volume Scatter material).
    Useful for ground fog, room haze, or localized atmosphere.

    Args:
        location: Center of the volume
        size: (width, depth, height) dimensions
        density: Fog density
        color: Fog color (RGB)
        anisotropy: Light scatter direction
        name: Object name

    Returns:
        The volume cube object

    Example:
        >>> ground_fog = create_volume_cube((0, 0, 0.5), size=(20, 20, 1), density=0.2)
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, scale=size)
    vol = bpy.context.active_object
    vol.name = name
    vol.display_type = 'WIRE'

    # Create volume material
    mat = bpy.data.materials.new(f"{name}_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)

    scatter = nodes.new('ShaderNodeVolumeScatter')
    scatter.inputs['Color'].default_value = (*color, 1.0)
    scatter.inputs['Density'].default_value = density
    scatter.inputs['Anisotropy'].default_value = anisotropy
    scatter.location = (0, 0)

    links.new(scatter.outputs['Volume'], output.inputs['Volume'])

    vol.data.materials.append(mat)
    return vol


def create_gradient_fog(
    location: tuple = (0, 0, 0),
    size: tuple = (20, 20, 5),
    density_bottom: float = 0.3,
    density_top: float = 0.0,
    color: tuple = (0.85, 0.88, 0.92),
    name: str = "GradientFog"
) -> bpy.types.Object:
    """
    Create height-based gradient fog (thicker at the bottom, fading up).
    Uses a texture coordinate Z ramp to control density.

    Args:
        location: Volume center
        size: Volume dimensions
        density_bottom: Density at the bottom
        density_top: Density at the top
        color: Fog color
        name: Object name

    Returns:
        The gradient fog object

    Example:
        >>> fog = create_gradient_fog(density_bottom=0.5, density_top=0.01)
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, scale=size)
    vol = bpy.context.active_object
    vol.name = name
    vol.display_type = 'WIRE'

    # Create gradient volume material
    mat = bpy.data.materials.new(f"{name}_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)

    # Volume Scatter
    scatter = nodes.new('ShaderNodeVolumeScatter')
    scatter.inputs['Color'].default_value = (*color, 1.0)
    scatter.location = (400, 0)

    # Texture Coordinate → use Object Z for height gradient
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-400, 0)

    # Separate XYZ to get Z
    sep = nodes.new('ShaderNodeSeparateXYZ')
    sep.location = (-200, 0)
    links.new(tex_coord.outputs['Object'], sep.inputs['Vector'])

    # Map Range: Z from [0, 1] → [density_bottom, density_top]
    map_range = nodes.new('ShaderNodeMapRange')
    map_range.inputs['From Min'].default_value = 0.0
    map_range.inputs['From Max'].default_value = 1.0
    map_range.inputs['To Min'].default_value = density_bottom
    map_range.inputs['To Max'].default_value = density_top
    map_range.location = (0, 0)

    links.new(sep.outputs['Z'], map_range.inputs['Value'])

    # Multiply density
    math_node = nodes.new('ShaderNodeMath')
    math_node.operation = 'MAXIMUM'
    math_node.inputs[1].default_value = 0.0  # Clamp to non-negative
    math_node.location = (200, 0)

    links.new(map_range.outputs['Result'], math_node.inputs[0])
    links.new(math_node.outputs['Value'], scatter.inputs['Density'])

    links.new(scatter.outputs['Volume'], output.inputs['Volume'])

    vol.data.materials.append(mat)
    return vol


def setup_mist_pass(
    scene: bpy.types.Scene = None,
    start: float = 5.0,
    depth: float = 25.0,
    falloff: str = 'QUADRATIC'
) -> None:
    """
    Enable and configure the mist render pass for distance-based fog in compositing.

    Args:
        scene: Target scene
        start: Distance where mist begins
        depth: Distance where mist reaches full opacity
        falloff: 'QUADRATIC', 'LINEAR', or 'INVERSE_QUADRATIC'

    Example:
        >>> setup_mist_pass(start=3.0, depth=20.0, falloff='LINEAR')
    """
    if scene is None:
        scene = bpy.context.scene

    # Enable mist pass
    scene.view_layers[0].use_pass_mist = True

    # Configure mist in world settings
    world = scene.world
    if world:
        world.mist_settings.use_mist = True
        world.mist_settings.start = start
        world.mist_settings.depth = depth
        world.mist_settings.falloff = falloff


def create_god_ray_spotlight(
    location: tuple = (0, 0, 5),
    target: tuple = (0, 0, 0),
    energy: float = 1000,
    spot_size: float = 0.6,
    spot_blend: float = 0.2,
    shadow_softness: float = 0.1,
    name: str = "GodRayLight"
) -> bpy.types.Object:
    """
    Create a spotlight optimized for god ray effects with volumetric fog.
    Requires world or local volume fog to be visible.

    Args:
        location: Light position
        target: Point the light aims at
        energy: Light power in watts
        spot_size: Cone angle in radians
        spot_blend: Edge softness (0-1)
        shadow_softness: Shadow blur radius
        name: Object name

    Returns:
        The spotlight object

    Example:
        >>> light = create_god_ray_spotlight((5, -5, 8), target=(0, 0, 0), energy=2000)
    """
    bpy.ops.object.light_add(type='SPOT', location=location)
    light_obj = bpy.context.active_object
    light_obj.name = name
    light = light_obj.data

    light.energy = energy
    light.spot_size = spot_size
    light.spot_blend = spot_blend
    light.shadow_soft_size = shadow_softness
    light.use_shadow = True

    # Point at target
    from mathutils import Vector
    direction = Vector(target) - Vector(location)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    light_obj.rotation_euler = rot_quat.to_euler()

    return light_obj


# Standalone execution
if __name__ == "__main__":
    # Create atmospheric scene with gradient fog and god rays
    fog = create_gradient_fog(density_bottom=0.2, density_top=0.01)
    light = create_god_ray_spotlight((3, -3, 6), target=(0, 0, 0), energy=1500)
    print(f"Created volumetric fog '{fog.name}' and god ray light '{light.name}'")
    print("Switch to Cycles and enable viewport volumetrics to preview")
