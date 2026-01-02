"""
{
  "title": "Modifier Utilities",
  "category": "modifier",
  "tags": ["subdivision", "bevel", "mirror", "array", "boolean"],
  "description": "Functions to add and configure common modifiers for objects."
}
"""
import bpy

def add_subdivision(obj, levels=2, render_levels=2):
    mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod.levels = levels
    mod.render_levels = render_levels
    return mod

def add_bevel(obj, width=0.1, segments=3):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    return mod

def add_mirror(obj, axis='X', clipping=True):
    mod = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod.use_axis[0] = (axis == 'X')
    mod.use_axis[1] = (axis == 'Y')
    mod.use_axis[2] = (axis == 'Z')
    mod.use_clip = clipping
    return mod

def add_array(obj, count=3, relative_offset=(1.0, 0.0, 0.0)):
    mod = obj.modifiers.new(name="Array", type='ARRAY')
    mod.count = count
    mod.use_relative_offset = True
    mod.relative_offset_displace = relative_offset
    return mod

def add_boolean(obj, target_obj, operation='DIFFERENCE'):
    mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.object = target_obj
    mod.operation = operation
    return mod
