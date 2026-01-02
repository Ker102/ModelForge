"""
{
  "title": "Object Transformations",
  "category": "transform",
  "tags": ["move", "rotate", "scale", "position"],
  "description": "Modifying object location, rotation, and scale properties directly."
}
"""
import bpy
import math

def move_object(obj, location=(0, 0, 0)):
    obj.location = location

def rotate_object(obj, rotation_degrees=(0, 0, 0)):
    # Blender uses radians for rotation_euler
    obj.rotation_euler[0] = math.radians(rotation_degrees[0])
    obj.rotation_euler[1] = math.radians(rotation_degrees[1])
    obj.rotation_euler[2] = math.radians(rotation_degrees[2])

def scale_object(obj, scale=(1, 1, 1)):
    obj.scale = scale

def apply_transforms(obj, location=True, rotation=True, scale=True):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)
