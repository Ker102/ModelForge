"""
{
  "title": "Bow and Arrow Generator",
  "category": "modeling",
  "subcategory": "weapons",
  "tags": ["bow", "arrow", "weapon", "archery", "medieval", "fantasy"],
  "difficulty": "intermediate",
  "description": "Generates bows and arrows for game/fantasy props.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math


def create_bow(
    size: float = 0.8,
    draw_amount: float = 0,
    style: str = 'RECURVE',
    location: tuple = (0, 0, 0),
    name: str = "Bow"
) -> dict:
    """
    Create a bow.
    
    Args:
        size: Bow size
        draw_amount: How much string is drawn (0-1)
        style: 'RECURVE', 'LONGBOW', 'SHORTBOW'
        location: Position
        name: Object name
    
    Returns:
        Dictionary with bow parts
    """
    result = {}
    
    # Bow curve
    curve_data = bpy.data.curves.new(f"{name}_Curve", 'CURVE')
    curve_data.dimensions = '3D'
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(2)  # 3 total points
    
    points = spline.bezier_points
    
    # Top
    points[0].co = (0, 0, size/2)
    points[0].handle_left = (-0.1, 0, size/2)
    points[0].handle_right = (0.1, 0, size/2)
    
    # Middle (grip)
    points[1].co = (-0.05 - draw_amount * 0.15, 0, 0)
    points[1].handle_left = (-0.05 - draw_amount * 0.15, 0, size * 0.2)
    points[1].handle_right = (-0.05 - draw_amount * 0.15, 0, -size * 0.2)
    
    # Bottom
    points[2].co = (0, 0, -size/2)
    points[2].handle_left = (0.1, 0, -size/2)
    points[2].handle_right = (-0.1, 0, -size/2)
    
    # Style adjustments
    if style == 'RECURVE':
        points[0].co.x = 0.08
        points[2].co.x = 0.08
    elif style == 'LONGBOW':
        size *= 1.3
        points[0].co.z = size/2
        points[2].co.z = -size/2
    
    # Bevel for thickness
    curve_data.bevel_depth = 0.015
    curve_data.bevel_resolution = 4
    
    bow = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(bow)
    bow.location = location
    
    # Material
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.4, 0.28, 0.15, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    bow.data.materials.append(mat)
    
    result['bow'] = bow
    
    # Bowstring
    string = _create_bowstring(size, draw_amount, location, name)
    result['string'] = string
    
    return result


def _create_bowstring(
    size: float,
    draw: float,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create bowstring."""
    curve_data = bpy.data.curves.new(f"{name}_StringCurve", 'CURVE')
    curve_data.dimensions = '3D'
    
    spline = curve_data.splines.new('POLY')
    spline.points.add(2)  # 3 points
    
    spline.points[0].co = (0, 0, size/2, 1)
    spline.points[1].co = (-0.1 - draw * 0.2, 0, 0, 1)
    spline.points[2].co = (0, 0, -size/2, 1)
    
    curve_data.bevel_depth = 0.002
    
    string = bpy.data.objects.new(f"{name}_String", curve_data)
    bpy.context.collection.objects.link(string)
    string.location = location
    
    mat = bpy.data.materials.new(f"{name}_StringMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.8, 0.75, 0.6, 1.0)
    string.data.materials.append(mat)
    
    return string


def create_arrow(
    length: float = 0.6,
    location: tuple = (0, 0, 0),
    name: str = "Arrow"
) -> dict:
    """Create an arrow."""
    result = {}
    
    # Shaft
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.005,
        depth=length,
        location=(location[0] + length/2, location[1], location[2])
    )
    shaft = bpy.context.active_object
    shaft.name = f"{name}_Shaft"
    shaft.rotation_euler.y = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    
    shaft_mat = bpy.data.materials.new(f"{name}_ShaftMat")
    shaft_mat.use_nodes = True
    bsdf = shaft_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.5, 0.4, 0.25, 1.0)
    shaft.data.materials.append(shaft_mat)
    
    result['shaft'] = shaft
    
    # Arrowhead
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.01,
        radius2=0,
        depth=0.04,
        location=(location[0] + length + 0.02, location[1], location[2])
    )
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    head.rotation_euler.y = math.radians(90)
    
    head_mat = bpy.data.materials.new(f"{name}_HeadMat")
    head_mat.use_nodes = True
    bsdf = head_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.55, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    head.data.materials.append(head_mat)
    
    result['head'] = head
    
    # Fletching
    for i in range(3):
        angle = i * 120
        bpy.ops.mesh.primitive_plane_add(
            size=0.04,
            location=(location[0], location[1], location[2])
        )
        fletch = bpy.context.active_object
        fletch.name = f"{name}_Fletch_{i}"
        fletch.scale = (0.5, 1, 1)
        fletch.rotation_euler = (math.radians(angle), math.radians(90), 0)
    
    result['fletching'] = True
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_bow(draw_amount=0, location=(0, 0, 0))
    create_bow(draw_amount=0.8, location=(0.3, 0, 0))
    create_arrow(location=(0, 0.3, 0))
    
    print("Created bow and arrow")
