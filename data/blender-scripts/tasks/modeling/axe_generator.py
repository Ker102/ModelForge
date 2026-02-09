"""
{
  "title": "Axe Generator",
  "category": "modeling",
  "subcategory": "weapons",
  "tags": ["axe", "weapon", "medieval", "fantasy", "props", "game"],
  "difficulty": "intermediate",
  "description": "Generates battle axes and hand axes.",
  "blender_version": "3.0+",
  "estimated_objects": 2
}
"""
import bpy
import math


def create_axe(
    handle_length: float = 0.6,
    head_size: float = 0.15,
    style: str = 'BATTLE',
    material_type: str = 'IRON',
    location: tuple = (0, 0, 0),
    name: str = "Axe"
) -> dict:
    """
    Create an axe.
    
    Args:
        handle_length: Handle length
        head_size: Axe head size
        style: 'BATTLE', 'HAND', 'DOUBLE'
        material_type: 'IRON', 'BRONZE', 'STEEL'
        location: Position
        name: Object name
    
    Returns:
        Dictionary with axe parts
    """
    result = {}
    
    # Handle
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.02,
        depth=handle_length,
        location=(location[0], location[1], location[2] + handle_length/2)
    )
    handle = bpy.context.active_object
    handle.name = f"{name}_Handle"
    
    handle_mat = bpy.data.materials.new(f"{name}_HandleMat")
    bsdf = handle_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    handle.data.materials.append(handle_mat)
    
    result['handle'] = handle
    
    # Axe head
    head_z = location[2] + handle_length - head_size * 0.3
    
    if style == 'DOUBLE':
        heads = [_create_axe_blade(head_size, (location[0], location[1], head_z), name, 1),
                 _create_axe_blade(head_size, (location[0], location[1], head_z), name, -1)]
        result['heads'] = heads
    else:
        head = _create_axe_blade(head_size, (location[0], location[1], head_z), name, 1)
        
        if style == 'HAND':
            head.scale *= 0.6
            bpy.ops.object.transform_apply(scale=True)
        
        result['head'] = head
    
    # Metal material
    metal_colors = {
        'IRON': (0.4, 0.4, 0.42),
        'BRONZE': (0.8, 0.5, 0.2),
        'STEEL': (0.6, 0.6, 0.65)
    }
    
    metal_mat = bpy.data.materials.new(f"{name}_MetalMat")
    bsdf = metal_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*metal_colors.get(material_type, metal_colors['IRON']), 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.35
    
    if 'head' in result:
        result['head'].data.materials.append(metal_mat)
    if 'heads' in result:
        for h in result['heads']:
            h.data.materials.append(metal_mat)
    
    return result


def _create_axe_blade(
    size: float,
    location: tuple,
    name: str,
    direction: int = 1
) -> bpy.types.Object:
    """Create axe blade."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0] + direction * size * 0.5,
        location[1],
        location[2]
    ))
    blade = bpy.context.active_object
    blade.name = f"{name}_Blade"
    blade.scale = (size, 0.02, size * 0.8)
    bpy.ops.object.transform_apply(scale=True)
    
    # Shape blade
    for v in blade.data.vertices:
        if direction * v.co.x > 0:
            # Curve cutting edge
            v.co.z *= 1 - abs(v.co.x) * 0.5
            v.co.x *= 0.7
    
    bpy.ops.object.shade_flat()
    
    return blade


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_axe(style='BATTLE', location=(0, 0, 0))
    create_axe(style='HAND', location=(0.4, 0, 0))
    create_axe(style='DOUBLE', location=(0.8, 0, 0))
    
    print("Created axes")
