"""
{
  "title": "Curve Geometry Utilities",
  "category": "curve",
  "tags": ["bezier", "circle", "path", "curve"],
  "description": "Functions to create curve objects like Bezier curves and circles."
}
"""
import bpy

def add_bezier_curve(location=(0, 0, 0), radius=1.0):
    bpy.ops.curve.primitive_bezier_curve_add(radius=radius, location=location)
    return bpy.context.active_object

def add_bezier_circle(location=(0, 0, 0), radius=1.0):
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, location=location)
    return bpy.context.active_object

def add_nurbs_path(location=(0, 0, 0), radius=1.0):
    bpy.ops.curve.primitive_nurbs_path_add(radius=radius, location=location)
    return bpy.context.active_object

def create_path_from_points(name="Path", points=[]):
    if not points:
        return None
    
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    
    spline = curve_data.splines.new(type='POLY')
    spline.points.add(len(points) - 1)
    
    for i, point in enumerate(points):
        x, y, z = point
        spline.points[i].co = (x, y, z, 1)
        
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    return obj
