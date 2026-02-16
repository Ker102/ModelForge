"""
{
  "title": "Procedural Shader Node Recipes",
  "category": "materials",
  "tags": ["procedural", "shader", "nodes", "noise", "voronoi", "gradient", "color ramp", "bump", "displacement", "PBR", "texture"],
  "description": "Professional procedural material recipes using Blender shader nodes. Covers noise-based textures, voronoi patterns (stone, scales), gradient effects, bump mapping, color ramp techniques, and multi-material mixing. All created via Python scripting without external textures. Inspired by CGWire shader guide and Blender best practices.",
  "blender_version": "4.0+"
}
"""
import bpy
import random


# =============================================================================
# PROCEDURAL SHADER NODE RECIPES
# =============================================================================
#
# PROCEDURAL MATERIALS = Math, not images.
# Benefits:
#   - Infinite resolution (no pixel limit)
#   - Fully parametric (change Scale → different look)
#   - Animatable (change values over time)
#   - No texture files needed
#
# KEY NODES:
#   - Noise Texture:    organic patterns (wood grain, clouds, dirt)
#   - Voronoi Texture:  cell patterns (stone, scales, cracks, tiles)
#   - Wave Texture:     stripes, rings (water ripples, wood rings)
#   - Gradient Texture: smooth interpolation (sky, fade effects)
#   - Color Ramp:       remap any value to colors (THE most useful node)
#   - Bump:             fake surface detail without geometry
#   - Mapping:          scale, rotate, offset textures
#
# CONNECTING NODES (Python):
#   links = mat.node_tree.links
#   links.new(source_node.outputs['Fac'], target_node.inputs['Fac'])
#   links.new(source_node.outputs['Color'], target_node.inputs['Base Color'])
# =============================================================================


