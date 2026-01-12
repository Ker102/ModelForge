"""
{
  "title": "Camera Shake Effect",
  "category": "animation",
  "subcategory": "camera",
  "tags": ["camera", "shake", "handheld", "animation", "effects"],
  "difficulty": "intermediate",
  "description": "Adds realistic camera shake and handheld motion effects.",
  "blender_version": "3.0+",
  "estimated_objects": 0
}
"""
import bpy
import random
import math


def add_camera_shake(
    camera: bpy.types.Object,
    intensity: float = 0.5,
    frequency: float = 2.0,
    frame_start: int = 1,
    frame_end: int = 250,
    shake_type: str = 'HANDHELD',
    seed: int = 42
) -> dict:
    """
    Add camera shake animation.
    
    Args:
        camera: Camera object
        intensity: Shake strength (0-1)
        frequency: Shake speed
        frame_start: Start frame
        frame_end: End frame
        shake_type: 'HANDHELD', 'EARTHQUAKE', 'SUBTLE'
        seed: Random seed
    
    Returns:
        Dictionary with animation data
    """
    random.seed(seed)
    
    # Intensity presets
    presets = {
        'SUBTLE': {'pos': 0.002, 'rot': 0.2},
        'HANDHELD': {'pos': 0.01, 'rot': 0.5},
        'EARTHQUAKE': {'pos': 0.05, 'rot': 1.5}
    }
    
    preset = presets.get(shake_type, presets['HANDHELD'])
    pos_strength = preset['pos'] * intensity
    rot_strength = preset['rot'] * intensity
    
    # Store original location
    orig_loc = camera.location.copy()
    orig_rot = camera.rotation_euler.copy()
    
    # Generate keyframes
    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)
        
        t = frame * frequency * 0.1
        
        # Position noise (Perlin-like)
        camera.location.x = orig_loc.x + _noise(t, seed) * pos_strength
        camera.location.y = orig_loc.y + _noise(t + 100, seed) * pos_strength
        camera.location.z = orig_loc.z + _noise(t + 200, seed) * pos_strength * 0.5
        
        # Rotation noise (smaller)
        camera.rotation_euler.x = orig_rot.x + math.radians(_noise(t + 300, seed) * rot_strength)
        camera.rotation_euler.y = orig_rot.y + math.radians(_noise(t + 400, seed) * rot_strength * 0.5)
        camera.rotation_euler.z = orig_rot.z + math.radians(_noise(t + 500, seed) * rot_strength * 0.3)
        
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # Smooth keyframes
    if camera.animation_data and camera.animation_data.action:
        for fcurve in camera.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
    
    return {
        'camera': camera.name,
        'frames': (frame_start, frame_end),
        'shake_type': shake_type
    }


def _noise(t: float, seed: int) -> float:
    """Simple noise function."""
    random.seed(int(t * 10) + seed)
    base = random.uniform(-1, 1)
    
    random.seed(int(t * 10) + 1 + seed)
    next_val = random.uniform(-1, 1)
    
    frac = (t * 10) % 1
    return base + (next_val - base) * frac


def add_camera_drift(
    camera: bpy.types.Object,
    amount: float = 0.1,
    speed: float = 0.5,
    frame_start: int = 1,
    frame_end: int = 250
) -> None:
    """Add subtle slow camera drift."""
    orig_loc = camera.location.copy()
    
    for frame in range(frame_start, frame_end + 1, 10):
        bpy.context.scene.frame_set(frame)
        
        t = frame / (frame_end - frame_start)
        
        camera.location.x = orig_loc.x + math.sin(t * math.pi * speed) * amount
        camera.location.y = orig_loc.y + math.cos(t * math.pi * speed * 0.7) * amount * 0.5
        
        camera.keyframe_insert(data_path="location", frame=frame)


def add_zoom_pulse(
    camera: bpy.types.Object,
    zoom_amount: float = 0.1,
    duration: int = 10,
    frame: int = 1
) -> None:
    """Add a quick zoom pulse effect."""
    orig_lens = camera.data.lens
    
    camera.data.keyframe_insert(data_path="lens", frame=frame)
    
    camera.data.lens = orig_lens * (1 - zoom_amount)
    camera.data.keyframe_insert(data_path="lens", frame=frame + duration // 2)
    
    camera.data.lens = orig_lens
    camera.data.keyframe_insert(data_path="lens", frame=frame + duration)
    
    # Make smooth
    if camera.data.animation_data and camera.data.animation_data.action:
        for fcurve in camera.data.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'


if __name__ == "__main__":
    camera = bpy.context.scene.camera
    if camera:
        add_camera_shake(camera, intensity=0.3, shake_type='HANDHELD')
        print("Added camera shake")
    else:
        print("No camera in scene")
