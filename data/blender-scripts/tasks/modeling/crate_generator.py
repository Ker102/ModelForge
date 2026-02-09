"""
{
  "title": "Crate and Box Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["crate", "box", "cargo", "props", "storage", "wooden"],
  "difficulty": "beginner",
  "description": "Generates wooden crates and cargo boxes.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import random


def create_crate(
    size: tuple = (0.5, 0.5, 0.5),
    style: str = 'WOODEN',
    plank_count: int = 4,
    worn: bool = False,
    location: tuple = (0, 0, 0),
    name: str = "Crate"
) -> bpy.types.Object:
    """
    Create a crate or box.
    
    Args:
        size: XYZ dimensions
        style: 'WOODEN', 'CARDBOARD', 'METAL'
        plank_count: Planks per side (wooden)
        worn: Add wear/damage look
        location: Position
        name: Object name
    
    Returns:
        The crate object
    """
    if style == 'WOODEN':
        crate = _create_wooden_crate(size, plank_count, location, name)
    elif style == 'CARDBOARD':
        crate = _create_cardboard_box(size, location, name)
    else:  # METAL
        crate = _create_metal_crate(size, location, name)
    
    return crate


def _create_wooden_crate(
    size: tuple,
    plank_count: int,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create wooden crate with planks."""
    plank_thickness = 0.02
    
    # Material
    wood_mat = bpy.data.materials.new(f"{name}_WoodMat")
    bsdf = wood_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.45, 0.32, 0.18, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    
    planks = []
    
    # Create planks for each face
    for face in ['front', 'back', 'left', 'right', 'top', 'bottom']:
        plank_size = _get_plank_dimensions(face, size, plank_count, plank_thickness)
        
        for i in range(plank_count):
            pos = _get_plank_position(face, size, i, plank_count, location)
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
            plank = bpy.context.active_object
            plank.scale = plank_size
            bpy.ops.object.transform_apply(scale=True)
            plank.data.materials.append(wood_mat)
            planks.append(plank)
    
    # Join all planks
    bpy.ops.object.select_all(action='DESELECT')
    for p in planks:
        p.select_set(True)
    bpy.context.view_layer.objects.active = planks[0]
    bpy.ops.object.join()
    
    crate = bpy.context.active_object
    crate.name = name
    
    return crate


def _get_plank_dimensions(
    face: str,
    size: tuple,
    plank_count: int,
    thickness: float
) -> tuple:
    """Get plank dimensions for face."""
    w, d, h = size
    
    if face in ['front', 'back']:
        return (w/(plank_count*2), thickness/2, h/2)
    elif face in ['left', 'right']:
        return (thickness/2, d/2, h/(plank_count*2))
    else:  # top/bottom
        return (w/2, d/(plank_count*2), thickness/2)


def _get_plank_position(
    face: str,
    size: tuple,
    index: int,
    count: int,
    location: tuple
) -> tuple:
    """Get plank position."""
    w, d, h = size
    offset = (index + 0.5) / count - 0.5
    
    positions = {
        'front': (location[0] + offset * w, location[1] - d/2, location[2] + h/2),
        'back': (location[0] + offset * w, location[1] + d/2, location[2] + h/2),
        'left': (location[0] - w/2, location[1], location[2] + h/2 + offset * h),
        'right': (location[0] + w/2, location[1], location[2] + h/2 + offset * h),
        'top': (location[0], location[1] + offset * d, location[2] + h),
        'bottom': (location[0], location[1] + offset * d, location[2])
    }
    
    return positions[face]


def _create_cardboard_box(
    size: tuple,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create simple cardboard box."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0], location[1], location[2] + size[2]/2
    ))
    box = bpy.context.active_object
    box.name = name
    box.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    
    mat = bpy.data.materials.new(f"{name}_CardboardMat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.6, 0.5, 0.35, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    box.data.materials.append(mat)
    
    return box


def _create_metal_crate(
    size: tuple,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create metal shipping container."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0], location[1], location[2] + size[2]/2
    ))
    crate = bpy.context.active_object
    crate.name = name
    crate.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    
    mat = bpy.data.materials.new(f"{name}_MetalMat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.35, 0.4, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.5
    crate.data.materials.append(mat)
    
    return crate


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_crate(style='WOODEN', location=(0, 0, 0))
    create_crate(style='CARDBOARD', location=(0.8, 0, 0))
    create_crate(style='METAL', size=(0.6, 0.4, 0.4), location=(1.6, 0, 0))
    
    print("Created 3 crate types")
