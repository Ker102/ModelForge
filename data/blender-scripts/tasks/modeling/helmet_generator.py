"""
{
  "title": "Helmet Generator",
  "category": "modeling",
  "subcategory": "armor",
  "tags": ["helmet", "armor", "medieval", "fantasy", "knight", "game"],
  "difficulty": "intermediate",
  "description": "Generates medieval and fantasy helmets.",
  "blender_version": "3.0+",
  "estimated_objects": 2
}
"""
import bpy
import math


def create_helmet(
    size: float = 0.25,
    style: str = 'KNIGHT',
    location: tuple = (0, 0, 0),
    name: str = "Helmet"
) -> dict:
    """
    Create a helmet.
    
    Args:
        size: Helmet size
        style: 'KNIGHT', 'VIKING', 'SPARTAN', 'BARBUTE'
        location: Position
        name: Object name
    
    Returns:
        Dictionary with helmet parts
    """
    result = {}
    
    # Base dome
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=size/2,
        location=(location[0], location[1], location[2] + size/2)
    )
    helmet = bpy.context.active_object
    helmet.name = name
    
    # Cut bottom half
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(
        plane_co=(0, 0, location[2] + size * 0.2),
        plane_no=(0, 0, 1),
        clear_inner=True
    )
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Style-specific modifications
    if style == 'VIKING':
        _add_viking_features(helmet, size, location, name, result)
    elif style == 'SPARTAN':
        _add_spartan_features(helmet, size, location, name, result)
    elif style == 'KNIGHT':
        _add_knight_features(helmet, size, location, name, result)
    
    # Material
    metal_mat = bpy.data.materials.new(f"{name}_MetalMat")
    bsdf = metal_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.53, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.35
    helmet.data.materials.append(metal_mat)
    
    bpy.ops.object.shade_smooth()
    result['helmet'] = helmet
    
    return result


def _add_viking_features(helmet, size, location, name, result):
    """Add Viking helmet horns."""
    horn_mat = bpy.data.materials.new(f"{name}_HornMat")
    bsdf = horn_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.8, 0.75, 0.6, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cone_add(
            radius1=size * 0.08,
            radius2=0,
            depth=size * 0.5,
            location=(
                location[0] + side * size * 0.35,
                location[1],
                location[2] + size * 0.6
            )
        )
        horn = bpy.context.active_object
        horn.name = f"{name}_Horn_{'L' if side < 0 else 'R'}"
        horn.rotation_euler = (
            math.radians(-30),
            math.radians(side * 30),
            0
        )
        horn.data.materials.append(horn_mat)


def _add_spartan_features(helmet, size, location, name, result):
    """Add Spartan helmet crest."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1],
        location[2] + size * 0.9
    ))
    crest = bpy.context.active_object
    crest.name = f"{name}_Crest"
    crest.scale = (0.02, size * 0.4, size * 0.4)
    bpy.ops.object.transform_apply(scale=True)
    
    crest_mat = bpy.data.materials.new(f"{name}_CrestMat")
    bsdf = crest_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1.0)
    crest.data.materials.append(crest_mat)
    result['crest'] = crest


def _add_knight_features(helmet, size, location, name, result):
    """Add knight helmet visor."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1] - size * 0.35,
        location[2] + size * 0.35
    ))
    visor = bpy.context.active_object
    visor.name = f"{name}_Visor"
    visor.scale = (size * 0.4, size * 0.15, size * 0.25)
    bpy.ops.object.transform_apply(scale=True)
    result['visor'] = visor


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_helmet(style='KNIGHT', location=(0, 0, 0))
    create_helmet(style='VIKING', location=(0.4, 0, 0))
    create_helmet(style='SPARTAN', location=(0.8, 0, 0))
    
    print("Created helmets")
