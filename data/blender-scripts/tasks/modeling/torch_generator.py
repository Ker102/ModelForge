"""
{
  "title": "Torch Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["torch", "fire", "medieval", "dungeon", "fantasy", "light"],
  "difficulty": "intermediate",
  "description": "Generates medieval-style torches with fire effects.",
  "blender_version": "3.0+",
  "estimated_objects": 4
}
"""
import bpy
import math
import random


def create_torch(
    handle_length: float = 0.5,
    handle_radius: float = 0.025,
    head_size: float = 0.08,
    style: str = 'MEDIEVAL',
    lit: bool = True,
    wall_mounted: bool = False,
    location: tuple = (0, 0, 0),
    name: str = "Torch"
) -> dict:
    """
    Create a torch.
    
    Args:
        handle_length: Handle length
        handle_radius: Handle thickness
        head_size: Burnable head size
        style: 'MEDIEVAL', 'PRIMITIVE'
        lit: Add fire effect
        wall_mounted: Angle for wall mount
        location: Position
        name: Object name
    
    Returns:
        Dictionary with torch parts
    """
    result = {}
    
    # Handle
    bpy.ops.mesh.primitive_cylinder_add(
        radius=handle_radius,
        depth=handle_length,
        location=(location[0], location[1], location[2] + handle_length/2)
    )
    handle = bpy.context.active_object
    handle.name = f"{name}_Handle"
    
    # Handle material
    handle_mat = bpy.data.materials.new(f"{name}_HandleMat")
    bsdf = handle_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.25, 0.18, 0.1, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    handle.data.materials.append(handle_mat)
    
    result['handle'] = handle
    
    # Torch head
    head_z = location[2] + handle_length
    
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=head_size,
        subdivisions=2,
        location=(location[0], location[1], head_z)
    )
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    head.scale.z = 1.3
    bpy.ops.object.transform_apply(scale=True)
    
    # Deform for organic look
    for v in head.data.vertices:
        v.co.x += random.uniform(-0.01, 0.01)
        v.co.y += random.uniform(-0.01, 0.01)
    
    # Head material (wrapped cloth/oil)
    head_mat = bpy.data.materials.new(f"{name}_HeadMat")
    bsdf = head_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.15, 0.1, 0.05, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    head.data.materials.append(head_mat)
    
    result['head'] = head
    
    # Fire effect
    if lit:
        fire = _create_torch_fire(
            (location[0], location[1], head_z + head_size),
            head_size,
            name
        )
        result.update(fire)
    
    # Wall mount bracket
    if wall_mounted:
        # Rotate torch
        handle.rotation_euler.y = math.radians(-30)
        head.rotation_euler.y = math.radians(-30)
        
        # Add bracket
        bracket = _create_wall_bracket(location, name)
        result['bracket'] = bracket
    
    return result


def _create_torch_fire(
    location: tuple,
    size: float,
    name: str
) -> dict:
    """Create fire effect for torch."""
    result = {}
    
    # Main flame
    bpy.ops.mesh.primitive_cone_add(
        radius1=size * 0.8,
        radius2=0,
        depth=size * 2,
        location=(location[0], location[1], location[2] + size)
    )
    flame = bpy.context.active_object
    flame.name = f"{name}_Flame"
    bpy.ops.object.shade_smooth()
    
    # Deform for natural flame shape
    for v in flame.data.vertices:
        if v.co.z > 0:
            offset = math.sin(v.co.z * 20) * 0.01
            v.co.x += offset
            v.co.y += offset
    
    # Flame material
    flame_mat = bpy.data.materials.new(f"{name}_FlameMat")
    flame_mat.blend_method = 'BLEND'
    bsdf = flame_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (1.0, 0.4, 0.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.3, 0.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 30.0
    bsdf.inputs['Alpha'].default_value = 0.8
    flame.data.materials.append(flame_mat)
    
    result['flame'] = flame
    
    # Point light
    bpy.ops.object.light_add(
        type='POINT',
        location=(location[0], location[1], location[2] + size * 0.5)
    )
    light = bpy.context.active_object
    light.name = f"{name}_Light"
    light.data.energy = 50
    light.data.color = (1.0, 0.6, 0.2)
    light.data.shadow_soft_size = size * 2
    
    result['light'] = light
    
    return result


def _create_wall_bracket(location: tuple, name: str) -> bpy.types.Object:
    """Create wall mounting bracket."""
    bpy.ops.mesh.primitive_cube_add(
        size=0.08,
        location=(location[0] - 0.1, location[1], location[2] + 0.25)
    )
    bracket = bpy.context.active_object
    bracket.name = f"{name}_Bracket"
    bracket.scale = (0.3, 0.5, 1)
    bpy.ops.object.transform_apply(scale=True)
    
    mat = bpy.data.materials.new(f"{name}_BracketMat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.25, 0.2, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.5
    bracket.data.materials.append(mat)
    
    return bracket


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_torch(lit=True, location=(0, 0, 0))
    create_torch(lit=True, wall_mounted=True, location=(0.5, 0, 0))
    
    print("Created torches")
