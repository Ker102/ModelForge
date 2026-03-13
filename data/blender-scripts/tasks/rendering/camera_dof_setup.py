"""
{
  "title": "Camera Depth of Field Setup",
  "category": "rendering",
  "subcategory": "camera",
  "tags": ["camera", "depth of field", "dof", "focal length", "aperture", "focus", "bokeh", "sensor", "lens"],
  "difficulty": "beginner",
  "description": "Configure camera depth of field, focal length, sensor size, and focus targets for cinematic shots via Python.",
  "blender_version": "5.0+",
  "estimated_objects": 1
}
"""
import bpy
import math


# Lens presets (focal length, sensor size, fstop)
LENS_PRESETS = {
    'wide': (24, 36, 5.6),
    'standard': (50, 36, 2.8),
    'portrait': (85, 36, 1.8),
    'telephoto': (135, 36, 2.0),
    'macro': (100, 36, 2.8),
    'cinematic': (35, 36, 1.4),
}


def create_camera(
    location: tuple = (0, -5, 2),
    rotation_euler: tuple = None,
    look_at: tuple = (0, 0, 0),
    focal_length: float = 50,
    sensor_width: float = 36,
    name: str = "Camera"
) -> bpy.types.Object:
    """
    Create a camera with configurable lens settings.

    Args:
        location: Camera world position
        rotation_euler: Camera rotation in radians (overrides look_at)
        look_at: Point to aim the camera at (if rotation_euler is None)
        focal_length: Lens focal length in mm
        sensor_width: Sensor width in mm
        name: Camera name

    Returns:
        The camera object

    Example:
        >>> cam = create_camera(location=(0, -8, 3), look_at=(0, 0, 1), focal_length=85)
    """
    bpy.ops.object.camera_add(location=location)
    cam_obj = bpy.context.active_object
    cam_obj.name = name
    cam = cam_obj.data
    cam.name = name

    cam.lens = focal_length
    cam.sensor_width = sensor_width

    if rotation_euler:
        cam_obj.rotation_euler = rotation_euler
    elif look_at:
        # Point camera at target
        direction = (
            look_at[0] - location[0],
            look_at[1] - location[1],
            look_at[2] - location[2],
        )
        # Calculate rotation from direction vector
        from mathutils import Vector
        dir_vec = Vector(direction).normalized()
        rot_quat = dir_vec.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()

    return cam_obj


def setup_depth_of_field(
    camera: bpy.types.Object = None,
    focus_object: bpy.types.Object = None,
    focus_distance: float = None,
    fstop: float = 2.8,
    blades: int = 0,
    rotation: float = 0
) -> None:
    """
    Enable and configure depth of field on a camera.

    Args:
        camera: Camera object (defaults to active camera)
        focus_object: Object to auto-focus on (overrides focus_distance)
        focus_distance: Manual focus distance in meters
        fstop: Aperture f-stop (lower = more blur, 0.5-32)
        blades: Aperture blade count (0=circular, 5-8=polygonal bokeh)
        rotation: Aperture blade rotation in radians

    Example:
        >>> setup_depth_of_field(cam, focus_object=hero_obj, fstop=1.8, blades=6)
        >>> setup_depth_of_field(cam, focus_distance=5.0, fstop=2.8)
    """
    if camera is None:
        camera = bpy.context.scene.camera

    if not camera or camera.type != 'CAMERA':
        raise ValueError("No valid camera provided")

    cam_data = camera.data
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = fstop
    cam_data.dof.aperture_blades = blades
    cam_data.dof.aperture_rotation = rotation

    if focus_object:
        cam_data.dof.focus_object = focus_object
    elif focus_distance is not None:
        cam_data.dof.focus_distance = focus_distance
    else:
        # Default: focus at 5 meters
        cam_data.dof.focus_distance = 5.0


def apply_lens_preset(
    camera: bpy.types.Object = None,
    preset: str = 'standard',
    enable_dof: bool = True
) -> dict:
    """
    Apply a lens preset to a camera.

    Args:
        camera: Camera object
        preset: 'wide', 'standard', 'portrait', 'telephoto', 'macro', 'cinematic'
        enable_dof: Also enable DOF with preset f-stop

    Returns:
        Dict of applied settings

    Example:
        >>> apply_lens_preset(cam, 'portrait', enable_dof=True)
    """
    if camera is None:
        camera = bpy.context.scene.camera

    focal, sensor, fstop = LENS_PRESETS.get(preset, LENS_PRESETS['standard'])

    camera.data.lens = focal
    camera.data.sensor_width = sensor

    if enable_dof:
        setup_depth_of_field(camera, fstop=fstop)

    return {
        'preset': preset,
        'focal_length': focal,
        'sensor_width': sensor,
        'fstop': fstop,
    }


def create_focus_empty(
    location: tuple = (0, 0, 0),
    name: str = "FocusTarget"
) -> bpy.types.Object:
    """
    Create an empty object to use as a DOF focus target.
    The empty can be animated to rack focus between subjects.

    Args:
        location: Position to focus on
        name: Object name

    Returns:
        The focus target empty

    Example:
        >>> target = create_focus_empty(location=(2, 0, 1))
        >>> setup_depth_of_field(cam, focus_object=target, fstop=1.4)
    """
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    empty.empty_display_size = 0.5

    return empty


def animate_rack_focus(
    camera: bpy.types.Object,
    distances: list,
    frame_start: int = 1,
    frames_per_hold: int = 48,
    transition_frames: int = 24
) -> None:
    """
    Animate a rack focus (shifting focal distance over time).

    Args:
        camera: Camera object
        distances: List of focus distances in meters
        frame_start: Starting frame
        frames_per_hold: Frames to hold each distance
        transition_frames: Frames for smooth transition

    Example:
        >>> animate_rack_focus(cam, distances=[2.0, 8.0, 2.0])
    """
    cam_data = camera.data
    cam_data.dof.use_dof = True

    frame = frame_start
    for i, dist in enumerate(distances):
        # Hold at this distance
        cam_data.dof.focus_distance = dist
        cam_data.dof.keyframe_insert(data_path="focus_distance", frame=frame)

        if i < len(distances) - 1:
            # End of hold
            frame += frames_per_hold
            cam_data.dof.keyframe_insert(data_path="focus_distance", frame=frame)

            # Next distance at end of transition
            frame += transition_frames
        else:
            frame += frames_per_hold


# Standalone execution
if __name__ == "__main__":
    cam = create_camera(location=(0, -8, 3), look_at=(0, 0, 1), focal_length=85)
    bpy.context.scene.camera = cam
    setup_depth_of_field(cam, focus_distance=8.0, fstop=1.8, blades=6)
    print(f"Camera '{cam.name}': 85mm, f/1.8, DOF @ 8m, 6-blade bokeh")
