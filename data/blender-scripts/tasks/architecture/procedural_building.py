"""
{
  "title": "Procedural Building Generator",
  "category": "architecture",
  "subcategory": "buildings",
  "tags": ["building", "procedural", "architecture", "city", "skyscraper", "facade"],
  "difficulty": "intermediate",
  "description": "Creates a procedural building with customizable floors, windows, and facade details.",
  "blender_version": "3.0+",
  "estimated_objects": 5
}
"""
import bpy
import math
import random


def create_procedural_building(
    location: tuple = (0, 0, 0),
    width: float = 10.0,
    depth: float = 8.0,
    floors: int = 5,
    floor_height: float = 3.0,
    window_rows: int = 4,
    window_cols: int = 3,
    name_prefix: str = "Building"
) -> dict:
    """
    Create a procedural building with windows and details.
    
    Args:
        location: Base position (ground level)
        width: Building width (X axis)
        depth: Building depth (Y axis)
        floors: Number of floors
        floor_height: Height per floor in meters
        window_rows: Windows per floor (horizontal)
        window_cols: Window columns per side
        name_prefix: Prefix for object names
    
    Returns:
        Dictionary with building components
    
    Example:
        >>> building = create_procedural_building(floors=8, width=15)
    """
    created = {}
    bx, by, bz = location
    total_height = floors * floor_height
    
    # === MAIN BODY ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, bz + total_height / 2))
    body = bpy.context.active_object
    body.name = f"{name_prefix}_Body"
    body.scale = (width / 2, depth / 2, total_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Building material
    building_mat = bpy.data.materials.new(name=f"{name_prefix}_Facade")
    building_mat.use_nodes = True
    bsdf = building_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.7, 0.68, 0.65, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    body.data.materials.append(building_mat)
    created['body'] = body
    
    # === WINDOWS ===
    glass_mat = bpy.data.materials.new(name=f"{name_prefix}_Glass")
    glass_mat.use_nodes = True
    glass_bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
    glass_bsdf.inputs['Base Color'].default_value = (0.2, 0.3, 0.4, 1.0)
    glass_bsdf.inputs['Metallic'].default_value = 0.8
    glass_bsdf.inputs['Roughness'].default_value = 0.1
    
    windows = []
    window_width = (width * 0.8) / window_rows
    window_height = floor_height * 0.5
    
    for floor in range(floors):
        floor_z = bz + (floor * floor_height) + floor_height * 0.6
        
        for row in range(window_rows):
            window_x = bx - (width * 0.4) + (row + 0.5) * window_width
            
            # Front windows
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(window_x, by + depth / 2 + 0.01, floor_z)
            )
            win = bpy.context.active_object
            win.name = f"{name_prefix}_Window_F{floor}_R{row}"
            win.scale = (window_width * 0.7 / 2, 0.05, window_height / 2)
            win.data.materials.append(glass_mat)
            windows.append(win)
            
            # Back windows
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(window_x, by - depth / 2 - 0.01, floor_z)
            )
            win = bpy.context.active_object
            win.name = f"{name_prefix}_Window_B{floor}_R{row}"
            win.scale = (window_width * 0.7 / 2, 0.05, window_height / 2)
            win.data.materials.append(glass_mat)
            windows.append(win)
    
    created['windows'] = windows
    
    # === ROOF DETAILS ===
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(bx, by, bz + total_height + 0.3)
    )
    roof_edge = bpy.context.active_object
    roof_edge.name = f"{name_prefix}_RoofEdge"
    roof_edge.scale = (width / 2 + 0.2, depth / 2 + 0.2, 0.3)
    
    roof_mat = bpy.data.materials.new(name=f"{name_prefix}_Concrete")
    roof_mat.use_nodes = True
    roof_bsdf = roof_mat.node_tree.nodes.get("Principled BSDF")
    roof_bsdf.inputs['Base Color'].default_value = (0.4, 0.4, 0.4, 1.0)
    roof_bsdf.inputs['Roughness'].default_value = 0.9
    roof_edge.data.materials.append(roof_mat)
    created['roof'] = roof_edge
    
    # === ENTRANCE ===
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(bx, by + depth / 2 + 0.5, bz + 1.5)
    )
    entrance = bpy.context.active_object
    entrance.name = f"{name_prefix}_Entrance"
    entrance.scale = (2.0, 0.5, 1.5)
    entrance.data.materials.append(glass_mat)
    created['entrance'] = entrance
    
    return created


def create_window_array(
    wall_object: bpy.types.Object,
    rows: int = 3,
    cols: int = 2,
    window_size: tuple = (1.0, 1.5),
    spacing: tuple = (0.5, 0.3)
) -> list:
    """
    Create an array of windows on a wall surface.
    
    Args:
        wall_object: The wall to add windows to
        rows: Number of horizontal windows
        cols: Number of vertical rows
        window_size: (width, height) of each window
        spacing: (horizontal, vertical) spacing between windows
    
    Returns:
        List of created window objects
    """
    windows = []
    wall_dims = wall_object.dimensions
    wall_loc = wall_object.location
    
    total_width = rows * (window_size[0] + spacing[0]) - spacing[0]
    total_height = cols * (window_size[1] + spacing[1]) - spacing[1]
    
    start_x = wall_loc.x - total_width / 2 + window_size[0] / 2
    start_z = wall_loc.z - total_height / 2 + window_size[1] / 2
    
    for row in range(rows):
        for col in range(cols):
            x = start_x + row * (window_size[0] + spacing[0])
            z = start_z + col * (window_size[1] + spacing[1])
            
            bpy.ops.mesh.primitive_plane_add(
                size=1,
                location=(x, wall_loc.y + wall_dims.y / 2 + 0.01, z)
            )
            window = bpy.context.active_object
            window.scale = (window_size[0] / 2, 1, window_size[1] / 2)
            window.rotation_euler[0] = math.radians(90)
            windows.append(window)
    
    return windows


# Standalone execution
if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    building = create_procedural_building(
        location=(0, 0, 0),
        floors=6,
        width=12,
        depth=10,
        window_rows=5
    )
    print(f"Created building with {len(building)} component groups")
