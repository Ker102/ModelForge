"""
{
  "title": "Door Generator",
  "category": "modeling",
  "subcategory": "architecture",
  "tags": ["door", "architecture", "interior", "building", "procedural"],
  "difficulty": "beginner",
  "description": "Generates various door types with frames and handles.",
  "blender_version": "3.0+",
  "estimated_objects": 4
}
"""
import bpy
import math


def create_door(
    width: float = 0.9,
    height: float = 2.1,
    thickness: float = 0.04,
    style: str = 'PANEL',
    with_frame: bool = True,
    with_handle: bool = True,
    open_angle: float = 0,
    location: tuple = (0, 0, 0),
    name: str = "Door"
) -> dict:
    """
    Create a door with optional frame and handle.
    
    Args:
        width: Door width
        height: Door height
        thickness: Door thickness
        style: 'FLAT', 'PANEL', 'GLASS'
        with_frame: Add door frame
        with_handle: Add door handle
        open_angle: Opening angle in degrees
        location: Position
        name: Object name
    
    Returns:
        Dictionary with door parts
    """
    result = {}
    
    # === DOOR PANEL ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1],
        location[2] + height/2
    ))
    door = bpy.context.active_object
    door.name = name
    door.scale = (width/2, thickness/2, height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Set origin to hinge side
    bpy.context.scene.cursor.location = (
        location[0] - width/2,
        location[1],
        location[2]
    )
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    # Apply opening angle
    door.rotation_euler.z = math.radians(open_angle)
    
    result['door'] = door
    
    # === PANEL DETAILS ===
    if style == 'PANEL':
        # Add beveled panels
        bpy.ops.object.modifier_add(type='BEVEL')
        door.modifiers["Bevel"].width = 0.01
        door.modifiers["Bevel"].segments = 2
    
    elif style == 'GLASS':
        # Add glass window
        window_height = height * 0.4
        window_y = height * 0.6
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0],
            location[1] - thickness * 0.3,
            location[2] + window_y
        ))
        window = bpy.context.active_object
        window.name = f"{name}_Window"
        window.scale = (width * 0.35, thickness * 0.1, window_height/2)
        bpy.ops.object.transform_apply(scale=True)
        
        # Glass material
        glass_mat = bpy.data.materials.new(f"{name}_GlassMat")
        glass_mat.use_nodes = True
        bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Transmission Weight'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.05
        window.data.materials.append(glass_mat)
        
        result['window'] = window
    
    # === DOOR MATERIAL ===
    door_mat = bpy.data.materials.new(f"{name}_Mat")
    door_mat.use_nodes = True
    bsdf = door_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.35, 0.25, 0.15, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    door.data.materials.append(door_mat)
    
    # === FRAME ===
    if with_frame:
        frame = _create_door_frame(width, height, location, name)
        result['frame'] = frame
    
    # === HANDLE ===
    if with_handle:
        handle = _create_door_handle(width, height, thickness, location, name)
        result['handle'] = handle
    
    return result


def _create_door_frame(
    width: float,
    height: float,
    location: tuple,
    name: str
) -> list:
    """Create door frame."""
    frame_width = 0.08
    frame_depth = 0.1
    frame_parts = []
    
    frame_mat = bpy.data.materials.new(f"{name}_FrameMat")
    frame_mat.use_nodes = True
    bsdf = frame_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.88, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    
    # Top
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1],
        location[2] + height + frame_width/2
    ))
    top = bpy.context.active_object
    top.name = f"{name}_Frame_Top"
    top.scale = ((width + frame_width*2)/2, frame_depth/2, frame_width/2)
    bpy.ops.object.transform_apply(scale=True)
    top.data.materials.append(frame_mat)
    frame_parts.append(top)
    
    # Sides
    for side, offset in [('L', -1), ('R', 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + offset * (width/2 + frame_width/2),
            location[1],
            location[2] + height/2
        ))
        side_frame = bpy.context.active_object
        side_frame.name = f"{name}_Frame_{side}"
        side_frame.scale = (frame_width/2, frame_depth/2, height/2)
        bpy.ops.object.transform_apply(scale=True)
        side_frame.data.materials.append(frame_mat)
        frame_parts.append(side_frame)
    
    return frame_parts


def _create_door_handle(
    width: float,
    height: float,
    thickness: float,
    location: tuple,
    name: str
) -> bpy.types.Object:
    """Create door handle."""
    handle_height = height * 0.45
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.02,
        depth=0.08,
        location=(
            location[0] + width * 0.35,
            location[1] - thickness/2 - 0.04,
            location[2] + handle_height
        )
    )
    handle = bpy.context.active_object
    handle.name = f"{name}_Handle"
    handle.rotation_euler.x = math.radians(90)
    
    handle_mat = bpy.data.materials.new(f"{name}_HandleMat")
    handle_mat.use_nodes = True
    bsdf = handle_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.6, 0.55, 0.4, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.25
    handle.data.materials.append(handle_mat)
    
    return handle


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_door(style='FLAT', location=(0, 0, 0))
    create_door(style='PANEL', location=(1.5, 0, 0))
    create_door(style='GLASS', open_angle=45, location=(3, 0, 0))
    
    print("Created 3 door variations")
