"""
{
  "title": "Node Material Utilities",
  "category": "materials",
  "tags": ["nodes", "shader", "material", "pbr", "procedural", "texture"],
  "description": "Functions for creating shader node setups and PBR materials.",
  "blender_version": "3.0+"
}
"""
import bpy


def create_pbr_material(
    name: str = "PBR_Material",
    base_color: tuple = (0.8, 0.8, 0.8),
    metallic: float = 0.0,
    roughness: float = 0.5,
    emission_color: tuple = None,
    emission_strength: float = 0.0
) -> bpy.types.Material:
    """
    Create a basic PBR material.
    
    Args:
        name: Material name
        base_color: RGB base color
        metallic: Metallic value (0-1)
        roughness: Roughness value (0-1)
        emission_color: RGB emission color
        emission_strength: Emission intensity
    
    Returns:
        The created material
    """
    mat = bpy.data.materials.new(name)
    nodes = mat.node_tree.nodes
    
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    if emission_color and emission_strength > 0:
        bsdf.inputs['Emission Color'].default_value = (*emission_color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    
    return mat


def create_glass_material(
    name: str = "Glass",
    color: tuple = (1, 1, 1),
    ior: float = 1.45,
    roughness: float = 0.0
) -> bpy.types.Material:
    """Create glass/transparent material."""
    mat = bpy.data.materials.new(name)
    nodes = mat.node_tree.nodes
    
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['IOR'].default_value = ior
    bsdf.inputs['Transmission Weight'].default_value = 1.0
    
    mat.blend_method = 'BLEND'
    return mat


def create_metal_material(
    name: str = "Metal",
    color: tuple = (0.8, 0.8, 0.85),
    roughness: float = 0.3
) -> bpy.types.Material:
    """Create metallic material."""
    mat = create_pbr_material(
        name=name,
        base_color=color,
        metallic=1.0,
        roughness=roughness
    )
    return mat


def create_emission_material(
    name: str = "Emission",
    color: tuple = (1, 1, 1),
    strength: float = 10.0
) -> bpy.types.Material:
    """Create emissive/glow material."""
    mat = create_pbr_material(
        name=name,
        base_color=color,
        emission_color=color,
        emission_strength=strength
    )
    return mat


def add_image_texture(
    material: bpy.types.Material,
    image_path: str,
    connection: str = 'BASE_COLOR'
) -> bpy.types.ShaderNodeTexImage:
    """
    Add image texture to material.
    
    Args:
        material: Target material
        image_path: Path to image file
        connection: 'BASE_COLOR', 'ROUGHNESS', 'NORMAL', 'METALLIC'
    
    Returns:
        The texture node
    """
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(image_path)
    
    bsdf = nodes.get("Principled BSDF")
    
    connections = {
        'BASE_COLOR': 'Base Color',
        'ROUGHNESS': 'Roughness',
        'METALLIC': 'Metallic',
    }
    
    if connection == 'NORMAL':
        normal_map = nodes.new('ShaderNodeNormalMap')
        links.new(tex.outputs['Color'], normal_map.inputs['Color'])
        links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
    elif connection in connections:
        links.new(tex.outputs['Color'], bsdf.inputs[connections[connection]])
    
    return tex


def create_procedural_noise_material(
    name: str = "ProceduralNoise",
    color1: tuple = (0.2, 0.2, 0.2),
    color2: tuple = (0.8, 0.8, 0.8),
    scale: float = 5.0,
    detail: float = 2.0
) -> bpy.types.Material:
    """Create material with procedural noise texture."""
    mat = bpy.data.materials.new(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Noise texture
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = detail
    
    # Color ramp
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*color1, 1.0)
    ramp.color_ramp.elements[1].color = (*color2, 1.0)
    
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    
    bsdf = nodes.get("Principled BSDF")
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    return mat


def create_gradient_material(
    name: str = "Gradient",
    color1: tuple = (0, 0, 0),
    color2: tuple = (1, 1, 1),
    gradient_type: str = 'LINEAR'
) -> bpy.types.Material:
    """Create gradient material."""
    mat = bpy.data.materials.new(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    gradient = nodes.new('ShaderNodeTexGradient')
    gradient.gradient_type = gradient_type
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*color1, 1.0)
    ramp.color_ramp.elements[1].color = (*color2, 1.0)
    
    links.new(coord.outputs['UV'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Fac'], ramp.inputs['Fac'])
    
    bsdf = nodes.get("Principled BSDF")
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    return mat


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    """Assign material to object."""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)
