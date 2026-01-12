"""
{
  "title": "Ladder Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["ladder", "climbing", "props", "construction", "utility"],
  "difficulty": "beginner",
  "description": "Generates ladders for environments and props.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy


def create_ladder(
    height: float = 2.0,
    width: float = 0.4,
    rung_spacing: float = 0.25,
    style: str = 'WOODEN',
    location: tuple = (0, 0, 0),
    name: str = "Ladder"
) -> dict:
    """
    Create a ladder.
    
    Args:
        height: Ladder height
        width: Ladder width
        rung_spacing: Distance between rungs
        style: 'WOODEN', 'METAL', 'ROPE'
        location: Position
        name: Object name
    
    Returns:
        Dictionary with ladder parts
    """
    result = {}
    parts = []
    
    rail_radius = 0.02 if style == 'METAL' else 0.025
    rung_radius = 0.015 if style == 'METAL' else 0.02
    
    # Materials
    if style == 'WOODEN':
        mat = bpy.data.materials.new(f"{name}_Mat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.4, 0.3, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8
    elif style == 'METAL':
        mat = bpy.data.materials.new(f"{name}_Mat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.52, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.4
    else:  # ROPE
        mat = bpy.data.materials.new(f"{name}_Mat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.6, 0.5, 0.35, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.9
    
    # Side rails
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=rail_radius,
            depth=height,
            location=(
                location[0] + side * width/2,
                location[1],
                location[2] + height/2
            )
        )
        rail = bpy.context.active_object
        rail.name = f"{name}_Rail_{'L' if side < 0 else 'R'}"
        rail.data.materials.append(mat)
        parts.append(rail)
    
    result['rails'] = parts[:2]
    
    # Rungs
    rungs = []
    rung_count = int(height / rung_spacing)
    
    for i in range(rung_count):
        rung_z = location[2] + rung_spacing * (i + 0.5)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=rung_radius,
            depth=width,
            location=(location[0], location[1], rung_z)
        )
        rung = bpy.context.active_object
        rung.name = f"{name}_Rung_{i}"
        rung.rotation_euler.y = 1.5708
        rung.data.materials.append(mat)
        rungs.append(rung)
        parts.append(rung)
    
    result['rungs'] = rungs
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_ladder(style='WOODEN', location=(0, 0, 0))
    create_ladder(style='METAL', location=(0.6, 0, 0))
    
    print("Created ladders")
