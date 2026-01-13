"""
{
  "title": "Well Generator",
  "category": "environment",
  "subcategory": "structures",
  "tags": ["well", "water", "medieval", "environment", "village"],
  "difficulty": "intermediate",
  "description": "Generates medieval-style wells with rope and bucket.",
  "blender_version": "3.0+",
  "estimated_objects": 6
}
"""
import bpy
import math


def create_well(
    radius: float = 0.5,
    height: float = 0.6,
    with_roof: bool = True,
    with_bucket: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Well"
) -> dict:
    """
    Create a well.
    
    Args:
        radius: Well radius
        height: Wall height
        with_roof: Add roof structure
        with_bucket: Add rope and bucket
        location: Position
        name: Object name
    
    Returns:
        Dictionary with well parts
    """
    result = {}
    
    # Stone wall
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        location=(location[0], location[1], location[2] + height/2)
    )
    wall = bpy.context.active_object
    wall.name = f"{name}_Wall"
    
    # Hollow out
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    wall.modifiers["Solidify"].thickness = -0.1
    
    wall_mat = bpy.data.materials.new(f"{name}_StoneMat")
    wall_mat.use_nodes = True
    bsdf = wall_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.4, 0.38, 0.35, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    wall.data.materials.append(wall_mat)
    
    result['wall'] = wall
    
    # Roof
    if with_roof:
        roof_parts = _create_well_roof(radius, height, location, name)
        result.update(roof_parts)
    
    # Bucket
    if with_bucket:
        bucket_parts = _create_well_bucket(radius, height, location, name)
        result.update(bucket_parts)
    
    return result


def _create_well_roof(radius, height, location, name):
    """Create well roof structure."""
    result = {}
    post_height = 1.2
    
    wood_mat = bpy.data.materials.new(f"{name}_WoodMat")
    wood_mat.use_nodes = True
    bsdf = wood_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.35, 0.25, 0.12, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    
    # Posts
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.04,
            depth=post_height,
            location=(
                location[0] + side * (radius - 0.05),
                location[1],
                location[2] + height + post_height/2
            )
        )
        post = bpy.context.active_object
        post.name = f"{name}_Post_{'L' if side < 0 else 'R'}"
        post.data.materials.append(wood_mat)
    
    # Crossbeam
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.04,
        depth=radius * 2,
        location=(location[0], location[1], location[2] + height + post_height)
    )
    beam = bpy.context.active_object
    beam.name = f"{name}_Beam"
    beam.rotation_euler.y = 1.5708
    beam.data.materials.append(wood_mat)
    result['beam'] = beam
    
    # Roof
    bpy.ops.mesh.primitive_cone_add(
        vertices=4,
        radius1=radius * 1.3,
        radius2=0,
        depth=0.6,
        location=(location[0], location[1], location[2] + height + post_height + 0.3)
    )
    roof = bpy.context.active_object
    roof.name = f"{name}_Roof"
    roof.rotation_euler.z = 0.785
    
    roof_mat = bpy.data.materials.new(f"{name}_RoofMat")
    roof_mat.use_nodes = True
    bsdf = roof_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.25, 0.18, 0.1, 1.0)
    roof.data.materials.append(roof_mat)
    result['roof'] = roof
    
    return result


def _create_well_bucket(radius, height, location, name):
    """Create bucket and rope."""
    result = {}
    
    # Bucket
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.08,
        depth=0.12,
        location=(location[0], location[1], location[2] + 0.2)
    )
    bucket = bpy.context.active_object
    bucket.name = f"{name}_Bucket"
    
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    bucket.modifiers["Solidify"].thickness = -0.008
    
    bucket_mat = bpy.data.materials.new(f"{name}_BucketMat")
    bucket_mat.use_nodes = True
    bsdf = bucket_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.4, 0.35, 0.25, 1.0)
    bucket.data.materials.append(bucket_mat)
    result['bucket'] = bucket
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_well(location=(0, 0, 0))
    
    print("Created well")
