"""
{
  "title": "Food Props Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["food", "fruit", "kitchen", "props", "procedural"],
  "difficulty": "beginner",
  "description": "Generates simple food items for scene decoration.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math
import random


def create_apple(
    radius: float = 0.04,
    color: tuple = (0.8, 0.15, 0.1),
    location: tuple = (0, 0, 0),
    name: str = "Apple"
) -> bpy.types.Object:
    """Create an apple."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=(location[0], location[1], location[2] + radius)
    )
    apple = bpy.context.active_object
    apple.name = name
    
    # Slight squish
    apple.scale.z = 0.85
    bpy.ops.object.transform_apply(scale=True)
    
    # Dimple at top
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for v in apple.data.vertices:
        if v.co.z > radius * 0.7:
            v.co.z -= (v.co.z - radius * 0.7) * 0.3
    
    bpy.ops.object.shade_smooth()
    
    # Material
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.4
    bsdf.inputs['Sheen Weight'].default_value = 0.3
    apple.data.materials.append(mat)
    
    # Stem
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.003,
        depth=0.015,
        location=(location[0], location[1], location[2] + radius * 1.65)
    )
    stem = bpy.context.active_object
    stem.name = f"{name}_Stem"
    
    stem_mat = bpy.data.materials.new(f"{name}_StemMat")
    bsdf = stem_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1.0)
    stem.data.materials.append(stem_mat)
    stem.parent = apple
    
    return apple


def create_orange(
    radius: float = 0.045,
    location: tuple = (0, 0, 0),
    name: str = "Orange"
) -> bpy.types.Object:
    """Create an orange."""
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=radius,
        subdivisions=3,
        location=(location[0], location[1], location[2] + radius)
    )
    orange = bpy.context.active_object
    orange.name = name
    
    # Add bump
    bpy.ops.object.modifier_add(type='DISPLACE')
    tex = bpy.data.textures.new(f"{name}_Bump", 'NOISE')
    tex.noise_scale = 0.5
    orange.modifiers["Displace"].texture = tex
    orange.modifiers["Displace"].strength = 0.002
    
    bpy.ops.object.shade_smooth()
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (1.0, 0.5, 0.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    bsdf.inputs['Subsurface Weight'].default_value = 0.1
    orange.data.materials.append(mat)
    
    return orange


def create_banana(
    length: float = 0.18,
    location: tuple = (0, 0, 0),
    name: str = "Banana"
) -> bpy.types.Object:
    """Create a banana."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.015,
        depth=length,
        location=(location[0], location[1], location[2] + 0.02)
    )
    banana = bpy.context.active_object
    banana.name = name
    banana.rotation_euler.y = math.radians(90)
    
    # Bend
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    banana.modifiers["SimpleDeform"].deform_method = 'BEND'
    banana.modifiers["SimpleDeform"].angle = math.radians(40)
    
    # Taper ends
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    banana.modifiers["SimpleDeform.001"].deform_method = 'TAPER'
    banana.modifiers["SimpleDeform.001"].factor = 0.3
    
    bpy.ops.object.shade_smooth()
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (1.0, 0.85, 0.2, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.5
    banana.data.materials.append(mat)
    
    return banana


def create_bread_loaf(
    length: float = 0.25,
    width: float = 0.1,
    height: float = 0.08,
    location: tuple = (0, 0, 0),
    name: str = "Bread"
) -> bpy.types.Object:
    """Create a bread loaf."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=1,
        location=(location[0], location[1], location[2] + height)
    )
    bread = bpy.context.active_object
    bread.name = name
    bread.scale = (length/2, width/2, height)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.object.shade_smooth()
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.7, 0.5, 0.3, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    bread.data.materials.append(mat)
    
    return bread


def create_fruit_bowl(
    location: tuple = (0, 0, 0),
    fruit_count: int = 5,
    name: str = "FruitBowl"
) -> dict:
    """Create a bowl with assorted fruit."""
    result = {}
    
    # Bowl
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.15,
        location=(location[0], location[1], location[2] + 0.05)
    )
    bowl = bpy.context.active_object
    bowl.name = f"{name}_Bowl"
    bowl.scale.z = 0.4
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.bisect(plane_co=(0, 0, 0.06), plane_no=(0, 0, 1), clear_inner=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    mat = bpy.data.materials.new(f"{name}_BowlMat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.85, 1.0)
    bowl.data.materials.append(mat)
    
    result['bowl'] = bowl
    
    # Add fruits
    fruits = []
    fruit_funcs = [create_apple, create_orange]
    
    for i in range(fruit_count):
        angle = (i / fruit_count) * 2 * math.pi
        r = random.uniform(0.03, 0.08)
        pos = (
            location[0] + math.cos(angle) * r,
            location[1] + math.sin(angle) * r,
            location[2] + 0.05
        )
        
        func = random.choice(fruit_funcs)
        fruit = func(location=pos, name=f"{name}_Fruit_{i}")
        fruits.append(fruit)
    
    result['fruits'] = fruits
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_apple(location=(0, 0, 0))
    create_orange(location=(0.1, 0, 0))
    create_banana(location=(0.2, 0, 0))
    create_fruit_bowl(location=(0, 0.3, 0))
    
    print("Created food items")
