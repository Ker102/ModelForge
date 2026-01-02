"""
{
  "title": "Text Object Utilities",
  "category": "text",
  "tags": ["text", "font", "3d text", "typography"],
  "description": "Functions to create and modify 3D text objects."
}
"""
import bpy

def create_3d_text(text="ModelForge", location=(0, 0, 0), size=1.0, extrude=0.1):
    bpy.ops.object.text_add(location=location)
    obj = bpy.context.active_object
    obj.data.body = text
    obj.data.size = size
    obj.data.extrude = extrude
    return obj

def set_text_font(obj, font_path):
    try:
        font = bpy.data.fonts.load(font_path)
        obj.data.font = font
    except Exception as e:
        print(f"Could not load font: {font_path}")

def set_text_alignment(obj, horizontal='CENTER', vertical='CENTER_VERTICAL'):
    obj.data.align_x = horizontal
    obj.data.align_y = vertical
