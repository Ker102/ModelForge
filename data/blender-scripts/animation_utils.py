"""
{
  "title": "Animation Utilities (Blender 5.0+)",
  "category": "animation",
  "tags": ["keyframe", "timeline", "fcurve", "action", "interpolation", "animate", "channelbag", "slotted-actions"],
  "description": "Functions for keyframing, timeline control, interpolation, and animation setup using the Blender 5.0+ Slotted Actions API. Uses channelbag-based fcurve access instead of the removed action.fcurves legacy API.",
  "blender_version": "5.0+"
}
"""
import bpy
import math
from bpy_extras import anim_utils


# =============================================================================
# CORE: F-Curve Access via Channelbag (Blender 5.0+ Slotted Actions)
# =============================================================================
# In Blender 5.0, action.fcurves was REMOVED.
# F-Curves now live inside Channelbags, which are per-slot containers
# within an Action's layer → strip → channelbag hierarchy.
#
# Use these helpers:
#   anim_utils.action_get_channelbag_for_slot(action, slot)   → read existing
#   anim_utils.action_ensure_channelbag_for_slot(action, slot) → create if needed
# =============================================================================


def get_fcurves(obj: bpy.types.Object) -> list:
    """
    Get all F-Curves for an object using the 5.0+ channelbag API.
    
    In Blender 5.0, action.fcurves was removed. F-Curves are now accessed
    through channelbags, which are per-slot containers in the action hierarchy.
    
    Args:
        obj: Animated object
    
    Returns:
        List of FCurves, or empty list if no animation data
    
    Example:
        >>> fcurves = get_fcurves(cube)
        >>> for fc in fcurves:
        ...     print(fc.data_path, fc.array_index)
    """
    if not obj.animation_data or not obj.animation_data.action:
        return []
    
    action = obj.animation_data.action
    slot = obj.animation_data.action_slot
    
    if not slot:
        return []
    
    channelbag = anim_utils.action_get_channelbag_for_slot(action, slot)
    if not channelbag:
        return []
    
    return list(channelbag.fcurves)


def set_keyframe(
    obj: bpy.types.Object,
    data_path: str,
    frame: int,
    value=None,
    index: int = -1
) -> None:
    """
    Insert a keyframe for an object property.
    
    Note: keyframe_insert() is unchanged in Blender 5.0 — it automatically
    handles slotted actions, creating layers/strips/channelbags as needed.
    
    Args:
        obj: Object to keyframe
        data_path: Property path (e.g., 'location', 'rotation_euler', 'scale')
        frame: Frame number
        value: Value to set (optional, uses current if None)
        index: Array index (-1 for all)
    
    Example:
        >>> set_keyframe(cube, 'location', 1)
        >>> cube.location.z = 5
        >>> set_keyframe(cube, 'location', 60)
    """
    if value is not None:
        if index >= 0:
            getattr(obj, data_path)[index] = value
        else:
            setattr(obj, data_path, value)
    
    obj.keyframe_insert(data_path=data_path, frame=frame, index=index)


def animate_property(
    obj: bpy.types.Object,
    data_path: str,
    keyframes: list,
    index: int = -1
) -> None:
    """
    Animate a property with multiple keyframes.
    
    Args:
        obj: Object to animate
        data_path: Property path
        keyframes: List of (frame, value) tuples
        index: Array index (-1 for all)
    
    Example:
        >>> animate_property(cube, 'location', [(1, (0,0,0)), (30, (0,0,5)), (60, (0,0,0))])
    """
    for frame, value in keyframes:
        set_keyframe(obj, data_path, frame, value, index)


def set_interpolation(
    obj: bpy.types.Object,
    interpolation: str = 'BEZIER',
    data_path: str = None
) -> None:
    """
    Set interpolation mode for keyframes using the 5.0+ channelbag API.
    
    In Blender 5.0, action.fcurves was removed. This function accesses
    F-Curves through the channelbag (per-slot container).
    
    Args:
        obj: Animated object
        interpolation: 'CONSTANT', 'LINEAR', 'BEZIER', 'SINE', 'QUAD',
                       'CUBIC', 'QUART', 'QUINT', 'EXPO', 'CIRC',
                       'BACK', 'BOUNCE', 'ELASTIC'
        data_path: Optional — only set interpolation for this data path.
                   If None, sets for all fcurves.
    
    Example:
        >>> set_interpolation(cube, 'LINEAR')
        >>> set_interpolation(cube, 'BEZIER', data_path='rotation_euler')
    """
    fcurves = get_fcurves(obj)
    for fcurve in fcurves:
        if data_path and fcurve.data_path != data_path:
            continue
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = interpolation


def set_handle_type(
    obj: bpy.types.Object,
    handle_type: str = 'AUTO_CLAMPED',
    data_path: str = None,
    index: int = -1
) -> None:
    """
    Set keyframe handle types for smooth motion control.
    
    Args:
        obj: Animated object
        handle_type: 'FREE', 'ALIGNED', 'VECTOR', 'AUTO', 'AUTO_CLAMPED'
        data_path: Optional — only set for this property path
        index: Array index (-1 for all)
    
    Example:
        >>> set_handle_type(cube, 'AUTO_CLAMPED')  # Smooth ease-in-out
        >>> set_handle_type(cube, 'VECTOR', data_path='location')  # Sharp
    """
    fcurves = get_fcurves(obj)
    for fcurve in fcurves:
        if data_path and fcurve.data_path != data_path:
            continue
        if index >= 0 and fcurve.array_index != index:
            continue
        for kf in fcurve.keyframe_points:
            kf.handle_left_type = handle_type
            kf.handle_right_type = handle_type


