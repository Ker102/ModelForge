"""
Displacement & Surface Texture Recipes — Blender 4.0/5.0
=========================================================
Category: materials
Blender: 4.0+ / 5.0
Source: Blender API Docs + Stack Exchange best practices

Procedural displacement patterns for terrain, raked sand, water ripples,
rocky surfaces, and other surface deformations using shader nodes.

TWO METHODS FOR SURFACE DEFORMATION:
1. Shader Displacement (node-based, no mesh change, render-only in Cycles)
   - ShaderNodeDisplacement → Material Output 'Displacement' input
   - Requires: material.displacement_method = 'DISPLACEMENT' or 'BOTH'
   - Works in Cycles only (EEVEE uses bump approximation)

2. Modifier Displacement (mesh-level, works everywhere)
   - Subdivision Surface modifier + Displace modifier
   - Uses bpy.data.textures for pattern source
   - Visible in viewport and all render engines

SHADER NODE REFERENCE:
| Node Type                    | Key Properties                          |
|------------------------------|-----------------------------------------|
| ShaderNodeTexWave            | wave_type: BANDS/RINGS                  |
|                              | wave_profile: SIN/SAW/TRI               |
|                              | bands_direction: X/Y/Z/DIAGONAL         |
|                              | Inputs: Scale, Distortion, Detail       |
| ShaderNodeTexNoise           | Inputs: Scale, Detail, Roughness        |
| ShaderNodeDisplacement       | space: OBJECT/WORLD                     |
|                              | Inputs: Height, Midlevel, Scale, Normal |
| ShaderNodeTexMusgrave        | REMOVED in Blender 4.1+                 |
|                              | Use ShaderNodeTexNoise instead          |
"""

import bpy


# =============================================================================
# SHADER-BASED DISPLACEMENT (Cycles)
# =============================================================================

def create_raked_sand_material(name="RakedSand", scale=8.0, distortion=2.0):
    """Create raked sand/zen garden material with wave displacement.

    Uses ShaderNodeTexWave (BANDS, SIN profile) for parallel rake lines,
    mixed with subtle noise for natural variation.
    Connects to Material Output Displacement socket for true displacement.
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.displacement_method = 'BOTH'  # Bump + true displacement
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Output + Principled
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Base Color'].default_value = (0.76, 0.70, 0.58, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Texture Coordinates
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)

    # Wave Texture — parallel rake lines
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-400, 100)
    wave.wave_type = 'BANDS'
    wave.wave_profile = 'SIN'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = scale
    wave.inputs['Distortion'].default_value = distortion
    wave.inputs['Detail'].default_value = 3.0
    wave.inputs['Detail Scale'].default_value = 1.5

    # Noise for natural variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, -100)
    noise.inputs['Scale'].default_value = 25.0
    noise.inputs['Detail'].default_value = 4.0
    noise.inputs['Roughness'].default_value = 0.6

    # Mix wave + noise
    mix = nodes.new('ShaderNodeMix')
    mix.location = (-200, 0)
    mix.data_type = 'FLOAT'
    mix.inputs[0].default_value = 0.7  # Factor: mostly wave
    links.new(wave.outputs['Fac'], mix.inputs[2])  # A
    links.new(noise.outputs['Fac'], mix.inputs[3])  # B

    # Displacement node
    disp = nodes.new('ShaderNodeDisplacement')
    disp.location = (200, -200)
    disp.inputs['Scale'].default_value = 0.05
    disp.inputs['Midlevel'].default_value = 0.5

    links.new(tex_coord.outputs['Object'], wave.inputs['Vector'])
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(mix.outputs[0], disp.inputs['Height'])
    links.new(disp.outputs['Displacement'], output.inputs['Displacement'])

    return mat


def create_water_ripple_material(name="WaterRipple"):
    """Create concentric water ripple displacement using RINGS wave type."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.displacement_method = 'BOTH'
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Base Color'].default_value = (0.1, 0.3, 0.5, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Transmission Weight'].default_value = 0.6
    bsdf.inputs['IOR'].default_value = 1.33
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-400, 0)
    wave.wave_type = 'RINGS'
    wave.wave_profile = 'SIN'
    wave.inputs['Scale'].default_value = 12.0
    wave.inputs['Distortion'].default_value = 1.0
    wave.inputs['Detail'].default_value = 2.0

    disp = nodes.new('ShaderNodeDisplacement')
    disp.location = (200, -200)
    disp.inputs['Scale'].default_value = 0.03

    links.new(wave.outputs['Fac'], disp.inputs['Height'])
    links.new(disp.outputs['Displacement'], output.inputs['Displacement'])

    return mat


