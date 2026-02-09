"""
{
  "title": "Grass and Foliage Generator",
  "category": "environment",
  "subcategory": "vegetation",
  "tags": ["grass", "foliage", "vegetation", "procedural", "particles"],
  "difficulty": "intermediate",
  "description": "Creates grass and ground foliage using particle systems or geometry nodes.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import random
import math


def create_grass_blade(
    height: float = 0.1,
    width: float = 0.01,
    bend: float = 0.3,
    name: str = "GrassBlade"
) -> bpy.types.Object:
    """Create a single grass blade mesh."""
    # Create plane for blade
    bpy.ops.mesh.primitive_plane_add(size=1)
    blade = bpy.context.active_object
    blade.name = name
    
    # Scale to blade shape
    blade.scale = (width, height, 1)
    bpy.ops.object.transform_apply(scale=True)
    
    # Rotate to stand up
    blade.rotation_euler.x = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    
    # Add bend
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    blade.modifiers["SimpleDeform"].deform_method = 'BEND'
    blade.modifiers["SimpleDeform"].angle = bend
    blade.modifiers["SimpleDeform"].deform_axis = 'X'
    
    # Material
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.15, 0.4, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    bsdf.inputs['Subsurface Weight'].default_value = 0.3
    blade.data.materials.append(mat)
    
    # Move to origin
    blade.location = (0, 0, height/2)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    blade.location = (0, 0, 0)
    
    return blade


def create_grass_particles(
    ground: bpy.types.Object,
    density: int = 5000,
    blade_height: float = 0.1,
    height_random: float = 0.5,
    blade: bpy.types.Object = None,
    name: str = "GrassSystem"
) -> tuple:
    """
    Create grass using particle system.
    
    Args:
        ground: Surface to grow grass on
        density: Number of grass blades
        blade_height: Base blade height
        height_random: Height variation
        blade: Custom blade object (creates one if None)
        name: System name
    
    Returns:
        Tuple of (particle_system, blade_object)
    """
    # Create blade if not provided
    if blade is None:
        blade = create_grass_blade(height=blade_height)
        blade.hide_viewport = True
        blade.hide_render = True
    
    bpy.context.view_layer.objects.active = ground
    bpy.ops.object.particle_system_add()
    
    ps = ground.particle_systems[-1]
    ps.name = name
    settings = ps.settings
    settings.name = f"{name}_Settings"
    
    # Hair type for static grass
    settings.type = 'HAIR'
    settings.count = density
    settings.hair_length = blade_height
    settings.render_type = 'OBJECT'
    settings.instance_object = blade
    settings.particle_size = 1.0
    settings.size_random = height_random
    settings.use_rotation_instance = True
    settings.rotation_factor_random = 0.1
    settings.phase_factor_random = 1.0
    
    return ps, blade


def create_flower(
    petals: int = 5,
    petal_size: float = 0.02,
    color: tuple = (1.0, 0.3, 0.4),
    stem_height: float = 0.15,
    name: str = "Flower"
) -> bpy.types.Object:
    """Create a simple flower."""
    # Center
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=petal_size * 0.3,
        location=(0, 0, stem_height)
    )
    center = bpy.context.active_object
    
    # Petals
    for i in range(petals):
        angle = (i / petals) * 2 * math.pi
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=petal_size,
            location=(
                math.cos(angle) * petal_size,
                math.sin(angle) * petal_size,
                stem_height
            )
        )
        petal = bpy.context.active_object
        petal.scale.z = 0.3
        bpy.ops.object.transform_apply(scale=True)
    
    # Stem
    bpy.ops.mesh.primitive_cylinder_add(
        radius=petal_size * 0.1,
        depth=stem_height,
        location=(0, 0, stem_height / 2)
    )
    
    # Select all and join
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    flower = bpy.context.active_object
    flower.name = name
    
    # Material
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    flower.data.materials.append(mat)
    
    return flower


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create ground
    bpy.ops.mesh.primitive_plane_add(size=5)
    ground = bpy.context.active_object
    
    # Add grass
    ps, blade = create_grass_particles(ground, density=3000)
    
    # Create flower
    create_flower(location=(1, 1, 0))
    
    print("Created grass and flower")
