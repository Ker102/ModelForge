"""
{
  "title": "Chair Generator",
  "category": "modeling",
  "subcategory": "furniture",
  "tags": ["chair", "furniture", "procedural", "interior", "seating"],
  "difficulty": "intermediate",
  "description": "Generates various chair types with customizable dimensions.",
  "blender_version": "3.0+",
  "estimated_objects": 6
}
"""
import bpy
import math


def create_chair(
    chair_type: str = 'DINING',
    seat_width: float = 0.45,
    seat_depth: float = 0.42,
    seat_height: float = 0.45,
    back_height: float = 0.45,
    location: tuple = (0, 0, 0),
    name: str = "Chair"
) -> dict:
    """
    Create a procedural chair.
    
    Args:
        chair_type: 'DINING', 'OFFICE', 'STOOL', 'ARMCHAIR'
        seat_width: Seat width
        seat_depth: Seat depth
        seat_height: Height from floor to seat
        back_height: Backrest height (0 for stool)
        location: Position
        name: Object name
    
    Returns:
        Dictionary with chair parts
    """
    result = {}
    
    if chair_type == 'STOOL':
        back_height = 0
    elif chair_type == 'ARMCHAIR':
        seat_width = 0.6
        seat_depth = 0.55
    
    seat_thickness = 0.05
    leg_size = 0.04
    
    # === SEAT ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0], location[1], location[2] + seat_height
    ))
    seat = bpy.context.active_object
    seat.name = f"{name}_Seat"
    seat.scale = (seat_width/2, seat_depth/2, seat_thickness/2)
    bpy.ops.object.transform_apply(scale=True)
    result['seat'] = seat
    
    # === LEGS ===
    leg_inset = 0.05
    legs = []
    
    leg_positions = [
        (-seat_width/2 + leg_inset, -seat_depth/2 + leg_inset),
        (seat_width/2 - leg_inset, -seat_depth/2 + leg_inset),
        (-seat_width/2 + leg_inset, seat_depth/2 - leg_inset),
        (seat_width/2 - leg_inset, seat_depth/2 - leg_inset)
    ]
    
    for i, (lx, ly) in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=leg_size,
            depth=seat_height,
            location=(location[0] + lx, location[1] + ly, location[2] + seat_height/2)
        )
        leg = bpy.context.active_object
        leg.name = f"{name}_Leg_{i+1}"
        legs.append(leg)
    
    result['legs'] = legs
    
    # === BACKREST ===
    if back_height > 0:
        back_thickness = 0.03
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0],
            location[1] + seat_depth/2 - back_thickness/2,
            location[2] + seat_height + back_height/2
        ))
        backrest = bpy.context.active_object
        backrest.name = f"{name}_Back"
        backrest.scale = (seat_width/2 - 0.02, back_thickness/2, back_height/2)
        bpy.ops.object.transform_apply(scale=True)
        result['backrest'] = backrest
        
        # Back supports
        for side in [-1, 1]:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=leg_size * 0.8,
                depth=back_height,
                location=(
                    location[0] + side * (seat_width/2 - leg_inset),
                    location[1] + seat_depth/2 - leg_inset,
                    location[2] + seat_height + back_height/2
                )
            )
            support = bpy.context.active_object
            support.name = f"{name}_BackSupport_{side}"
    
    # === ARMRESTS ===
    if chair_type == 'ARMCHAIR':
        arm_height = 0.25
        arm_width = 0.06
        
        for side, offset in [('L', -1), ('R', 1)]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(
                location[0] + offset * (seat_width/2 + arm_width/2),
                location[1],
                location[2] + seat_height + arm_height/2
            ))
            armrest = bpy.context.active_object
            armrest.name = f"{name}_Armrest_{side}"
            armrest.scale = (arm_width/2, seat_depth/2, arm_height/2)
            bpy.ops.object.transform_apply(scale=True)
    
    # === MATERIAL ===
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.18, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.45
    
    for obj in result.values():
        if isinstance(obj, bpy.types.Object):
            obj.data.materials.append(mat)
        elif isinstance(obj, list):
            for o in obj:
                o.data.materials.append(mat)
    
    result['material'] = mat
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_chair('DINING', location=(0, 0, 0))
    create_chair('STOOL', location=(1.5, 0, 0))
    create_chair('ARMCHAIR', location=(-1.5, 0, 0))
    
    print("Created 3 chair variations")
