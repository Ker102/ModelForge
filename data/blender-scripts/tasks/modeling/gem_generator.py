"""
{
  "title": "Gem and Crystal Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["gem", "crystal", "jewel", "procedural", "fantasy", "props"],
  "difficulty": "intermediate",
  "description": "Generates gem and crystal shapes with refractive materials.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math
import random


def create_gem(
    size: float = 0.05,
    style: str = 'ROUND',
    color: tuple = (0.1, 0.3, 0.9),
    location: tuple = (0, 0, 0),
    name: str = "Gem"
) -> bpy.types.Object:
    """
    Create a gem/jewel.
    
    Args:
        size: Gem diameter
        style: 'ROUND', 'PRINCESS', 'EMERALD', 'OVAL'
        color: RGB gem color
        location: Position
        name: Object name
    
    Returns:
        The gem object
    """
    if style == 'ROUND':
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=size/2,
            subdivisions=2,
            location=location
        )
        gem = bpy.context.active_object
        gem.scale.z = 0.6
        
    elif style == 'PRINCESS':
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        gem = bpy.context.active_object
        gem.scale.z = 0.7
        
        bpy.ops.object.modifier_add(type='BEVEL')
        gem.modifiers["Bevel"].width = size * 0.15
        gem.modifiers["Bevel"].segments = 2
        
    elif style == 'EMERALD':
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=size/2,
            depth=size * 0.7,
            location=location
        )
        gem = bpy.context.active_object
        
        bpy.ops.object.modifier_add(type='BEVEL')
        gem.modifiers["Bevel"].width = size * 0.1
        
    else:  # OVAL
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=size/2,
            location=location
        )
        gem = bpy.context.active_object
        gem.scale = (1, 0.7, 0.5)
    
    bpy.ops.object.transform_apply(scale=True)
    gem.name = name
    bpy.ops.object.shade_smooth()
    
    # Glass material with color
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.blend_method = 'BLEND'
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['IOR'].default_value = 2.4  # Diamond-like
    bsdf.inputs['Transmission Weight'].default_value = 1.0
    gem.data.materials.append(mat)
    
    return gem


def create_crystal(
    height: float = 0.15,
    base_radius: float = 0.03,
    facets: int = 6,
    color: tuple = (0.8, 0.4, 0.9),
    location: tuple = (0, 0, 0),
    name: str = "Crystal"
) -> bpy.types.Object:
    """
    Create a crystal formation.
    
    Args:
        height: Crystal height
        base_radius: Base radius
        facets: Number of sides
        color: RGB color
        location: Position
        name: Object name
    
    Returns:
        The crystal object
    """
    bpy.ops.mesh.primitive_cone_add(
        vertices=facets,
        radius1=base_radius,
        radius2=0,
        depth=height,
        location=(location[0], location[1], location[2] + height/2)
    )
    crystal = bpy.context.active_object
    crystal.name = name
    
    # Add some variation
    bpy.ops.object.modifier_add(type='DISPLACE')
    tex = bpy.data.textures.new(f"{name}_Disp", 'NOISE')
    crystal.modifiers["Displace"].texture = tex
    crystal.modifiers["Displace"].strength = base_radius * 0.2
    
    # Material
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.blend_method = 'BLEND'
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.1
    bsdf.inputs['Transmission Weight'].default_value = 0.8
    bsdf.inputs['IOR'].default_value = 1.55
    
    # Emission for glow
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 0.5
    
    crystal.data.materials.append(mat)
    
    return crystal


def create_crystal_cluster(
    count: int = 5,
    max_height: float = 0.2,
    spread: float = 0.1,
    color: tuple = (0.6, 0.3, 0.9),
    location: tuple = (0, 0, 0),
    seed: int = 42,
    name: str = "CrystalCluster"
) -> list:
    """Create a cluster of crystals."""
    random.seed(seed)
    crystals = []
    
    for i in range(count):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, spread)
        
        pos = (
            location[0] + math.cos(angle) * dist,
            location[1] + math.sin(angle) * dist,
            location[2]
        )
        
        height = max_height * random.uniform(0.5, 1.0)
        radius = height * random.uniform(0.15, 0.25)
        
        # Slight color variation
        c_var = random.uniform(-0.1, 0.1)
        c = (
            max(0, min(1, color[0] + c_var)),
            max(0, min(1, color[1] + c_var)),
            max(0, min(1, color[2] + c_var))
        )
        
        crystal = create_crystal(
            height=height,
            base_radius=radius,
            color=c,
            location=pos,
            name=f"{name}_{i+1}"
        )
        
        # Tilt slightly
        crystal.rotation_euler.x = random.uniform(-0.2, 0.2)
        crystal.rotation_euler.y = random.uniform(-0.2, 0.2)
        
        crystals.append(crystal)
    
    return crystals


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_gem(style='ROUND', color=(0.9, 0.1, 0.1), location=(0, 0, 0))
    create_gem(style='PRINCESS', color=(0.1, 0.8, 0.2), location=(0.1, 0, 0))
    create_gem(style='EMERALD', color=(0.1, 0.3, 0.9), location=(0.2, 0, 0))
    
    create_crystal_cluster(location=(0, 0.3, 0))
    
    bpy.context.scene.render.engine = 'CYCLES'
    print("Created gems and crystals")
