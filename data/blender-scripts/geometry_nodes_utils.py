"""
{
  "title": "Geometry Nodes Utilities",
  "category": "geometry_nodes",
  "tags": ["geometry", "nodes", "procedural", "modifier", "instances"],
  "description": "Functions for creating and manipulating geometry node setups.",
  "blender_version": "3.0+"
}
"""
import bpy


def add_geometry_nodes_modifier(
    obj: bpy.types.Object,
    name: str = "GeometryNodes"
) -> tuple:
    """
    Add geometry nodes modifier to object.
    
    Returns:
        Tuple of (modifier, node_tree)
    """
    mod = obj.modifiers.new(name, 'NODES')
    
    if mod.node_group is None:
        node_group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
        mod.node_group = node_group
    else:
        node_group = mod.node_group
    
    return mod, node_group


def setup_basic_geonodes(node_group: bpy.types.NodeTree) -> dict:
    """Set up basic input/output for geometry nodes."""
    nodes = node_group.nodes
    nodes.clear()
    
    # Group input
    group_input = nodes.new('NodeGroupInput')
    group_input.location = (-200, 0)
    
    # Group output
    group_output = nodes.new('NodeGroupOutput')
    group_output.location = (200, 0)
    
    # Add geometry socket
    node_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    node_group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # Connect
    node_group.links.new(group_input.outputs['Geometry'], group_output.inputs['Geometry'])
    
    return {'input': group_input, 'output': group_output}


def add_scatter_points(
    node_group: bpy.types.NodeTree,
    density: float = 10.0,
    seed: int = 0
) -> bpy.types.Node:
    """Add point distribution node."""
    nodes = node_group.nodes
    
    distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
    distribute.distribute_method = 'POISSON'
    distribute.inputs['Density'].default_value = density
    distribute.inputs['Seed'].default_value = seed
    
    return distribute


def add_instance_on_points(
    node_group: bpy.types.NodeTree,
    instance_object: bpy.types.Object = None
) -> bpy.types.Node:
    """Add instance on points node."""
    nodes = node_group.nodes
    
    instance = nodes.new('GeometryNodeInstanceOnPoints')
    
    if instance_object:
        obj_info = nodes.new('GeometryNodeObjectInfo')
        obj_info.inputs['Object'].default_value = instance_object
        node_group.links.new(obj_info.outputs['Geometry'], instance.inputs['Instance'])
    
    return instance


def add_random_scale(
    node_group: bpy.types.NodeTree,
    min_scale: float = 0.5,
    max_scale: float = 1.5,
    seed: int = 0
) -> bpy.types.Node:
    """Add random value for scaling."""
    nodes = node_group.nodes
    
    random = nodes.new('FunctionNodeRandomValue')
    random.data_type = 'FLOAT_VECTOR'
    random.inputs['Min'].default_value = (min_scale, min_scale, min_scale)
    random.inputs['Max'].default_value = (max_scale, max_scale, max_scale)
    random.inputs['Seed'].default_value = seed
    
    return random


def add_random_rotation(
    node_group: bpy.types.NodeTree,
    seed: int = 0
) -> bpy.types.Node:
    """Add random rotation."""
    nodes = node_group.nodes
    
    random = nodes.new('FunctionNodeRandomValue')
    random.data_type = 'FLOAT_VECTOR'
    random.inputs['Min'].default_value = (0, 0, 0)
    random.inputs['Max'].default_value = (0, 0, 6.28319)  # Z rotation only
    random.inputs['Seed'].default_value = seed
    
    return random


def create_scatter_setup(
    obj: bpy.types.Object,
    instance_obj: bpy.types.Object,
    density: float = 5.0,
    random_scale: bool = True,
    random_rotation: bool = True,
    name: str = "ScatterSetup"
) -> dict:
    """
    Create a complete scatter setup on object.
    
    Args:
        obj: Surface object to scatter on
        instance_obj: Object to instance
        density: Points per unit area
        random_scale: Add random scale variation
        random_rotation: Add random Z rotation
        name: Node group name
    
    Returns:
        Dictionary with modifier and nodes
    """
    mod, node_group = add_geometry_nodes_modifier(obj, name)
    base = setup_basic_geonodes(node_group)
    nodes = node_group.nodes
    links = node_group.links
    
    # Distribute points
    distribute = add_scatter_points(node_group, density)
    distribute.location = (0, 100)
    
    # Instance on points
    instance = add_instance_on_points(node_group, instance_obj)
    instance.location = (200, 100)
    
    # Connect
    links.new(base['input'].outputs['Geometry'], distribute.inputs['Mesh'])
    links.new(distribute.outputs['Points'], instance.inputs['Points'])
    
    # Join geometry
    join = nodes.new('GeometryNodeJoinGeometry')
    join.location = (400, 0)
    
    links.new(base['input'].outputs['Geometry'], join.inputs['Geometry'])
    links.new(instance.outputs['Instances'], join.inputs['Geometry'])
    links.new(join.outputs['Geometry'], base['output'].inputs['Geometry'])
    
    # Random scale
    if random_scale:
        rand_scale = add_random_scale(node_group, 0.7, 1.3)
        rand_scale.location = (0, -100)
        links.new(rand_scale.outputs['Value'], instance.inputs['Scale'])
    
    # Random rotation
    if random_rotation:
        rand_rot = add_random_rotation(node_group)
        rand_rot.location = (0, -200)
        
        euler = nodes.new('FunctionNodeRotateEuler')
        euler.location = (100, -200)
        links.new(rand_rot.outputs['Value'], euler.inputs['Rotate By'])
        links.new(euler.outputs['Rotation'], instance.inputs['Rotation'])
    
    return {
        'modifier': mod,
        'node_group': node_group,
        'distribute': distribute,
        'instance': instance
    }
