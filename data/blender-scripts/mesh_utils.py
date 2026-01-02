"""
{
  "title": "Create Basic Mesh Primitives",
  "category": "mesh",
  "tags": ["cube", "sphere", "cylinder", "primitive"],
  "description": "Standard way to add basic geometric shapes to the scene using bpy.ops.mesh."
}
"""
import bpy
import math

def add_cube(location=(0, 0, 0), rotation=(0, 0, 0), size=2, name="Cube"):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location, rotation=tuple(math.radians(d) for d in rotation))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_sphere(location=(0, 0, 0), rotation=(0, 0, 0), radius=1, segments=32, ring_count=16, name="Sphere"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments, ring_count=ring_count, location=location, rotation=tuple(math.radians(d) for d in rotation))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_cylinder(location=(0, 0, 0), rotation=(0, 0, 0), radius=1, depth=2, vertices=32, name="Cylinder"):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=vertices, location=location, rotation=tuple(math.radians(d) for d in rotation))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_plane(location=(0, 0, 0), rotation=(0, 0, 0), size=2, name="Plane"):
    bpy.ops.mesh.primitive_plane_add(size=size, location=location, rotation=tuple(math.radians(d) for d in rotation))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_torus(location=(0, 0, 0), rotation=(0, 0, 0), major_radius=1, minor_radius=0.25, major_segments=48, minor_segments=12, name="Torus"):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_radius, minor_radius=minor_radius, major_segments=major_segments, minor_segments=minor_segments, location=location, rotation=tuple(math.radians(d) for d in rotation))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_cone(location=(0, 0, 0), rotation=(0, 0, 0), radius1=1, radius2=0, depth=2, vertices=32, name="Cone"):
    bpy.ops.mesh.primitive_cone_add(radius1=radius1, radius2=radius2, depth=depth, vertices=vertices, location=location, rotation=tuple(math.radians(d) for d in rotation))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_monkey(location=(0, 0, 0), rotation=(0, 0, 0), size=2, name="Suzanne"):
    bpy.ops.mesh.primitive_monkey_add(size=size, location=location, rotation=tuple(math.radians(d) for d in rotation))
    obj = bpy.context.active_object
    obj.name = name
    return obj
