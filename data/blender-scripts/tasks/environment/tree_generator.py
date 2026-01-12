"""
{
  "title": "Tree Generator",
  "category": "environment",
  "subcategory": "vegetation",
  "tags": ["tree", "vegetation", "nature", "procedural", "foliage", "trunk", "branches"],
  "difficulty": "intermediate",
  "description": "Procedurally generates different types of trees with trunks, branches, and foliage.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math
import random


def create_tree(
    tree_type: str = 'OAK',
    height: float = 5.0,
    trunk_radius: float = 0.2,
    location: tuple = (0, 0, 0),
    seed: int = 42,
    foliage_density: float = 1.0,
    name_prefix: str = "Tree"
) -> dict:
    """
    Create a procedural tree.
    
    Args:
        tree_type: 'OAK', 'PINE', 'PALM', 'BIRCH', 'WILLOW'
        height: Total tree height
        trunk_radius: Base trunk radius
        location: Tree base position
        seed: Random seed for variation
        foliage_density: Foliage amount multiplier
        name_prefix: Prefix for object names
    
    Returns:
        Dictionary with tree objects
    
    Example:
        >>> tree = create_tree('PINE', height=8, location=(5, 0, 0))
    """
    random.seed(seed)
    result = {}
    
    tree_configs = {
        'OAK': {
            'trunk_height': 0.35,
            'crown_shape': 'SPHERE',
            'crown_scale': (1.0, 1.0, 0.8),
            'branch_count': 5,
            'trunk_color': (0.25, 0.15, 0.08),
            'foliage_color': (0.15, 0.4, 0.12)
        },
        'PINE': {
            'trunk_height': 0.9,
            'crown_shape': 'CONE',
            'crown_scale': (0.6, 0.6, 1.5),
            'branch_count': 0,
            'trunk_color': (0.35, 0.2, 0.1),
            'foliage_color': (0.08, 0.25, 0.08)
        },
        'PALM': {
            'trunk_height': 0.85,
            'crown_shape': 'FRONDS',
            'crown_scale': (1.0, 1.0, 0.3),
            'branch_count': 0,
            'trunk_color': (0.4, 0.3, 0.2),
            'foliage_color': (0.12, 0.35, 0.08)
        },
        'BIRCH': {
            'trunk_height': 0.4,
            'crown_shape': 'ELLIPSOID',
            'crown_scale': (0.7, 0.7, 1.2),
            'branch_count': 4,
            'trunk_color': (0.9, 0.88, 0.85),
            'foliage_color': (0.2, 0.45, 0.1)
        },
        'WILLOW': {
            'trunk_height': 0.3,
            'crown_shape': 'HANGING',
            'crown_scale': (1.5, 1.5, 1.0),
            'branch_count': 6,
            'trunk_color': (0.3, 0.22, 0.12),
            'foliage_color': (0.18, 0.4, 0.15)
        }
    }
    
    config = tree_configs.get(tree_type, tree_configs['OAK'])
    
    # Create trunk
    trunk = _create_trunk(height, trunk_radius, config, location, name_prefix)
    result['trunk'] = trunk
    
    # Create crown/foliage
    crown_height = height * config['trunk_height']
    crown = _create_crown(
        height, crown_height, config, location, 
        foliage_density, name_prefix
    )
    result['crown'] = crown
    
    # Create branches for certain tree types
    if config['branch_count'] > 0:
        branches = _create_branches(
            height, trunk_radius, config, location, name_prefix
        )
        result['branches'] = branches
    
    return result


def _create_trunk(
    height: float,
    radius: float,
    config: dict,
    location: tuple,
    name_prefix: str
) -> bpy.types.Object:
    """Create tree trunk."""
    trunk_height = height * config['trunk_height']
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=trunk_height,
        location=(location[0], location[1], location[2] + trunk_height/2)
    )
    trunk = bpy.context.active_object
    trunk.name = f"{name_prefix}_Trunk"
    
    # Taper the trunk
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    trunk.modifiers["SimpleDeform"].deform_method = 'TAPER'
    trunk.modifiers["SimpleDeform"].factor = 0.4
    trunk.modifiers["SimpleDeform"].deform_axis = 'Z'
    
    # Add slight bend for naturalness
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    trunk.modifiers["SimpleDeform.001"].deform_method = 'BEND'
    trunk.modifiers["SimpleDeform.001"].angle = math.radians(random.uniform(-5, 5))
    trunk.modifiers["SimpleDeform.001"].deform_axis = 'X'
    
    # Trunk material
    mat = bpy.data.materials.new(f"{name_prefix}_TrunkMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*config['trunk_color'], 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    trunk.data.materials.append(mat)
    
    return trunk


def _create_crown(
    height: float,
    crown_base_height: float,
    config: dict,
    location: tuple,
    density: float,
    name_prefix: str
) -> bpy.types.Object:
    """Create tree crown/foliage."""
    crown_pos = (
        location[0],
        location[1],
        location[2] + crown_base_height + height * 0.2
    )
    
    shape = config['crown_shape']
    scale = config['crown_scale']
    crown_size = height * 0.4 * density
    
    if shape == 'SPHERE':
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=crown_size,
            subdivisions=2,
            location=crown_pos
        )
    elif shape == 'CONE':
        bpy.ops.mesh.primitive_cone_add(
            radius1=crown_size * 0.8,
            radius2=0.1,
            depth=height * 0.6,
            location=(crown_pos[0], crown_pos[1], crown_pos[2] + height * 0.15)
        )
    elif shape == 'ELLIPSOID':
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=crown_size,
            location=crown_pos
        )
    elif shape == 'FRONDS':
        # Palm fronds - create multiple leaves
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=crown_size * 0.5,
            location=crown_pos
        )
    else:  # HANGING/WILLOW
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=crown_size,
            location=crown_pos
        )
    
    crown = bpy.context.active_object
    crown.name = f"{name_prefix}_Crown"
    
    # Apply scale
    crown.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    
    # Add noise for organic shape
    bpy.ops.object.modifier_add(type='DISPLACE')
    crown.modifiers["Displace"].strength = crown_size * 0.2
    
    # Create noise texture
    tex = bpy.data.textures.new(f"{name_prefix}_Noise", type='CLOUDS')
    tex.noise_scale = 1.5
    crown.modifiers["Displace"].texture = tex
    
    # Foliage material
    mat = bpy.data.materials.new(f"{name_prefix}_FoliageMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*config['foliage_color'], 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    bsdf.inputs['Subsurface Weight'].default_value = 0.2
    bsdf.inputs['Subsurface Radius'].default_value = (0.1, 0.2, 0.05)
    crown.data.materials.append(mat)
    
    return crown


def _create_branches(
    height: float,
    trunk_radius: float,
    config: dict,
    location: tuple,
    name_prefix: str
) -> list:
    """Create tree branches."""
    branches = []
    count = config['branch_count']
    branch_height = height * config['trunk_height']
    
    for i in range(count):
        angle = (i / count) * 2 * math.pi + random.uniform(-0.3, 0.3)
        branch_z = branch_height * (0.5 + random.uniform(0, 0.4))
        
        # Branch start position
        start_x = location[0] + math.cos(angle) * trunk_radius * 0.8
        start_y = location[1] + math.sin(angle) * trunk_radius * 0.8
        
        # Branch end position
        branch_length = height * random.uniform(0.2, 0.4)
        end_x = location[0] + math.cos(angle) * (trunk_radius + branch_length)
        end_y = location[1] + math.sin(angle) * (trunk_radius + branch_length)
        end_z = branch_z + branch_length * 0.3
        
        # Create branch cylinder
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        mid_z = (branch_z + end_z) / 2
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=trunk_radius * 0.2,
            depth=branch_length,
            location=(mid_x, mid_y, mid_z)
        )
        
        branch = bpy.context.active_object
        branch.name = f"{name_prefix}_Branch_{i}"
        
        # Rotate to point outward
        branch.rotation_euler.x = math.radians(-20 + random.uniform(-10, 10))
        branch.rotation_euler.z = angle
        
        # Use trunk material
        if bpy.data.materials.get(f"{name_prefix}_TrunkMat"):
            branch.data.materials.append(bpy.data.materials[f"{name_prefix}_TrunkMat"])
        
        branches.append(branch)
    
    return branches


def create_forest_patch(
    center: tuple = (0, 0, 0),
    radius: float = 10,
    tree_count: int = 10,
    tree_types: list = None,
    min_height: float = 4,
    max_height: float = 8,
    seed: int = 123
) -> list:
    """
    Create a patch of randomly placed trees.
    
    Args:
        center: Center of the forest area
        radius: Spread radius
        tree_count: Number of trees
        tree_types: List of tree types to use
        min_height: Minimum tree height
        max_height: Maximum tree height
        seed: Random seed
    
    Returns:
        List of tree dictionaries
    """
    random.seed(seed)
    
    if tree_types is None:
        tree_types = ['OAK', 'PINE', 'BIRCH']
    
    trees = []
    
    for i in range(tree_count):
        # Random position within radius
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius)
        
        pos = (
            center[0] + math.cos(angle) * dist,
            center[1] + math.sin(angle) * dist,
            center[2]
        )
        
        tree_type = random.choice(tree_types)
        height = random.uniform(min_height, max_height)
        
        tree = create_tree(
            tree_type=tree_type,
            height=height,
            location=pos,
            seed=seed + i,
            name_prefix=f"Tree_{i}"
        )
        trees.append(tree)
    
    return trees


# Standalone execution
if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create different tree types
    tree1 = create_tree('OAK', height=6, location=(0, 0, 0))
    tree2 = create_tree('PINE', height=8, location=(4, 0, 0))
    tree3 = create_tree('BIRCH', height=5, location=(-4, 0, 0))
    
    print(f"Created 3 trees")