def set_frame_range(start: int, end: int, current: int = None) -> None:
    """
    Set the animation frame range.
    
    Args:
        start: Start frame
        end: End frame
        current: Current frame (optional)
    
    Example:
        >>> set_frame_range(1, 250, 1)
    """
    scene = bpy.context.scene
    scene.frame_start = start
    scene.frame_end = end
    if current is not None:
        scene.frame_set(current)


def set_fps(fps: int = 24) -> None:
    """
    Set the scene frame rate.
    
    Args:
        fps: Frames per second (24=film, 30=video, 60=game)
    
    Example:
        >>> set_fps(30)  # Standard video
        >>> set_fps(24)  # Film
    """
    bpy.context.scene.render.fps = fps
    bpy.context.scene.render.fps_base = 1.0


def create_bounce_animation(
    obj: bpy.types.Object,
    height: float = 2.0,
    duration: int = 30,
    start_frame: int = 1,
    bounces: int = 3
) -> None:
    """
    Create a bouncing animation with decreasing height.
    
    Args:
        obj: Object to animate
        height: Initial bounce height
        duration: Total frames
        start_frame: Starting frame
        bounces: Number of bounces
    
    Example:
        >>> create_bounce_animation(ball, height=3, duration=60, bounces=4)
    """
    base_z = obj.location.z
    frames_per_bounce = duration // bounces
    
    frame = start_frame
    for i in range(bounces):
        bounce_height = height * (0.6 ** i)
        
        # Ground position
        obj.location.z = base_z
        obj.keyframe_insert('location', frame=frame, index=2)
        
        # Peak position
        peak_frame = frame + frames_per_bounce // 2
        obj.location.z = base_z + bounce_height
        obj.keyframe_insert('location', frame=peak_frame, index=2)
        
        frame += frames_per_bounce
    
    # Final ground position
    obj.location.z = base_z
    obj.keyframe_insert('location', frame=frame, index=2)
    
    # Set bezier interpolation for natural arc
    set_interpolation(obj, 'BEZIER')


def create_rotation_animation(
    obj: bpy.types.Object,
    axis: str = 'Z',
    degrees: float = 360,
    duration: int = 60,
    start_frame: int = 1,
    cycles: int = 1
) -> None:
    """
    Create a rotation animation (e.g., for turntables).
    
    Args:
        obj: Object to rotate
        axis: 'X', 'Y', or 'Z'
        degrees: Total rotation per cycle
        duration: Frames per cycle
        start_frame: Starting frame
        cycles: Number of rotations
    
    Example:
        >>> create_rotation_animation(product, axis='Z', degrees=360, duration=120)
    """
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[axis.upper()]
    
    for cycle in range(cycles):
        frame_start = start_frame + (cycle * duration)
        frame_end = frame_start + duration
        
        # Start rotation
        obj.keyframe_insert('rotation_euler', frame=frame_start, index=axis_index)
        
        # End rotation
        obj.rotation_euler[axis_index] += math.radians(degrees)
        obj.keyframe_insert('rotation_euler', frame=frame_end, index=axis_index)
    
    # Set linear interpolation for smooth rotation
    set_interpolation(obj, 'LINEAR')


def create_path_animation(
    obj: bpy.types.Object,
    path: bpy.types.Object,
    duration: int = 100,
    follow_curve: bool = True
) -> bpy.types.Constraint:
    """
    Animate an object along a curve path.
    
    Args:
        obj: Object to animate
        path: Curve object to follow
        duration: Animation duration in frames
        follow_curve: Rotate object to follow path direction
    
    Returns:
        The Follow Path constraint
    
    Example:
        >>> constraint = create_path_animation(car, road_curve, duration=200)
    """
    constraint = obj.constraints.new('FOLLOW_PATH')
    constraint.target = path
    constraint.use_curve_follow = follow_curve
    
    # Animate the offset
    constraint.offset = 0
    constraint.keyframe_insert('offset', frame=1)
    constraint.offset = -100
    constraint.keyframe_insert('offset', frame=duration)
    
    return constraint


def ensure_fcurve(
    obj: bpy.types.Object,
    data_path: str,
    index: int = 0,
    group_name: str = ""
):
    """
    Ensure an F-Curve exists for a given data path using 5.0+ API.
    Creates the channelbag, layer, strip, and F-Curve if needed.
    
    Args:
        obj: Object that owns the animation
        data_path: RNA property path (e.g., 'location')
        index: Array index (0, 1, 2 for x, y, z)
        group_name: Optional channel group name
    
    Returns:
        The FCurve object
    
    Example:
        >>> fc = ensure_fcurve(cube, 'location', index=2, group_name='Position')
    """
    if not obj.animation_data:
        obj.animation_data_create()
    
    action = obj.animation_data.action
    if not action:
        action = bpy.data.actions.new(name=f"{obj.name}Action")
        obj.animation_data.action = action
    
    slot = obj.animation_data.action_slot
    if not slot:
        # Auto-assign a suitable slot
        if action.slots:
            for s in action.slots:
                if s.target_id_type == obj.id_type:
                    obj.animation_data.action_slot = s
                    slot = s
                    break
        if not slot:
            slot = action.slots.new(id_type=obj.id_type, name=obj.name)
            obj.animation_data.action_slot = slot
    
    channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)
    
    if group_name:
        fcurve = channelbag.fcurves.ensure(data_path, index=index, group_name=group_name)
    else:
        fcurve = channelbag.fcurves.ensure(data_path, index=index)
    
    return fcurve
