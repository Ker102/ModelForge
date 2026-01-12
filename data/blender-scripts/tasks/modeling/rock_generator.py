"""
{
  "title": "Low Poly Rock Generator",
  "category": "modeling",
  "subcategory": "environment",
  "tags": ["rock", "stone", "procedural", "lowpoly", "environment", "props"],
  "difficulty": "beginner",
  "description": "Generates low-poly rocks with random variations.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import random
import math


def create_rock(
    size: float = 1.0,
    detail: int = 2,
    roughness: float = 0.3,
    seed: int = 42,
    location: tuple = (0, 0, 0),
    name: str = "Rock"
) -> bpy.types.Object:
    """
    Create a procedural low-poly rock.
    
    Args:
        size: Base rock size
        detail: Subdivision level (1-3)
        roughness: Surface variation amount
        seed: Random seed
        location: Position
        name: Object name
    
    Returns:
        The created rock object
    """
    random.seed(seed)
    
    # Start with icosphere
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=size,
        subdivisions=detail,
        location=location
    )
    rock = bpy.context.active_object
    rock.name = name
    
    # Deform vertices randomly
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for v in rock.data.vertices:
        displacement = random.uniform(-roughness, roughness) * size
        v.co.x += displacement * random.uniform(0.5, 1.5)
        v.co.y += displacement * random.uniform(0.5, 1.5)
        v.co.z += displacement * random.uniform(0.3, 1.0)
    
    # Flatten bottom slightly
    for v in rock.data.vertices:
        if v.co.z < -size * 0.3:
            v.co.z = -size * 0.3
    
    # Material
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    gray = random.uniform(0.2, 0.5)
    bsdf.inputs['Base Color'].default_value = (gray, gray * 0.95, gray * 0.9, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    
    rock.data.materials.append(mat)
    
    # Shade flat for low-poly look
    bpy.ops.object.shade_flat()
    
    return rock


def create_rock_pile(
    count: int = 5,
    area_radius: float = 2.0,
    min_size: float = 0.3,
    max_size: float = 1.0,
    location: tuple = (0, 0, 0),
    seed: int = 123
) -> list:
    """Create a pile of rocks."""
    random.seed(seed)
    rocks = []
    
    for i in range(count):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, area_radius)
        size = random.uniform(min_size, max_size)
        
        pos = (
            location[0] + math.cos(angle) * dist,
            location[1] + math.sin(angle) * dist,
            location[2] + size * 0.3
        )
        
        rock = create_rock(
            size=size,
            roughness=random.uniform(0.2, 0.4),
            seed=seed + i,
            location=pos,
            name=f"Rock_{i+1}"
        )
        
        rock.rotation_euler = (
            random.uniform(0, 0.3),
            random.uniform(0, 0.3),
            random.uniform(0, math.pi * 2)
        )
        
        rocks.append(rock)
    
    return rocks


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_rock(size=1.5, location=(0, 0, 0))
    create_rock_pile(count=7, location=(5, 0, 0))
    
    print("Created rock and rock pile")
