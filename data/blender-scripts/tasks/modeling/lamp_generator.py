"""
{
  "title": "Lamp Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["lamp", "light", "procedural", "interior", "props", "lighting"],
  "difficulty": "intermediate",
  "description": "Generates various lamp types with working light sources.",
  "blender_version": "3.0+",
  "estimated_objects": 4
}
"""
import bpy
import math


def create_lamp(
    lamp_type: str = 'TABLE',
    height: float = 0.5,
    shade_color: tuple = (0.9, 0.85, 0.75),
    light_color: tuple = (1.0, 0.95, 0.85),
    light_power: float = 100,
    location: tuple = (0, 0, 0),
    name: str = "Lamp"
) -> dict:
    """
    Create a lamp with light source.
    
    Args:
        lamp_type: 'TABLE', 'FLOOR', 'DESK', 'PENDANT'
        height: Total lamp height
        shade_color: RGB shade color
        light_color: RGB light color
        light_power: Light intensity in watts
        location: Position
        name: Object name
    
    Returns:
        Dictionary with lamp parts
    """
    result = {}
    
    if lamp_type == 'FLOOR':
        height = 1.6
    elif lamp_type == 'PENDANT':
        height = 0.3  # Just shade height
    
    # === BASE (not for pendant) ===
    if lamp_type != 'PENDANT':
        base_height = height * 0.08
        base_radius = height * 0.15
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=base_radius,
            depth=base_height,
            location=(location[0], location[1], location[2] + base_height/2)
        )
        base = bpy.context.active_object
        base.name = f"{name}_Base"
        result['base'] = base
        
        # Add metal material to base
        base_mat = bpy.data.materials.new(f"{name}_BaseMat")
        bsdf = base_mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.18, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.8
        bsdf.inputs['Roughness'].default_value = 0.3
        base.data.materials.append(base_mat)
    
    # === POLE ===
    if lamp_type != 'PENDANT':
        pole_radius = height * 0.015
        pole_height = height * 0.7
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=pole_radius,
            depth=pole_height,
            location=(location[0], location[1], location[2] + pole_height/2 + height * 0.08)
        )
        pole = bpy.context.active_object
        pole.name = f"{name}_Pole"
        
        pole_mat = bpy.data.materials.new(f"{name}_PoleMat")
        bsdf = pole_mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.6, 0.55, 0.4, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.25
        pole.data.materials.append(pole_mat)
        
        result['pole'] = pole
    
    # === SHADE ===
    shade_height = height * 0.25
    shade_radius_bottom = height * 0.18
    shade_radius_top = height * 0.12
    
    if lamp_type == 'PENDANT':
        shade_z = location[2]
    else:
        shade_z = location[2] + height - shade_height/2
    
    bpy.ops.mesh.primitive_cone_add(
        radius1=shade_radius_bottom,
        radius2=shade_radius_top,
        depth=shade_height,
        location=(location[0], location[1], shade_z)
    )
    shade = bpy.context.active_object
    shade.name = f"{name}_Shade"
    
    # Flip and hollow for shade
    shade.rotation_euler.x = math.radians(180)
    bpy.ops.object.transform_apply(rotation=True)
    
    # Shade material (slightly translucent)
    shade_mat = bpy.data.materials.new(f"{name}_ShadeMat")
    bsdf = shade_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*shade_color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Subsurface Weight'].default_value = 0.3
    shade.data.materials.append(shade_mat)
    
    result['shade'] = shade
    
    # === LIGHT SOURCE ===
    light_z = shade_z if lamp_type == 'PENDANT' else location[2] + height - shade_height * 0.6
    
    bpy.ops.object.light_add(
        type='POINT',
        location=(location[0], location[1], light_z)
    )
    light = bpy.context.active_object
    light.name = f"{name}_Light"
    light.data.energy = light_power
    light.data.color = light_color
    light.data.shadow_soft_size = shade_radius_bottom * 0.3
    
    result['light'] = light
    
    # === CORD (for pendant) ===
    if lamp_type == 'PENDANT':
        cord_length = 1.0
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.005,
            depth=cord_length,
            location=(location[0], location[1], location[2] + shade_height/2 + cord_length/2)
        )
        cord = bpy.context.active_object
        cord.name = f"{name}_Cord"
        result['cord'] = cord
    
    return result


def create_spotlight(
    location: tuple = (0, 0, 3),
    target: tuple = (0, 0, 0),
    power: float = 500,
    spot_size: float = 45,
    name: str = "Spotlight"
) -> bpy.types.Object:
    """Create a spotlight pointing at target."""
    bpy.ops.object.light_add(type='SPOT', location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = power
    light.data.spot_size = math.radians(spot_size)
    light.data.spot_blend = 0.3
    
    # Point at target
    from mathutils import Vector
    direction = Vector(target) - Vector(location)
    light.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    return light


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_lamp('TABLE', location=(0, 0, 0))
    create_lamp('FLOOR', location=(2, 0, 0))
    create_lamp('PENDANT', location=(-2, 0, 2))
    
    print("Created 3 lamp variations")
