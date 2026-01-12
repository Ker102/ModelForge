"""
{
  "title": "Bottle Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["bottle", "container", "glass", "props", "procedural"],
  "difficulty": "beginner",
  "description": "Generates various bottle types with glass materials.",
  "blender_version": "3.0+",
  "estimated_objects": 2
}
"""
import bpy
import math


def create_bottle(
    height: float = 0.3,
    body_radius: float = 0.04,
    neck_radius: float = 0.015,
    neck_height: float = 0.06,
    style: str = 'WINE',
    glass_color: tuple = (0.1, 0.5, 0.2),
    location: tuple = (0, 0, 0),
    name: str = "Bottle"
) -> dict:
    """
    Create a bottle.
    
    Args:
        height: Total bottle height
        body_radius: Body radius
        neck_radius: Neck radius
        neck_height: Neck length
        style: 'WINE', 'BEER', 'SODA', 'PERFUME'
        glass_color: RGB glass tint
        location: Position
        name: Object name
    
    Returns:
        Dictionary with bottle parts
    """
    result = {}
    
    # Style adjustments
    styles = {
        'WINE': {'body_ratio': 0.65, 'shoulder': 0.2, 'neck_taper': True},
        'BEER': {'body_ratio': 0.75, 'shoulder': 0.1, 'neck_taper': False},
        'SODA': {'body_ratio': 0.7, 'shoulder': 0.15, 'neck_taper': False},
        'PERFUME': {'body_ratio': 0.5, 'shoulder': 0.3, 'neck_taper': True}
    }
    
    s = styles.get(style, styles['WINE'])
    body_height = height * s['body_ratio']
    shoulder_height = height * s['shoulder']
    
    # Body cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=body_radius,
        depth=body_height,
        location=(location[0], location[1], location[2] + body_height/2)
    )
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    
    # Shoulder (cone)
    bpy.ops.mesh.primitive_cone_add(
        radius1=body_radius,
        radius2=neck_radius,
        depth=shoulder_height,
        location=(
            location[0], location[1],
            location[2] + body_height + shoulder_height/2
        )
    )
    shoulder = bpy.context.active_object
    shoulder.name = f"{name}_Shoulder"
    
    # Neck
    bpy.ops.mesh.primitive_cylinder_add(
        radius=neck_radius,
        depth=neck_height,
        location=(
            location[0], location[1],
            location[2] + body_height + shoulder_height + neck_height/2
        )
    )
    neck = bpy.context.active_object
    neck.name = f"{name}_Neck"
    
    # Join parts
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    shoulder.select_set(True)
    neck.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    
    bottle = bpy.context.active_object
    bottle.name = name
    bpy.ops.object.shade_smooth()
    
    result['bottle'] = bottle
    
    # Glass material
    glass_mat = bpy.data.materials.new(f"{name}_GlassMat")
    glass_mat.use_nodes = True
    glass_mat.blend_method = 'BLEND'
    bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*glass_color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['IOR'].default_value = 1.52
    bsdf.inputs['Transmission Weight'].default_value = 0.95
    bottle.data.materials.append(glass_mat)
    
    result['material'] = glass_mat
    
    # Cap/Cork
    cap = _create_bottle_cap(
        location[0], location[1],
        location[2] + height + 0.005,
        neck_radius, style, name
    )
    result['cap'] = cap
    
    return result


def _create_bottle_cap(
    x: float, y: float, z: float,
    radius: float, style: str, name: str
) -> bpy.types.Object:
    """Create bottle cap or cork."""
    if style == 'WINE':
        # Cork
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius * 0.9,
            depth=0.025,
            location=(x, y, z)
        )
        cap = bpy.context.active_object
        cap.name = f"{name}_Cork"
        
        mat = bpy.data.materials.new(f"{name}_CorkMat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.6, 0.5, 0.35, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.9
        cap.data.materials.append(mat)
    else:
        # Metal cap
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius * 1.2,
            depth=0.015,
            location=(x, y, z)
        )
        cap = bpy.context.active_object
        cap.name = f"{name}_Cap"
        
        mat = bpy.data.materials.new(f"{name}_CapMat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.75, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.3
        cap.data.materials.append(mat)
    
    return cap


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_bottle(style='WINE', location=(0, 0, 0))
    create_bottle(style='BEER', glass_color=(0.3, 0.25, 0.1), location=(0.15, 0, 0))
    create_bottle(style='SODA', glass_color=(0.1, 0.1, 0.1), location=(0.3, 0, 0))
    
    print("Created 3 bottle types")
