"""
{
  "title": "Muzzle Flash Effect",
  "category": "effects",
  "subcategory": "visual",
  "tags": ["muzzle", "flash", "gunfire", "effects", "particles", "light"],
  "difficulty": "intermediate",
  "description": "Creates a muzzle flash effect for weapons with light and geometry.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math
import random


def create_muzzle_flash(
    location: tuple = (0, 0, 0),
    direction: tuple = (0, -1, 0),
    size: float = 0.3,
    color: tuple = (1.0, 0.7, 0.2),
    intensity: float = 500,
    frame: int = 1,
    duration: int = 3,
    name: str = "MuzzleFlash"
) -> dict:
    """
    Create a muzzle flash effect.
    
    Args:
        location: Flash position
        direction: Direction of fire (normalized)
        size: Flash size
        color: RGB flash color
        intensity: Light intensity
        frame: Start frame
        duration: Flash duration in frames
        name: Object name
    
    Returns:
        Dictionary with flash components
    """
    result = {}
    
    # === FLASH MESH ===
    # Create cone for flash shape
    bpy.ops.mesh.primitive_cone_add(
        radius1=size * 0.3,
        radius2=0,
        depth=size,
        location=location
    )
    flash = bpy.context.active_object
    flash.name = f"{name}_Cone"
    
    # Orient to direction
    from mathutils import Vector
    dir_vec = Vector(direction).normalized()
    flash.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    
    # Move tip to location
    flash.location = (
        location[0] + dir_vec.x * size * 0.5,
        location[1] + dir_vec.y * size * 0.5,
        location[2] + dir_vec.z * size * 0.5
    )
    
    # Emission material
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = intensity * 0.1
    flash.data.materials.append(mat)
    
    result['flash'] = flash
    
    # === POINT LIGHT ===
    bpy.ops.object.light_add(type='POINT', location=location)
    light = bpy.context.active_object
    light.name = f"{name}_Light"
    light.data.energy = intensity
    light.data.color = color
    light.data.shadow_soft_size = size * 0.5
    
    result['light'] = light
    
    # === SPARKS (small spheres) ===
    sparks = []
    for i in range(5):
        angle = random.uniform(0, 2 * math.pi)
        spread = random.uniform(0, size * 0.3)
        
        spark_pos = (
            location[0] + math.cos(angle) * spread,
            location[1] + math.sin(angle) * spread,
            location[2] + random.uniform(-size * 0.1, size * 0.1)
        )
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=size * 0.02,
            location=spark_pos
        )
        spark = bpy.context.active_object
        spark.name = f"{name}_Spark_{i}"
        spark.data.materials.append(mat)
        sparks.append(spark)
    
    result['sparks'] = sparks
    
    # === ANIMATION ===
    # Keyframe visibility
    all_objects = [flash, light] + sparks
    
    for obj in all_objects:
        # Hidden before frame
        obj.hide_viewport = True
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_viewport", frame=frame - 1)
        obj.keyframe_insert(data_path="hide_render", frame=frame - 1)
        
        # Visible at frame
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_viewport", frame=frame)
        obj.keyframe_insert(data_path="hide_render", frame=frame)
        
        # Hidden after duration
        obj.hide_viewport = True
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_viewport", frame=frame + duration)
        obj.keyframe_insert(data_path="hide_render", frame=frame + duration)
    
    # Light intensity animation
    light.data.energy = intensity
    light.data.keyframe_insert(data_path="energy", frame=frame)
    light.data.energy = 0
    light.data.keyframe_insert(data_path="energy", frame=frame + duration)
    
    return result


def create_muzzle_flash_sequence(
    location: tuple,
    direction: tuple,
    count: int = 3,
    interval: int = 5,
    start_frame: int = 1
) -> list:
    """Create multiple muzzle flashes in sequence."""
    flashes = []
    
    for i in range(count):
        frame = start_frame + i * interval
        flash = create_muzzle_flash(
            location=location,
            direction=direction,
            frame=frame,
            name=f"MuzzleFlash_{i+1}"
        )
        flashes.append(flash)
    
    return flashes


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Single flash
    create_muzzle_flash(location=(0, 0, 1), direction=(0, -1, 0))
    
    # Sequence
    create_muzzle_flash_sequence((2, 0, 1), (0, -1, 0), count=5, interval=8)
    
    print("Created muzzle flash effects")
