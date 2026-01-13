"""
{
  "title": "Geometry Nodes Utilities",
  "category": "nodes",
  "tags": ["geometry", "nodes", "procedural", "modifier", "geonodes"],
  "description": "Functions for creating and managing Geometry Nodes.",
  "blender_version": "3.0+"
}
"""
import bpy


def add_geometry_nodes_modifier(
    obj: bpy.types.Object,
    name: str = "GeometryNodes"
) -> tuple:
    """
    Add Geometry Nodes modifier to object.
    
    Args:
        obj: Target object
        name: Modifier name
    
    Returns:
        Tuple of (modifier, node_group)
    """
    mod = obj.modifiers.new(name, 'NODES')
    
    # Create node group
    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    mod.node_group = group
    
    # Add input/output nodes
    group_input = group.nodes.new('NodeGroupInput')
    group_input.location = (-200, 0)
    
    group_output = group.nodes.new('NodeGroupOutput')
    group_output.location = (200, 0)
    
    # Add geometry socket
    group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # Connect input to output
    group.links.new(group_input.outputs['Geometry'], group_output.inputs['Geometry'])
    
    return mod, group


def add_gn_node(
    group: bpy.types.NodeTree,
    node_type: str,
    location: tuple = (0, 0),
    name: str = None
) -> bpy.types.Node:
    """
    Add node to geometry node tree.
    
    Args:
        group: Node group
        node_type: Node type (e.g., 'GeometryNodeMeshPrimitiveCube')
        location: Node position
        name: Optional node name
    
    Returns:
        Created node
    """
    node = group.nodes.new(node_type)
    node.location = location
    if name:
        node.name = name
    return node


def connect_gn_nodes(
    group: bpy.types.NodeTree,
    from_node: str,
    from_socket: str,
    to_node: str,
    to_socket: str
) -> None:
    """Connect two geometry nodes."""
    source = group.nodes.get(from_node)
    dest = group.nodes.get(to_node)
    
    if source and dest:
        group.links.new(source.outputs[from_socket], dest.inputs[to_socket])


def add_gn_input(
    group: bpy.types.NodeTree,
    name: str,
    socket_type: str,
    default_value = None
) -> None:
    """
    Add input socket to geometry node group.
    
    Args:
        group: Node group
        name: Input name
        socket_type: 'NodeSocketFloat', 'NodeSocketVector', 'NodeSocketInt', etc.
        default_value: Optional default value
    """
    socket = group.interface.new_socket(name, in_out='INPUT', socket_type=socket_type)
    if default_value is not None:
        socket.default_value = default_value


def add_gn_scatter_setup(
    obj: bpy.types.Object,
    density: float = 10.0,
    scale: float = 1.0,
    seed: int = 0
) -> bpy.types.Modifier:
    """
    Add point scatter setup to object.
    
    Args:
        obj: Target object
        density: Points per unit area
        scale: Instance scale
        seed: Random seed
    
    Returns:
        The geometry nodes modifier
    """
    mod, group = add_geometry_nodes_modifier(obj, "Scatter")
    
    # Get input/output
    group_input = group.nodes.get('Group Input')
    group_output = group.nodes.get('Group Output')
    
    # Distribute points
    distribute = add_gn_node(group, 'GeometryNodeDistributePointsOnFaces', (-100, 0))
    distribute.distribute_method = 'RANDOM'
    distribute.inputs['Density'].default_value = density
    distribute.inputs['Seed'].default_value = seed
    
    # Instance on points
    instance = add_gn_node(group, 'GeometryNodeInstanceOnPoints', (100, 0))
    
    # Join geometry
    join = add_gn_node(group, 'GeometryNodeJoinGeometry', (300, 0))
    
    # Connect
    group.links.new(group_input.outputs['Geometry'], distribute.inputs['Mesh'])
    group.links.new(distribute.outputs['Points'], instance.inputs['Points'])
    group.links.new(group_input.outputs['Geometry'], join.inputs['Geometry'])
    group.links.new(instance.outputs['Instances'], join.inputs['Geometry'])
    group.links.new(join.outputs['Geometry'], group_output.inputs['Geometry'])
    
    # Add instance input
    add_gn_input(group, 'Instance', 'NodeSocketGeometry')
    
    return mod


def add_gn_extrude_setup(
    obj: bpy.types.Object,
    height: float = 0.5,
    individual: bool = False
) -> bpy.types.Modifier:
    """
    Add extrude along normals setup.
    
    Args:
        obj: Target object
        height: Extrude height
        individual: Extrude faces individually
    
    Returns:
        The geometry nodes modifier
    """
    mod, group = add_geometry_nodes_modifier(obj, "Extrude")
    
    group_input = group.nodes.get('Group Input')
    group_output = group.nodes.get('Group Output')
    
    # Extrude mesh
    extrude = add_gn_node(group, 'GeometryNodeExtrudeMesh', (0, 0))
    extrude.mode = 'FACES'
    extrude.inputs['Offset Scale'].default_value = height
    extrude.inputs['Individual'].default_value = individual
    
    group.links.new(group_input.outputs['Geometry'], extrude.inputs['Mesh'])
    group.links.new(extrude.outputs['Mesh'], group_output.inputs['Geometry'])
    
    # Add height input
    add_gn_input(group, 'Height', 'NodeSocketFloat', height)
    
    return mod


def add_gn_array_setup(
    obj: bpy.types.Object,
    count: int = 5,
    offset: tuple = (1, 0, 0)
) -> bpy.types.Modifier:
    """
    Add linear array setup.
    
    Args:
        obj: Target object
        count: Number of instances
        offset: Offset between instances
    
    Returns:
        The geometry nodes modifier
    """
    mod, group = add_geometry_nodes_modifier(obj, "Array")
    
    group_input = group.nodes.get('Group Input')
    group_output = group.nodes.get('Group Output')
    
    # Mesh to points line
    mesh_line = add_gn_node(group, 'GeometryNodeMeshLine', (-100, -100))
    mesh_line.mode = 'OFFSET'
    mesh_line.inputs['Count'].default_value = count
    mesh_line.inputs['Offset'].default_value = offset
    
    # Instance on points
    instance = add_gn_node(group, 'GeometryNodeInstanceOnPoints', (100, 0))
    
    # Realize instances
    realize = add_gn_node(group, 'GeometryNodeRealizeInstances', (300, 0))
    
    # Connect
    group.links.new(mesh_line.outputs['Mesh'], instance.inputs['Points'])
    group.links.new(group_input.outputs['Geometry'], instance.inputs['Instance'])
    group.links.new(instance.outputs['Instances'], realize.inputs['Geometry'])
    group.links.new(realize.outputs['Geometry'], group_output.inputs['Geometry'])
    
    return mod


def apply_geometry_nodes(obj: bpy.types.Object, modifier_name: str = None) -> bool:
    """Apply geometry nodes modifier."""
    bpy.context.view_layer.objects.active = obj
    
    if modifier_name:
        try:
            bpy.ops.object.modifier_apply(modifier=modifier_name)
            return True
        except:
            return False
    else:
        # Apply first geometry nodes modifier
        for mod in obj.modifiers:
            if mod.type == 'NODES':
                try:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                    return True
                except:
                    return False
    
    return False
