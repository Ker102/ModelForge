"""
{
  "title": "Candle Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["candle", "flame", "light", "props", "interior", "atmosphere"],
  "difficulty": "beginner",
  "description": "Generates candles with optional flames and holders.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math
import random


def create_candle(
    height: float = 0.15,
    radius: float = 0.015,
    lit: bool = True,
    melted: bool = False,
    color: tuple = (0.95, 0.9, 0.85),
    location: tuple = (0, 0, 0),
    name: str = "Candle"
) -> dict:
    """
    Create a candle.
    
    Args:
        height: Candle height
        radius: Candle radius
        lit: Add flame
        melted: Add melted wax drips
        color: RGB wax color
        location: Position
        name: Object name
    
    Returns:
        Dictionary with candle parts
    """
    result = {}
    
    # Candle body
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        location=(location[0], location[1], location[2] + height/2)
    )
    candle = bpy.context.active_object
    candle.name = name
    bpy.ops.object.shade_smooth()
    
    # Wax material
    wax_mat = bpy.data.materials.new(f"{name}_WaxMat")
    bsdf = wax_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.5
    bsdf.inputs['Subsurface Weight'].default_value = 0.3
    bsdf.inputs['Subsurface Radius'].default_value = (0.1, 0.05, 0.02)
    candle.data.materials.append(wax_mat)
    
    result['candle'] = candle
    
    # Wick
    wick_height = 0.01
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.001,
        depth=wick_height,
        location=(location[0], location[1], location[2] + height + wick_height/2)
    )
    wick = bpy.context.active_object
    wick.name = f"{name}_Wick"
    
    wick_mat = bpy.data.materials.new(f"{name}_WickMat")
    bsdf = wick_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)
    wick.data.materials.append(wick_mat)
    
    result['wick'] = wick
    
    # Flame
    if lit:
        flame = _create_candle_flame(
            (location[0], location[1], location[2] + height + wick_height),
            name
        )
        result['flame'] = flame
        
        # Light
        bpy.ops.object.light_add(
            type='POINT',
            location=(location[0], location[1], location[2] + height + 0.02)
        )
        light = bpy.context.active_object
        light.name = f"{name}_Light"
        light.data.energy = 10
        light.data.color = (1.0, 0.7, 0.3)
        light.data.shadow_soft_size = 0.05
        result['light'] = light
    
    # Melted wax drips
    if melted:
        drips = _create_wax_drips(radius, height, location, wax_mat, name)
        result['drips'] = drips
    
    return result


def _create_candle_flame(location: tuple, name: str) -> bpy.types.Object:
    """Create candle flame."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.008,
        location=(location[0], location[1], location[2] + 0.012)
    )
    flame = bpy.context.active_object
    flame.name = f"{name}_Flame"
    flame.scale.z = 2.0
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    
    # Flame material
    mat = bpy.data.materials.new(f"{name}_FlameMat")
    mat.blend_method = 'BLEND'
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (1.0, 0.6, 0.1, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.5, 0.1, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 20.0
    bsdf.inputs['Alpha'].default_value = 0.9
    flame.data.materials.append(mat)
    
    return flame


def _create_wax_drips(
    radius: float,
    height: float,
    location: tuple,
    material: bpy.types.Material,
    name: str
) -> list:
    """Create melted wax drips."""
    drips = []
    drip_count = random.randint(3, 6)
    
    for i in range(drip_count):
        angle = random.uniform(0, 2 * math.pi)
        start_z = random.uniform(height * 0.5, height * 0.9)
        drip_length = random.uniform(height * 0.2, height * 0.5)
        
        # Drip sphere chain
        for j in range(3):
            pos = (
                location[0] + math.cos(angle) * (radius + 0.003),
                location[1] + math.sin(angle) * (radius + 0.003),
                location[2] + start_z - j * drip_length/3
            )
            
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.003 * (1 - j * 0.2),
                location=pos
            )
            drip = bpy.context.active_object
            drip.name = f"{name}_Drip_{i}_{j}"
            drip.data.materials.append(material)
            drips.append(drip)
    
    return drips


def create_candle_holder(
    candle_radius: float = 0.015,
    style: str = 'SIMPLE',
    location: tuple = (0, 0, 0),
    name: str = "CandleHolder"
) -> bpy.types.Object:
    """
    Create a candle holder.
    
    Args:
        candle_radius: Radius of candle to hold
        style: 'SIMPLE', 'TAPER', 'DISH'
        location: Position
        name: Object name
    """
    if style == 'SIMPLE':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=candle_radius * 2,
            depth=0.02,
            location=location
        )
    elif style == 'TAPER':
        bpy.ops.mesh.primitive_cone_add(
            radius1=candle_radius * 3,
            radius2=candle_radius * 1.5,
            depth=0.03,
            location=(location[0], location[1], location[2] + 0.015)
        )
    else:  # DISH
        bpy.ops.mesh.primitive_cylinder_add(
            radius=candle_radius * 4,
            depth=0.01,
            location=location
        )
    
    holder = bpy.context.active_object
    holder.name = name
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.6, 0.5, 0.35, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.4
    holder.data.materials.append(mat)
    
    return holder


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_candle(lit=True, location=(0, 0, 0))
    create_candle(lit=True, melted=True, location=(0.1, 0, 0))
    
    print("Created candles")
