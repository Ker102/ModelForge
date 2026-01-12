"""
{
  "title": "Object Operations Utilities",
  "category": "object",
  "tags": ["object", "duplicate", "join", "parent", "origin", "convert", "constraints"],
  "description": "Object-level operations including duplication, joining, parenting, origin manipulation, and constraints.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def duplicate_object(
    obj: bpy.types.Object = None,
    linked: bool = False,
    offset: tuple = (0, 0, 0)
) -> bpy.types.Object:
    """
    Duplicate an object.
    
    Args:
        obj: Object to duplicate (uses active if None)
        linked: Create linked duplicate (shares mesh data)
        offset: Position offset from original
    
    Returns:
        The duplicated object
    
    Example:
        >>> new_obj = duplicate_object(cube, offset=(2, 0, 0))
    """
    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
    
    bpy.ops.object.duplicate(linked=linked)
    duplicate = bpy.context.active_object
    duplicate.location.x += offset[0]
    duplicate.location.y += offset[1]
    duplicate.location.z += offset[2]
    
    return duplicate


def join_objects(objects: list) -> bpy.types.Object:
    """
    Join multiple objects into one.
    
    Args:
        objects: List of objects to join
    
    Returns:
        The resulting joined object
    
    Example:
        >>> result = join_objects([cube1, cube2, cube3])
    """
    bpy.ops.object.select_all(action='DESELECT')
    
    for obj in objects:
        obj.select_set(True)
    
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    
    return bpy.context.active_object


def set_parent(
    child: bpy.types.Object,
    parent: bpy.types.Object,
    keep_transform: bool = True
) -> None:
    """
    Parent one object to another.
    
    Args:
        child: Object to parent
        parent: Parent object
        keep_transform: Maintain child's world transform
    
    Example:
        >>> set_parent(wheel, car_body)
    """
    bpy.ops.object.select_all(action='DESELECT')
    child.select_set(True)
    parent.select_set(True)
    bpy.context.view_layer.objects.active = parent
    
    if keep_transform:
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    else:
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)


def clear_parent(obj: bpy.types.Object, keep_transform: bool = True) -> None:
    """
    Remove parent from object.
    
    Args:
        obj: Object to unparent
        keep_transform: Maintain world transform
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM' if keep_transform else 'CLEAR')


def set_origin(
    obj: bpy.types.Object,
    origin_type: str = 'GEOMETRY'
) -> None:
    """
    Set object origin point.
    
    Args:
        obj: Target object
        origin_type: 'GEOMETRY' (center of mesh), 'CURSOR' (3D cursor),
                    'CENTER_OF_MASS' (based on volume), 'CENTER_OF_VOLUME'
    
    Example:
        >>> set_origin(cube, 'GEOMETRY')
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    type_map = {
        'GEOMETRY': 'ORIGIN_GEOMETRY',
        'CURSOR': 'ORIGIN_CURSOR',
        'CENTER_OF_MASS': 'ORIGIN_CENTER_OF_MASS',
        'CENTER_OF_VOLUME': 'ORIGIN_CENTER_OF_VOLUME'
    }
    
    bpy.ops.object.origin_set(type=type_map.get(origin_type, 'ORIGIN_GEOMETRY'))


def apply_transforms(
    obj: bpy.types.Object,
    location: bool = False,
    rotation: bool = True,
    scale: bool = True
) -> None:
    """
    Apply object transforms to mesh data.
    
    Args:
        obj: Target object
        location: Apply location (move to origin)
        rotation: Apply rotation
        scale: Apply scale
    
    Example:
        >>> apply_transforms(obj, rotation=True, scale=True)
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def convert_to_mesh(obj: bpy.types.Object, keep_original: bool = False) -> bpy.types.Object:
    """
    Convert curve, text, or other object to mesh.
    
    Args:
        obj: Object to convert
        keep_original: Keep the original object
    
    Returns:
        The converted mesh object
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH', keep_original=keep_original)
    return bpy.context.active_object


def add_constraint(
    obj: bpy.types.Object,
    constraint_type: str,
    target: bpy.types.Object = None,
    **kwargs
) -> bpy.types.Constraint:
    """
    Add a constraint to an object.
    
    Args:
        obj: Object to constrain
        constraint_type: 'COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE',
                        'TRACK_TO', 'FOLLOW_PATH', 'LIMIT_LOCATION', etc.
        target: Target object for the constraint
        **kwargs: Additional constraint properties
    
    Returns:
        The created constraint
    
    Example:
        >>> add_constraint(camera, 'TRACK_TO', target=subject)
    """
    constraint = obj.constraints.new(type=constraint_type)
    
    if target and hasattr(constraint, 'target'):
        constraint.target = target
    
    for key, value in kwargs.items():
        if hasattr(constraint, key):
            setattr(constraint, key, value)
    
    return constraint


def copy_transforms(source: bpy.types.Object, target: bpy.types.Object) -> None:
    """
    Copy transforms from one object to another.
    
    Args:
        source: Object to copy from
        target: Object to copy to
    """
    target.location = source.location.copy()
    target.rotation_euler = source.rotation_euler.copy()
    target.scale = source.scale.copy()


def make_single_user(obj: bpy.types.Object, data: bool = True, materials: bool = True) -> None:
    """
    Make object data single-user (unlink from other objects).
    
    Args:
        obj: Object to make single-user
        data: Make mesh/curve data single-user
        materials: Make materials single-user
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.make_single_user(
        type='SELECTED_OBJECTS',
        object=True,
        obdata=data,
        material=materials
    )


def shade_smooth(obj: bpy.types.Object) -> None:
    """Set object to smooth shading."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()


def shade_flat(obj: bpy.types.Object) -> None:
    """Set object to flat shading."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_flat()


def add_empty(
    location: tuple = (0, 0, 0),
    empty_type: str = 'PLAIN_AXES',
    size: float = 1.0,
    name: str = "Empty"
) -> bpy.types.Object:
    """
    Add an empty object.
    
    Args:
        location: Position
        empty_type: 'PLAIN_AXES', 'ARROWS', 'CIRCLE', 'CUBE', 'SPHERE', 'CONE'
        size: Display size
        name: Object name
    
    Returns:
        The created empty
    """
    bpy.ops.object.empty_add(type=empty_type, location=location, radius=size)
    empty = bpy.context.active_object
    empty.name = name
    return empty


def group_objects(objects: list, empty_name: str = "Group") -> bpy.types.Object:
    """
    Group objects under an empty parent.
    
    Args:
        objects: Objects to group
        empty_name: Name for the group empty
    
    Returns:
        The group empty object
    """
    # Calculate center
    center = [0, 0, 0]
    for obj in objects:
        center[0] += obj.location.x
        center[1] += obj.location.y
        center[2] += obj.location.z
    
    n = len(objects)
    center = (center[0]/n, center[1]/n, center[2]/n)
    
    # Create empty at center
    group = add_empty(location=center, name=empty_name)
    
    # Parent all objects to empty
    for obj in objects:
        set_parent(obj, group, keep_transform=True)
    
    return group
