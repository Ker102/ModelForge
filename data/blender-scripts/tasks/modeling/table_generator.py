"""
{
  "title": "Procedural Table Generator",
  "category": "modeling",
  "subcategory": "furniture",
  "tags": ["table", "furniture", "procedural", "interior", "props"],
  "difficulty": "beginner",
  "description": "Generates various table types with customizable dimensions.",
  "blender_version": "3.0+",
  "estimated_objects": 5
}
"""
import bpy
import math


def create_table(
    table_type: str = 'DINING',
    width: float = 1.5,
    depth: float = 0.9,
    height: float = 0.75,
    leg_style: str = 'SQUARE',
    location: tuple = (0, 0, 0),
    name: str = "Table"
) -> dict:
    """
    Create a procedural table.
    
    Args:
        table_type: 'DINING', 'COFFEE', 'DESK', 'ROUND'
        width: Table width (X)
        depth: Table depth (Y)
        height: Table height
        leg_style: 'SQUARE', 'ROUND', 'TAPERED'
        location: Position
        name: Object name
    
    Returns:
        Dictionary with table parts
    """
    result = {}
    
    # Adjust for table type
    if table_type == 'COFFEE':
        height = 0.45
    elif table_type == 'DESK':
        depth = 0.7
    elif table_type == 'ROUND':
        depth = width  # Make circular
    
    top_thickness = 0.04
    
    # === TABLE TOP ===
    if table_type == 'ROUND':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=width/2,
            depth=top_thickness,
            location=(location[0], location[1], location[2] + height - top_thickness/2)
        )
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0], location[1], location[2] + height - top_thickness/2
        ))
        bpy.context.active_object.scale = (width/2, depth/2, top_thickness/2)
        bpy.ops.object.transform_apply(scale=True)
    
    top = bpy.context.active_object
    top.name = f"{name}_Top"
    result['top'] = top
    
    # === LEGS ===
    leg_inset = 0.08
    leg_size = 0.05
    leg_height = height - top_thickness
    
    if table_type == 'ROUND':
        # 4 legs in circular pattern
        leg_positions = [
            (math.cos(a) * (width/2 - leg_inset), math.sin(a) * (width/2 - leg_inset))
            for a in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]
        ]
    else:
        leg_positions = [
            (-width/2 + leg_inset, -depth/2 + leg_inset),
            (width/2 - leg_inset, -depth/2 + leg_inset),
            (-width/2 + leg_inset, depth/2 - leg_inset),
            (width/2 - leg_inset, depth/2 - leg_inset)
        ]
    
    legs = []
    for i, (lx, ly) in enumerate(leg_positions):
        if leg_style == 'ROUND':
            bpy.ops.mesh.primitive_cylinder_add(
                radius=leg_size,
                depth=leg_height,
                location=(location[0] + lx, location[1] + ly, location[2] + leg_height/2)
            )
        elif leg_style == 'TAPERED':
            bpy.ops.mesh.primitive_cone_add(
                radius1=leg_size * 1.5,
                radius2=leg_size * 0.8,
                depth=leg_height,
                location=(location[0] + lx, location[1] + ly, location[2] + leg_height/2)
            )
        else:  # SQUARE
            bpy.ops.mesh.primitive_cube_add(size=1, location=(
                location[0] + lx, location[1] + ly, location[2] + leg_height/2
            ))
            bpy.context.active_object.scale = (leg_size, leg_size, leg_height/2)
            bpy.ops.object.transform_apply(scale=True)
        
        leg = bpy.context.active_object
        leg.name = f"{name}_Leg_{i+1}"
        legs.append(leg)
    
    result['legs'] = legs
    
    # === MATERIAL ===
    mat = bpy.data.materials.new(f"{name}_WoodMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.35, 0.22, 0.1, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.5
    
    top.data.materials.append(mat)
    for leg in legs:
        leg.data.materials.append(mat)
    
    result['material'] = mat
    
    return result


def create_desk_with_drawers(
    width: float = 1.4,
    depth: float = 0.7,
    height: float = 0.75,
    drawer_count: int = 2,
    location: tuple = (0, 0, 0),
    name: str = "Desk"
) -> dict:
    """Create a desk with drawer unit."""
    result = create_table(
        table_type='DESK',
        width=width,
        depth=depth,
        height=height,
        location=location,
        name=name
    )
    
    # Add drawer unit on one side
    drawer_width = width * 0.35
    drawer_height = (height - 0.1) / drawer_count
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0] - width/2 + drawer_width/2 + 0.05,
        location[1],
        location[2] + height/2 - 0.02
    ))
    drawer_unit = bpy.context.active_object
    drawer_unit.name = f"{name}_DrawerUnit"
    drawer_unit.scale = (drawer_width/2, depth/2 - 0.03, height/2 - 0.05)
    bpy.ops.object.transform_apply(scale=True)
    
    result['drawer_unit'] = drawer_unit
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_table('DINING', location=(0, 0, 0))
    create_table('COFFEE', location=(3, 0, 0))
    create_table('ROUND', leg_style='ROUND', location=(-3, 0, 0))
    
    print("Created 3 table variations")
