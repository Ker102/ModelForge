"""
{
  "title": "Shader Node Utilities",
  "category": "materials",
  "tags": ["node", "shader", "material", "graph", "procedural"],
  "description": "Functions for creating and manipulating shader nodes.",
  "blender_version": "3.0+"
}
"""
import bpy


def get_material_nodes(
    material: bpy.types.Material
) -> tuple:
    """
    Get material node tree components.
    
    Returns:
        Tuple of (nodes, links)
    """
    material.use_nodes = True
    return material.node_tree.nodes, material.node_tree.links


def add_node(
    material: bpy.types.Material,
    node_type: str,
    location: tuple = (0, 0),
    name: str = None
) -> bpy.types.Node:
    """
    Add node to material.
    
    Args:
        material: Target material
        node_type: Node type (e.g., 'ShaderNodeTexNoise')
        location: Node position
        name: Optional node name
    
    Returns:
        Created node
    """
    nodes, _ = get_material_nodes(material)
    node = nodes.new(node_type)
    node.location = location
    if name:
        node.name = name
    return node


def connect_nodes(
    material: bpy.types.Material,
    from_node: str,
    from_socket: str,
    to_node: str,
    to_socket: str
) -> None:
    """
    Connect two nodes.
    
    Args:
        material: Target material
        from_node: Source node name
        from_socket: Output socket name
        to_node: Destination node name
        to_socket: Input socket name
    """
    nodes, links = get_material_nodes(material)
    
    source = nodes.get(from_node)
    dest = nodes.get(to_node)
    
    if source and dest:
        links.new(source.outputs[from_socket], dest.inputs[to_socket])


def add_mix_rgb(
    material: bpy.types.Material,
    blend_type: str = 'MIX',
    fac: float = 0.5,
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """
    Add Mix RGB node.
    
    Args:
        blend_type: 'MIX', 'ADD', 'MULTIPLY', 'SCREEN', 'OVERLAY', etc.
        fac: Mix factor
    """
    node = add_node(material, 'ShaderNodeMix', location)
    node.data_type = 'RGBA'
    node.blend_type = blend_type
    node.inputs['Factor'].default_value = fac
    return node


def add_color_ramp(
    material: bpy.types.Material,
    colors: list = None,
    positions: list = None,
    interpolation: str = 'LINEAR',
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """
    Add Color Ramp node.
    
    Args:
        colors: List of RGBA colors
        positions: List of positions (0-1)
        interpolation: 'LINEAR', 'CONSTANT', 'EASE'
    """
    node = add_node(material, 'ShaderNodeValToRGB', location)
    node.color_ramp.interpolation = interpolation
    
    if colors and positions:
        ramp = node.color_ramp
        # Clear default elements
        while len(ramp.elements) > len(colors):
            ramp.elements.remove(ramp.elements[-1])
        while len(ramp.elements) < len(colors):
            ramp.elements.new(0)
        
        for i, (color, pos) in enumerate(zip(colors, positions)):
            ramp.elements[i].position = pos
            ramp.elements[i].color = color
    
    return node


def add_noise_texture(
    material: bpy.types.Material,
    scale: float = 5.0,
    detail: float = 2.0,
    roughness: float = 0.5,
    noise_type: str = 'FBM',
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """Add Noise Texture node."""
    node = add_node(material, 'ShaderNodeTexNoise', location)
    node.inputs['Scale'].default_value = scale
    node.inputs['Detail'].default_value = detail
    node.inputs['Roughness'].default_value = roughness
    node.noise_dimensions = '3D'
    return node


def add_voronoi_texture(
    material: bpy.types.Material,
    scale: float = 5.0,
    feature: str = 'F1',
    distance: str = 'EUCLIDEAN',
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """Add Voronoi Texture node."""
    node = add_node(material, 'ShaderNodeTexVoronoi', location)
    node.inputs['Scale'].default_value = scale
    node.feature = feature
    node.distance = distance
    return node


def add_wave_texture(
    material: bpy.types.Material,
    scale: float = 5.0,
    distortion: float = 0.0,
    wave_type: str = 'BANDS',
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """Add Wave Texture node."""
    node = add_node(material, 'ShaderNodeTexWave', location)
    node.inputs['Scale'].default_value = scale
    node.inputs['Distortion'].default_value = distortion
    node.wave_type = wave_type
    return node


def add_image_texture(
    material: bpy.types.Material,
    image_path: str = None,
    image: bpy.types.Image = None,
    extension: str = 'REPEAT',
    interpolation: str = 'Linear',
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """Add Image Texture node."""
    node = add_node(material, 'ShaderNodeTexImage', location)
    
    if image_path:
        node.image = bpy.data.images.load(image_path)
    elif image:
        node.image = image
    
    node.extension = extension
    node.interpolation = interpolation
    
    return node


def add_mapping_node(
    material: bpy.types.Material,
    location_offset: tuple = (0, 0, 0),
    rotation: tuple = (0, 0, 0),
    scale: tuple = (1, 1, 1),
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """Add Mapping node for texture coordinates."""
    node = add_node(material, 'ShaderNodeMapping', location)
    node.inputs['Location'].default_value = location_offset
    node.inputs['Rotation'].default_value = rotation
    node.inputs['Scale'].default_value = scale
    return node


def add_tex_coordinate_node(
    material: bpy.types.Material,
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """Add Texture Coordinate node."""
    return add_node(material, 'ShaderNodeTexCoord', location)


def add_bump_node(
    material: bpy.types.Material,
    strength: float = 1.0,
    distance: float = 1.0,
    invert: bool = False,
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """Add Bump node."""
    node = add_node(material, 'ShaderNodeBump', location)
    node.inputs['Strength'].default_value = strength
    node.inputs['Distance'].default_value = distance
    node.invert = invert
    return node


def add_normal_map_node(
    material: bpy.types.Material,
    strength: float = 1.0,
    space: str = 'TANGENT',
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """Add Normal Map node."""
    node = add_node(material, 'ShaderNodeNormalMap', location)
    node.inputs['Strength'].default_value = strength
    node.space = space
    return node


def add_math_node(
    material: bpy.types.Material,
    operation: str = 'ADD',
    value1: float = 0.0,
    value2: float = 0.0,
    clamp: bool = False,
    location: tuple = (0, 0)
) -> bpy.types.Node:
    """
    Add Math node.
    
    Args:
        operation: 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'POWER',
                  'SINE', 'COSINE', 'MINIMUM', 'MAXIMUM', etc.
    """
    node = add_node(material, 'ShaderNodeMath', location)
    node.operation = operation
    node.inputs[0].default_value = value1
    node.inputs[1].default_value = value2
    node.use_clamp = clamp
    return node


def frame_nodes(
    material: bpy.types.Material,
    node_names: list,
    label: str = "Group"
) -> bpy.types.Node:
    """Create frame around nodes."""
    nodes, _ = get_material_nodes(material)
    frame = nodes.new('NodeFrame')
    frame.label = label
    
    for name in node_names:
        node = nodes.get(name)
        if node:
            node.parent = frame
    
    return frame
