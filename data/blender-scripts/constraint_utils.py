"""
{
  "title": "Constraint Utilities",
  "category": "constraints",
  "tags": ["constraint", "track", "follow", "copy", "limit", "animation"],
  "description": "Functions for adding and configuring object and bone constraints.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def add_copy_location(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    use_offset: bool = False,
    axes: str = 'XYZ'
) -> bpy.types.Constraint:
    """Add copy location constraint."""
    c = obj.constraints.new('COPY_LOCATION')
    c.target = target
    c.use_offset = use_offset
    c.use_x = 'X' in axes
    c.use_y = 'Y' in axes
    c.use_z = 'Z' in axes
    return c


def add_copy_rotation(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    use_offset: bool = False,
    axes: str = 'XYZ'
) -> bpy.types.Constraint:
    """Add copy rotation constraint."""
    c = obj.constraints.new('COPY_ROTATION')
    c.target = target
    c.use_offset = use_offset
    c.use_x = 'X' in axes
    c.use_y = 'Y' in axes
    c.use_z = 'Z' in axes
    return c


def add_copy_scale(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    axes: str = 'XYZ'
) -> bpy.types.Constraint:
    """Add copy scale constraint."""
    c = obj.constraints.new('COPY_SCALE')
    c.target = target
    c.use_x = 'X' in axes
    c.use_y = 'Y' in axes
    c.use_z = 'Z' in axes
    return c


def add_copy_transforms(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    mix_mode: str = 'REPLACE'
) -> bpy.types.Constraint:
    """Add copy transforms constraint."""
    c = obj.constraints.new('COPY_TRANSFORMS')
    c.target = target
    c.mix_mode = mix_mode
    return c


def add_track_to(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    track_axis: str = 'TRACK_NEGATIVE_Z',
    up_axis: str = 'UP_Y'
) -> bpy.types.Constraint:
    """Add track to constraint (point at target)."""
    c = obj.constraints.new('TRACK_TO')
    c.target = target
    c.track_axis = track_axis
    c.up_axis = up_axis
    return c


def add_damped_track(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    track_axis: str = 'TRACK_NEGATIVE_Z'
) -> bpy.types.Constraint:
    """Add damped track constraint (simpler pointing)."""
    c = obj.constraints.new('DAMPED_TRACK')
    c.target = target
    c.track_axis = track_axis
    return c


def add_follow_path(
    obj: bpy.types.Object,
    path: bpy.types.Object,
    use_curve_follow: bool = True,
    forward_axis: str = 'FORWARD_Y',
    up_axis: str = 'UP_Z'
) -> bpy.types.Constraint:
    """Add follow path constraint."""
    c = obj.constraints.new('FOLLOW_PATH')
    c.target = path
    c.use_curve_follow = use_curve_follow
    c.forward_axis = forward_axis
    c.up_axis = up_axis
    return c


def add_limit_location(
    obj: bpy.types.Object,
    min_x: float = None, max_x: float = None,
    min_y: float = None, max_y: float = None,
    min_z: float = None, max_z: float = None,
    use_transform_limit: bool = True
) -> bpy.types.Constraint:
    """Add limit location constraint."""
    c = obj.constraints.new('LIMIT_LOCATION')
    
    if min_x is not None:
        c.use_min_x = True
        c.min_x = min_x
    if max_x is not None:
        c.use_max_x = True
        c.max_x = max_x
    if min_y is not None:
        c.use_min_y = True
        c.min_y = min_y
    if max_y is not None:
        c.use_max_y = True
        c.max_y = max_y
    if min_z is not None:
        c.use_min_z = True
        c.min_z = min_z
    if max_z is not None:
        c.use_max_z = True
        c.max_z = max_z
    
    c.use_transform_limit = use_transform_limit
    return c


def add_limit_rotation(
    obj: bpy.types.Object,
    min_x: float = None, max_x: float = None,
    min_y: float = None, max_y: float = None,
    min_z: float = None, max_z: float = None
) -> bpy.types.Constraint:
    """Add limit rotation constraint (angles in degrees)."""
    c = obj.constraints.new('LIMIT_ROTATION')
    
    if min_x is not None:
        c.use_limit_x = True
        c.min_x = math.radians(min_x)
    if max_x is not None:
        c.use_limit_x = True
        c.max_x = math.radians(max_x)
    if min_y is not None:
        c.use_limit_y = True
        c.min_y = math.radians(min_y)
    if max_y is not None:
        c.use_limit_y = True
        c.max_y = math.radians(max_y)
    if min_z is not None:
        c.use_limit_z = True
        c.min_z = math.radians(min_z)
    if max_z is not None:
        c.use_limit_z = True
        c.max_z = math.radians(max_z)
    
    return c


def add_floor(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    offset: float = 0.0,
    floor_location: str = 'FLOOR_Z'
) -> bpy.types.Constraint:
    """Add floor constraint (prevent going below target)."""
    c = obj.constraints.new('FLOOR')
    c.target = target
    c.offset = offset
    c.floor_location = floor_location
    return c


def add_child_of(
    obj: bpy.types.Object,
    parent: bpy.types.Object,
    subtarget: str = None
) -> bpy.types.Constraint:
    """Add child of constraint."""
    c = obj.constraints.new('CHILD_OF')
    c.target = parent
    if subtarget:
        c.subtarget = subtarget
    return c


def add_locked_track(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    track_axis: str = 'TRACK_Y',
    lock_axis: str = 'LOCK_Z'
) -> bpy.types.Constraint:
    """Add locked track constraint."""
    c = obj.constraints.new('LOCKED_TRACK')
    c.target = target
    c.track_axis = track_axis
    c.lock_axis = lock_axis
    return c


def remove_all_constraints(obj: bpy.types.Object) -> None:
    """Remove all constraints from object."""
    for c in obj.constraints[:]:
        obj.constraints.remove(c)


def set_constraint_influence(
    obj: bpy.types.Object,
    constraint_name: str,
    influence: float
) -> None:
    """Set constraint influence (0-1)."""
    if constraint_name in obj.constraints:
        obj.constraints[constraint_name].influence = influence
