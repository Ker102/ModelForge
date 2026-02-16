"""
Volumetric Effects — Atmosphere, God Rays, Fog
===============================================
Category: lighting
Blender: 4.0+ / 5.0
Source: NotebookLM (89-source Blender knowledge base)

Create atmospheric depth using volumetric shaders.
Key principle: Principled Volume → Volume output (NOT Surface output).

DENSITY GUIDELINES:
- Clear atmosphere: 0.001 - 0.003
- Light haze: 0.005 - 0.01
- Fog: 0.02 - 0.05
- Thick fog: 0.05 - 0.1
- Dense smoke: 0.1 - 0.5

IMPORTANT: Keep density VERY LOW to avoid obscuring the scene.
"""

import bpy


# =============================================================================
# VOLUMETRIC ATMOSPHERE — God Rays & Depth
# =============================================================================

def create_atmosphere(density=0.005, scale=10):
    """Create atmospheric volume for god rays and depth.

    Creates a large cube with Principled Volume material.
    CRITICAL: Volume shader connects to Volume output (not Surface).

    Args:
        density: Volumetric density (0.001=clear, 0.005=haze, 0.05=fog)
        scale: Size of the atmosphere cube (should cover entire scene)
    """
    # Create domain cube
    bpy.ops.mesh.primitive_cube_add(size=1)
    cube = bpy.context.active_object
    cube.name = "Atmosphere_Volume"
    cube.scale = (scale, scale, scale)
    cube.display_type = 'WIRE'  # Don't obstruct viewport

    # Create Volume Material
    mat = bpy.data.materials.new(name="Volumetric_Atmosphere")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Principled Volume node
    vol_node = nodes.new('ShaderNodeVolumePrincipled')
    vol_node.location = (0, 0)
    vol_node.inputs['Density'].default_value = density
    vol_node.inputs['Color'].default_value = (0.8, 0.85, 0.9)  # Slightly blue haze

    # Output node
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    # CRITICAL: Connect to VOLUME output, NOT Surface
    links.new(vol_node.outputs['Volume'], output.inputs['Volume'])

    cube.data.materials.append(mat)
    return cube


# =============================================================================
# FOG — Ground-Level Atmospheric Effect
# =============================================================================

def create_ground_fog(density=0.03, height=2.0, scale=20):
    """Create ground-hugging fog using a flattened volume domain.

    Args:
        density: Fog density (0.02-0.1)
        height: Height of fog layer in meters
        scale: Horizontal coverage
    """
    bpy.ops.mesh.primitive_cube_add(size=1)
    fog = bpy.context.active_object
    fog.name = "Ground_Fog"
    fog.scale = (scale, scale, height / 2)
    fog.location = (0, 0, height / 2)
    fog.display_type = 'WIRE'

    mat = bpy.data.materials.new(name="Fog_Material")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Volume with gradient for natural falloff
    vol_node = nodes.new('ShaderNodeVolumePrincipled')
    vol_node.location = (0, 0)
    vol_node.inputs['Density'].default_value = density
    vol_node.inputs['Color'].default_value = (0.9, 0.9, 0.95)

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    # CRITICAL: Volume output, not Surface
    links.new(vol_node.outputs['Volume'], output.inputs['Volume'])

    fog.data.materials.append(mat)
    return fog


# =============================================================================
# PROCEDURAL FOG WITH NOISE — More Realistic
# =============================================================================

def create_procedural_fog(density=0.02, noise_scale=3.0, height=3.0, coverage=20):
    """Create fog with procedural noise for organic wispy appearance.

    Uses Noise Texture to vary density across the volume.
    """
    bpy.ops.mesh.primitive_cube_add(size=1)
    fog = bpy.context.active_object
    fog.name = "Procedural_Fog"
    fog.scale = (coverage, coverage, height)
    fog.location = (0, 0, height)
    fog.display_type = 'WIRE'

    mat = bpy.data.materials.new(name="Procedural_Fog_Mat")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Texture Coordinate → Mapping → Noise → Multiply with Density
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = noise_scale
    noise.inputs['Detail'].default_value = 5.0

    # Math multiply to control density
    multiply = nodes.new('ShaderNodeMath')
    multiply.location = (-200, 0)
    multiply.operation = 'MULTIPLY'
    multiply.inputs[1].default_value = density

    # Principled Volume
    vol_node = nodes.new('ShaderNodeVolumePrincipled')
    vol_node.location = (0, 0)
    vol_node.inputs['Color'].default_value = (0.85, 0.88, 0.92)

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    # Link chain
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], multiply.inputs[0])
    links.new(multiply.outputs['Value'], vol_node.inputs['Density'])
    links.new(vol_node.outputs['Volume'], output.inputs['Volume'])

    fog.data.materials.append(mat)
    return fog


# =============================================================================
# WORLD VOLUME — Entire Scene Atmosphere
# =============================================================================

def create_world_volume(density=0.002):
    """Add volumetric atmosphere via World shader (affects entire scene).

    Simpler than domain cube but less controllable.
    Good for subtle overall haze.
    """
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Find or create output
    output = None
    for node in nodes:
        if node.type == 'OUTPUT_WORLD':
            output = node
            break
    if not output:
        output = nodes.new('ShaderNodeOutputWorld')

    # Create volume shader
    vol_node = nodes.new('ShaderNodeVolumePrincipled')
    vol_node.location = (-200, -200)
    vol_node.inputs['Density'].default_value = density
    vol_node.inputs['Color'].default_value = (0.8, 0.85, 0.92)

    # Connect to Volume output of World
    links.new(vol_node.outputs['Volume'], output.inputs['Volume'])

    return world


# =============================================================================
# HDRI WITH VOLUMETRIC ATMOSPHERE — Complete Lighting Setup
# =============================================================================

def setup_hdri_with_atmosphere(hdri_path, strength=1.0, atmo_density=0.003):
    """Complete setup: HDRI environment lighting + volumetric atmosphere.

    Args:
        hdri_path: Path to .hdr or .exr file
        strength: HDRI intensity
        atmo_density: Atmospheric density for god rays
    """
    # Set up HDRI world
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    # Environment Texture
    env_tex = nodes.new('ShaderNodeTexEnvironment')
    env_tex.location = (-400, 200)
    env_tex.image = bpy.data.images.load(hdri_path)

    # Mapping for rotation
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 200)

    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 200)

    # Background
    bg = nodes.new('ShaderNodeBackground')
    bg.location = (-200, 200)
    bg.inputs['Strength'].default_value = strength

    # Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)

    # Link: Coord → Mapping → Env Tex → Background → Output
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
    links.new(env_tex.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])

    # Add atmosphere domain for god rays
    atmo = create_atmosphere(density=atmo_density)

    return world, atmo
