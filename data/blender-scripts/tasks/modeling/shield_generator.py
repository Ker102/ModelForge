"""
{
  "title": "Shield Generator",
  "category": "modeling",
  "subcategory": "weapons",
  "tags": ["shield", "weapon", "armor", "medieval", "fantasy", "game"],
  "difficulty": "intermediate",
  "description": "Generates various shield types for game/fantasy props.",
  "blender_version": "3.0+",
  "estimated_objects": 2
}
"""
import bpy
import math


def create_shield(
    size: float = 0.5,
    style: str = 'ROUND',
    thickness: float = 0.02,
    material_type: str = 'WOOD',
    emblem: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Shield"
) -> dict:
    """
    Create a shield.
    
    Args:
        size: Shield size
        style: 'ROUND', 'KITE', 'HEATER', 'TOWER'
        thickness: Shield thickness
        material_type: 'WOOD', 'METAL', 'LEATHER'
        emblem: Add center emblem
        location: Position
        name: Object name
    
    Returns:
        Dictionary with shield parts
    """
    result = {}
    
    # Create base shape
    if style == 'ROUND':
        bpy.ops.mesh.primitive_circle_add(
            radius=size/2,
            fill_type='NGON',
            location=location
        )
        shield = bpy.context.active_object
        
    elif style == 'KITE':
        bpy.ops.mesh.primitive_cone_add(
            vertices=4,
            radius1=size * 0.4,
            radius2=0,
            depth=size,
            location=(location[0], location[1], location[2] - size * 0.2)
        )
        shield = bpy.context.active_object
        shield.rotation_euler.x = math.radians(90)
        bpy.ops.object.transform_apply(rotation=True)
        
    elif style == 'HEATER':
        bpy.ops.mesh.primitive_plane_add(size=size, location=location)
        shield = bpy.context.active_object
        # Make pointed at bottom
        for v in shield.data.vertices:
            if v.co.y < 0:
                v.co.y *= 0.6
                v.co.x *= 1 + v.co.y
                
    else:  # TOWER
        bpy.ops.mesh.primitive_plane_add(size=1, location=location)
        shield = bpy.context.active_object
        shield.scale = (size * 0.5, size, 1)
        bpy.ops.object.transform_apply(scale=True)
    
    shield.name = name
    
    # Rotate to stand upright
    shield.rotation_euler.x = math.radians(90)
    
    # Add thickness
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    shield.modifiers["Solidify"].thickness = thickness
    
    # Slight curve
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    shield.modifiers["SimpleDeform"].deform_method = 'BEND'
    shield.modifiers["SimpleDeform"].angle = 0.3
    shield.modifiers["SimpleDeform"].deform_axis = 'X'
    
    # Material
    mat = _create_shield_material(material_type, name)
    shield.data.materials.append(mat)
    
    bpy.ops.object.shade_smooth()
    result['shield'] = shield
    
    # Emblem/Boss
    if emblem and style == 'ROUND':
        boss = _create_shield_boss(size * 0.15, location, name)
        result['boss'] = boss
    
    # Handle on back
    handle = _create_shield_handle(size, thickness, location, name)
    result['handle'] = handle
    
    return result


def _create_shield_material(
    material_type: str,
    name: str
) -> bpy.types.Material:
    """Create shield material."""
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    if material_type == 'WOOD':
        bsdf.inputs['Base Color'].default_value = (0.4, 0.28, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.7
    elif material_type == 'METAL':
        bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.65, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.35
    else:  # LEATHER
        bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.12, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8
    
    return mat


def _create_shield_boss(
    radius: float,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create center boss/emblem."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=(location[0], location[1] - 0.02, location[2])
    )
    boss = bpy.context.active_object
    boss.name = f"{name}_Boss"
    boss.scale.y = 0.5
    bpy.ops.object.transform_apply(scale=True)
    
    mat = bpy.data.materials.new(f"{name}_BossMat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.7, 0.65, 0.4, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.3
    boss.data.materials.append(mat)
    
    return boss


def _create_shield_handle(
    size: float,
    thickness: float,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create handle on back of shield."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.015,
        depth=size * 0.3,
        location=(location[0], location[1] + thickness + 0.03, location[2])
    )
    handle = bpy.context.active_object
    handle.name = f"{name}_Handle"
    handle.rotation_euler.z = math.radians(90)
    
    mat = bpy.data.materials.new(f"{name}_HandleMat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.15, 0.1, 0.05, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    handle.data.materials.append(mat)
    
    return handle


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_shield(style='ROUND', location=(0, 0, 0))
    create_shield(style='KITE', location=(0.7, 0, 0))
    create_shield(style='HEATER', material_type='METAL', location=(1.4, 0, 0))
    
    print("Created shields")
