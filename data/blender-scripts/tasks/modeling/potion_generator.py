"""
{
  "title": "Potion Bottle Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["potion", "bottle", "fantasy", "game", "magic", "alchemy"],
  "difficulty": "intermediate",
  "description": "Generates fantasy potion bottles with glowing liquids.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math
import random


def create_potion(
    height: float = 0.12,
    style: str = 'ROUND',
    liquid_color: tuple = (0.2, 0.8, 0.3),
    liquid_level: float = 0.7,
    glow: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Potion"
) -> dict:
    """
    Create a potion bottle.
    
    Args:
        height: Bottle height
        style: 'ROUND', 'FLASK', 'VIAL', 'HEART'
        liquid_color: RGB liquid color
        liquid_level: Fill amount (0-1)
        glow: Add emission to liquid
        location: Position
        name: Object name
    
    Returns:
        Dictionary with potion parts
    """
    result = {}
    
    # Style dimensions
    styles = {
        'ROUND': {'body_h': 0.6, 'body_r': 0.35, 'neck_r': 0.1},
        'FLASK': {'body_h': 0.5, 'body_r': 0.25, 'neck_r': 0.08},
        'VIAL': {'body_h': 0.65, 'body_r': 0.15, 'neck_r': 0.1},
        'HEART': {'body_h': 0.5, 'body_r': 0.3, 'neck_r': 0.08}
    }
    
    s = styles.get(style, styles['ROUND'])
    body_height = height * s['body_h']
    body_radius = height * s['body_r']
    neck_radius = height * s['neck_r']
    neck_height = height * 0.2
    
    # Bottle body
    if style == 'ROUND':
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=body_radius,
            location=(location[0], location[1], location[2] + body_radius)
        )
    else:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=body_radius,
            depth=body_height,
            location=(location[0], location[1], location[2] + body_height/2)
        )
    
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    
    # Neck
    neck_z = location[2] + body_height + neck_height/2
    if style == 'ROUND':
        neck_z = location[2] + body_radius * 1.6
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=neck_radius,
        depth=neck_height,
        location=(location[0], location[1], neck_z)
    )
    neck = bpy.context.active_object
    neck.name = f"{name}_Neck"
    
    # Join
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    neck.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    
    bottle = bpy.context.active_object
    bottle.name = f"{name}_Bottle"
    bpy.ops.object.shade_smooth()
    
    # Glass material
    glass_mat = bpy.data.materials.new(f"{name}_GlassMat")
    glass_mat.use_nodes = True
    glass_mat.blend_method = 'BLEND'
    bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 1.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.5
    bsdf.inputs['Transmission Weight'].default_value = 0.95
    bottle.data.materials.append(glass_mat)
    
    result['bottle'] = bottle
    
    # Liquid
    liquid = _create_potion_liquid(
        body_radius * 0.9,
        body_height * liquid_level,
        liquid_color,
        glow,
        (location[0], location[1], location[2]),
        name
    )
    result['liquid'] = liquid
    
    # Cork
    cork = _create_potion_cork(
        neck_radius,
        (location[0], location[1], neck_z + neck_height/2),
        name
    )
    result['cork'] = cork
    
    return result


def _create_potion_liquid(
    radius: float,
    height: float,
    color: tuple,
    glow: bool,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create potion liquid."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        location=(location[0], location[1], location[2] + height/2)
    )
    liquid = bpy.context.active_object
    liquid.name = f"{name}_Liquid"
    
    mat = bpy.data.materials.new(f"{name}_LiquidMat")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.1
    bsdf.inputs['Transmission Weight'].default_value = 0.8
    bsdf.inputs['IOR'].default_value = 1.36
    
    if glow:
        bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 3.0
    
    liquid.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    
    return liquid


def _create_potion_cork(
    radius: float,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create cork stopper."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius * 1.1,
        depth=radius * 1.5,
        location=(location[0], location[1], location[2] + radius * 0.3)
    )
    cork = bpy.context.active_object
    cork.name = f"{name}_Cork"
    
    mat = bpy.data.materials.new(f"{name}_CorkMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.55, 0.45, 0.3, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    cork.data.materials.append(mat)
    
    return cork


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_potion(style='ROUND', liquid_color=(0.2, 0.9, 0.3), location=(0, 0, 0))
    create_potion(style='FLASK', liquid_color=(0.9, 0.2, 0.2), location=(0.15, 0, 0))
    create_potion(style='VIAL', liquid_color=(0.2, 0.4, 0.9), location=(0.25, 0, 0))
    
    bpy.context.scene.render.engine = 'CYCLES'
    print("Created potions")
