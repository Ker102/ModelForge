"""
{
  "title": "Campfire Generator",
  "category": "environment",
  "subcategory": "props",
  "tags": ["campfire", "fire", "outdoor", "environment", "light"],
  "difficulty": "intermediate",
  "description": "Generates campfires with logs, fire, and ambient lighting.",
  "blender_version": "3.0+",
  "estimated_objects": 8
}
"""
import bpy
import math
import random


def create_campfire(
    size: float = 0.5,
    lit: bool = True,
    with_stones: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Campfire"
) -> dict:
    """
    Create a campfire.
    
    Args:
        size: Campfire size
        lit: Add fire effect
        with_stones: Add surrounding stones
        location: Position
        name: Object name
    
    Returns:
        Dictionary with campfire parts
    """
    result = {}
    
    # === LOGS ===
    logs = _create_logs(size, location, name)
    result['logs'] = logs
    
    # === STONES ===
    if with_stones:
        stones = _create_fire_stones(size, location, name)
        result['stones'] = stones
    
    # === FIRE ===
    if lit:
        fire = _create_fire_effect(size, location, name)
        result.update(fire)
    
    return result


def _create_logs(
    size: float,
    location: tuple,
    name: str
) -> list:
    """Create log arrangement."""
    logs = []
    log_mat = bpy.data.materials.new(f"{name}_LogMat")
    log_mat.use_nodes = True
    bsdf = log_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.2, 0.12, 0.06, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    
    # Create 3-4 logs
    for i in range(4):
        angle = (i / 4) * 2 * math.pi + random.uniform(-0.3, 0.3)
        log_length = size * random.uniform(0.6, 0.9)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=size * 0.08,
            depth=log_length,
            location=(
                location[0] + math.cos(angle) * size * 0.2,
                location[1] + math.sin(angle) * size * 0.2,
                location[2] + size * 0.1
            )
        )
        log = bpy.context.active_object
        log.name = f"{name}_Log_{i}"
        log.rotation_euler = (
            random.uniform(-0.3, 0.3),
            math.radians(90) + random.uniform(-0.2, 0.2),
            angle + math.radians(90)
        )
        log.data.materials.append(log_mat)
        logs.append(log)
    
    return logs


def _create_fire_stones(
    size: float,
    location: tuple,
    name: str
) -> list:
    """Create surrounding stones."""
    stones = []
    stone_mat = bpy.data.materials.new(f"{name}_StoneMat")
    stone_mat.use_nodes = True
    bsdf = stone_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.35, 0.32, 0.3, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    
    stone_count = 8
    for i in range(stone_count):
        angle = (i / stone_count) * 2 * math.pi
        stone_size = size * random.uniform(0.08, 0.15)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=stone_size,
            subdivisions=1,
            location=(
                location[0] + math.cos(angle) * size * 0.6,
                location[1] + math.sin(angle) * size * 0.6,
                location[2] + stone_size * 0.5
            )
        )
        stone = bpy.context.active_object
        stone.name = f"{name}_Stone_{i}"
        stone.scale.z = random.uniform(0.5, 0.8)
        bpy.ops.object.transform_apply(scale=True)
        
        # Deform
        for v in stone.data.vertices:
            v.co += (random.uniform(-0.02, 0.02),
                     random.uniform(-0.02, 0.02),
                     random.uniform(-0.02, 0.02))
        
        stone.data.materials.append(stone_mat)
        stones.append(stone)
    
    return stones


def _create_fire_effect(
    size: float,
    location: tuple,
    name: str
) -> dict:
    """Create fire and light."""
    result = {}
    
    # Fire cone
    bpy.ops.mesh.primitive_cone_add(
        radius1=size * 0.25,
        radius2=0,
        depth=size * 0.8,
        location=(location[0], location[1], location[2] + size * 0.5)
    )
    fire = bpy.context.active_object
    fire.name = f"{name}_Fire"
    bpy.ops.object.shade_smooth()
    
    # Deform for natural shape
    for v in fire.data.vertices:
        v.co.x += random.uniform(-0.02, 0.02)
        v.co.y += random.uniform(-0.02, 0.02)
    
    fire_mat = bpy.data.materials.new(f"{name}_FireMat")
    fire_mat.use_nodes = True
    fire_mat.blend_method = 'BLEND'
    bsdf = fire_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (1.0, 0.4, 0.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.3, 0.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 25.0
    bsdf.inputs['Alpha'].default_value = 0.8
    fire.data.materials.append(fire_mat)
    result['fire'] = fire
    
    # Point light
    bpy.ops.object.light_add(
        type='POINT',
        location=(location[0], location[1], location[2] + size * 0.4)
    )
    light = bpy.context.active_object
    light.name = f"{name}_Light"
    light.data.energy = 200
    light.data.color = (1.0, 0.6, 0.2)
    light.data.shadow_soft_size = size
    result['light'] = light
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_campfire(lit=True, location=(0, 0, 0))
    
    print("Created campfire")
