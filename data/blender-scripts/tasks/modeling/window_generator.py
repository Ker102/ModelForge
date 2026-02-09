"""
{
  "title": "Window Generator",
  "category": "modeling",
  "subcategory": "architecture",
  "tags": ["window", "architecture", "glass", "building", "interior"],
  "difficulty": "intermediate",
  "description": "Generates various window types with frames and glass panes.",
  "blender_version": "3.0+",
  "estimated_objects": 6
}
"""
import bpy


def create_window(
    width: float = 1.0,
    height: float = 1.2,
    frame_depth: float = 0.1,
    panes_x: int = 2,
    panes_y: int = 2,
    style: str = 'STANDARD',
    location: tuple = (0, 0, 0),
    name: str = "Window"
) -> dict:
    """
    Create a window with frame and glass.
    
    Args:
        width: Window width
        height: Window height
        frame_depth: Frame thickness
        panes_x: Horizontal pane divisions
        panes_y: Vertical pane divisions
        style: 'STANDARD', 'ARCHED', 'CIRCULAR'
        location: Position
        name: Object name
    
    Returns:
        Dictionary with window parts
    """
    result = {}
    frame_width = 0.05
    
    # === OUTER FRAME ===
    frame_parts = _create_window_frame(
        width, height, frame_width, frame_depth, 
        location, name, style
    )
    result['frame'] = frame_parts
    
    # === GLASS PANES ===
    inner_w = width - frame_width * 2
    inner_h = height - frame_width * 2
    pane_w = inner_w / panes_x
    pane_h = inner_h / panes_y
    
    glass_mat = bpy.data.materials.new(f"{name}_GlassMat")
    glass_mat.blend_method = 'BLEND'
    bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 1.0)
    bsdf.inputs['Transmission Weight'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.5
    
    panes = []
    divider_w = 0.02
    
    for px in range(panes_x):
        for py in range(panes_y):
            pane_center_x = location[0] - inner_w/2 + pane_w/2 + px * pane_w
            pane_center_z = location[2] - inner_h/2 + pane_h/2 + py * pane_h
            
            actual_w = pane_w - divider_w if panes_x > 1 else pane_w
            actual_h = pane_h - divider_w if panes_y > 1 else pane_h
            
            bpy.ops.mesh.primitive_plane_add(size=1, location=(
                pane_center_x,
                location[1],
                pane_center_z
            ))
            pane = bpy.context.active_object
            pane.name = f"{name}_Glass_{px}_{py}"
            pane.scale = (actual_w/2, 1, actual_h/2)
            pane.rotation_euler.x = 1.5708
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            pane.data.materials.append(glass_mat)
            panes.append(pane)
    
    result['glass'] = panes
    
    # === DIVIDERS ===
    if panes_x > 1 or panes_y > 1:
        dividers = _create_dividers(
            width, height, frame_width, panes_x, panes_y,
            location, name
        )
        result['dividers'] = dividers
    
    return result


def _create_window_frame(
    width: float,
    height: float,
    frame_width: float,
    frame_depth: float,
    location: tuple,
    name: str,
    style: str
) -> list:
    """Create window frame."""
    parts = []
    
    frame_mat = bpy.data.materials.new(f"{name}_FrameMat")
    bsdf = frame_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.93, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    
    # Top
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1],
        location[2] + height/2 - frame_width/2
    ))
    top = bpy.context.active_object
    top.name = f"{name}_Frame_Top"
    top.scale = (width/2, frame_depth/2, frame_width/2)
    bpy.ops.object.transform_apply(scale=True)
    top.data.materials.append(frame_mat)
    parts.append(top)
    
    # Bottom
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1],
        location[2] - height/2 + frame_width/2
    ))
    bottom = bpy.context.active_object
    bottom.name = f"{name}_Frame_Bottom"
    bottom.scale = (width/2, frame_depth/2, frame_width/2)
    bpy.ops.object.transform_apply(scale=True)
    bottom.data.materials.append(frame_mat)
    parts.append(bottom)
    
    # Sides
    inner_h = height - frame_width * 2
    for side, offset in [('L', -1), ('R', 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + offset * (width/2 - frame_width/2),
            location[1],
            location[2]
        ))
        side_frame = bpy.context.active_object
        side_frame.name = f"{name}_Frame_{side}"
        side_frame.scale = (frame_width/2, frame_depth/2, inner_h/2)
        bpy.ops.object.transform_apply(scale=True)
        side_frame.data.materials.append(frame_mat)
        parts.append(side_frame)
    
    return parts


def _create_dividers(
    width: float,
    height: float,
    frame_width: float,
    panes_x: int,
    panes_y: int,
    location: tuple,
    name: str
) -> list:
    """Create window dividers."""
    dividers = []
    inner_w = width - frame_width * 2
    inner_h = height - frame_width * 2
    divider_size = 0.015
    
    divider_mat = bpy.data.materials.get(f"{name}_FrameMat")
    
    # Vertical dividers
    if panes_x > 1:
        pane_w = inner_w / panes_x
        for i in range(1, panes_x):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(
                location[0] - inner_w/2 + i * pane_w,
                location[1],
                location[2]
            ))
            div = bpy.context.active_object
            div.name = f"{name}_DivV_{i}"
            div.scale = (divider_size, divider_size, inner_h/2)
            bpy.ops.object.transform_apply(scale=True)
            if divider_mat:
                div.data.materials.append(divider_mat)
            dividers.append(div)
    
    # Horizontal dividers
    if panes_y > 1:
        pane_h = inner_h / panes_y
        for i in range(1, panes_y):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(
                location[0],
                location[1],
                location[2] - inner_h/2 + i * pane_h
            ))
            div = bpy.context.active_object
            div.name = f"{name}_DivH_{i}"
            div.scale = (inner_w/2, divider_size, divider_size)
            bpy.ops.object.transform_apply(scale=True)
            if divider_mat:
                div.data.materials.append(divider_mat)
            dividers.append(div)
    
    return dividers


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_window(panes_x=1, panes_y=1, location=(0, 0, 1))
    create_window(panes_x=2, panes_y=3, location=(1.5, 0, 1))
    
    print("Created 2 window variations")
