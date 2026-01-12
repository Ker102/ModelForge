"""
{
  "title": "Magic Spell Effect",
  "category": "effects",
  "subcategory": "magic",
  "tags": ["magic", "spell", "particles", "effects", "fantasy", "glow"],
  "difficulty": "intermediate",
  "description": "Creates magic spell effects with particles and glowing elements.",
  "blender_version": "3.0+",
  "estimated_objects": 5
}
"""
import bpy
import math
import random


def create_magic_projectile(
    location: tuple = (0, 0, 1),
    color: tuple = (0.2, 0.5, 1.0),
    size: float = 0.2,
    trail_length: float = 1.0,
    animated: bool = True,
    name: str = "MagicProjectile"
) -> dict:
    """
    Create a magic projectile with trail.
    
    Args:
        location: Starting position
        color: RGB glow color
        size: Projectile size
        trail_length: Trail particle length
        animated: Add motion animation
        name: Object name
    
    Returns:
        Dictionary with projectile parts
    """
    result = {}
    
    # Core sphere
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=size,
        subdivisions=2,
        location=location
    )
    core = bpy.context.active_object
    core.name = f"{name}_Core"
    bpy.ops.object.shade_smooth()
    
    # Glow material
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 30.0
    core.data.materials.append(mat)
    
    result['core'] = core
    
    # Outer glow
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=size * 2,
        subdivisions=2,
        location=location
    )
    glow = bpy.context.active_object
    glow.name = f"{name}_Glow"
    
    glow_mat = bpy.data.materials.new(f"{name}_GlowMat")
    glow_mat.use_nodes = True
    glow_mat.blend_method = 'BLEND'
    bsdf = glow_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 5.0
    bsdf.inputs['Alpha'].default_value = 0.3
    glow.data.materials.append(glow_mat)
    
    result['glow'] = glow
    
    # Trail particles
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.01, location=location)
    emitter = bpy.context.active_object
    emitter.name = f"{name}_Emitter"
    
    bpy.ops.object.particle_system_add()
    ps = emitter.particle_systems[-1]
    settings = ps.settings
    
    settings.count = 100
    settings.lifetime = 20
    settings.emit_from = 'VERT'
    settings.normal_factor = 0
    settings.factor_random = 0.5
    settings.render_type = 'HALO'
    settings.particle_size = size * 0.3
    
    result['emitter'] = emitter
    
    # Parent glow to core
    glow.parent = core
    emitter.parent = core
    
    # Animation
    if animated:
        core.location = location
        core.keyframe_insert(data_path="location", frame=1)
        core.location = (location[0], location[1] - 10, location[2])
        core.keyframe_insert(data_path="location", frame=60)
    
    return result


def create_magic_circle(
    radius: float = 1.5,
    rune_count: int = 6,
    color: tuple = (1.0, 0.5, 0.2),
    animated: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "MagicCircle"
) -> dict:
    """
    Create a magic summoning circle.
    
    Args:
        radius: Circle radius
        rune_count: Number of rune symbols
        color: RGB glow color
        animated: Add rotation animation
        location: Position
        name: Object name
    
    Returns:
        Dictionary with circle parts
    """
    result = {}
    
    # Outer ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=0.02,
        location=location
    )
    outer = bpy.context.active_object
    outer.name = f"{name}_Outer"
    outer.rotation_euler.x = math.radians(90)
    
    # Material
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 20.0
    outer.data.materials.append(mat)
    
    result['outer_ring'] = outer
    
    # Inner ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius * 0.7,
        minor_radius=0.015,
        location=location
    )
    inner = bpy.context.active_object
    inner.name = f"{name}_Inner"
    inner.rotation_euler.x = math.radians(90)
    inner.data.materials.append(mat)
    
    result['inner_ring'] = inner
    
    # Rune symbols (simple spheres for now)
    runes = []
    for i in range(rune_count):
        angle = (i / rune_count) * 2 * math.pi
        pos_x = location[0] + math.cos(angle) * radius * 0.85
        pos_y = location[1] + math.sin(angle) * radius * 0.85
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.05,
            location=(pos_x, pos_y, location[2])
        )
        rune = bpy.context.active_object
        rune.name = f"{name}_Rune_{i}"
        rune.data.materials.append(mat)
        runes.append(rune)
    
    result['runes'] = runes
    
    # Light
    bpy.ops.object.light_add(
        type='POINT',
        location=(location[0], location[1], location[2] + 0.5)
    )
    light = bpy.context.active_object
    light.name = f"{name}_Light"
    light.data.energy = 100
    light.data.color = color
    result['light'] = light
    
    # Animation
    if animated:
        for ring in [outer, inner]:
            ring.rotation_euler = (math.radians(90), 0, 0)
            ring.keyframe_insert(data_path="rotation_euler", frame=1)
            ring.rotation_euler = (math.radians(90), 0, math.radians(360))
            ring.keyframe_insert(data_path="rotation_euler", frame=120)
            
            if ring.animation_data and ring.animation_data.action:
                for fc in ring.animation_data.action.fcurves:
                    fc.modifiers.new('CYCLES')
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_magic_projectile(location=(0, 5, 1))
    create_magic_circle(location=(0, 0, 0))
    
    bpy.context.scene.render.engine = 'CYCLES'
    print("Created magic spell effects")
