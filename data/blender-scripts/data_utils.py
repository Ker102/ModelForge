"""
{
  "title": "Data Management Utilities",
  "category": "scene",
  "tags": ["data", "cleanup", "orphan", "purge", "management"],
  "description": "Functions for managing Blender data blocks and cleanup.",
  "blender_version": "3.0+"
}
"""
import bpy


def purge_orphans() -> dict:
    """
    Remove all orphan data blocks.
    
    Returns:
        Dictionary with counts of removed items by type
    """
    counts = {}
    
    # Get counts before
    for attr in ['meshes', 'materials', 'textures', 'images', 
                 'curves', 'armatures', 'actions']:
        data = getattr(bpy.data, attr)
        orphans = [d for d in data if d.users == 0]
        if orphans:
            counts[attr] = len(orphans)
    
    # Purge
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    
    return counts


def list_unused_materials() -> list:
    """List materials with no users."""
    return [mat.name for mat in bpy.data.materials if mat.users == 0]


def list_unused_images() -> list:
    """List images with no users."""
    return [img.name for img in bpy.data.images if img.users == 0]


def remove_material(name: str) -> bool:
    """Remove material by name."""
    mat = bpy.data.materials.get(name)
    if mat:
        bpy.data.materials.remove(mat)
        return True
    return False


def remove_image(name: str) -> bool:
    """Remove image by name."""
    img = bpy.data.images.get(name)
    if img:
        bpy.data.images.remove(img)
        return True
    return False


def remove_mesh(name: str) -> bool:
    """Remove mesh data by name."""
    mesh = bpy.data.meshes.get(name)
    if mesh:
        bpy.data.meshes.remove(mesh)
        return True
    return False


def duplicate_data_block(
    data_block: bpy.types.ID,
    new_name: str = None
) -> bpy.types.ID:
    """
    Duplicate any data block.
    
    Args:
        data_block: Any Blender data block
        new_name: Optional new name
    
    Returns:
        Duplicated data block
    """
    copy = data_block.copy()
    if new_name:
        copy.name = new_name
    return copy


def rename_data_block(
    data_type: str,
    old_name: str,
    new_name: str
) -> bool:
    """
    Rename a data block.
    
    Args:
        data_type: 'objects', 'materials', 'meshes', 'images', etc.
        old_name: Current name
        new_name: New name
    
    Returns:
        Success status
    """
    data = getattr(bpy.data, data_type, None)
    if data:
        item = data.get(old_name)
        if item:
            item.name = new_name
            return True
    return False


def make_local(obj: bpy.types.Object, data: bool = True) -> None:
    """Make linked object local."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.make_local(type='ALL' if data else 'SELECT_OBJECT')


def make_single_user(
    obj: bpy.types.Object,
    object_data: bool = True,
    material: bool = True,
    animation: bool = True
) -> None:
    """Make object data single-user (unlink from other objects)."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.make_single_user(
        type='SELECTED_OBJECTS',
        object=True,
        obdata=object_data,
        material=material,
        animation=animation
    )


def pack_all_external() -> None:
    """Pack all external files into blend file."""
    bpy.ops.file.pack_all()


def unpack_all(method: str = 'USE_ORIGINAL') -> None:
    """
    Unpack all external files.
    
    Args:
        method: 'USE_ORIGINAL', 'WRITE_ORIGINAL', 'USE_LOCAL', 'WRITE_LOCAL'
    """
    bpy.ops.file.unpack_all(method=method)


def get_data_stats() -> dict:
    """Get statistics about scene data."""
    return {
        'objects': len(bpy.data.objects),
        'meshes': len(bpy.data.meshes),
        'materials': len(bpy.data.materials),
        'textures': len(bpy.data.textures),
        'images': len(bpy.data.images),
        'armatures': len(bpy.data.armatures),
        'actions': len(bpy.data.actions),
        'curves': len(bpy.data.curves),
        'cameras': len(bpy.data.cameras),
        'lights': len(bpy.data.lights),
        'worlds': len(bpy.data.worlds),
        'node_groups': len(bpy.data.node_groups)
    }


def list_linked_libraries() -> list:
    """List all linked library paths."""
    return [lib.filepath for lib in bpy.data.libraries]


def reload_linked_library(filepath: str) -> bool:
    """Reload a linked library."""
    lib = [l for l in bpy.data.libraries if l.filepath == filepath]
    if lib:
        lib[0].reload()
        return True
    return False


def merge_duplicate_materials(threshold: float = 0.01) -> int:
    """
    Merge materials with identical settings.
    
    Returns:
        Number of materials merged
    """
    merged = 0
    # This is a simplified approach - full implementation would
    # compare actual node setups
    seen = {}
    
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        
        for slot in obj.material_slots:
            if not slot.material:
                continue
            
            mat = slot.material
            base_name = mat.name.rsplit('.', 1)[0]
            
            if base_name in seen:
                slot.material = seen[base_name]
                merged += 1
            else:
                seen[base_name] = mat
    
    return merged
