"""
{
  "title": "Scroll Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["scroll", "paper", "parchment", "fantasy", "medieval", "props"],
  "difficulty": "beginner",
  "description": "Generates scrolls and parchment props.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math


def create_scroll(
    length: float = 0.25,
    width: float = 0.15,
    roll_radius: float = 0.015,
    unrolled: float = 0.5,
    with_ribbon: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Scroll"
) -> dict:
    """
    Create a scroll.
    
    Args:
        length: Scroll length
        width: Paper width when unrolled
        roll_radius: Roll thickness
        unrolled: How much is unrolled (0-1)
        with_ribbon: Add decorative ribbon
        location: Position
        name: Object name
    
    Returns:
        Dictionary with scroll parts
    """
    result = {}
    
    unrolled_length = width * unrolled
    rolled_length = width * (1 - unrolled) * 0.3
    
    # === UNROLLED PART ===
    if unrolled > 0.1:
        bpy.ops.mesh.primitive_plane_add(
            size=1,
            location=(location[0], location[1], location[2] + 0.001)
        )
        paper = bpy.context.active_object
        paper.name = f"{name}_Paper"
        paper.scale = (unrolled_length/2, length/2, 1)
        bpy.ops.object.transform_apply(scale=True)
        
        # Slight curve
        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
        paper.modifiers["SimpleDeform"].deform_method = 'BEND'
        paper.modifiers["SimpleDeform"].angle = 0.1
        
        # Paper material
        paper_mat = bpy.data.materials.new(f"{name}_PaperMat")
        paper_mat.use_nodes = True
        bsdf = paper_mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.9, 0.85, 0.7, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8
        paper.data.materials.append(paper_mat)
        
        result['paper'] = paper
    
    # === ROLLS ===
    # Main roll
    bpy.ops.mesh.primitive_cylinder_add(
        radius=roll_radius,
        depth=length,
        location=(
            location[0] + unrolled_length/2 + roll_radius,
            location[1],
            location[2] + roll_radius
        )
    )
    roll = bpy.context.active_object
    roll.name = f"{name}_Roll"
    roll.rotation_euler.x = math.radians(90)
    
    roll_mat = bpy.data.materials.new(f"{name}_RollMat")
    roll_mat.use_nodes = True
    bsdf = roll_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.85, 0.8, 0.65, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    roll.data.materials.append(roll_mat)
    
    result['roll'] = roll
    
    # Second roll if partially unrolled
    if unrolled > 0.1 and unrolled < 0.9:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=roll_radius * 0.7,
            depth=length,
            location=(
                location[0] - unrolled_length/2 - roll_radius * 0.7,
                location[1],
                location[2] + roll_radius * 0.7
            )
        )
        roll2 = bpy.context.active_object
        roll2.name = f"{name}_Roll2"
        roll2.rotation_euler.x = math.radians(90)
        roll2.data.materials.append(roll_mat)
        result['roll2'] = roll2
    
    # === RIBBON ===
    if with_ribbon and unrolled < 0.3:
        ribbon = _create_scroll_ribbon(
            roll_radius, length, location, name
        )
        result['ribbon'] = ribbon
    
    return result


def _create_scroll_ribbon(
    radius: float,
    length: float,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create decorative ribbon."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius * 1.3,
        depth=length * 0.1,
        location=(location[0], location[1], location[2] + radius)
    )
    ribbon = bpy.context.active_object
    ribbon.name = f"{name}_Ribbon"
    ribbon.rotation_euler.x = math.radians(90)
    
    mat = bpy.data.materials.new(f"{name}_RibbonMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.6, 0.1, 0.1, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.5
    ribbon.data.materials.append(mat)
    
    return ribbon


def create_book_page(
    width: float = 0.15,
    height: float = 0.2,
    curl: float = 0.1,
    location: tuple = (0, 0, 0),
    name: str = "Page"
) -> bpy.types.Object:
    """Create a single loose page."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(
        location[0], location[1], location[2]
    ))
    page = bpy.context.active_object
    page.name = name
    page.scale = (width/2, height/2, 1)
    bpy.ops.object.transform_apply(scale=True)
    
    # Subdivide for curl
    bpy.ops.object.modifier_add(type='SUBSURF')
    page.modifiers["Subdivision"].levels = 3
    
    # Curl corners
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    page.modifiers["SimpleDeform"].deform_method = 'BEND'
    page.modifiers["SimpleDeform"].angle = curl
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.95, 0.93, 0.88, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    page.data.materials.append(mat)
    
    return page


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_scroll(unrolled=0.0, location=(0, 0, 0))
    create_scroll(unrolled=0.7, location=(0.3, 0, 0))
    create_book_page(location=(0.6, 0, 0))
    
    print("Created scrolls and pages")
