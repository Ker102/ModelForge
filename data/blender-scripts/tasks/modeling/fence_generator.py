"""
{
  "title": "Fence Generator",
  "category": "modeling",
  "subcategory": "environment",
  "tags": ["fence", "barrier", "outdoor", "environment", "procedural"],
  "difficulty": "beginner",
  "description": "Generates fence sections with posts and rails.",
  "blender_version": "3.0+",
  "estimated_objects": 10
}
"""
import bpy
import math


def create_fence(
    length: float = 5.0,
    height: float = 1.2,
    post_spacing: float = 2.0,
    style: str = 'PICKET',
    location: tuple = (0, 0, 0),
    direction: float = 0,
    name: str = "Fence"
) -> dict:
    """
    Create a fence section.
    
    Args:
        length: Total fence length
        height: Fence height
        post_spacing: Distance between posts
        style: 'PICKET', 'RAIL', 'CHAIN_LINK', 'PRIVACY'
        location: Start position
        direction: Direction angle in degrees
        name: Object name
    
    Returns:
        Dictionary with fence parts
    """
    result = {}
    dir_rad = math.radians(direction)
    
    # Calculate number of posts
    num_posts = int(length / post_spacing) + 1
    actual_spacing = length / (num_posts - 1) if num_posts > 1 else 0
    
    # Materials
    post_mat = bpy.data.materials.new(f"{name}_PostMat")
    bsdf = post_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.45, 0.35, 0.2, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    
    # === POSTS ===
    posts = []
    post_size = 0.08
    
    for i in range(num_posts):
        dist = i * actual_spacing
        pos_x = location[0] + math.cos(dir_rad) * dist
        pos_y = location[1] + math.sin(dir_rad) * dist
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            pos_x, pos_y, location[2] + height/2
        ))
        post = bpy.context.active_object
        post.name = f"{name}_Post_{i+1}"
        post.scale = (post_size/2, post_size/2, height/2)
        bpy.ops.object.transform_apply(scale=True)
        post.data.materials.append(post_mat)
        posts.append(post)
    
    result['posts'] = posts
    
    # === STYLE-SPECIFIC ELEMENTS ===
    if style == 'PICKET':
        pickets = _create_picket_fence(
            length, height, post_spacing, location, dir_rad, name, post_mat
        )
        result['pickets'] = pickets
        
    elif style == 'RAIL':
        rails = _create_rail_fence(
            length, height, location, dir_rad, name, post_mat
        )
        result['rails'] = rails
        
    elif style == 'PRIVACY':
        boards = _create_privacy_fence(
            length, height, location, dir_rad, name, post_mat
        )
        result['boards'] = boards
    
    return result


def _create_picket_fence(
    length: float,
    height: float,
    post_spacing: float,
    location: tuple,
    dir_rad: float,
    name: str,
    material: bpy.types.Material
) -> list:
    """Create picket fence elements."""
    pickets = []
    picket_spacing = 0.1
    picket_width = 0.07
    picket_height = height * 0.9
    
    num_pickets = int(length / picket_spacing)
    
    for i in range(num_pickets):
        dist = i * picket_spacing + picket_spacing/2
        pos_x = location[0] + math.cos(dir_rad) * dist
        pos_y = location[1] + math.sin(dir_rad) * dist
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            pos_x, pos_y, location[2] + picket_height/2
        ))
        picket = bpy.context.active_object
        picket.name = f"{name}_Picket_{i+1}"
        picket.scale = (picket_width/2, 0.015, picket_height/2)
        picket.rotation_euler.z = dir_rad
        bpy.ops.object.transform_apply(scale=True)
        picket.data.materials.append(material)
        pickets.append(picket)
    
    # Top rail
    rail_height = height * 0.8
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0] + math.cos(dir_rad) * length/2,
        location[1] + math.sin(dir_rad) * length/2,
        location[2] + rail_height
    ))
    rail = bpy.context.active_object
    rail.name = f"{name}_TopRail"
    rail.scale = (length/2, 0.03, 0.04)
    rail.rotation_euler.z = dir_rad
    bpy.ops.object.transform_apply(scale=True)
    rail.data.materials.append(material)
    pickets.append(rail)
    
    return pickets


def _create_rail_fence(
    length: float,
    height: float,
    location: tuple,
    dir_rad: float,
    name: str,
    material: bpy.types.Material
) -> list:
    """Create horizontal rail fence."""
    rails = []
    rail_heights = [height * 0.25, height * 0.55, height * 0.85]
    
    for i, h in enumerate(rail_heights):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.03,
            depth=length,
            location=(
                location[0] + math.cos(dir_rad) * length/2,
                location[1] + math.sin(dir_rad) * length/2,
                location[2] + h
            )
        )
        rail = bpy.context.active_object
        rail.name = f"{name}_Rail_{i+1}"
        rail.rotation_euler.y = math.pi/2
        rail.rotation_euler.z = dir_rad
        rail.data.materials.append(material)
        rails.append(rail)
    
    return rails


def _create_privacy_fence(
    length: float,
    height: float,
    location: tuple,
    dir_rad: float,
    name: str,
    material: bpy.types.Material
) -> list:
    """Create solid privacy fence boards."""
    boards = []
    board_width = 0.15
    num_boards = int(length / board_width)
    
    for i in range(num_boards):
        dist = i * board_width + board_width/2
        pos_x = location[0] + math.cos(dir_rad) * dist
        pos_y = location[1] + math.sin(dir_rad) * dist
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            pos_x, pos_y, location[2] + height/2
        ))
        board = bpy.context.active_object
        board.name = f"{name}_Board_{i+1}"
        board.scale = (board_width/2 - 0.005, 0.02, height/2)
        board.rotation_euler.z = dir_rad
        bpy.ops.object.transform_apply(scale=True)
        board.data.materials.append(material)
        boards.append(board)
    
    return boards


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_fence(style='PICKET', location=(0, 0, 0))
    create_fence(style='RAIL', location=(0, 3, 0))
    create_fence(style='PRIVACY', location=(0, 6, 0))
    
    print("Created 3 fence styles")
