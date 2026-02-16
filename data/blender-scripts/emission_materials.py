"""
{
  "title": "Emission Material Best Practices",
  "category": "materials",
  "tags": ["emission", "glow", "emissive", "light", "neon", "fire", "star", "sun", "lava", "screen"],
  "description": "Best practices for creating emissive materials in Blender that retain their color in Material Preview mode. Covers suns, neon lights, fire, lava, glowing screens, and more.",
  "blender_version": "4.0+"
}
"""
import bpy
import math


# =============================================================================
# EMISSION MATERIAL BEST PRACTICES
# =============================================================================
#
# PROBLEM: When Emission Strength is too high (>10), the material appears
# white in Material Preview mode because the emission overwhelms the color.
# This is especially common with suns, stars, and glowing objects.
#
# SOLUTION: Always use these rules:
# 1. Set BOTH "Base Color" AND "Emission Color" to the SAME saturated color
# 2. Keep Emission Strength between 3–8 for Material Preview
# 3. For stronger glow, add a Point Light INSIDE or near the object instead
# 4. Never rely on emission alone — always set a vibrant Base Color too
#
# RECOMMENDED EMISSION STRENGTHS:
# - Subtle glow (screens, indicators):  1–3
# - Medium glow (neon signs, lamps):    3–6
# - Strong glow (fire, lava, stars):    5–8
# - Point light supplement:             Add a Point Light with energy 500–2000
#
# BAD:  emission_strength=15, base_color=(1,1,1) → appears pure white
# GOOD: emission_strength=5,  base_color=(1,0.85,0.2) + emission_color=(1,0.85,0.2) → visible yellow
# =============================================================================


def create_glow_material(
    name: str,
    color: tuple,
    emission_strength: float = 5.0,
    roughness: float = 0.5
) -> bpy.types.Material:
    """
    Create an emissive material that retains its color in Material Preview.
    
    Sets both Base Color and Emission Color to the same saturated value,
    preventing the white-wash effect at moderate emission strengths.
    
    Args:
        name: Material name
        color: RGB or RGBA tuple — use SATURATED colors, not white
        emission_strength: 3–8 recommended. Above 10 washes out in viewport.
        roughness: Surface roughness (lower = shinier glow surface)
    
    Returns:
        The created material
    """
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    rgba = color if len(color) == 4 else (*color, 1.0)
    
    if bsdf:
        # Set base color to retain color identity even without emission
        bsdf.inputs['Base Color'].default_value = rgba
        bsdf.inputs['Roughness'].default_value = roughness
        
        # Set emission color to SAME saturated color
        bsdf.inputs['Emission Color'].default_value = rgba
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    
    return mat


def create_sun_material(
    name: str = "Sun_Material",
    color: tuple = (1.0, 0.85, 0.2),
    strength: float = 5.0
) -> bpy.types.Material:
    """
    Create a sun/star material that glows yellow (not white).
    
    Uses moderate emission strength (5) and supplements with a Point Light
    inside the sphere for scene illumination.
    
    Pattern:
        sun_mat = create_sun_material("Sun", (1.0, 0.85, 0.2), strength=5)
        sun_obj.data.materials.append(sun_mat)
        
        # Add a point light inside for actual illumination
        bpy.ops.object.light_add(type='POINT', location=sun_obj.location)
        light = bpy.context.active_object
        light.data.energy = 1000
        light.data.color = (1.0, 0.9, 0.6)
    """
    return create_glow_material(name, color, emission_strength=strength, roughness=0.0)


def create_neon_material(
    name: str = "Neon_Material",
    color: tuple = (0.1, 0.3, 1.0),
    strength: float = 5.0
) -> bpy.types.Material:
    """
    Create a neon sign / tube light material.
    
    Neon colors should be highly saturated:
        Red neon:    (1.0, 0.1, 0.05)
        Blue neon:   (0.1, 0.3, 1.0)
        Green neon:  (0.1, 1.0, 0.2)
        Pink neon:   (1.0, 0.1, 0.5)
        Purple neon: (0.6, 0.1, 1.0)
        Cyan neon:   (0.0, 0.9, 1.0)
    """
    return create_glow_material(name, color, emission_strength=strength, roughness=0.0)


def create_fire_material(
    name: str = "Fire_Material",
    intensity: str = "MEDIUM"
) -> bpy.types.Material:
    """
    Create a fire/lava emissive material.
    
    Intensity presets:
        EMBER:  dark red-orange glow, strength 3
        MEDIUM: orange flame, strength 5
        HOT:    bright yellow-white core, strength 8
    
    For best results, pair with a Point Light (energy 500, warm color).
    """
    presets = {
        'EMBER':  ((0.8, 0.2, 0.0), 3.0),
        'MEDIUM': ((1.0, 0.45, 0.05), 5.0),
        'HOT':    ((1.0, 0.75, 0.2), 8.0),
    }
    color, strength = presets.get(intensity, presets['MEDIUM'])
    return create_glow_material(name, color, emission_strength=strength, roughness=0.3)


def create_screen_material(
    name: str = "Screen_Material",
    color: tuple = (0.2, 0.5, 1.0),
    brightness: float = 2.0
) -> bpy.types.Material:
    """
    Create a computer/TV screen emissive material.
    
    Uses low emission strength (1–3) for a subtle screen glow.
    
    Common screen colors:
        Blue screen:  (0.2, 0.5, 1.0)  — idle/loading screen
        Green screen: (0.1, 0.8, 0.3)  — terminal/matrix
        White screen: (0.9, 0.9, 0.95) — bright display
        Red alert:    (0.9, 0.1, 0.05) — warning display
    """
    return create_glow_material(name, color, emission_strength=brightness, roughness=0.0)


# =============================================================================
# COMPLETE EXAMPLE: Glowing Sun with Point Light
# =============================================================================
#
# import bpy
#
# # Create sun sphere
# bpy.ops.mesh.primitive_uv_sphere_add(radius=4, location=(0, 0, 0))
# sun = bpy.context.active_object
# sun.name = "Sun"
# bpy.ops.object.shade_smooth()
#
# # Apply sun material — SATURATED YELLOW, strength 5 (NOT 15!)
# sun_mat = bpy.data.materials.new(name="Sun_Material")
# bsdf = sun_mat.node_tree.nodes.get("Principled BSDF")
# bsdf.inputs['Base Color'].default_value = (1.0, 0.85, 0.2, 1.0)
# bsdf.inputs['Emission Color'].default_value = (1.0, 0.85, 0.2, 1.0)
# bsdf.inputs['Emission Strength'].default_value = 5.0
# bsdf.inputs['Roughness'].default_value = 0.0
# sun.data.materials.append(sun_mat)
#
# # Add a point light inside for actual scene illumination
# bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
# light = bpy.context.active_object
# light.name = "Sun_Light"
# light.data.energy = 1500
# light.data.color = (1.0, 0.92, 0.7)
# light.data.shadow_soft_size = 4.0
#
# Result: Sun appears BRIGHT YELLOW (not white) with a warm glow in the scene.
# =============================================================================
