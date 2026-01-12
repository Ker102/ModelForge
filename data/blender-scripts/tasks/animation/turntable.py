"""
{
  "title": "Product Turntable Animation",
  "category": "animation",
  "subcategory": "product",
  "tags": ["turntable", "rotation", "product", "showcase", "360", "spin"],
  "difficulty": "beginner",
  "description": "Creates a smooth 360-degree turntable animation for product visualization.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math


def create_turntable_animation(
    target_object: bpy.types.Object = None,
    duration: int = 120,
    start_frame: int = 1,
    axis: str = 'Z',
    rotations: int = 1,
    ease_in_out: bool = False,
    name: str = None
) -> bpy.types.Object:
    """
    Create a smooth turntable rotation animation for an object.
    
    Args:
        target_object: Object to animate (uses active if None)
        duration: Animation length in frames
        start_frame: Starting frame number
        axis: Rotation axis ('X', 'Y', or 'Z')
        rotations: Number of full 360° rotations
        ease_in_out: Add easing at start/end
        name: Object to find by name (alternative to target_object)
    
    Returns:
        The animated object
    
    Example:
        >>> create_turntable_animation(bpy.data.objects['Product'], duration=90)
    """
    if target_object is None:
        if name:
            target_object = bpy.data.objects.get(name)
        else:
            target_object = bpy.context.active_object
    
    if target_object is None:
        raise ValueError("No target object specified")
    
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[axis.upper()]
    end_frame = start_frame + duration
    
    # Set frame range
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame
    
    # Store initial rotation
    initial_rotation = target_object.rotation_euler[axis_index]
    
    # Keyframe start
    bpy.context.scene.frame_set(start_frame)
    target_object.rotation_euler[axis_index] = initial_rotation
    target_object.keyframe_insert(data_path='rotation_euler', index=axis_index, frame=start_frame)
    
    # Keyframe end
    target_object.rotation_euler[axis_index] = initial_rotation + (math.pi * 2 * rotations)
    target_object.keyframe_insert(data_path='rotation_euler', index=axis_index, frame=end_frame)
    
    # Set interpolation
    if target_object.animation_data and target_object.animation_data.action:
        for fcurve in target_object.animation_data.action.fcurves:
            if fcurve.data_path == 'rotation_euler' and fcurve.array_index == axis_index:
                for keyframe in fcurve.keyframe_points:
                    if ease_in_out:
                        keyframe.interpolation = 'BEZIER'
                        keyframe.easing = 'EASE_IN_OUT'
                    else:
                        keyframe.interpolation = 'LINEAR'
    
    # Reset to start
    bpy.context.scene.frame_set(start_frame)
    
    return target_object


def create_turntable_with_camera(
    target_object: bpy.types.Object = None,
    camera_distance: float = 5.0,
    camera_height: float = 2.0,
    duration: int = 120,
    orbit_camera: bool = True
) -> dict:
    """
    Create a turntable setup with orbiting camera.
    
    Args:
        target_object: Object to showcase
        camera_distance: Distance from object center
        camera_height: Camera height above object
        duration: Animation duration in frames
        orbit_camera: If True, camera orbits; if False, object rotates
    
    Returns:
        Dictionary with camera and animation info
    
    Example:
        >>> setup = create_turntable_with_camera(product, camera_distance=8)
    """
    result = {}
    
    if target_object is None:
        target_object = bpy.context.active_object
    
    obj_location = target_object.location
    
    # Create camera
    cam_x = obj_location.x + camera_distance
    cam_y = obj_location.y
    cam_z = obj_location.z + camera_height
    
    bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
    camera = bpy.context.active_object
    camera.name = "TurntableCamera"
    
    # Point camera at object
    from mathutils import Vector
    direction = Vector(obj_location) - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    # Set as active camera
    bpy.context.scene.camera = camera
    result['camera'] = camera
    
    if orbit_camera:
        # Create empty at object center for camera to orbit around
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_location)
        pivot = bpy.context.active_object
        pivot.name = "TurntablePivot"
        
        # Parent camera to pivot
        camera.parent = pivot
        
        # Animate pivot rotation
        create_turntable_animation(
            target_object=pivot,
            duration=duration,
            axis='Z'
        )
        result['pivot'] = pivot
    else:
        # Animate object directly
        create_turntable_animation(
            target_object=target_object,
            duration=duration,
            axis='Z'
        )
    
    result['target'] = target_object
    result['duration'] = duration
    
    return result


def setup_turntable_render(
    output_path: str = "//turntable_",
    format: str = 'PNG',
    resolution: tuple = (1920, 1080)
) -> None:
    """
    Configure render settings for turntable animation.
    
    Args:
        output_path: Output file path (// = relative to .blend)
        format: 'PNG', 'JPEG', 'FFMPEG' (video)
        resolution: (width, height) in pixels
    
    Example:
        >>> setup_turntable_render("//renders/product_", 'PNG', (4096, 4096))
    """
    scene = bpy.context.scene
    
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = format
    
    if format == 'FFMPEG':
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    
    # Enable transparency for PNG
    if format == 'PNG':
        scene.render.film_transparent = True
        scene.render.image_settings.color_mode = 'RGBA'


# Standalone execution
if __name__ == "__main__":
    # Get selected object
    obj = bpy.context.active_object
    if obj:
        setup = create_turntable_with_camera(
            target_object=obj,
            camera_distance=6,
            duration=90
        )
        setup_turntable_render("//turntable_", 'PNG')
        print("Turntable animation created! Render with Ctrl+F12")