def create_procedural_noise_material(
    name="ProceduralNoise",
    color1=(0.02, 0.02, 0.03),
    color2=(0.6, 0.35, 0.1),
    noise_scale=5.0,
    noise_detail=10.0,
    roughness=0.4,
    metallic=0.0,
    bump_strength=0.3
):
    """
    Create a noise-based procedural material with color ramp and bump.
    
    Great for: organic surfaces, dirt, rust, wood grain, stone variation.
    
    Args:
        name: Material name
        color1: Dark color in the ramp
        color2: Light color in the ramp
        noise_scale: Noise pattern scale (smaller = larger features)
        noise_detail: Noise complexity (higher = more detail)
        roughness: Surface roughness
        metallic: Metallic amount
        bump_strength: Bump map intensity (0 = flat, 1 = strong)
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Noise Texture
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-500, 0)
    noise.inputs['Scale'].default_value = noise_scale
    noise.inputs['Detail'].default_value = noise_detail
    
    # Color Ramp (maps noise to two colors)
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (*color1, 1.0)
    ramp.color_ramp.elements[1].color = (*color2, 1.0)
    
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Bump map using noise
    if bump_strength > 0:
        bump = nodes.new('ShaderNodeBump')
        bump.location = (100, -200)
        bump.inputs['Strength'].default_value = bump_strength
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    return mat


def create_voronoi_stone_material(
    name="VoronoiStone",
    color1=(0.3, 0.28, 0.25),
    color2=(0.5, 0.48, 0.42),
    scale=3.0,
    roughness=0.85,
    bump_strength=0.5
):
    """
    Create a stone/tile material using Voronoi texture.
    
    Voronoi naturally creates cell-like patterns perfect for:
    stone tiles, dragon scales, cracked earth, cobblestones.
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Roughness'].default_value = roughness
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Voronoi Texture
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-500, 0)
    voronoi.inputs['Scale'].default_value = scale
    voronoi.feature = 'F1'  # Closest point distance
    
    # Color Ramp
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (*color1, 1.0)
    ramp.color_ramp.elements[1].color = (*color2, 1.0)
    
    links.new(voronoi.outputs['Distance'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Bump from voronoi for surface detail
    bump = nodes.new('ShaderNodeBump')
    bump.location = (100, -200)
    bump.inputs['Strength'].default_value = bump_strength
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    return mat


def create_gradient_sky_material(
    name="GradientSky",
    top_color=(0.1, 0.2, 0.6),
    bottom_color=(0.8, 0.65, 0.4),
    blend_position=0.5
):
    """
    Create a gradient material (useful for sky backgrounds, fade effects).
    
    Uses Generated texture coordinates with a gradient for smooth blending.
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Texture Coordinate + Gradient
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-700, 0)
    
    gradient = nodes.new('ShaderNodeTexGradient')
    gradient.location = (-500, 0)
    gradient.gradient_type = 'LINEAR'
    
    # Separate XYZ to get Z (height)
    separate = nodes.new('ShaderNodeSeparateXYZ')
    separate.location = (-500, -200)
    links.new(tex_coord.outputs['Generated'], separate.inputs['Vector'])
    
    # Color Ramp for gradient colors
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*bottom_color, 1.0)
    ramp.color_ramp.elements[1].position = blend_position
    ramp.color_ramp.elements[1].color = (*top_color, 1.0)
    
    links.new(separate.outputs['Z'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    return mat


def create_worn_metal_material(
    name="WornMetal",
    metal_color=(0.6, 0.55, 0.5),
    rust_color=(0.35, 0.15, 0.05),
    wear_amount=0.4,
    base_roughness=0.2,
    rust_roughness=0.75
):
    """
    Create a worn/rusted metal material using noise-driven mixing.
    
    Uses noise texture to blend between clean metal and rusty areas.
    Great for: weathered machinery, old robots, medieval armor.
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Metallic'].default_value = 1.0
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Noise for wear mask
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-600, -200)
    noise.inputs['Scale'].default_value = 4.0
    noise.inputs['Detail'].default_value = 12.0
    noise.inputs['Roughness'].default_value = 0.7
    
    # Color Ramp to control wear threshold
    wear_mask = nodes.new('ShaderNodeValToRGB')
    wear_mask.location = (-300, -200)
    wear_mask.color_ramp.elements[0].position = wear_amount - 0.1
    wear_mask.color_ramp.elements[1].position = wear_amount + 0.1
    links.new(noise.outputs['Fac'], wear_mask.inputs['Fac'])
    
    # Mix Color nodes for base color and roughness
    # Use ShaderNodeMix (Blender 4.0+ — replaces old MixRGB)
    mix_color = nodes.new('ShaderNodeMix')
    mix_color.data_type = 'RGBA'
    mix_color.location = (0, 100)
    mix_color.inputs[6].default_value = (*metal_color, 1.0)  # A
    mix_color.inputs[7].default_value = (*rust_color, 1.0)   # B
    links.new(wear_mask.outputs['Color'], mix_color.inputs[0])  # Factor
    links.new(mix_color.outputs[2], bsdf.inputs['Base Color'])  # Result
    
    # Mix roughness
    mix_rough = nodes.new('ShaderNodeMix')
    mix_rough.data_type = 'FLOAT'
    mix_rough.location = (0, -100)
    mix_rough.inputs[2].default_value = base_roughness  # A
    mix_rough.inputs[3].default_value = rust_roughness   # B
    links.new(wear_mask.outputs['Color'], mix_rough.inputs[0])
    links.new(mix_rough.outputs[0], bsdf.inputs['Roughness'])
    
    # Bump
    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, -300)
    bump.inputs['Strength'].default_value = 0.4
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    return mat


def apply_random_color_variation(obj, base_color=(0.5, 0.5, 0.5), variation=0.1):
    """
    Apply a material with slight random color variation to an object.
    
    Useful for applying variation across many similar objects (bricks,
    leaves, crowd characters) without creating unique textures.
    """
    r = max(0, min(1, base_color[0] + random.uniform(-variation, variation)))
    g = max(0, min(1, base_color[1] + random.uniform(-variation, variation)))
    b = max(0, min(1, base_color[2] + random.uniform(-variation, variation)))
    
    mat = bpy.data.materials.new(name=f"{obj.name}_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (r, g, b, 1.0)
    
    obj.data.materials.append(mat)
    return mat


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

# --- Example: Worn metal robot ---
# mat = create_worn_metal_material(
#     name="RobotArmor",
#     metal_color=(0.3, 0.35, 0.4),  # Steel blue
#     rust_color=(0.4, 0.2, 0.08),   # Rust brown
#     wear_amount=0.5
# )
# bpy.context.active_object.data.materials.append(mat)

# --- Example: Alien stone floor ---
# mat = create_voronoi_stone_material(
#     name="AlienStone",
#     color1=(0.1, 0.15, 0.1),
#     color2=(0.2, 0.35, 0.15),
#     scale=5.0,
#     bump_strength=0.8
# )

# --- Example: Apply random variations to all selected objects ---
# for obj in bpy.context.selected_objects:
#     if obj.type == 'MESH':
#         apply_random_color_variation(obj, base_color=(0.8, 0.2, 0.1), variation=0.15)
