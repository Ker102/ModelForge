"""
{
  "title": "Staff and Wand Generator",
  "category": "modeling",
  "subcategory": "weapons",
  "tags": ["staff", "wand", "magic", "wizard", "fantasy", "props"],
  "difficulty": "intermediate",
  "description": "Generates magical staffs and wands.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math
import random


def create_staff(
    length: float = 1.5,
    style: str = 'WIZARD',
    with_crystal: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Staff"
) -> dict:
    """
    Create a magical staff.
    
    Args:
        length: Staff length
        style: 'WIZARD', 'DRUID', 'DARK'
        with_crystal: Add crystal at top
        location: Position
        name: Object name
    
    Returns:
        Dictionary with staff parts
    """
    result = {}
    
    # Main shaft
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.025,
        depth=length,
        location=(location[0], location[1], location[2] + length/2)
    )
    shaft = bpy.context.active_object
    shaft.name = f"{name}_Shaft"
    
    # Slight taper
    for v in shaft.data.vertices:
        if v.co.z > 0:
            factor = 1 - (v.co.z / (length/2)) * 0.3
            v.co.x *= factor
            v.co.y *= factor
    
    # Style-specific modifications
    if style == 'DRUID':
        # Add knotty texture
        bpy.ops.object.modifier_add(type='DISPLACE')
        tex = bpy.data.textures.new(f"{name}_Knots", 'NOISE')
        shaft.modifiers["Displace"].texture = tex
        shaft.modifiers["Displace"].strength = 0.01
    
    shaft_mat = bpy.data.materials.new(f"{name}_ShaftMat")
    bsdf = shaft_mat.node_tree.nodes.get("Principled BSDF")
    
    if style == 'DARK':
        bsdf.inputs['Base Color'].default_value = (0.1, 0.08, 0.08, 1.0)
    else:
        bsdf.inputs['Base Color'].default_value = (0.35, 0.25, 0.12, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    shaft.data.materials.append(shaft_mat)
    
    bpy.ops.object.shade_smooth()
    result['shaft'] = shaft
    
    # Crystal/Orb
    if with_crystal:
        crystal = _create_staff_crystal(
            length, style, location, name
        )
        result['crystal'] = crystal
    
    # Head ornament
    head = _create_staff_head(length, style, location, name)
    result['head'] = head
    
    return result


def _create_staff_crystal(
    length: float,
    style: str,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create crystal at staff top."""
    crystal_pos = (location[0], location[1], location[2] + length + 0.05)
    
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=0.04,
        subdivisions=2,
        location=crystal_pos
    )
    crystal = bpy.context.active_object
    crystal.name = f"{name}_Crystal"
    
    colors = {
        'WIZARD': (0.2, 0.5, 1.0),
        'DRUID': (0.2, 0.8, 0.3),
        'DARK': (0.5, 0.1, 0.5)
    }
    
    mat = bpy.data.materials.new(f"{name}_CrystalMat")
    mat.blend_method = 'BLEND'
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    color = colors.get(style, colors['WIZARD'])
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Transmission Weight'].default_value = 0.8
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 3.0
    crystal.data.materials.append(mat)
    
    bpy.ops.object.shade_smooth()
    return crystal


def _create_staff_head(
    length: float,
    style: str,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create staff head/holder."""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.05,
        minor_radius=0.01,
        location=(location[0], location[1], location[2] + length)
    )
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    
    mat = bpy.data.materials.new(f"{name}_HeadMat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.6, 0.5, 0.3, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    head.data.materials.append(mat)
    
    return head


def create_wand(
    length: float = 0.35,
    core_glow: tuple = (0.8, 0.6, 0.2),
    location: tuple = (0, 0, 0),
    name: str = "Wand"
) -> dict:
    """
    Create a magic wand.
    
    Args:
        length: Wand length
        core_glow: RGB glow color
        location: Position
        name: Object name
    """
    result = {}
    
    # Wand body
    bpy.ops.mesh.primitive_cone_add(
        vertices=8,
        radius1=0.015,
        radius2=0.008,
        depth=length,
        location=(location[0], location[1], location[2] + length/2)
    )
    wand = bpy.context.active_object
    wand.name = name
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.25, 0.18, 0.1, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.5
    wand.data.materials.append(mat)
    
    result['wand'] = wand
    
    # Handle decoration
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.018,
        location=(location[0], location[1], location[2] + 0.01)
    )
    pommel = bpy.context.active_object
    pommel.name = f"{name}_Pommel"
    pommel.data.materials.append(mat)
    result['pommel'] = pommel
    
    # Tip glow
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.01,
        location=(location[0], location[1], location[2] + length + 0.005)
    )
    tip = bpy.context.active_object
    tip.name = f"{name}_Tip"
    
    tip_mat = bpy.data.materials.new(f"{name}_TipMat")
    bsdf = tip_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Emission Color'].default_value = (*core_glow, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 5.0
    tip.data.materials.append(tip_mat)
    result['tip'] = tip
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_staff(style='WIZARD', location=(0, 0, 0))
    create_staff(style='DRUID', location=(0.3, 0, 0))
    create_wand(location=(0.6, 0, 0))
    
    bpy.context.scene.render.engine = 'CYCLES'
    print("Created staffs and wand")
