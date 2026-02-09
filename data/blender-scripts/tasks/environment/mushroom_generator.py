"""
{
  "title": "Mushroom Generator",
  "category": "environment",
  "subcategory": "vegetation",
  "tags": ["mushroom", "flora", "nature", "forest", "fantasy", "props"],
  "difficulty": "beginner",
  "description": "Generates mushrooms and fungi for environment props.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math
import random


def create_mushroom(
    cap_radius: float = 0.05,
    stem_height: float = 0.08,
    style: str = 'TOADSTOOL',
    cap_color: tuple = (0.8, 0.2, 0.1),
    location: tuple = (0, 0, 0),
    name: str = "Mushroom"
) -> dict:
    """
    Create a mushroom.
    
    Args:
        cap_radius: Cap radius
        stem_height: Stem height
        style: 'TOADSTOOL', 'FLAT', 'FANTASY'
        cap_color: RGB cap color
        location: Position
        name: Object name
    
    Returns:
        Dictionary with mushroom parts
    """
    result = {}
    
    # === STEM ===
    bpy.ops.mesh.primitive_cylinder_add(
        radius=cap_radius * 0.25,
        depth=stem_height,
        location=(location[0], location[1], location[2] + stem_height/2)
    )
    stem = bpy.context.active_object
    stem.name = f"{name}_Stem"
    
    # Slightly wider at base
    for v in stem.data.vertices:
        if v.co.z < 0:
            v.co.x *= 1.3
            v.co.y *= 1.3
    
    stem_mat = bpy.data.materials.new(f"{name}_StemMat")
    bsdf = stem_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.9, 0.88, 0.8, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    stem.data.materials.append(stem_mat)
    
    bpy.ops.object.shade_smooth()
    result['stem'] = stem
    
    # === CAP ===
    if style == 'TOADSTOOL':
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=cap_radius,
            location=(location[0], location[1], location[2] + stem_height)
        )
        cap = bpy.context.active_object
        cap.scale.z = 0.5
        
    elif style == 'FLAT':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=cap_radius,
            depth=cap_radius * 0.3,
            location=(location[0], location[1], location[2] + stem_height)
        )
        cap = bpy.context.active_object
        
    else:  # FANTASY
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=cap_radius,
            location=(location[0], location[1], location[2] + stem_height)
        )
        cap = bpy.context.active_object
        cap.scale.z = 0.8
    
    bpy.ops.object.transform_apply(scale=True)
    cap.name = f"{name}_Cap"
    
    cap_mat = bpy.data.materials.new(f"{name}_CapMat")
    bsdf = cap_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*cap_color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    
    if style == 'FANTASY':
        bsdf.inputs['Emission Color'].default_value = (*cap_color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 1.0
    
    cap.data.materials.append(cap_mat)
    bpy.ops.object.shade_smooth()
    result['cap'] = cap
    
    # Spots for toadstool
    if style == 'TOADSTOOL':
        spots = _create_mushroom_spots(cap_radius, stem_height, location, name)
        result['spots'] = spots
    
    return result


def _create_mushroom_spots(
    cap_radius: float,
    stem_height: float,
    location: tuple,
    name: str
) -> list:
    """Create white spots on toadstool cap."""
    spots = []
    spot_mat = bpy.data.materials.new(f"{name}_SpotMat")
    bsdf = spot_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.9, 1.0)
    
    for i in range(5):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0.3, 0.7) * cap_radius
        
        spot_pos = (
            location[0] + math.cos(angle) * dist,
            location[1] + math.sin(angle) * dist,
            location[2] + stem_height + cap_radius * 0.3
        )
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=cap_radius * 0.1,
            location=spot_pos
        )
        spot = bpy.context.active_object
        spot.name = f"{name}_Spot_{i}"
        spot.scale.z = 0.3
        spot.data.materials.append(spot_mat)
        spots.append(spot)
    
    return spots


def create_mushroom_cluster(
    count: int = 5,
    spread: float = 0.15,
    location: tuple = (0, 0, 0),
    seed: int = 42,
    name: str = "MushroomCluster"
) -> list:
    """Create a cluster of mushrooms."""
    random.seed(seed)
    mushrooms = []
    
    styles = ['TOADSTOOL', 'FLAT', 'FANTASY']
    colors = [
        (0.8, 0.2, 0.1),
        (0.6, 0.5, 0.3),
        (0.4, 0.3, 0.6)
    ]
    
    for i in range(count):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, spread)
        
        pos = (
            location[0] + math.cos(angle) * dist,
            location[1] + math.sin(angle) * dist,
            location[2]
        )
        
        size = random.uniform(0.03, 0.08)
        
        mushroom = create_mushroom(
            cap_radius=size,
            stem_height=size * random.uniform(1.0, 1.5),
            style=random.choice(styles),
            cap_color=random.choice(colors),
            location=pos,
            name=f"{name}_{i+1}"
        )
        mushrooms.append(mushroom)
    
    return mushrooms


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_mushroom(style='TOADSTOOL', location=(0, 0, 0))
    create_mushroom(style='FLAT', location=(0.15, 0, 0))
    create_mushroom_cluster(count=7, location=(0, 0.3, 0))
    
    print("Created mushrooms")
