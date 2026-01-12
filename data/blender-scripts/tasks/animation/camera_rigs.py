"""
{
  "title": "Camera Rig Presets",
  "category": "animation",
  "subcategory": "camera",
  "tags": ["camera", "rig", "animation", "cinematography", "presets"],
  "difficulty": "intermediate",
  "description": "Pre-configured camera rigs for common cinematography setups.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math


def create_orbit_rig(
    target_location: tuple = (0, 0, 0),
    radius: float = 5.0,
    height: float = 2.0,
    name: str = "OrbitRig"
) -> dict:
    """
    Create an orbital camera rig.
    
    Args:
        target_location: Point to orbit around
        radius: Orbit radius
        height: Camera height above target
        name: Rig name
    
    Returns:
        Dictionary with rig components
    """
    result = {}
    
    # Pivot empty
    bpy.ops.object.empty_add(
        type='PLAIN_AXES',
        location=target_location
    )
    pivot = bpy.context.active_object
    pivot.name = f"{name}_Pivot"
    result['pivot'] = pivot
    
    # Camera
    bpy.ops.object.camera_add(location=(
        target_location[0] + radius,
        target_location[1],
        target_location[2] + height
    ))
    camera = bpy.context.active_object
    camera.name = f"{name}_Camera"
    camera.parent = pivot
    
    # Track to target
    constraint = camera.constraints.new('TRACK_TO')
    constraint.target = pivot
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    
    result['camera'] = camera
    
    return result


def create_dolly_rig(
    start: tuple = (-5, 0, 1.6),
    end: tuple = (5, 0, 1.6),
    target: tuple = (0, 0, 1),
    name: str = "DollyRig"
) -> dict:
    """
    Create a dolly track rig.
    
    Args:
        start: Track start position
        end: Track end position
        target: Look-at target
        name: Rig name
    
    Returns:
        Dictionary with rig components
    """
    result = {}
    
    # Create path
    curve_data = bpy.data.curves.new(f"{name}_Track", 'CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('NURBS')
    spline.points.add(1)
    spline.points[0].co = (*start, 1)
    spline.points[1].co = (*end, 1)
    
    track = bpy.data.objects.new(f"{name}_Track", curve_data)
    bpy.context.collection.objects.link(track)
    result['track'] = track
    
    # Target empty
    bpy.ops.object.empty_add(type='SPHERE', location=target)
    target_obj = bpy.context.active_object
    target_obj.name = f"{name}_Target"
    result['target'] = target_obj
    
    # Camera
    bpy.ops.object.camera_add(location=start)
    camera = bpy.context.active_object
    camera.name = f"{name}_Camera"
    
    # Follow path
    follow = camera.constraints.new('FOLLOW_PATH')
    follow.target = track
    follow.use_curve_follow = False
    
    # Track to target
    track_to = camera.constraints.new('TRACK_TO')
    track_to.target = target_obj
    track_to.track_axis = 'TRACK_NEGATIVE_Z'
    track_to.up_axis = 'UP_Y'
    
    result['camera'] = camera
    
    return result


def create_crane_rig(
    base_location: tuple = (0, -5, 0),
    arm_length: float = 5.0,
    height: float = 3.0,
    name: str = "CraneRig"
) -> dict:
    """
    Create a crane/jib camera rig.
    
    Args:
        base_location: Crane base position
        arm_length: Arm length
        height: Arm pivot height
        name: Rig name
    
    Returns:
        Dictionary with rig components
    """
    result = {}
    
    # Base (rotation)
    bpy.ops.object.empty_add(type='CIRCLE', location=base_location)
    base = bpy.context.active_object
    base.name = f"{name}_Base"
    result['base'] = base
    
    # Arm pivot
    bpy.ops.object.empty_add(
        type='ARROWS',
        location=(base_location[0], base_location[1], base_location[2] + height)
    )
    arm = bpy.context.active_object
    arm.name = f"{name}_Arm"
    arm.parent = base
    result['arm'] = arm
    
    # Camera at end of arm
    bpy.ops.object.camera_add(location=(
        base_location[0],
        base_location[1] + arm_length,
        base_location[2] + height
    ))
    camera = bpy.context.active_object
    camera.name = f"{name}_Camera"
    camera.parent = arm
    
    result['camera'] = camera
    
    return result


def create_handheld_rig(
    location: tuple = (0, -3, 1.6),
    shake_intensity: float = 0.3,
    name: str = "HandheldRig"
) -> dict:
    """
    Create handheld camera rig with noise.
    
    Args:
        location: Camera position
        shake_intensity: Shake amount
        name: Rig name
    
    Returns:
        Dictionary with rig components
    """
    result = {}
    
    # Stabilizer empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    stabilizer = bpy.context.active_object
    stabilizer.name = f"{name}_Stabilizer"
    result['stabilizer'] = stabilizer
    
    # Camera
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.active_object
    camera.name = f"{name}_Camera"
    camera.parent = stabilizer
    
    # Add noise drivers for shake
    for i, axis in enumerate(['x', 'y', 'z']):
        strength = shake_intensity * (0.5 if axis == 'z' else 1.0)
        fcurve = camera.driver_add('rotation_euler', i)
        driver = fcurve.driver
        driver.expression = f"noise.random() * {strength} * 0.02"
    
    result['camera'] = camera
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_orbit_rig()
    create_dolly_rig(start=(-5, 5, 1.6), end=(5, 5, 1.6))
    
    print("Created camera rigs")
