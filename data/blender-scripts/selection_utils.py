"""
{
  "title": "Object Selection Utilities",
  "category": "selection",
  "tags": ["select", "deselect", "active", "find"],
  "description": "Helper functions to manage object selection state in the scene."
}
"""
import bpy

def select_all():
    bpy.ops.object.select_all(action='SELECT')

def deselect_all():
    bpy.ops.object.select_all(action='DESELECT')

def select_object(obj):
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def select_by_name(name):
    deselect_all()
    obj = bpy.data.objects.get(name)
    if obj:
        select_object(obj)
        return obj
    return None

def select_by_type(type='MESH'):
    deselect_all()
    for obj in bpy.context.scene.objects:
        if obj.type == type:
            obj.select_set(True)

def invert_selection():
    bpy.ops.object.select_all(action='INVERT')
