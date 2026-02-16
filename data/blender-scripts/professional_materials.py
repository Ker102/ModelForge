"""
Professional PBR Material Recipes — Blender 4.0/5.0
=====================================================
Category: materials
Blender: 4.0+ / 5.0
Source: NotebookLM (89-source Blender knowledge base)

Complete recipes for Metallic, Dielectric, Glass, SSS, and Procedural materials
using the correct OpenPBR socket names (Blender 4.0+).

BLENDER 4.0/5.0 PRINCIPLED BSDF SOCKET REFERENCE:
| Socket Name (4.0/5.0)    | Type   | Notes                          |
|---------------------------|--------|--------------------------------|
| "Base Color"              | Color  | Unchanged                      |
| "Metallic"                | Float  | 0.0 = dielectric, 1.0 = metal |
| "Roughness"               | Float  | 0.0 = mirror, 1.0 = matte     |
| "Specular IOR Level"      | Float  | Was "Specular" in 3.x         |
| "Subsurface Weight"       | Float  | Was "Subsurface" in 3.x       |
| "Transmission Weight"     | Float  | Was "Transmission" in 3.x     |
| "Coat Weight"             | Float  | Was "Clearcoat" in 3.x        |
| "Sheen Weight"            | Float  | Was "Sheen" in 3.x            |
| "Emission Color"          | Color  | Was "Emission" in 3.x         |
| "Emission Strength"       | Float  | Unchanged                      |
| "IOR"                     | Float  | Index of Refraction            |
| "Alpha"                   | Float  | Transparency (1.0 = opaque)    |
| "Thin Film Thickness"     | Float  | NEW in 4.0 — soap bubbles      |
| "Thin Film IOR"           | Float  | NEW in 4.0                     |
"""

import bpy


# =============================================================================
# CORE SETUP FUNCTION
# =============================================================================

def create_pbr_material(name):
    """Create a clean Principled BSDF material with factory pattern.
    Returns (material, principled_node, nodes, links).
    """
    mat = bpy.data.materials.new(name=name)
    # use_nodes deprecated in 5.0, always True by default
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)

    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)

    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    return mat, principled, nodes, links


# =============================================================================
# METALLIC MATERIALS — Metallic = 1.0, Base Color = Specular Color
# =============================================================================
# For metals, Base Color represents SPECULAR reflection color (not diffuse).
# Metals have NO diffuse component. Roughness controls polish level.

METAL_RECIPES = {
    "Gold":       {"base_color": (1.0, 0.766, 0.336, 1.0), "roughness": 0.15},
    "Copper":     {"base_color": (0.955, 0.637, 0.538, 1.0), "roughness": 0.2},
    "Iron":       {"base_color": (0.560, 0.570, 0.580, 1.0), "roughness": 0.35},
    "Silver":     {"base_color": (0.972, 0.960, 0.915, 1.0), "roughness": 0.1},
    "Aluminum":   {"base_color": (0.913, 0.921, 0.925, 1.0), "roughness": 0.25},
    "Titanium":   {"base_color": (0.616, 0.582, 0.544, 1.0), "roughness": 0.3},
    "Chrome":     {"base_color": (0.550, 0.556, 0.554, 1.0), "roughness": 0.05},
    "Brass":      {"base_color": (0.887, 0.789, 0.434, 1.0), "roughness": 0.2},
    "Bronze":     {"base_color": (0.804, 0.498, 0.196, 1.0), "roughness": 0.3},
}

def create_metal(name, base_color, roughness=0.15):
    """Create a PBR metallic material. Metallic=1.0, colored base."""
    mat, bsdf, nodes, links = create_pbr_material(name)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

def create_gold():
    return create_metal("Gold", (1.0, 0.766, 0.336, 1.0), 0.15)

def create_copper():
    return create_metal("Copper", (0.955, 0.637, 0.538, 1.0), 0.2)

def create_chrome():
    return create_metal("Chrome", (0.550, 0.556, 0.554, 1.0), 0.05)


# =============================================================================
# DIELECTRIC MATERIALS — Metallic = 0.0, White Specular, Colored Diffuse
# =============================================================================
# For non-metals, Base Color = diffuse color. Specular reflection is white
# and controlled by IOR (default 1.5 = standard dielectric).

def create_plastic(name, color, roughness=0.3):
    """Create a PBR plastic material. Metallic=0, high-gloss dielectric."""
    mat, bsdf, nodes, links = create_pbr_material(name)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.5  # Standard plastic
    return mat

def create_rubber(name, color):
    """Matte rubber — high roughness, zero specular."""
    mat, bsdf, nodes, links = create_pbr_material(name)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Specular IOR Level'].default_value = 0.2
    return mat


# =============================================================================
# GLASS — Transmission Weight = 1.0, Low Roughness, IOR = 1.5
# =============================================================================
# In Blender 4.0+: Use "Transmission Weight" (was "Transmission" in 3.x).
# IOR values: Glass=1.5, Water=1.33, Diamond=2.42, Crystal=2.0.

