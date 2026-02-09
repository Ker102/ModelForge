"""
{
  "title": "Lantern Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["lantern", "light", "lamp", "props", "medieval", "interior"],
  "difficulty": "beginner",
  "description": "Generates decorative lanterns with light sources.",
  "blender_version": "3.0+",
  "estimated_objects": 4
}
"""
import bpy
import math


def create_lantern(
    size: float = 0.15,
    style: str = 'CLASSIC',
    lit: bool = True,
    hanging: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Lantern"
) -> dict:
    """
    Create a lantern.
    
    Args:
        size: Lantern size
        style: 'CLASSIC', 'PAPER', 'MODERN'
        lit: Add light source
        hanging: Add hanging hook
        location: Position
        name: Object name
    
    Returns:
        Dictionary with lantern parts
    """
    result = {}
    
    if style == 'CLASSIC':
        result = _create_classic_lantern(size, location, name)
    elif style == 'PAPER':
        result = _create_paper_lantern(size, location, name)
    else:
        result = _create_modern_lantern(size, location, name)
    
    # Light source
    if lit:
        bpy.ops.object.light_add(
            type='POINT',
            location=(location[0], location[1], location[2])
        )
        light = bpy.context.active_object
        light.name = f"{name}_Light"
        light.data.energy = 30
        light.data.color = (1.0, 0.8, 0.5)
        light.data.shadow_soft_size = size * 0.5
        result['light'] = light
    
    # Hanging hook
    if hanging:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=size * 0.15,
            minor_radius=size * 0.02,
            location=(location[0], location[1], location[2] + size * 0.7)
        )
        hook = bpy.context.active_object
        hook.name = f"{name}_Hook"
        result['hook'] = hook
    
    return result


def _create_classic_lantern(size, location, name):
    """Create classic metal lantern."""
    result = {}
    
    # Frame
    bpy.ops.mesh.primitive_cube_add(
        size=size,
        location=location
    )
    frame = bpy.context.active_object
    frame.name = f"{name}_Frame"
    
    # Hollow out
    bpy.ops.object.modifier_add(type='WIREFRAME')
    frame.modifiers["Wireframe"].thickness = size * 0.05
    
    frame_mat = bpy.data.materials.new(f"{name}_FrameMat")
    bsdf = frame_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.2, 0.18, 0.15, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    frame.data.materials.append(frame_mat)
    
    result['frame'] = frame
    
    # Glass panels
    bpy.ops.mesh.primitive_cube_add(
        size=size * 0.9,
        location=location
    )
    glass = bpy.context.active_object
    glass.name = f"{name}_Glass"
    
    glass_mat = bpy.data.materials.new(f"{name}_GlassMat")
    glass_mat.blend_method = 'BLEND'
    bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.9, 0.85, 0.7, 0.3)
    bsdf.inputs['Transmission Weight'].default_value = 0.9
    bsdf.inputs['Alpha'].default_value = 0.3
    glass.data.materials.append(glass_mat)
    
    result['glass'] = glass
    
    return result


def _create_paper_lantern(size, location, name):
    """Create paper lantern."""
    result = {}
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=size * 0.6,
        location=location
    )
    lantern = bpy.context.active_object
    lantern.name = f"{name}_Paper"
    lantern.scale.z = 1.3
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    
    mat = bpy.data.materials.new(f"{name}_PaperMat")
    mat.blend_method = 'BLEND'
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.9, 0.3, 0.2, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Emission Color'].default_value = (0.9, 0.4, 0.2, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 2.0
    lantern.data.materials.append(mat)
    
    result['paper'] = lantern
    
    return result


def _create_modern_lantern(size, location, name):
    """Create modern geometric lantern."""
    result = {}
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=size * 0.4,
        depth=size,
        location=location
    )
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.12, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    body.data.materials.append(mat)
    
    result['body'] = body
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_lantern(style='CLASSIC', location=(0, 0, 0))
    create_lantern(style='PAPER', location=(0.4, 0, 0))
    create_lantern(style='MODERN', location=(0.8, 0, 0))
    
    print("Created lanterns")
