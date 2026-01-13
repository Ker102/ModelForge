"""
{
  "title": "Batch Operations Utilities",
  "category": "automation",
  "tags": ["batch", "bulk", "automation", "multiple", "operations"],
  "description": "Functions for performing operations on multiple objects.",
  "blender_version": "3.0+"
}
"""
import bpy


def batch_rename(
    prefix: str = None,
    suffix: str = None,
    replace_from: str = None,
    replace_to: str = None,
    selection_only: bool = True
) -> int:
    """
    Batch rename objects.
    
    Args:
        prefix: Add prefix to names
        suffix: Add suffix to names
        replace_from: Text to replace
        replace_to: Replacement text
        selection_only: Only selected objects
    
    Returns:
        Number of objects renamed
    """
    count = 0
    objects = bpy.context.selected_objects if selection_only else bpy.data.objects
    
    for obj in objects:
        new_name = obj.name
        
        if replace_from and replace_to is not None:
            new_name = new_name.replace(replace_from, replace_to)
        
        if prefix:
            new_name = prefix + new_name
        
        if suffix:
            new_name = new_name + suffix
        
        if new_name != obj.name:
            obj.name = new_name
            count += 1
    
    return count


def batch_apply_modifier(
    modifier_type: str,
    selection_only: bool = True,
    **modifier_settings
) -> int:
    """
    Add modifier to multiple objects.
    
    Args:
        modifier_type: Modifier type name
        selection_only: Only selected objects
        **modifier_settings: Modifier-specific settings
    
    Returns:
        Number of objects modified
    """
    count = 0
    objects = bpy.context.selected_objects if selection_only else bpy.data.objects
    
    for obj in objects:
        if obj.type != 'MESH':
            continue
        
        mod = obj.modifiers.new(modifier_type, modifier_type.upper())
        
        for key, value in modifier_settings.items():
            if hasattr(mod, key):
                setattr(mod, key, value)
        
        count += 1
    
    return count


def batch_apply_material(
    material: bpy.types.Material,
    selection_only: bool = True,
    replace_all: bool = False
) -> int:
    """
    Apply material to multiple objects.
    
    Args:
        material: Material to apply
        selection_only: Only selected objects
        replace_all: Replace all materials or just add
    
    Returns:
        Number of objects modified
    """
    count = 0
    objects = bpy.context.selected_objects if selection_only else bpy.data.objects
    
    for obj in objects:
        if obj.type != 'MESH':
            continue
        
        if replace_all:
            obj.data.materials.clear()
        
        obj.data.materials.append(material)
        count += 1
    
    return count


def batch_set_smooth(
    smooth: bool = True,
    selection_only: bool = True
) -> int:
    """
    Set smooth/flat shading for multiple objects.
    
    Returns:
        Number of objects modified
    """
    count = 0
    objects = bpy.context.selected_objects if selection_only else bpy.data.objects
    
    for obj in objects:
        if obj.type != 'MESH':
            continue
        
        for poly in obj.data.polygons:
            poly.use_smooth = smooth
        count += 1
    
    return count


def batch_origin_to_geometry(selection_only: bool = True) -> int:
    """Set origin to geometry center for multiple objects."""
    count = 0
    objects = bpy.context.selected_objects if selection_only else bpy.data.objects
    
    bpy.ops.object.select_all(action='DESELECT')
    
    for obj in objects:
        if obj.type != 'MESH':
            continue
        
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        obj.select_set(False)
        count += 1
    
    return count


def batch_apply_transforms(
    location: bool = True,
    rotation: bool = True,
    scale: bool = True,
    selection_only: bool = True
) -> int:
    """Apply transforms to multiple objects."""
    objects = bpy.context.selected_objects if selection_only else list(bpy.data.objects)
    
    bpy.ops.object.select_all(action='DESELECT')
    
    for obj in objects:
        obj.select_set(True)
    
    bpy.ops.object.transform_apply(
        location=location,
        rotation=rotation,
        scale=scale
    )
    
    return len(objects)


def batch_convert_to_mesh(selection_only: bool = True) -> int:
    """Convert curves/text/etc to mesh for multiple objects."""
    count = 0
    objects = bpy.context.selected_objects if selection_only else list(bpy.data.objects)
    
    for obj in objects:
        if obj.type in ['CURVE', 'FONT', 'SURFACE', 'META']:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.convert(target='MESH')
            obj.select_set(False)
            count += 1
    
    return count


def batch_set_property(
    property_path: str,
    value,
    selection_only: bool = True
) -> int:
    """
    Set property on multiple objects.
    
    Args:
        property_path: Property path (e.g., 'display_type', 'hide_render')
        value: Value to set
        selection_only: Only selected objects
    
    Returns:
        Number of objects modified
    """
    count = 0
    objects = bpy.context.selected_objects if selection_only else bpy.data.objects
    
    for obj in objects:
        try:
            setattr(obj, property_path, value)
            count += 1
        except:
            pass
    
    return count


def batch_parent_to(
    parent: bpy.types.Object,
    keep_transform: bool = True,
    selection_only: bool = True
) -> int:
    """Parent multiple objects to one parent."""
    count = 0
    objects = bpy.context.selected_objects if selection_only else list(bpy.data.objects)
    
    for obj in objects:
        if obj == parent:
            continue
        
        if keep_transform:
            matrix = obj.matrix_world.copy()
        
        obj.parent = parent
        
        if keep_transform:
            obj.matrix_world = matrix
        
        count += 1
    
    return count


def batch_unparent(
    keep_transform: bool = True,
    selection_only: bool = True
) -> int:
    """Unparent multiple objects."""
    count = 0
    objects = bpy.context.selected_objects if selection_only else list(bpy.data.objects)
    
    for obj in objects:
        if obj.parent:
            if keep_transform:
                matrix = obj.matrix_world.copy()
            
            obj.parent = None
            
            if keep_transform:
                obj.matrix_world = matrix
            
            count += 1
    
    return count


def foreach_selected(callback, *args, **kwargs) -> list:
    """
    Execute callback function on each selected object.
    
    Args:
        callback: Function to call with (object, *args, **kwargs)
    
    Returns:
        List of callback return values
    """
    results = []
    for obj in bpy.context.selected_objects:
        result = callback(obj, *args, **kwargs)
        results.append(result)
    return results
