"""
{
  "title": "Camera Utilities",
  "category": "camera",
  "tags": ["camera", "render", "viewport", "tracking", "dof", "focus"],
  "description": "Functions for creating, positioning, and configuring cameras in Blender.",
  "blender_version": "3.0+"
}
"""
import bpy
import math
from mathutils import Vector


def add_camera(
    location: tuple = (7, -7, 5),
    rotation: tuple = (63, 0, 45),
    lens: float = 50,
    name: str = "Camera"
) -> bpy.types.Object:
    """
    Add a camera to the scene.
    
    Args:
        location: XYZ position tuple
        rotation: XYZ rotation in degrees
        lens: Focal length in mm
        name: Camera name
    
    Returns:
        The created camera object
    
    Example:
        >>> cam = add_camera((10, -10, 8), (60, 0, 45), lens=85)
    """
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    cam.name = name
    cam.rotation_euler = tuple(math.radians(r) for r in rotation)
    cam.data.lens = lens
    return cam


def set_active_camera(camera: bpy.types.Object) -> None:
    """
    Set a camera as the active render camera.
    
    Args:
        camera: Camera object to make active
    
    Example:
        >>> set_active_camera(bpy.data.objects['Camera.001'])
    """
    bpy.context.scene.camera = camera


def point_camera_at(camera: bpy.types.Object, target: tuple) -> None:
    """
    Point a camera to look at a specific location.
    
    Args:
        camera: Camera object
        target: XYZ location to look at
    
    Example:
        >>> point_camera_at(cam, (0, 0, 1))
    """
    direction = Vector(target) - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()


def add_camera_track_to(
    camera: bpy.types.Object,
    target: bpy.types.Object,
    track_axis: str = 'TRACK_NEGATIVE_Z',
    up_axis: str = 'UP_Y'
) -> bpy.types.Constraint:
    """
    Add a Track To constraint so camera always looks at target.
    
    Args:
        camera: Camera object
        target: Object to track
        track_axis: Axis pointing at target
        up_axis: Axis pointing up
    
    Returns:
        The created constraint
    
    Example:
        >>> constraint = add_camera_track_to(cam, bpy.data.objects['Cube'])
    """
    constraint = camera.constraints.new('TRACK_TO')
    constraint.target = target
    constraint.track_axis = track_axis
    constraint.up_axis = up_axis
    return constraint


def setup_depth_of_field(
    camera: bpy.types.Object,
    focus_object: bpy.types.Object = None,
    focus_distance: float = None,
    fstop: float = 2.8,
    blades: int = 0
) -> None:
    """
    Configure depth of field settings for cinematic blur.
    
    Args:
        camera: Camera object
        focus_object: Object to focus on (overrides distance)
        focus_distance: Manual focus distance in meters
        fstop: Aperture f-stop (lower = more blur)
        blades: Aperture blade count (0 = circular)
    
    Example:
        >>> setup_depth_of_field(cam, focus_object=subject, fstop=1.4)
    """
    camera.data.dof.use_dof = True
    camera.data.dof.aperture_fstop = fstop
    camera.data.dof.aperture_blades = blades
    
    if focus_object:
        camera.data.dof.focus_object = focus_object
    elif focus_distance:
        camera.data.dof.focus_distance = focus_distance


def setup_render_resolution(
    width: int = 1920,
    height: int = 1080,
    percentage: int = 100
) -> None:
    """
    Set render resolution.
    
    Args:
        width: Horizontal resolution in pixels
        height: Vertical resolution in pixels
        percentage: Scale factor (50 = half resolution)
    
    Example:
        >>> setup_render_resolution(3840, 2160, 100)  # 4K
    """
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = percentage


def create_camera_orbit_path(
    center: tuple = (0, 0, 0),
    radius: float = 10,
    height: float = 5,
    name: str = "CameraPath"
) -> tuple:
    """
    Create a circular path for camera animation.
    
    Args:
        center: Center point of orbit
        radius: Distance from center
        height: Height above center
        name: Path object name
    
    Returns:
        Tuple of (path_object, camera_object)
    
    Example:
        >>> path, cam = create_camera_orbit_path(radius=8, height=4)
    """
    # Create circle path
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, location=(center[0], center[1], center[2] + height))
    path = bpy.context.active_object
    path.name = name
    
    # Create camera
    cam_location = (center[0] + radius, center[1], center[2] + height)
    bpy.ops.object.camera_add(location=cam_location)
    cam = bpy.context.active_object
    cam.name = f"{name}_Camera"
    
    # Add follow path constraint
    constraint = cam.constraints.new('FOLLOW_PATH')
    constraint.target = path
    constraint.use_curve_follow = True
    
    # Point camera at center
    point_camera_at(cam, center)
    
    return path, cam
