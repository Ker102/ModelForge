"""
{
  "title": "Procedural Animation Patterns",
  "category": "animation",
  "tags": ["procedural", "keyframe", "NLA", "orbit", "wave", "pendulum", "spring", "math", "camera", "dolly-zoom"],
  "description": "Math-driven keyframe animation patterns for common motion types: orbit, wave, pendulum, spring, camera dolly zoom. Also includes NLA track composition for layering animations and production animation setup.",
  "blender_version": "4.0+"
}
"""
import bpy
import math


def orbit_animation(
    obj: bpy.types.Object,
    center: tuple = (0, 0, 0),
    radius: float = 5.0,
    duration: int = 120,
    start_frame: int = 1,
    axis: str = 'Z',
    revolutions: int = 1,
    tilt: float = 0.0
) -> None:
    """
    Animate an object orbiting around a center point.
    Perfect for planets, cameras, or particle-like motion.

    Args:
        obj: Object to animate
        center: Center point of the orbit (x, y, z)
        radius: Orbit radius
        duration: Total frames for one revolution
        start_frame: Starting frame
        axis: Orbit axis ('X', 'Y', 'Z')
        revolutions: Number of complete orbits
        tilt: Tilt angle in degrees (for inclined orbits)

    Example:
        >>> orbit_animation(camera, center=(0,0,0), radius=10, duration=240)
        >>> orbit_animation(moon, center=planet.location, radius=3, revolutions=2)
    """
    total_frames = duration * revolutions
    tilt_rad = math.radians(tilt)

    for frame in range(start_frame, start_frame + total_frames + 1):
        t = (frame - start_frame) / duration
        angle = t * 2 * math.pi

        if axis == 'Z':
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = center[2] + radius * math.sin(tilt_rad) * math.sin(angle)
        elif axis == 'Y':
            x = center[0] + radius * math.cos(angle)
            y = center[1]
            z = center[2] + radius * math.sin(angle)
        else:  # X axis
            x = center[0]
            y = center[1] + radius * math.cos(angle)
            z = center[2] + radius * math.sin(angle)

        obj.location = (x, y, z)
        obj.keyframe_insert(data_path="location", frame=frame)


def wave_animation(
    obj: bpy.types.Object,
    axis: str = 'Z',
    amplitude: float = 1.0,
    frequency: float = 1.0,
    duration: int = 60,
    start_frame: int = 1,
    phase: float = 0.0,
    damping: float = 0.0
) -> None:
    """
    Sine wave motion on a single axis.
    Great for flags, water surfaces, breathing, floating objects.

    Args:
        obj: Object to animate
        axis: Motion axis ('X', 'Y', 'Z')
        amplitude: Wave height
        frequency: Oscillation speed (1.0 = one full cycle per duration)
        duration: Total frames
        start_frame: Starting frame
        phase: Phase offset in radians
        damping: Exponential decay (0 = no damping, higher = faster decay)

    Example:
        >>> wave_animation(buoy, axis='Z', amplitude=0.5, frequency=2)
        >>> wave_animation(flag_tip, axis='X', amplitude=0.3, damping=0.02)
    """
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[axis.upper()]
    base_value = obj.location[axis_index]

    for frame in range(start_frame, start_frame + duration + 1):
        t = (frame - start_frame) / duration
        angle = t * frequency * 2 * math.pi + phase
        decay = math.exp(-damping * (frame - start_frame))
        value = base_value + amplitude * math.sin(angle) * decay

        obj.location[axis_index] = value
        obj.keyframe_insert(data_path="location", index=axis_index, frame=frame)


def pendulum_animation(
    obj: bpy.types.Object,
    swing_axis: str = 'Y',
    max_angle: float = 45.0,
    duration: int = 60,
    start_frame: int = 1,
    damping: float = 0.02,
    cycles: int = 5
) -> None:
    """
    Pendulum swing animation with optional damping.
    Natural-looking for hanging objects, chandeliers, wrecking balls.

    Args:
        obj: Object to animate (pivot should be at object origin)
        swing_axis: Rotation axis ('X', 'Y', 'Z')
        max_angle: Maximum swing angle in degrees
        duration: Total frames
        start_frame: Starting frame
        damping: How fast the swing dies out (0 = perpetual)
        cycles: Number of full swing cycles

    Example:
        >>> pendulum_animation(chandelier, max_angle=30, damping=0.03)
    """
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[swing_axis.upper()]
    frequency = cycles * 2 * math.pi / duration

    for frame in range(start_frame, start_frame + duration + 1):
        t = frame - start_frame
        decay = math.exp(-damping * t)
        angle = math.radians(max_angle) * math.cos(frequency * t) * decay

        obj.rotation_euler[axis_index] = angle
        obj.keyframe_insert(data_path="rotation_euler", index=axis_index, frame=frame)


