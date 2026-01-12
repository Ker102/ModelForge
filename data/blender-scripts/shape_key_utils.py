"""
{
  "title": "Shape Key Utilities",
  "category": "animation",
  "tags": ["shape", "key", "morph", "blend", "deform", "facial"],
  "description": "Functions for creating and managing shape keys for mesh deformation.",
  "blender_version": "3.0+"
}
"""
import bpy


def add_basis_shape_key(obj: bpy.types.Object) -> bpy.types.ShapeKey:
    """Add basis (reference) shape key to mesh."""
    if obj.data.shape_keys is None:
        obj.shape_key_add(name='Basis', from_mix=False)
    return obj.data.shape_keys.key_blocks['Basis']


def add_shape_key(
    obj: bpy.types.Object,
    name: str,
    from_mix: bool = False
) -> bpy.types.ShapeKey:
    """
    Add a new shape key.
    
    Args:
        obj: Target mesh object
        name: Shape key name
        from_mix: Create from current mix of all keys
    
    Returns:
        The created shape key
    """
    if obj.data.shape_keys is None:
        add_basis_shape_key(obj)
    
    key = obj.shape_key_add(name=name, from_mix=from_mix)
    return key


def set_shape_key_value(
    obj: bpy.types.Object,
    name: str,
    value: float
) -> None:
    """Set shape key value (0-1)."""
    if obj.data.shape_keys and name in obj.data.shape_keys.key_blocks:
        obj.data.shape_keys.key_blocks[name].value = value


def get_shape_key_value(obj: bpy.types.Object, name: str) -> float:
    """Get shape key value."""
    if obj.data.shape_keys and name in obj.data.shape_keys.key_blocks:
        return obj.data.shape_keys.key_blocks[name].value
    return 0.0


def set_shape_key_range(
    obj: bpy.types.Object,
    name: str,
    min_val: float = 0.0,
    max_val: float = 1.0
) -> None:
    """Set shape key value range."""
    if obj.data.shape_keys and name in obj.data.shape_keys.key_blocks:
        key = obj.data.shape_keys.key_blocks[name]
        key.slider_min = min_val
        key.slider_max = max_val


def keyframe_shape_key(
    obj: bpy.types.Object,
    name: str,
    value: float,
    frame: int
) -> None:
    """Insert keyframe for shape key."""
    if obj.data.shape_keys and name in obj.data.shape_keys.key_blocks:
        key = obj.data.shape_keys.key_blocks[name]
        key.value = value
        key.keyframe_insert(data_path='value', frame=frame)


def create_morph_animation(
    obj: bpy.types.Object,
    shape_name: str,
    start_frame: int = 1,
    peak_frame: int = 12,
    end_frame: int = 24
) -> None:
    """
    Create a morph in/out animation.
    
    Args:
        obj: Target mesh
        shape_name: Shape key name
        start_frame: Animation start
        peak_frame: Full morph frame
        end_frame: Animation end
    """
    keyframe_shape_key(obj, shape_name, 0.0, start_frame)
    keyframe_shape_key(obj, shape_name, 1.0, peak_frame)
    keyframe_shape_key(obj, shape_name, 0.0, end_frame)


def copy_shape_key_from_object(
    target: bpy.types.Object,
    source: bpy.types.Object,
    key_name: str,
    new_name: str = None
) -> bpy.types.ShapeKey:
    """
    Copy shape key from another object.
    
    Args:
        target: Object to receive shape key
        source: Object with source shape key
        key_name: Name of key to copy
        new_name: Name for copied key (uses original if None)
    
    Returns:
        The new shape key
    """
    if source.data.shape_keys is None:
        return None
    
    source_key = source.data.shape_keys.key_blocks.get(key_name)
    if source_key is None:
        return None
    
    # Add basis if needed
    if target.data.shape_keys is None:
        add_basis_shape_key(target)
    
    # Create new key
    new_key = target.shape_key_add(name=new_name or key_name, from_mix=False)
    
    # Copy vertex positions
    for i, (sv, tv) in enumerate(zip(source_key.data, new_key.data)):
        tv.co = sv.co.copy()
    
    return new_key


def remove_shape_key(obj: bpy.types.Object, name: str) -> None:
    """Remove shape key by name."""
    if obj.data.shape_keys and name in obj.data.shape_keys.key_blocks:
        key = obj.data.shape_keys.key_blocks[name]
        obj.shape_key_remove(key)


def remove_all_shape_keys(obj: bpy.types.Object) -> None:
    """Remove all shape keys."""
    if obj.data.shape_keys:
        obj.shape_key_clear()


def list_shape_keys(obj: bpy.types.Object) -> list:
    """Return list of shape key names."""
    if obj.data.shape_keys:
        return [k.name for k in obj.data.shape_keys.key_blocks]
    return []
