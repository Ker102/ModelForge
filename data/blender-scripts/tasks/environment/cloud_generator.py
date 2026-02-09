"""
{
  "title": "Cloud Generator",
  "category": "environment",
  "subcategory": "sky",
  "tags": ["cloud", "sky", "volumetric", "environment", "weather"],
  "difficulty": "intermediate",
  "description": "Generates volumetric clouds for sky environments.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import random
import math


def create_cloud(
    size: tuple = (5, 3, 2),
    density: float = 0.5,
    detail: float = 5.0,
    location: tuple = (0, 0, 10),
    name: str = "Cloud"
) -> bpy.types.Object:
    """
    Create a volumetric cloud.
    
    Args:
        size: XYZ cloud dimensions
        density: Cloud density
        detail: Noise detail level
        location: Position
        name: Object name
    
    Returns:
        The cloud object
    """
    # Create base shape
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=1,
        subdivisions=2,
        location=location
    )
    cloud = bpy.context.active_object
    cloud.name = name
    cloud.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Deform for cloud shape
    bpy.ops.object.modifier_add(type='DISPLACE')
    tex = bpy.data.textures.new(f"{name}_CloudTex", 'CLOUDS')
    tex.noise_scale = 1.0
    cloud.modifiers["Displace"].texture = tex
    cloud.modifiers["Displace"].strength = size[0] * 0.3
    
    # Volumetric material
    mat = _create_cloud_material(name, density, detail)
    cloud.data.materials.append(mat)
    
    return cloud


def _create_cloud_material(
    name: str,
    density: float,
    detail: float
) -> bpy.types.Material:
    """Create volumetric cloud material."""
    mat = bpy.data.materials.new(f"{name}_Mat")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    # Principled Volume
    volume = nodes.new('ShaderNodeVolumePrincipled')
    volume.location = (0, 0)
    volume.inputs['Color'].default_value = (1, 1, 1, 1)
    volume.inputs['Density'].default_value = density
    volume.inputs['Anisotropy'].default_value = 0.3
    
    # Noise for cloud shape
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = detail
    noise.inputs['Detail'].default_value = 8.0
    
    # Math to control density
    math_node = nodes.new('ShaderNodeMath')
    math_node.location = (-200, 0)
    math_node.operation = 'MULTIPLY'
    math_node.inputs[1].default_value = density * 5
    
    links.new(noise.outputs['Fac'], math_node.inputs[0])
    links.new(math_node.outputs['Value'], volume.inputs['Density'])
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (200, 0)
    links.new(volume.outputs['Volume'], output.inputs['Volume'])
    
    return mat


def create_cloud_layer(
    cloud_count: int = 5,
    area_size: tuple = (50, 50),
    altitude: float = 15,
    altitude_variation: float = 3,
    seed: int = 42,
    name: str = "CloudLayer"
) -> list:
    """
    Create a layer of clouds.
    
    Args:
        cloud_count: Number of clouds
        area_size: XY area to cover
        altitude: Base altitude
        altitude_variation: Height variation
        seed: Random seed
        name: Layer name
    
    Returns:
        List of cloud objects
    """
    random.seed(seed)
    clouds = []
    
    for i in range(cloud_count):
        pos = (
            random.uniform(-area_size[0]/2, area_size[0]/2),
            random.uniform(-area_size[1]/2, area_size[1]/2),
            altitude + random.uniform(-altitude_variation, altitude_variation)
        )
        
        size = (
            random.uniform(3, 8),
            random.uniform(2, 5),
            random.uniform(1.5, 3)
        )
        
        cloud = create_cloud(
            size=size,
            density=random.uniform(0.3, 0.7),
            location=pos,
            name=f"{name}_{i+1}"
        )
        clouds.append(cloud)
    
    return clouds


def create_stylized_cloud(
    size: float = 2.0,
    puff_count: int = 5,
    color: tuple = (1, 1, 1),
    location: tuple = (0, 0, 5),
    name: str = "StylizedCloud"
) -> bpy.types.Object:
    """
    Create a cartoon-style cloud from spheres.
    
    Args:
        size: Overall cloud size
        puff_count: Number of puffs
        color: Cloud color
        location: Position
        name: Object name
    """
    puffs = []
    
    # Main puff
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=size * 0.4,
        location=location
    )
    main_puff = bpy.context.active_object
    puffs.append(main_puff)
    
    # Surrounding puffs
    for i in range(puff_count):
        angle = (i / puff_count) * 2 * math.pi
        dist = size * 0.3
        puff_size = size * random.uniform(0.25, 0.35)
        
        pos = (
            location[0] + math.cos(angle) * dist,
            location[1] + math.sin(angle) * dist * 0.5,
            location[2] + random.uniform(-size * 0.1, size * 0.15)
        )
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=puff_size,
            location=pos
        )
        puffs.append(bpy.context.active_object)
    
    # Join all
    bpy.ops.object.select_all(action='DESELECT')
    for p in puffs:
        p.select_set(True)
    bpy.context.view_layer.objects.active = puffs[0]
    bpy.ops.object.join()
    
    cloud = bpy.context.active_object
    cloud.name = name
    bpy.ops.object.shade_smooth()
    
    # Simple white material
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    cloud.data.materials.append(mat)
    
    return cloud


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_cloud(location=(0, 0, 10))
    create_stylized_cloud(location=(10, 0, 8))
    
    bpy.context.scene.render.engine = 'CYCLES'
    print("Created clouds")