def create_glass(name="Glass", color=(1.0, 1.0, 1.0, 1.0), ior=1.5, roughness=0.0):
    """Create physically accurate glass material."""
    mat, bsdf, nodes, links = create_pbr_material(name)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Transmission Weight'].default_value = 1.0  # Full transmission
    bsdf.inputs['IOR'].default_value = ior
    bsdf.inputs['Roughness'].default_value = roughness  # 0 = clear, 0.3 = frosted
    bsdf.inputs['Metallic'].default_value = 0.0
    return mat

def create_frosted_glass(name="FrostedGlass"):
    """Frosted glass — transmission + medium roughness."""
    return create_glass(name, roughness=0.3)

def create_water(name="Water"):
    """Water — IOR 1.33, slight tint."""
    return create_glass(name, color=(0.8, 0.9, 1.0, 1.0), ior=1.33)

def create_diamond(name="Diamond"):
    """Diamond — IOR 2.42, high dispersion."""
    return create_glass(name, ior=2.42)


# =============================================================================
# SUBSURFACE SCATTERING — Subsurface Weight = 1.0, Base Color drives SSS
# =============================================================================
# In Blender 4.0+: "Subsurface Color" socket is REMOVED.
# Base Color now drives SSS color directly.
# Use Subsurface Radius to control R/G/B scatter distances.

def create_skin(name="Skin"):
    """Human skin — SSS with warm undertone."""
    mat, bsdf, nodes, links = create_pbr_material(name)
    bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.5, 1.0)
    bsdf.inputs['Subsurface Weight'].default_value = 1.0
    bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)
    bsdf.inputs['Roughness'].default_value = 0.4
    return mat

def create_wax(name="Wax"):
    """Candle wax — strong SSS, warm tint."""
    mat, bsdf, nodes, links = create_pbr_material(name)
    bsdf.inputs['Base Color'].default_value = (0.95, 0.9, 0.7, 1.0)
    bsdf.inputs['Subsurface Weight'].default_value = 1.0
    bsdf.inputs['Subsurface Radius'].default_value = (0.8, 0.5, 0.2)
    bsdf.inputs['Roughness'].default_value = 0.5
    return mat

def create_marble(name="Marble"):
    """Marble — SSS with cool blue-white base."""
    mat, bsdf, nodes, links = create_pbr_material(name)
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.97, 1.0)
    bsdf.inputs['Subsurface Weight'].default_value = 0.5
    bsdf.inputs['Subsurface Radius'].default_value = (0.6, 0.6, 0.8)
    bsdf.inputs['Roughness'].default_value = 0.1
    return mat


# =============================================================================
# THIN FILM — NEW in Blender 4.0 (Soap Bubbles, Oil Slicks)
# =============================================================================

def create_soap_bubble(name="SoapBubble"):
    """Iridescent soap bubble using Thin Film inputs (4.0+)."""
    mat, bsdf, nodes, links = create_pbr_material(name)
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 1.0, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['Transmission Weight'].default_value = 0.9
    bsdf.inputs['Alpha'].default_value = 0.3
    bsdf.inputs['Thin Film Thickness'].default_value = 500.0  # nm
    bsdf.inputs['Thin Film IOR'].default_value = 1.4
    mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else None
    return mat


# =============================================================================
# PROCEDURAL GOLD WITH IMPERFECTIONS
# =============================================================================
# Pattern: Macro noise (color variation) + Micro noise (roughness) + Voronoi (bumps)

def create_procedural_gold(name="Procedural_Gold"):
    """Gold with micro-scratches via procedural noise on roughness."""
    if name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[name])

    mat, bsdf, nodes, links = create_pbr_material(name)

    # Texture Coordinates → Mapping → Noise
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 200)

    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 200)

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 200)
    noise.inputs['Scale'].default_value = 50.0
    noise.inputs['Detail'].default_value = 15.0
    noise.inputs['Roughness'].default_value = 0.6

    # Color Ramp to control roughness range (mostly shiny with variation)
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 200)
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.2, 0.2, 0.2, 1)

    # PBR Gold settings
    bsdf.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0

    # Link chain: TexCoord → Mapping → Noise → Ramp → Roughness
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Roughness'])

    return mat


# =============================================================================
# EMISSIVE MATERIALS — Correct 4.0/5.0 Socket Names
# =============================================================================

def create_emissive(name, color, strength=5.0):
    """Create emissive material. Use 'Emission Color' (was 'Emission' in 3.x)."""
    mat, bsdf, nodes, links = create_pbr_material(name)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Emission Color'].default_value = color  # NOT "Emission"!
    bsdf.inputs['Emission Strength'].default_value = strength
    return mat

def create_neon_glow(name="NeonGlow", color=(0.0, 1.0, 0.5, 1.0)):
    """Bright neon glow — high emission strength."""
    return create_emissive(name, color, strength=8.0)
