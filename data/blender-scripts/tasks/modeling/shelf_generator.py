"""
{
  "title": "Shelf Unit Generator",
  "category": "modeling",
  "subcategory": "furniture",
  "tags": ["shelf", "bookshelf", "storage", "furniture", "interior"],
  "difficulty": "intermediate",
  "description": "Generates shelf units and bookcases with adjustable shelves.",
  "blender_version": "3.0+",
  "estimated_objects": 8
}
"""
import bpy


def create_shelf_unit(
    width: float = 0.8,
    depth: float = 0.3,
    height: float = 1.8,
    shelf_count: int = 5,
    with_back: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "ShelfUnit"
) -> dict:
    """
    Create a shelf unit/bookcase.
    
    Args:
        width: Unit width
        depth: Unit depth
        height: Total height
        shelf_count: Number of shelves (including top/bottom)
        with_back: Add back panel
        location: Position
        name: Object name
    
    Returns:
        Dictionary with shelf parts
    """
    result = {}
    
    panel_thickness = 0.02
    
    # === SIDE PANELS ===
    sides = []
    for side, offset in [('L', -width/2 + panel_thickness/2), 
                          ('R', width/2 - panel_thickness/2)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + offset,
            location[1],
            location[2] + height/2
        ))
        panel = bpy.context.active_object
        panel.name = f"{name}_Side_{side}"
        panel.scale = (panel_thickness/2, depth/2, height/2)
        bpy.ops.object.transform_apply(scale=True)
        sides.append(panel)
    
    result['sides'] = sides
    
    # === SHELVES ===
    shelves = []
    shelf_spacing = height / (shelf_count - 1)
    inner_width = width - panel_thickness * 2
    
    for i in range(shelf_count):
        shelf_z = location[2] + i * shelf_spacing + panel_thickness/2
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0],
            location[1],
            shelf_z
        ))
        shelf = bpy.context.active_object
        shelf.name = f"{name}_Shelf_{i+1}"
        shelf.scale = (inner_width/2, depth/2, panel_thickness/2)
        bpy.ops.object.transform_apply(scale=True)
        shelves.append(shelf)
    
    result['shelves'] = shelves
    
    # === BACK PANEL ===
    if with_back:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0],
            location[1] + depth/2 - panel_thickness/2,
            location[2] + height/2
        ))
        back = bpy.context.active_object
        back.name = f"{name}_Back"
        back.scale = (width/2, panel_thickness/2, height/2)
        bpy.ops.object.transform_apply(scale=True)
        result['back'] = back
    
    # === MATERIAL ===
    mat = bpy.data.materials.new(f"{name}_WoodMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.4, 0.28, 0.15, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    
    all_parts = sides + shelves
    if with_back:
        all_parts.append(result['back'])
    
    for part in all_parts:
        part.data.materials.append(mat)
    
    result['material'] = mat
    
    return result


def create_wall_shelf(
    width: float = 1.0,
    depth: float = 0.2,
    thickness: float = 0.03,
    bracket_style: str = 'HIDDEN',
    location: tuple = (0, 0, 1.5),
    name: str = "WallShelf"
) -> dict:
    """Create a floating wall shelf."""
    result = {}
    
    # Shelf
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    shelf = bpy.context.active_object
    shelf.name = name
    shelf.scale = (width/2, depth/2, thickness/2)
    bpy.ops.object.transform_apply(scale=True)
    result['shelf'] = shelf
    
    # Brackets
    if bracket_style == 'L_BRACKET':
        for side, offset in [('L', -width/3), ('R', width/3)]:
            # Horizontal part
            bpy.ops.mesh.primitive_cube_add(size=1, location=(
                location[0] + offset,
                location[1] + depth/4,
                location[2] - thickness
            ))
            h_bracket = bpy.context.active_object
            h_bracket.scale = (0.015, depth/4, 0.015)
            bpy.ops.object.transform_apply(scale=True)
            
            # Vertical part
            bpy.ops.mesh.primitive_cube_add(size=1, location=(
                location[0] + offset,
                location[1] + depth/2 - 0.01,
                location[2] - thickness - 0.05
            ))
            v_bracket = bpy.context.active_object
            v_bracket.scale = (0.015, 0.015, 0.05)
            bpy.ops.object.transform_apply(scale=True)
    
    # Material
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.35, 0.25, 0.12, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.5
    shelf.data.materials.append(mat)
    
    result['material'] = mat
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_shelf_unit(location=(0, 0, 0))
    create_wall_shelf(location=(2, 0, 1.2), bracket_style='L_BRACKET')
    
    print("Created shelf unit and wall shelf")
