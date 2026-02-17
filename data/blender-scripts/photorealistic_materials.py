"""
Photorealistic PBR Texture Materials — Blender 4.0/5.0
======================================================
Category: materials
Blender: 4.0+ / 5.0
Source: cgbookcase.com PBR guide + Blender docs

Complete image-based PBR material workflows for photorealistic rendering.
Teaches how to set up materials using texture maps (not just procedural).

PBR TEXTURE MAP CONNECTIONS:
| Map Type       | Destination                    | Color Space |
|----------------|--------------------------------|-------------|
| Base Color     | Principled BSDF → Base Color   | sRGB/Color  |
| Roughness      | Principled BSDF → Roughness    | Non-Color   |
| Metallic       | Principled BSDF → Metallic     | Non-Color   |
| Normal Map     | Normal Map node → Principled   | Non-Color   |
| Height/Bump    | Bump node → Principled Normal  | Non-Color   |
| Displacement   | Displacement → Material Output | Non-Color   |
| AO             | Mix(Multiply) with Base Color  | Non-Color   |
| Opacity        | Mix Shader (Principled+Transp) | Non-Color   |

CRITICAL RULES:
- ALL non-color maps MUST have color_space set to 'Non-Color'
- Base Color is the ONLY map that stays 'sRGB' (or 'Color')
- Normal maps need a Normal Map node (NOT directly to Principled)
- Height maps need either Bump node (fake) or Displacement node (real)
"""

import bpy
import os


