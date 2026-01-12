"""
{
  "title": "Animation Utilities",
  "category": "animation",
  "tags": ["keyframe", "timeline", "fcurve", "action", "interpolation", "animate"],
  "description": "Functions for keyframing, timeline control, and animation setup in Blender.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def set_keyframe(
    obj: bpy.types.Object,
    data_path: str,
    frame: int,
    value = None,
    index: int = -1
) -> None:
    """
    Insert a keyframe for an object property.
    
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
    interpolation: str = 'BEZIER'
) -> None:
    """
    Set interpolation mode for all keyframes of an object.
    
    Args:
        obj: Animated object
        interpolation: 'CONSTANT', 'LINEAR', 'BEZIER', 'SINE', 'QUAD', 'CUBIC', etc.
    
    Example:
        >>> set_interpolation(cube, 'LINEAR')
    """
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = interpolation


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
        fps: Frames per second
    
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