def create_rocky_surface_material(name="RockySurface"):
    """Create rough rocky terrain using noise displacement + bump."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.displacement_method = 'BOTH'
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Base Color'].default_value = (0.35, 0.30, 0.25, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)

    # Large-scale noise for terrain shape
    noise_large = nodes.new('ShaderNodeTexNoise')
    noise_large.location = (-400, 100)
    noise_large.inputs['Scale'].default_value = 3.0
    noise_large.inputs['Detail'].default_value = 8.0
    noise_large.inputs['Roughness'].default_value = 0.7

    # Small-scale noise for surface detail
    noise_small = nodes.new('ShaderNodeTexNoise')
    noise_small.location = (-400, -100)
    noise_small.inputs['Scale'].default_value = 20.0
    noise_small.inputs['Detail'].default_value = 12.0
    noise_small.inputs['Roughness'].default_value = 0.8

    # Mix large + small
    mix = nodes.new('ShaderNodeMix')
    mix.location = (-200, 0)
    mix.data_type = 'FLOAT'
    mix.inputs[0].default_value = 0.3
    links.new(noise_large.outputs['Fac'], mix.inputs[2])
    links.new(noise_small.outputs['Fac'], mix.inputs[3])

    disp = nodes.new('ShaderNodeDisplacement')
    disp.location = (200, -200)
    disp.inputs['Scale'].default_value = 0.15

    links.new(tex_coord.outputs['Object'], noise_large.inputs['Vector'])
    links.new(tex_coord.outputs['Object'], noise_small.inputs['Vector'])
    links.new(mix.outputs[0], disp.inputs['Height'])
    links.new(disp.outputs['Displacement'], output.inputs['Displacement'])

    return mat


# =============================================================================
# MODIFIER-BASED DISPLACEMENT (works in EEVEE + viewport)
# =============================================================================

def add_wave_displacement_modifier(obj, texture_type='WAVES',
                                   scale=0.1, subdivisions=4):
    """Add modifier-based displacement using Subdivision + Displace.

    This method works in EEVEE and is visible in the viewport.
    Good for: terrain, raked sand, rippled surfaces.

    Args:
        obj: Target mesh object
        texture_type: 'WAVES', 'NOISE', 'VORONOI', 'CLOUDS'
        scale: Displacement strength
        subdivisions: Subdivision level (higher = smoother)
    """
    # Add subdivision for geometry detail
    subsurf = obj.modifiers.new(name="Subdiv", type='SUBSURF')
    subsurf.levels = subdivisions
    subsurf.render_levels = subdivisions + 1

    # Create displacement texture
    tex = bpy.data.textures.new(name=f"{obj.name}_DispTex", type=texture_type)

    if texture_type == 'WAVES':
        # Blender internal texture for modifier displacement
        # Note: This uses bpy.data.textures, NOT shader nodes
        pass  # WAVES type has built-in wave pattern
    elif texture_type == 'NOISE':
        tex.noise_scale = 0.5
    elif texture_type == 'VORONOI':
        tex.noise_intensity = 1.0
    elif texture_type == 'CLOUDS':
        tex.noise_scale = 0.5
        tex.noise_depth = 3

    # Add displace modifier
    displace = obj.modifiers.new(name="Displace", type='DISPLACE')
    displace.texture = tex
    displace.strength = scale
    displace.mid_level = 0.5

    return subsurf, displace


def create_terrain_plane(name="Terrain", size=10, subdivisions=5,
                         noise_scale=0.3):
    """Create a subdivided plane with noise displacement for terrain.

    Creates a ready-to-use terrain mesh with modifier-based displacement.
    Works in both EEVEE and Cycles, visible in viewport.
    """
    # Create subdivided plane
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    terrain = bpy.context.active_object
    terrain.name = name

    # Add subdivision + displacement
    add_wave_displacement_modifier(
        terrain,
        texture_type='NOISE',
        scale=noise_scale,
        subdivisions=subdivisions
    )

    # Add earth-tone material
    mat = bpy.data.materials.new(name=f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.4, 0.32, 0.2, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    terrain.data.materials.append(mat)

    return terrain


def create_raked_sand_plane(name="RakedSandFloor", size=10):
    """Create a zen garden raked sand floor plane.

    Uses modifier-based displacement visible in EEVEE and viewport.
    Combines wave pattern (rake lines) with subtle noise (natural grain).
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    sand = bpy.context.active_object
    sand.name = name

    # Subdivision for detail
    subsurf = sand.modifiers.new(name="Subdiv", type='SUBSURF')
    subsurf.levels = 5
    subsurf.render_levels = 6

    # Wave displacement for rake lines
    wave_tex = bpy.data.textures.new(name="RakeWaves", type='WAVES')
    wave_disp = sand.modifiers.new(name="RakeLines", type='DISPLACE')
    wave_disp.texture = wave_tex
    wave_disp.strength = 0.04
    wave_disp.mid_level = 0.5

    # Subtle noise for natural grain
    noise_tex = bpy.data.textures.new(name="SandGrain", type='NOISE')
    noise_disp = sand.modifiers.new(name="SandGrain", type='DISPLACE')
    noise_disp.texture = noise_tex
    noise_disp.strength = 0.01
    noise_disp.mid_level = 0.5

    # Sand material
    mat = bpy.data.materials.new(name="SandMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.76, 0.70, 0.58, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    sand.data.materials.append(mat)

    return sand
