"""
{
  "title": "Terrain Scatter System",
  "category": "environment",
  "subcategory": "landscape",
  "tags": ["terrain", "scatter", "trees", "rocks", "particles", "environment", "landscape"],
  "difficulty": "intermediate",
  "description": "Creates terrain with scattered objects (trees, rocks, grass) using particle systems or geometry nodes.",
  "blender_version": "3.0+",
  "estimated_objects": 10
}
"""
import bpy
import math
import random


def create_simple_terrain(
    size: float = 50.0,
    subdivisions: int = 100,
    noise_strength: float = 3.0,
    location: tuple = (0, 0, 0),
    name: str = "Terrain"
) -> bpy.types.Object:
    """
    Create a terrain mesh with procedural displacement.
    
    Args:
        size: Terrain size in meters
        subdivisions: Mesh resolution
        noise_strength: Height variation amount
        location: Terrain position
        name: Object name
    
    Returns:
        The created terrain object
    
    Example:
        >>> terrain = create_simple_terrain(size=100, noise_strength=5)
    """
    # Create base plane
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    terrain = bpy.context.active_object
    terrain.name = name
    
    # Subdivide for detail
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=subdivisions)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add displacement modifier
    bpy.ops.object.modifier_add(type='DISPLACE')
    displace = terrain.modifiers["Displace"]
    
    # Create noise texture
    tex = bpy.data.textures.new(f"{name}_Noise", type='CLOUDS')
    tex.noise_scale = 2.0
    tex.noise_depth = 3
    
    displace.texture = tex
    displace.strength = noise_strength
    displace.mid_level = 0.5
    
    # Apply modifier
    bpy.ops.object.modifier_apply(modifier="Displace")
    
    # Smooth shading
    bpy.ops.object.shade_smooth()
    
    # Add terrain material
    terrain_mat = bpy.data.materials.new(name=f"{name}_Material")
    terrain_mat.use_nodes = True
    bsdf = terrain_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.2, 0.35, 0.1, 1.0)  # Green
    bsdf.inputs['Roughness'].default_value = 0.9
    terrain.data.materials.append(terrain_mat)
    
    return terrain


def create_scatter_object(
    scatter_type: str = 'TREE',
    name: str = None
) -> bpy.types.Object:
    """
    Create a simple object for scattering (tree, rock, grass).
    
    Args:
        scatter_type: 'TREE', 'ROCK', 'GRASS', 'BUSH'
        name: Custom name (auto-generated if None)
    
    Returns:
        Created object
    """
    obj_name = name or f"Scatter_{scatter_type}"
    
    if scatter_type.upper() == 'TREE':
        # Simple tree: cone + cylinder
        bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0, depth=2, location=(0, 0, 2.5))
        foliage = bpy.context.active_object
        foliage.name = f"{obj_name}_Foliage"
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.5, location=(0, 0, 0.75))
        trunk = bpy.context.active_object
        trunk.name = f"{obj_name}_Trunk"
        
        # Materials
        foliage_mat = bpy.data.materials.new(name=f"{obj_name}_FoliageMat")
        foliage_mat.use_nodes = True
        foliage_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.1, 0.4, 0.1, 1.0)
        foliage.data.materials.append(foliage_mat)
        
        trunk_mat = bpy.data.materials.new(name=f"{obj_name}_TrunkMat")
        trunk_mat.use_nodes = True
        trunk_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1.0)
        trunk.data.materials.append(trunk_mat)
        
        # Join into single object
        foliage.select_set(True)
        trunk.select_set(True)
        bpy.context.view_layer.objects.active = foliage
        bpy.ops.object.join()
        foliage.name = obj_name
        return foliage
        
    elif scatter_type.upper() == 'ROCK':
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.5, location=(0, 0, 0.25))
        rock = bpy.context.active_object
        rock.name = obj_name
        rock.scale = (1.0, 0.8, 0.6)
        
        # Randomize
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.vertices_smooth(factor=0.5)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        rock_mat = bpy.data.materials.new(name=f"{obj_name}_Mat")
        rock_mat.use_nodes = True
        rock_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.4, 0.4, 0.4, 1.0)
        rock_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.9
        rock.data.materials.append(rock_mat)
        return rock
        
    elif scatter_type.upper() == 'GRASS':
        bpy.ops.mesh.primitive_cone_add(radius1=0.02, radius2=0, depth=0.3, location=(0, 0, 0.15))
        grass = bpy.context.active_object
        grass.name = obj_name
        
        grass_mat = bpy.data.materials.new(name=f"{obj_name}_Mat")
        grass_mat.use_nodes = True
        grass_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.15, 0.5, 0.1, 1.0)
        grass.data.materials.append(grass_mat)
        return grass
    
    return None


def scatter_on_surface(
    surface: bpy.types.Object,
    scatter_object: bpy.types.Object,
    count: int = 100,
    seed: int = 0,
    scale_min: float = 0.8,
    scale_max: float = 1.2,
    rotation_random: float = 1.0,
    name: str = "ScatterSystem"
) -> bpy.types.ParticleSystem:
    """
    Scatter objects on a surface using particle system.
    
    Args:
        surface: Target surface for scattering
        scatter_object: Object to scatter (will be instanced)
        count: Number of instances
        seed: Random seed for reproducibility
        scale_min: Minimum scale multiplier
        scale_max: Maximum scale multiplier
        rotation_random: Rotation randomness factor
        name: Particle system name
    
    Returns:
        The created particle system
    
    Example:
        >>> tree = create_scatter_object('TREE')
        >>> scatter_on_surface(terrain, tree, count=50)
    """
    # Add particle system
    bpy.context.view_layer.objects.active = surface
    bpy.ops.object.particle_system_add()
    
    particle_sys = surface.particle_systems[-1]
    particle_sys.name = name
    settings = particle_sys.settings
    settings.name = f"{name}_Settings"
    
    # Configure as hair (static particles)
    settings.type = 'HAIR'
    settings.use_advanced_hair = True
    
    # Count and distribution
    settings.count = count
    settings.hair_length = 1.0
    settings.emit_from = 'FACE'
    settings.use_modifier_stack = True
    
    # Random seed
    settings.use_emit_random = True
    particle_sys.seed = seed
    
    # Render as object
    settings.render_type = 'OBJECT'
    settings.instance_object = scatter_object
    settings.use_rotation_instance = True
    settings.use_scale_instance = True
    
    # Random scale
    settings.particle_size = (scale_min + scale_max) / 2
    settings.size_random = (scale_max - scale_min) / (scale_min + scale_max)
    
    # Random rotation
    settings.rotation_mode = 'OB_Z'
    settings.rotation_factor_random = rotation_random
    settings.phase_factor_random = 2.0
    
    # Hide original object
    scatter_object.hide_viewport = True
    scatter_object.hide_render = True
    
    return particle_sys


# Standalone execution
if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create terrain
    terrain = create_simple_terrain(size=30, noise_strength=2)
    
    # Create and scatter trees
    tree = create_scatter_object('TREE', 'PineTree')
    scatter_on_surface(terrain, tree, count=30, seed=42)
    
    # Create and scatter rocks
    rock = create_scatter_object('ROCK', 'Boulder')
    scatter_on_surface(terrain, rock, count=20, seed=123, scale_min=0.5, scale_max=2.0)
    
    print("Terrain with scattered objects created!")