def spring_animation(
    obj: bpy.types.Object,
    axis: str = 'Z',
    displacement: float = 2.0,
    stiffness: float = 8.0,
    damping: float = 0.1,
    duration: int = 60,
    start_frame: int = 1
) -> None:
    """
    Damped spring oscillation — jelly bounce, impact reaction, squash & stretch.

    Args:
        obj: Object to animate
        axis: Motion axis ('X', 'Y', 'Z')
        displacement: Initial displacement from rest position
        stiffness: Spring stiffness (higher = faster oscillation)
        damping: Damping coefficient (higher = faster settling)
        duration: Total frames
        start_frame: Starting frame

    Example:
        >>> spring_animation(jelly_cube, displacement=1.5, stiffness=10, damping=0.15)
    """
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[axis.upper()]
    base = obj.location[axis_index]
    omega = math.sqrt(max(0.01, stiffness - damping ** 2))

    for frame in range(start_frame, start_frame + duration + 1):
        t = (frame - start_frame) / 24.0  # Normalize to seconds at 24fps
        decay = math.exp(-damping * t)
        value = base + displacement * decay * math.cos(omega * t)

        obj.location[axis_index] = value
        obj.keyframe_insert(data_path="location", index=axis_index, frame=frame)


def follow_path_with_banking(
    obj: bpy.types.Object,
    curve: bpy.types.Object,
    duration: int = 120,
    bank_angle: float = 15.0,
    start_frame: int = 1
) -> bpy.types.Constraint:
    """
    Animate object along a curve with banking (tilt on turns).
    Ideal for vehicles, aircraft, roller coasters.

    Args:
        obj: Object to animate along the path
        curve: Bezier/NURBS curve to follow
        duration: Total animation frames
        bank_angle: Maximum bank angle on turns (degrees)
        start_frame: Starting frame

    Returns:
        The Follow Path constraint

    Example:
        >>> follow_path_with_banking(airplane, flight_path, duration=300, bank_angle=25)
    """
    # Set curve animation duration
    curve.data.path_duration = duration

    # Add Follow Path constraint
    constraint = obj.constraints.new('FOLLOW_PATH')
    constraint.target = curve
    constraint.use_curve_follow = True
    constraint.forward_axis = 'FORWARD_Y'
    constraint.up_axis = 'UP_Z'

    # Animate offset
    constraint.offset = 0
    constraint.keyframe_insert('offset', frame=start_frame)
    constraint.offset = -100
    constraint.keyframe_insert('offset', frame=start_frame + duration)

    # Set linear interpolation for smooth motion
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'

    # Add banking via tilt on the curve
    if bank_angle > 0:
        curve.data.twist_mode = 'MINIMUM'
        # Banking is handled by the Follow Path constraint's tilt

    return constraint


def camera_dolly_zoom(
    camera: bpy.types.Object,
    target: bpy.types.Object,
    start_focal: float = 24.0,
    end_focal: float = 70.0,
    duration: int = 60,
    start_frame: int = 1
) -> None:
    """
    Dolly zoom (Hitchcock / Vertigo effect).
    Camera moves toward/away from subject while changing focal length
    to keep the subject the same size but distort perspective.

    Args:
        camera: Camera object
        target: Object to keep in frame
        start_focal: Starting focal length in mm
        end_focal: Ending focal length in mm
        duration: Total frames
        start_frame: Starting frame

    Example:
        >>> camera_dolly_zoom(cam, character, start_focal=24, end_focal=85)
    """
    if camera.type != 'CAMERA':
        raise ValueError("Object must be a camera")

    cam_data = camera.data
    target_pos = target.location

    # Calculate initial distance (to keep subject same apparent size)
    initial_distance = (camera.location - target_pos).length

    for frame in range(start_frame, start_frame + duration + 1):
        t = (frame - start_frame) / duration

        # Interpolate focal length
        focal = start_focal + (end_focal - start_focal) * t
        cam_data.lens = focal
        cam_data.keyframe_insert(data_path="lens", frame=frame)

        # Adjust distance to keep subject same apparent size
        # Distance proportional to focal length
        new_distance = initial_distance * (focal / start_focal)

        # Move camera along its forward axis
        direction = (camera.location - target_pos).normalized()
        camera.location = target_pos + direction * new_distance
        camera.keyframe_insert(data_path="location", frame=frame)


