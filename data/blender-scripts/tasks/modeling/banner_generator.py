"""
{
  "title": "Banner Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["banner", "flag", "medieval", "cloth", "decoration", "props"],
  "difficulty": "beginner",
  "description": "Generates banners and flags with cloth simulation ready.",
  "blender_version": "3.0+",
  "estimated_objects": 2
}
"""
import bpy
import math


def create_banner(
    width: float = 0.5,
    height: float = 1.0,
    style: str = 'HANGING',
    color: tuple = (0.7, 0.1, 0.1),
    with_pole: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Banner"
) -> dict:
    """
    Create a banner/flag.
    
    Args:
        width: Banner width
        height: Banner height
        style: 'HANGING', 'FLAG', 'PENNANT'
        color: RGB banner color
        with_pole: Add pole/staff
        location: Position
        name: Object name
    
    Returns:
        Dictionary with banner parts
    """
    result = {}
    
    # === CLOTH ===
    if style == 'PENNANT':
        bpy.ops.mesh.primitive_cone_add(
            vertices=3,
            radius1=width/2,
            radius2=0,
            depth=0.01,
            location=(location[0], location[1], location[2] - height/2)
        )
        cloth = bpy.context.active_object
        cloth.rotation_euler.x = math.radians(90)
        cloth.rotation_euler.z = math.radians(90)
    else:
        bpy.ops.mesh.primitive_plane_add(
            size=1,
            location=(location[0], location[1], location[2] - height/2)
        )
        cloth = bpy.context.active_object
        cloth.scale = (width/2, height/2, 1)
        cloth.rotation_euler.x = math.radians(90)
    
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    cloth.name = f"{name}_Cloth"
    
    # Subdivide for cloth sim
    bpy.ops.object.modifier_add(type='SUBSURF')
    cloth.modifiers["Subdivision"].levels = 3
    
    # Cloth material
    cloth_mat = bpy.data.materials.new(f"{name}_ClothMat")
    cloth_mat.use_nodes = True
    bsdf = cloth_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    bsdf.inputs['Sheen Weight'].default_value = 0.3
    cloth.data.materials.append(cloth_mat)
    
    result['cloth'] = cloth
    
    # === POLE ===
    if with_pole:
        pole_height = height + 0.5 if style == 'FLAG' else height + 0.2
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.02,
            depth=pole_height,
            location=(
                location[0] - width/2 - 0.02 if style != 'HANGING' else location[0],
                location[1],
                location[2] if style == 'HANGING' else location[2] + 0.2
            )
        )
        pole = bpy.context.active_object
        pole.name = f"{name}_Pole"
        
        if style == 'FLAG':
            pole.rotation_euler.x = math.radians(15)
        
        pole_mat = bpy.data.materials.new(f"{name}_PoleMat")
        pole_mat.use_nodes = True
        bsdf = pole_mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.7
        pole.data.materials.append(pole_mat)
        
        result['pole'] = pole
    
    return result


def add_cloth_simulation(
    cloth_obj: bpy.types.Object,
    pin_group: str = None,
    stiffness: float = 15.0
) -> bpy.types.Modifier:
    """
    Add cloth simulation to banner.
    
    Args:
        cloth_obj: The banner cloth object
        pin_group: Vertex group name to pin
        stiffness: Cloth stiffness
    
    Returns:
        The cloth modifier
    """
    mod = cloth_obj.modifiers.new("Cloth", 'CLOTH')
    settings = mod.settings
    
    settings.quality = 5
    settings.mass = 0.3
    settings.tension_stiffness = stiffness
    settings.compression_stiffness = stiffness
    settings.bending_stiffness = 5.0
    
    if pin_group:
        settings.vertex_group_mass = pin_group
    
    return mod


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_banner(style='HANGING', location=(0, 0, 2))
    create_banner(style='FLAG', color=(0.1, 0.2, 0.7), location=(1, 0, 0))
    create_banner(style='PENNANT', location=(2, 0, 2))
    
    print("Created banners")
