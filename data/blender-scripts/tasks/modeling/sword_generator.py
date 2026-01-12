"""
{
  "title": "Low Poly Sword Generator",
  "category": "modeling",
  "subcategory": "weapons",
  "tags": ["sword", "weapon", "lowpoly", "game", "props"],
  "difficulty": "intermediate",
  "description": "Generates low-poly swords with customizable blade and handle.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy


def create_sword(
    blade_length: float = 1.0,
    blade_width: float = 0.1,
    handle_length: float = 0.25,
    guard_width: float = 0.2,
    style: str = 'LONGSWORD',
    location: tuple = (0, 0, 0),
    name: str = "Sword"
) -> dict:
    """
    Create a low-poly sword.
    
    Args:
        blade_length: Length of blade
        blade_width: Width at base of blade
        handle_length: Handle/grip length
        guard_width: Crossguard width
        style: 'LONGSWORD', 'DAGGER', 'KATANA', 'RAPIER'
        location: Position
        name: Object name
    
    Returns:
        Dictionary with sword parts
    """
    result = {}
    
    # Style adjustments
    if style == 'DAGGER':
        blade_length *= 0.4
        handle_length *= 0.7
        guard_width *= 0.6
    elif style == 'KATANA':
        blade_width *= 0.6
        guard_width *= 0.4
    elif style == 'RAPIER':
        blade_width *= 0.4
        blade_length *= 1.2
        guard_width *= 1.2
    
    # === BLADE ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1],
        location[2] + handle_length + blade_length/2
    ))
    blade = bpy.context.active_object
    blade.name = f"{name}_Blade"
    blade.scale = (blade_width/2, 0.01, blade_length/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Taper blade to point
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Select top vertices and scale to point
    for v in blade.data.vertices:
        if v.co.z > blade_length/2 - 0.01:
            v.co.x = 0
    
    result['blade'] = blade
    
    # Blade material
    blade_mat = bpy.data.materials.new(f"{name}_BladeMat")
    blade_mat.use_nodes = True
    bsdf = blade_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.8, 0.82, 0.85, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.2
    blade.data.materials.append(blade_mat)
    
    # === GUARD (Crossguard) ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1],
        location[2] + handle_length - 0.01
    ))
    guard = bpy.context.active_object
    guard.name = f"{name}_Guard"
    guard.scale = (guard_width/2, 0.02, 0.02)
    bpy.ops.object.transform_apply(scale=True)
    
    guard_mat = bpy.data.materials.new(f"{name}_GuardMat")
    guard_mat.use_nodes = True
    bsdf = guard_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.6, 0.5, 0.2, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.3
    guard.data.materials.append(guard_mat)
    
    result['guard'] = guard
    
    # === HANDLE ===
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.02,
        depth=handle_length,
        location=(
            location[0],
            location[1],
            location[2] + handle_length/2
        )
    )
    handle = bpy.context.active_object
    handle.name = f"{name}_Handle"
    
    handle_mat = bpy.data.materials.new(f"{name}_HandleMat")
    handle_mat.use_nodes = True
    bsdf = handle_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.15, 0.08, 0.02, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    handle.data.materials.append(handle_mat)
    
    result['handle'] = handle
    
    # === POMMEL ===
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.03,
        location=(location[0], location[1], location[2])
    )
    pommel = bpy.context.active_object
    pommel.name = f"{name}_Pommel"
    pommel.data.materials.append(guard_mat)
    
    result['pommel'] = pommel
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_sword(style='LONGSWORD', location=(0, 0, 0))
    create_sword(style='DAGGER', location=(0.5, 0, 0))
    create_sword(style='KATANA', location=(-0.5, 0, 0))
    
    print("Created 3 sword variations")