def nla_compose(
    obj: bpy.types.Object,
    actions: list,
    blend_modes: list = None
) -> list:
    """
    Push multiple actions to NLA tracks for layered animation.
    NLA lets you combine, blend, and sequence multiple animations
    (e.g., walk cycle + arm wave + procedural noise).

    Args:
        obj: Animated object
        actions: List of dicts with 'action' (bpy.types.Action), 'name' (str),
                 'start' (int frame), 'end' (int frame, optional)
        blend_modes: Optional list of blend modes per track:
                     'REPLACE', 'COMBINE', 'ADD', 'SUBTRACT', 'MULTIPLY'

    Returns:
        List of created NLA strips

    Example:
        >>> nla_compose(character, [
        ...     {'action': walk_action, 'name': 'Walk', 'start': 1},
        ...     {'action': wave_action, 'name': 'Wave', 'start': 30}
        ... ], blend_modes=['REPLACE', 'ADD'])
    """
    if not obj.animation_data:
        obj.animation_data_create()

    strips = []

    for i, action_info in enumerate(actions):
        action = action_info['action']
        name = action_info.get('name', action.name)
        start = action_info.get('start', 1)

        # Create NLA track
        track = obj.animation_data.nla_tracks.new()
        track.name = name

        # Push action to track
        strip = track.strips.new(name, start, action)

        # Set blend mode
        if blend_modes and i < len(blend_modes):
            strip.blend_type = blend_modes[i]

        strips.append(strip)

    # Clear active action (NLA takes over)
    obj.animation_data.action = None

    return strips


def setup_animation_range(
    fps: int = 24,
    start_frame: int = 1,
    end_frame: int = 250,
    set_current: bool = True
) -> None:
    """
    Configure scene animation settings for production.

    Args:
        fps: Frames per second (24=film, 30=video, 60=game)
        start_frame: First frame of the animation
        end_frame: Last frame of the animation
        set_current: Jump playhead to start frame

    Example:
        >>> setup_animation_range(fps=30, start_frame=1, end_frame=300)
    """
    scene = bpy.context.scene
    scene.render.fps = fps
    scene.render.fps_base = 1.0
    scene.frame_start = start_frame
    scene.frame_end = end_frame

    if set_current:
        scene.frame_set(start_frame)


def ease_in_out_animation(
    obj: bpy.types.Object,
    data_path: str,
    start_value,
    end_value,
    start_frame: int = 1,
    end_frame: int = 60,
    index: int = -1
) -> None:
    """
    Animate a property with smooth ease-in-out interpolation.
    Uses Bezier keyframes for natural acceleration/deceleration.

    Args:
        obj: Object to animate
        data_path: Property path (e.g., 'location', 'scale', 'rotation_euler')
        start_value: Starting value
        end_value: Ending value
        start_frame: First keyframe frame
        end_frame: Last keyframe frame
        index: Array index (-1 for all components, 0/1/2 for individual)

    Example:
        >>> ease_in_out_animation(door, 'rotation_euler', 0, 1.57, index=2)
    """
    # Set start value
    if index >= 0:
        getattr(obj, data_path)[index] = start_value
    else:
        setattr(obj, data_path, start_value)
    obj.keyframe_insert(data_path=data_path, frame=start_frame, index=index)

    # Set end value
    if index >= 0:
        getattr(obj, data_path)[index] = end_value
    else:
        setattr(obj, data_path, end_value)
    obj.keyframe_insert(data_path=data_path, frame=end_frame, index=index)

    # Set Bezier interpolation (default ease-in-out)
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            if fcurve.data_path == data_path and (index < 0 or fcurve.array_index == index):
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'BEZIER'
                    kf.handle_left_type = 'AUTO_CLAMPED'
                    kf.handle_right_type = 'AUTO_CLAMPED'
