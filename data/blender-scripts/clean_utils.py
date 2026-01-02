"""
{
  "title": "Scene Cleanup Utilities",
  "category": "clean",
  "tags": ["delete", "remove", "clean", "purge"],
  "description": "Functions to clear the scene or remove unused data blocks."
}
"""
import bpy

def delete_all_objects():
    if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def delete_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)

def purge_orphans():
    # Purge unused data blocks (meshes, materials, textures, etc.)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
            
    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)
            
    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)
