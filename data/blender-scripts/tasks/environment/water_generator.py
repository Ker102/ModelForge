"""
{
  "title": "Water Plane Generator",
  "category": "environment",
  "subcategory": "water",
  "tags": ["water", "ocean", "lake", "procedural", "animated", "material"],
  "difficulty": "intermediate",
  "description": "Creates stylized water surfaces with animated materials.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math


def create_water_plane(
    size: float = 10.0,
    style: str = 'STYLIZED',
    color: tuple = (0.1, 0.4, 0.6),
    wave_scale: float = 2.0,
    animated: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Water"
) -> bpy.types.Object:
    """
    Create a water surface.
    
    Args:
        size: Plane size
        style: 'STYLIZED', 'REALISTIC', 'TOON'
        color: RGB water color
        wave_scale: Wave pattern scale
        animated: Add wave animation
        location: Position
        name: Object name
    
    Returns:
        The water plane object
    """
    # Create subdivided plane
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    water = bpy.context.active_object
    water.name = name
    
    # Subdivide for waves
    bpy.ops.object.modifier_add(type='SUBSURF')
    water.modifiers["Subdivision"].levels = 4
    water.modifiers["Subdivision"].render_levels = 4
    
    # Create water material
    mat = _create_water_material(name, style, color, wave_scale, animated)
    water.data.materials.append(mat)
    
    return water


def _create_water_material(
    name: str,
    style: str,
    color: tuple,
    wave_scale: float,
    animated: bool
) -> bpy.types.Material:
    """Create water shader material."""
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    
    if style == 'STYLIZED':
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.1
        bsdf.inputs['IOR'].default_value = 1.33
        bsdf.inputs['Transmission Weight'].default_value = 0.5
        
    elif style == 'REALISTIC':
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.05
        bsdf.inputs['IOR'].default_value = 1.33
        bsdf.inputs['Transmission Weight'].default_value = 0.9
        
    elif style == 'TOON':
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.5
        bsdf.inputs['Specular IOR Level'].default_value = 0.8
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Wave normal
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-400, 100)
    
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.location = (-200, 200)
    noise1.inputs['Scale'].default_value = wave_scale
    noise1.inputs['Detail'].default_value = 2.0
    
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-200, 0)
    noise2.inputs['Scale'].default_value = wave_scale * 2
    noise2.inputs['Detail'].default_value = 4.0
    
    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.location = (0, 100)
    mix.inputs['Factor'].default_value = 0.5
    
    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, 100)
    bump.inputs['Strength'].default_value = 0.3
    
    links.new(tex_coord.outputs['Generated'], noise1.inputs['Vector'])
    links.new(tex_coord.outputs['Generated'], noise2.inputs['Vector'])
    links.new(noise1.outputs['Fac'], mix.inputs[6])
    links.new(noise2.outputs['Fac'], mix.inputs[7])
    links.new(mix.outputs[2], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    # Animation driver
    if animated:
        # Add driver to noise offset
        driver = noise1.inputs['W'].driver_add('default_value')
        driver.driver.expression = 'frame / 50'
        
        driver2 = noise2.inputs['W'].driver_add('default_value')
        driver2.driver.expression = 'frame / 30'
        
        noise1.noise_dimensions = '4D'
        noise2.noise_dimensions = '4D'
    
    return mat


def create_ocean_modifier(
    plane: bpy.types.Object,
    resolution: int = 10,
    spatial_size: int = 50,
    wave_scale: float = 1.0,
    choppiness: float = 1.0
) -> bpy.types.Modifier:
    """Add ocean modifier for realistic water."""
    mod = plane.modifiers.new("Ocean", 'OCEAN')
    mod.resolution = resolution
    mod.spatial_size = spatial_size
    mod.wave_scale = wave_scale
    mod.choppiness = choppiness
    mod.use_normals = True
    mod.time = 1.0
    
    # Animate
    mod.keyframe_insert('time', frame=1)
    bpy.context.scene.frame_set(250)
    mod.time = 10.0
    mod.keyframe_insert('time', frame=250)
    bpy.context.scene.frame_set(1)
    
    return mod


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_water_plane(size=20, style='STYLIZED')
    
    print("Created water plane")
