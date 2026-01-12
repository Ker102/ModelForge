"""
{
  "title": "Street Lamp Generator",
  "category": "environment",
  "subcategory": "urban",
  "tags": ["lamp", "street", "light", "urban", "city", "exterior"],
  "difficulty": "beginner",
  "description": "Generates street lamps and light posts.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math


def create_street_lamp(
    height: float = 3.0,
    style: str = 'MODERN',
    lit: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "StreetLamp"
) -> dict:
    """
    Create a street lamp.
    
    Args:
        height: Lamp height
        style: 'MODERN', 'CLASSIC', 'INDUSTRIAL'
        lit: Turn light on
        location: Position
        name: Object name
    
    Returns:
        Dictionary with lamp parts
    """
    result = {}
    
    # === POLE ===
    if style == 'MODERN':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.05,
            depth=height,
            location=(location[0], location[1], location[2] + height/2)
        )
    elif style == 'CLASSIC':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.08,
            depth=height,
            location=(location[0], location[1], location[2] + height/2)
        )
    else:  # INDUSTRIAL
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0], location[1], location[2] + height/2
        ))
        bpy.context.active_object.scale = (0.05, 0.05, height/2)
        bpy.ops.object.transform_apply(scale=True)
    
    pole = bpy.context.active_object
    pole.name = f"{name}_Pole"
    
    pole_mat = bpy.data.materials.new(f"{name}_PoleMat")
    pole_mat.use_nodes = True
    bsdf = pole_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.17, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.4
    pole.data.materials.append(pole_mat)
    
    result['pole'] = pole
    
    # === LAMP HEAD ===
    head = _create_lamp_head(height, style, location, name, lit)
    result.update(head)
    
    # === BASE ===
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.15,
        depth=0.05,
        location=(location[0], location[1], location[2] + 0.025)
    )
    base = bpy.context.active_object
    base.name = f"{name}_Base"
    base.data.materials.append(pole_mat)
    result['base'] = base
    
    return result


def _create_lamp_head(
    height: float,
    style: str,
    location: tuple,
    name: str,
    lit: bool
) -> dict:
    """Create lamp head based on style."""
    result = {}
    head_z = location[2] + height
    
    if style == 'MODERN':
        # Arm
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.03,
            depth=0.5,
            location=(location[0] + 0.25, location[1], head_z)
        )
        arm = bpy.context.active_object
        arm.rotation_euler.y = math.radians(90)
        arm.name = f"{name}_Arm"
        result['arm'] = arm
        
        # Head box
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + 0.4, location[1], head_z - 0.1
        ))
        head = bpy.context.active_object
        head.scale = (0.15, 0.08, 0.05)
        head.name = f"{name}_Head"
        result['head'] = head
        
        light_pos = (location[0] + 0.4, location[1], head_z - 0.15)
        
    elif style == 'CLASSIC':
        # Ornate lantern
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.15,
            depth=0.3,
            location=(location[0], location[1], head_z + 0.1)
        )
        head = bpy.context.active_object
        head.name = f"{name}_Lantern"
        result['head'] = head
        
        light_pos = (location[0], location[1], head_z)
        
    else:  # INDUSTRIAL
        bpy.ops.mesh.primitive_cone_add(
            radius1=0.2,
            radius2=0.05,
            depth=0.15,
            location=(location[0], location[1], head_z)
        )
        head = bpy.context.active_object
        head.name = f"{name}_Shade"
        result['head'] = head
        
        light_pos = (location[0], location[1], head_z - 0.05)
    
    # Light source
    if lit:
        bpy.ops.object.light_add(type='POINT', location=light_pos)
        light = bpy.context.active_object
        light.name = f"{name}_Light"
        light.data.energy = 500
        light.data.color = (1.0, 0.9, 0.7)
        light.data.shadow_soft_size = 0.1
        result['light'] = light
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_street_lamp(style='MODERN', location=(0, 0, 0))
    create_street_lamp(style='CLASSIC', location=(2, 0, 0))
    create_street_lamp(style='INDUSTRIAL', location=(4, 0, 0))
    
    print("Created street lamps")
