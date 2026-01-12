"""
{
  "title": "Signpost Generator",
  "category": "environment",
  "subcategory": "props",
  "tags": ["sign", "post", "direction", "props", "outdoor", "medieval"],
  "difficulty": "beginner",
  "description": "Generates directional signposts for environments.",
  "blender_version": "3.0+",
  "estimated_objects": 4
}
"""
import bpy
import math
import random


def create_signpost(
    height: float = 2.0,
    sign_count: int = 3,
    style: str = 'WOODEN',
    location: tuple = (0, 0, 0),
    name: str = "Signpost"
) -> dict:
    """
    Create a directional signpost.
    
    Args:
        height: Post height
        sign_count: Number of direction signs
        style: 'WOODEN', 'METAL', 'RUSTIC'
        location: Position
        name: Object name
    
    Returns:
        Dictionary with signpost parts
    """
    result = {}
    
    # === POST ===
    if style == 'WOODEN':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.05,
            depth=height,
            location=(location[0], location[1], location[2] + height/2)
        )
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0], location[1], location[2] + height/2
        ))
        bpy.context.active_object.scale = (0.04, 0.04, height/2)
        bpy.ops.object.transform_apply(scale=True)
    
    post = bpy.context.active_object
    post.name = f"{name}_Post"
    
    post_mat = bpy.data.materials.new(f"{name}_PostMat")
    post_mat.use_nodes = True
    bsdf = post_mat.node_tree.nodes.get("Principled BSDF")
    
    if style == 'METAL':
        bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.32, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.8
    else:
        bsdf.inputs['Base Color'].default_value = (0.35, 0.25, 0.12, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8
    
    post.data.materials.append(post_mat)
    result['post'] = post
    
    # === SIGNS ===
    signs = []
    sign_mat = bpy.data.materials.new(f"{name}_SignMat")
    sign_mat.use_nodes = True
    bsdf = sign_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.5, 0.4, 0.25, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    
    for i in range(sign_count):
        sign_height = height * 0.6 + (i / sign_count) * height * 0.3
        angle = (i / sign_count) * math.pi * 0.8 - 0.4
        
        sign = _create_direction_sign(
            (location[0], location[1], location[2] + sign_height),
            angle,
            name,
            i
        )
        sign.data.materials.append(sign_mat)
        signs.append(sign)
    
    result['signs'] = signs
    
    return result


def _create_direction_sign(
    location: tuple,
    angle: float,
    name: str,
    index: int
) -> bpy.types.Object:
    """Create arrow-shaped direction sign."""
    sign_length = random.uniform(0.4, 0.6)
    sign_height = 0.12
    
    # Create plane
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0] + math.cos(angle) * sign_length/2,
        location[1] + math.sin(angle) * sign_length/2,
        location[2]
    ))
    sign = bpy.context.active_object
    sign.name = f"{name}_Sign_{index}"
    sign.scale = (sign_length/2, 0.01, sign_height/2)
    sign.rotation_euler.z = angle
    bpy.ops.object.transform_apply(scale=True)
    
    # Make arrow point
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for v in sign.data.vertices:
        local_x = v.co.x * math.cos(-angle) - v.co.y * math.sin(-angle)
        if local_x > sign_length * 0.3:
            factor = (local_x - sign_length * 0.3) / (sign_length * 0.2)
            v.co.z *= 1 - factor * 0.8
    
    return sign


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_signpost(sign_count=3, location=(0, 0, 0))
    create_signpost(style='METAL', sign_count=2, location=(1, 0, 0))
    
    print("Created signposts")
