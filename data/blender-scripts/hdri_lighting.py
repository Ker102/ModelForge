"""
HDRI Environment & Image-Based Lighting — Blender 4.0/5.0
==========================================================
Category: lighting
Blender: 4.0+ / 5.0
Source: Blender Stack Exchange + Official Docs

HDRI (High Dynamic Range Image) environment textures for realistic
image-based lighting. Covers:
- Loading HDRI files as world environment
- Background strength + color control
- Rotation via Mapping node
- Ground projection for infinite backgrounds
- Combining HDRI with solid background (compositing trick)

NODE PATTERN FOR HDRI:
    Tex Coord → Mapping → Environment Texture → Background → World Output
                                                      ↑
                                                 Strength value

IMPORTANT NOTES:
- Environment Texture node: type = 'ShaderNodeTexEnvironment'
- NOT ShaderNodeTexImage — that's for meshes, not world backgrounds
- HDRI files typically use .hdr or .exr format
- Color space should usually be 'Linear' (default for HDR files)
- For non-HDR images used as background: set to 'sRGB'
"""

import bpy
import math


def setup_hdri_world(hdri_path, strength=1.0, rotation_z=0.0):
    """Set up HDRI environment lighting for the scene.

    This is the standard pattern for image-based lighting in Blender.
    Creates: Tex Coord → Mapping → Environment Texture → Background → Output

    Args:
        hdri_path: Path to .hdr/.exr file (absolute or relative //)
        strength: Background light intensity (1.0 = natural, 2.0 = bright)
        rotation_z: Z rotation in degrees for rotating the environment
    """
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    node_tree = world.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    nodes.clear()

    # Texture Coordinate → Mapping (for rotation control)
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-400, 0)
    mapping.inputs['Rotation'].default_value[2] = math.radians(rotation_z)

    # Environment Texture — NOT ShaderNodeTexImage!
    env_tex = nodes.new('ShaderNodeTexEnvironment')
    env_tex.location = (-200, 0)
    env_tex.image = bpy.data.images.load(hdri_path)
    # HDR files default to Linear color space — do NOT change to Non-Color

    # Background shader
    background = nodes.new('ShaderNodeBackground')
    background.location = (100, 0)
    background.inputs['Strength'].default_value = strength

    # World Output
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (300, 0)

    # Link chain
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
    links.new(env_tex.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], output.inputs['Surface'])

    return world


def setup_solid_color_world(color=(0.05, 0.05, 0.1), strength=1.0):
    """Set up a solid color world background (no HDRI needed).

    Useful for studio-style renders or when you want full lighting control.
    """
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    node_tree = world.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    nodes.clear()

    background = nodes.new('ShaderNodeBackground')
    background.location = (0, 0)
    background.inputs['Color'].default_value = (*color, 1.0)
    background.inputs['Strength'].default_value = strength

    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (200, 0)

    links.new(background.outputs['Background'], output.inputs['Surface'])
    return world


def setup_gradient_sky_world(sky_color=(0.4, 0.6, 0.9),
                              horizon_color=(0.85, 0.85, 0.9),
                              strength=1.0):
    """Create a gradient sky from horizon to zenith (no HDRI file needed).

    Uses ColorRamp + Texture Coordinate to create a natural sky gradient.
    Good for outdoor scenes without a specific HDRI.
    """
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    node_tree = world.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    nodes.clear()

    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    separate = nodes.new('ShaderNodeSeparateXYZ')
    separate.location = (-400, 0)

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (*horizon_color, 1.0)
    ramp.color_ramp.elements[1].position = 0.6
    ramp.color_ramp.elements[1].color = (*sky_color, 1.0)

    background = nodes.new('ShaderNodeBackground')
    background.location = (100, 0)
    background.inputs['Strength'].default_value = strength

    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (300, 0)

    links.new(tex_coord.outputs['Generated'], separate.inputs['Vector'])
    links.new(separate.outputs['Z'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], background.inputs['Color'])
    links.new(background.outputs['Background'], output.inputs['Surface'])

    return world