def create_pbr_material(name, textures_dir,
                         base_color_file=None,
                         roughness_file=None,
                         metallic_file=None,
                         normal_file=None,
                         height_file=None,
                         ao_file=None,
                         displacement_scale=0.1):
    """Create a full PBR material from image texture files.

    This function creates a production-ready PBR material by loading
    texture map files and connecting them to the Principled BSDF.

    Args:
        name: Material name
        textures_dir: Directory containing texture files
        base_color_file: Filename for albedo/diffuse map (sRGB)
        roughness_file: Filename for roughness map (Non-Color)
        metallic_file: Filename for metallic map (Non-Color)
        normal_file: Filename for normal map (Non-Color)
        height_file: Filename for height/bump map (Non-Color)
        ao_file: Filename for ambient occlusion map (Non-Color)
        displacement_scale: Scale for true displacement
    """
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Core nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Texture Coordinate + Mapping for UV control
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1200, 0)
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-1000, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    y_offset = 300
    x_base = -600

    # --- Base Color (sRGB) ---
    if base_color_file:
        bc_tex = _add_image_texture(
            nodes, links, mapping,
            os.path.join(textures_dir, base_color_file),
            color_space='sRGB',
            location=(x_base, y_offset)
        )
        # If AO map exists, multiply it with base color
        if ao_file:
            ao_tex = _add_image_texture(
                nodes, links, mapping,
                os.path.join(textures_dir, ao_file),
                color_space='Non-Color',
                location=(x_base, y_offset - 200)
            )
            mix = nodes.new('ShaderNodeMix')
            mix.data_type = 'RGBA'
            mix.blend_type = 'MULTIPLY'
            mix.location = (x_base + 300, y_offset)
            mix.inputs[0].default_value = 1.0  # Factor
            links.new(bc_tex.outputs['Color'], mix.inputs[6])  # A
            links.new(ao_tex.outputs['Color'], mix.inputs[7])  # B
            links.new(mix.outputs[2], bsdf.inputs['Base Color'])
        else:
            links.new(bc_tex.outputs['Color'], bsdf.inputs['Base Color'])

    # --- Roughness (Non-Color) ---
    if roughness_file:
        rough_tex = _add_image_texture(
            nodes, links, mapping,
            os.path.join(textures_dir, roughness_file),
            color_space='Non-Color',
            location=(x_base, y_offset - 400)
        )
        links.new(rough_tex.outputs['Color'], bsdf.inputs['Roughness'])

    # --- Metallic (Non-Color) ---
    if metallic_file:
        metal_tex = _add_image_texture(
            nodes, links, mapping,
            os.path.join(textures_dir, metallic_file),
            color_space='Non-Color',
            location=(x_base, y_offset - 600)
        )
        links.new(metal_tex.outputs['Color'], bsdf.inputs['Metallic'])

    # --- Normal Map (Non-Color, needs Normal Map node) ---
    if normal_file:
        norm_tex = _add_image_texture(
            nodes, links, mapping,
            os.path.join(textures_dir, normal_file),
            color_space='Non-Color',
            location=(x_base, y_offset - 800)
        )
        normal_node = nodes.new('ShaderNodeNormalMap')
        normal_node.location = (x_base + 300, y_offset - 800)
        normal_node.inputs['Strength'].default_value = 1.0
        links.new(norm_tex.outputs['Color'], normal_node.inputs['Color'])
        links.new(normal_node.outputs['Normal'], bsdf.inputs['Normal'])

    # --- Height/Bump (Non-Color, uses Bump node) ---
    if height_file and not normal_file:
        # Use Bump node only if no Normal Map (they're redundant together)
        height_tex = _add_image_texture(
            nodes, links, mapping,
            os.path.join(textures_dir, height_file),
            color_space='Non-Color',
            location=(x_base, y_offset - 1000)
        )
        bump = nodes.new('ShaderNodeBump')
        bump.location = (x_base + 300, y_offset - 1000)
        bump.inputs['Strength'].default_value = 0.5
        links.new(height_tex.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # --- True Displacement (Cycles only) ---
    if height_file:
        mat.displacement_method = 'BOTH'
        height_tex_disp = _add_image_texture(
            nodes, links, mapping,
            os.path.join(textures_dir, height_file),
            color_space='Non-Color',
            location=(x_base, y_offset - 1200)
        )
        disp = nodes.new('ShaderNodeDisplacement')
        disp.location = (400, -300)
        disp.inputs['Scale'].default_value = displacement_scale
        disp.inputs['Midlevel'].default_value = 0.5
        links.new(height_tex_disp.outputs['Color'], disp.inputs['Height'])
        links.new(disp.outputs['Displacement'], output.inputs['Displacement'])

    return mat


def _add_image_texture(nodes, links, mapping_node, filepath,
                        color_space='sRGB', location=(0, 0)):
    """Helper: create an Image Texture node, load image, connect mapping."""
    tex = nodes.new('ShaderNodeTexImage')
    tex.location = location
    tex.image = bpy.data.images.load(filepath)
    tex.image.colorspace_settings.name = color_space
    links.new(mapping_node.outputs['Vector'], tex.inputs['Vector'])
    return tex


# =============================================================================
# PROCEDURAL PHOTOREALISTIC MATERIALS (no image files needed)
# =============================================================================

def create_procedural_stone_wall(name="StoneWall"):
    """Create photorealistic stone wall using only procedural textures.

    Uses layered noise + voronoi for stone pattern with mortar gaps.
    No image files needed — everything is generated procedurally.
    """
    mat = bpy.data.materials.new(name=name)
    mat.displacement_method = 'BOTH'
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 0)
    bsdf.inputs['Roughness'].default_value = 0.85
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)

    # Voronoi for stone cell pattern
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-400, 200)
    voronoi.feature = 'F1'
    voronoi.inputs['Scale'].default_value = 4.0
    voronoi.inputs['Randomness'].default_value = 0.8

    # Noise for color variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 6.0

    # Color ramp for stone vs mortar
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-100, 200)
    ramp.color_ramp.elements[0].position = 0.05
    ramp.color_ramp.elements[0].color = (0.15, 0.12, 0.10, 1)  # Mortar
    ramp.color_ramp.elements[1].position = 0.1
    ramp.color_ramp.elements[1].color = (0.5, 0.45, 0.38, 1)   # Stone

    # Mix stone color with noise variation
    mix_color = nodes.new('ShaderNodeMix')
    mix_color.location = (100, 100)
    mix_color.data_type = 'RGBA'
    mix_color.inputs[0].default_value = 0.3

    links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(voronoi.outputs['Distance'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], mix_color.inputs[6])
    links.new(noise.outputs['Color'], mix_color.inputs[7])
    links.new(mix_color.outputs[2], bsdf.inputs['Base Color'])

    # Displacement from voronoi distance
    disp = nodes.new('ShaderNodeDisplacement')
    disp.location = (400, -200)
    disp.inputs['Scale'].default_value = 0.05
    links.new(voronoi.outputs['Distance'], disp.inputs['Height'])
    links.new(disp.outputs['Displacement'], output.inputs['Displacement'])

    return mat


def create_procedural_wood_floor(name="WoodFloor"):
    """Create procedural wood planks material.

    Uses Wave Texture in BANDS mode for wood grain pattern.
    """
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 0)
    bsdf.inputs['Roughness'].default_value = 0.55
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)

    # Wave for grain lines
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-400, 100)
    wave.wave_type = 'BANDS'
    wave.wave_profile = 'SAW'
    wave.bands_direction = 'Y'
    wave.inputs['Scale'].default_value = 2.0
    wave.inputs['Distortion'].default_value = 8.0
    wave.inputs['Detail'].default_value = 3.0
    wave.inputs['Detail Scale'].default_value = 1.5

    # Color ramp for wood tones
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-100, 100)
    ramp.color_ramp.elements[0].color = (0.25, 0.15, 0.08, 1)  # Dark wood
    ramp.color_ramp.elements[1].color = (0.55, 0.35, 0.18, 1)  # Light wood

    # Subtle noise for grain variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, -100)
    noise.inputs['Scale'].default_value = 50.0
    noise.inputs['Detail'].default_value = 4.0

    # Bump for surface texture
    bump = nodes.new('ShaderNodeBump')
    bump.location = (100, -200)
    bump.inputs['Strength'].default_value = 0.3

    links.new(tex_coord.outputs['Object'], wave.inputs['Vector'])
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat
