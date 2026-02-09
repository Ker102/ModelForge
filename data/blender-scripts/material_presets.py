"""
{
  "title": "Material Presets",
  "category": "materials",
  "tags": ["material", "preset", "pbr", "texture", "common", "library"],
  "description": "Pre-configured material presets for common surfaces.",
  "blender_version": "3.0+"
}
"""
import bpy


def create_wood_material(
    name: str = "Wood",
    color: tuple = (0.35, 0.22, 0.1),
    grain_scale: float = 5.0,
    roughness: float = 0.55
) -> bpy.types.Material:
    """Create procedural wood material."""
    mat = bpy.data.materials.new(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    bsdf = nodes.get("Principled BSDF")
    
    # Wave texture for grain
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = grain_scale
    wave.inputs['Distortion'].default_value = 8.0
    wave.inputs['Detail'].default_value = 2.0
    
    # Color ramp for wood tones
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[c * 0.7 for c in color], 1.0)
    ramp.color_ramp.elements[1].color = (*color, 1.0)
    
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    bsdf.inputs['Roughness'].default_value = roughness
    
    return mat


def create_metal_material(
    name: str = "Metal",
    color: tuple = (0.8, 0.8, 0.85),
    roughness: float = 0.3,
    metal_type: str = 'STEEL'
) -> bpy.types.Material:
    """Create metal material preset."""
    colors = {
        'STEEL': (0.8, 0.8, 0.85),
        'GOLD': (1.0, 0.84, 0.0),
        'COPPER': (0.95, 0.64, 0.54),
        'BRONZE': (0.8, 0.5, 0.2),
        'IRON': (0.5, 0.5, 0.5)
    }
    
    mat = bpy.data.materials.new(name)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    final_color = colors.get(metal_type, color)
    bsdf.inputs['Base Color'].default_value = (*final_color, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = roughness
    
    return mat


def create_fabric_material(
    name: str = "Fabric",
    color: tuple = (0.3, 0.3, 0.5),
    roughness: float = 0.9,
    sheen: float = 0.3
) -> bpy.types.Material:
    """Create fabric/cloth material."""
    mat = bpy.data.materials.new(name)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Sheen Weight'].default_value = sheen
    bsdf.inputs['Sheen Tint'].default_value = 0.5
    
    return mat


def create_plastic_material(
    name: str = "Plastic",
    color: tuple = (0.8, 0.2, 0.2),
    roughness: float = 0.4,
    clearcoat: float = 0.5
) -> bpy.types.Material:
    """Create plastic material."""
    mat = bpy.data.materials.new(name)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Coat Weight'].default_value = clearcoat
    bsdf.inputs['Coat Roughness'].default_value = 0.1
    
    return mat


def create_concrete_material(
    name: str = "Concrete",
    color: tuple = (0.5, 0.5, 0.48),
    roughness: float = 0.9
) -> bpy.types.Material:
    """Create concrete material with noise."""
    mat = bpy.data.materials.new(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    bsdf = nodes.get("Principled BSDF")
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 50.0
    noise.inputs['Detail'].default_value = 10.0
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[c * 0.85 for c in color], 1.0)
    ramp.color_ramp.elements[1].color = (*color, 1.0)
    
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    bsdf.inputs['Roughness'].default_value = roughness
    
    return mat


def create_brick_material(
    name: str = "Brick",
    brick_color: tuple = (0.6, 0.25, 0.15),
    mortar_color: tuple = (0.7, 0.7, 0.65),
    scale: float = 5.0
) -> bpy.types.Material:
    """Create procedural brick material."""
    mat = bpy.data.materials.new(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    bsdf = nodes.get("Principled BSDF")
    
    brick = nodes.new('ShaderNodeTexBrick')
    brick.inputs['Scale'].default_value = scale
    brick.inputs['Mortar Size'].default_value = 0.02
    brick.inputs['Color1'].default_value = (*brick_color, 1.0)
    brick.inputs['Color2'].default_value = (*[c * 0.9 for c in brick_color], 1.0)
    brick.inputs['Mortar'].default_value = (*mortar_color, 1.0)
    
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    
    bsdf.inputs['Roughness'].default_value = 0.8
    
    return mat


def create_skin_material(
    name: str = "Skin",
    tone: str = 'MEDIUM',
    roughness: float = 0.5
) -> bpy.types.Material:
    """Create skin material with subsurface scattering."""
    tones = {
        'LIGHT': (0.95, 0.8, 0.7),
        'MEDIUM': (0.8, 0.6, 0.45),
        'DARK': (0.4, 0.25, 0.18)
    }
    
    mat = bpy.data.materials.new(name)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    color = tones.get(tone, tones['MEDIUM'])
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Subsurface Weight'].default_value = 0.3
    bsdf.inputs['Subsurface Radius'].default_value = (0.1, 0.05, 0.02)
    
    return mat


def create_water_material(name: str = "Water") -> bpy.types.Material:
    """Create water material."""
    mat = bpy.data.materials.new(name)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    bsdf.inputs['Base Color'].default_value = (0.1, 0.4, 0.6, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['IOR'].default_value = 1.33
    bsdf.inputs['Transmission Weight'].default_value = 0.9
    
    return mat
