"""
{
  "title": "Interior Room Generator",
  "category": "architecture",
  "subcategory": "interior",
  "tags": ["room", "interior", "walls", "floor", "ceiling", "door", "window", "architecture"],
  "difficulty": "intermediate",
  "description": "Creates a basic interior room with walls, floor, ceiling, and optional door/window openings.",
  "blender_version": "3.0+",
  "estimated_objects": 6
}
"""
import bpy
import math


def create_interior_room(
    width: float = 5.0,
    depth: float = 4.0,
    height: float = 2.8,
    wall_thickness: float = 0.15,
    location: tuple = (0, 0, 0),
    add_floor: bool = True,
    add_ceiling: bool = True,
    floor_material: str = 'WOOD',
    wall_color: tuple = (0.9, 0.9, 0.88),
    name_prefix: str = "Room"
) -> dict:
    """
    Create a basic interior room.
    
    Args:
        width: Room width (X axis)
        depth: Room depth (Y axis)
        height: Room height (Z axis)
        wall_thickness: Wall thickness
        location: Room base position
        add_floor: Create floor
        add_ceiling: Create ceiling
        floor_material: 'WOOD', 'TILE', 'CARPET', 'CONCRETE'
        wall_color: RGB wall color
        name_prefix: Prefix for object names
    
    Returns:
        Dictionary with all created objects
    
    Example:
        >>> room = create_interior_room(width=6, depth=5, height=3)
    """
    result = {}
    bx, by, bz = location
    
    # === WALLS ===
    walls = _create_walls(width, depth, height, wall_thickness, location, wall_color, name_prefix)
    result.update(walls)
    
    # === FLOOR ===
    if add_floor:
        floor = _create_floor(width, depth, location, floor_material, name_prefix)
        result['floor'] = floor
    
    # === CEILING ===
    if add_ceiling:
        ceiling = _create_ceiling(width, depth, height, location, name_prefix)
        result['ceiling'] = ceiling
    
    return result


def _create_walls(
    width: float,
    depth: float,
    height: float,
    thickness: float,
    location: tuple,
    color: tuple,
    name_prefix: str
) -> dict:
    """Create the four walls."""
    walls = {}
    bx, by, bz = location
    
    # Wall material
    wall_mat = bpy.data.materials.new(f"{name_prefix}_WallMat")
    bsdf = wall_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    
    # Back wall (positive Y)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by + depth/2 - thickness/2, bz + height/2))
    back = bpy.context.active_object
    back.name = f"{name_prefix}_Wall_Back"
    back.scale = (width/2, thickness/2, height/2)
    bpy.ops.object.transform_apply(scale=True)
    back.data.materials.append(wall_mat)
    walls['back'] = back
    
    # Front wall (negative Y)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by - depth/2 + thickness/2, bz + height/2))
    front = bpy.context.active_object
    front.name = f"{name_prefix}_Wall_Front"
    front.scale = (width/2, thickness/2, height/2)
    bpy.ops.object.transform_apply(scale=True)
    front.data.materials.append(wall_mat)
    walls['front'] = front
    
    # Left wall (negative X)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx - width/2 + thickness/2, by, bz + height/2))
    left = bpy.context.active_object
    left.name = f"{name_prefix}_Wall_Left"
    left.scale = (thickness/2, depth/2, height/2)
    bpy.ops.object.transform_apply(scale=True)
    left.data.materials.append(wall_mat)
    walls['left'] = left
    
    # Right wall (positive X)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx + width/2 - thickness/2, by, bz + height/2))
    right = bpy.context.active_object
    right.name = f"{name_prefix}_Wall_Right"
    right.scale = (thickness/2, depth/2, height/2)
    bpy.ops.object.transform_apply(scale=True)
    right.data.materials.append(wall_mat)
    walls['right'] = right
    
    return walls


def _create_floor(
    width: float,
    depth: float,
    location: tuple,
    material_type: str,
    name_prefix: str
) -> bpy.types.Object:
    """Create floor with material."""
    bx, by, bz = location
    
    bpy.ops.mesh.primitive_plane_add(size=1, location=(bx, by, bz))
    floor = bpy.context.active_object
    floor.name = f"{name_prefix}_Floor"
    floor.scale = (width/2, depth/2, 1)
    bpy.ops.object.transform_apply(scale=True)
    
    # Floor material
    floor_mat = bpy.data.materials.new(f"{name_prefix}_FloorMat")
    nodes = floor_mat.node_tree.nodes
    links = floor_mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    
    materials = {
        'WOOD': {'color': (0.4, 0.25, 0.1, 1.0), 'roughness': 0.4},
        'TILE': {'color': (0.8, 0.8, 0.78, 1.0), 'roughness': 0.3},
        'CARPET': {'color': (0.3, 0.3, 0.35, 1.0), 'roughness': 0.95},
        'CONCRETE': {'color': (0.5, 0.5, 0.5, 1.0), 'roughness': 0.8}
    }
    
    mat_props = materials.get(material_type, materials['WOOD'])
    bsdf.inputs['Base Color'].default_value = mat_props['color']
    bsdf.inputs['Roughness'].default_value = mat_props['roughness']
    
    floor.data.materials.append(floor_mat)
    
    return floor


def _create_ceiling(
    width: float,
    depth: float,
    height: float,
    location: tuple,
    name_prefix: str
) -> bpy.types.Object:
    """Create ceiling."""
    bx, by, bz = location
    
    bpy.ops.mesh.primitive_plane_add(size=1, location=(bx, by, bz + height))
    ceiling = bpy.context.active_object
    ceiling.name = f"{name_prefix}_Ceiling"
    ceiling.scale = (width/2, depth/2, 1)
    ceiling.rotation_euler[0] = math.radians(180)  # Flip normals down
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    
    # Ceiling material
    ceiling_mat = bpy.data.materials.new(f"{name_prefix}_CeilingMat")
    bsdf = ceiling_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    
    ceiling.data.materials.append(ceiling_mat)
    
    return ceiling


def add_door_opening(
    wall: bpy.types.Object,
    door_width: float = 0.9,
    door_height: float = 2.1,
    position: float = 0.5,
    name: str = "DoorOpening"
) -> bpy.types.Object:
    """
    Add a door opening to a wall using boolean.
    
    Args:
        wall: Wall object to cut
        door_width: Door width
        door_height: Door height
        position: Horizontal position (0-1 along wall)
        name: Cutting object name
    
    Returns:
        The cutting cube (hidden after operation)
    """
    # Create cutting cube
    wall_dims = wall.dimensions
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    cutter = bpy.context.active_object
    cutter.name = name
    
    # Position at door location
    cutter.location = wall.location.copy()
    cutter.location.z = door_height / 2
    
    # Scale to door size
    cutter.scale = (door_width / 2, wall_dims.y + 0.1, door_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add boolean modifier
    bool_mod = wall.modifiers.new(name=f"Door_{name}", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter
    
    # Apply modifier
    bpy.context.view_layer.objects.active = wall
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    
    # Hide cutter
    cutter.hide_viewport = True
    cutter.hide_render = True
    
    return cutter


def add_window_opening(
    wall: bpy.types.Object,
    window_width: float = 1.2,
    window_height: float = 1.0,
    sill_height: float = 0.9,
    position: float = 0.5,
    name: str = "WindowOpening"
) -> bpy.types.Object:
    """
    Add a window opening to a wall.
    
    Args:
        wall: Wall object to cut
        window_width: Window width
        window_height: Window height
        sill_height: Height from floor to window sill
        position: Horizontal position (0-1)
        name: Object name
    
    Returns:
        The cutting cube
    """
    wall_dims = wall.dimensions
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    cutter = bpy.context.active_object
    cutter.name = name
    
    cutter.location = wall.location.copy()
    cutter.location.z = sill_height + window_height / 2
    
    cutter.scale = (window_width / 2, wall_dims.y + 0.1, window_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    
    bool_mod = wall.modifiers.new(name=f"Window_{name}", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter
    
    bpy.context.view_layer.objects.active = wall
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    
    cutter.hide_viewport = True
    cutter.hide_render = True
    
    return cutter


# Standalone execution
if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create a room
    room = create_interior_room(
        width=5,
        depth=4,
        height=2.8,
        floor_material='WOOD'
    )
    
    # Add door to front wall
    if 'front' in room:
        add_door_opening(room['front'])
    
    # Add window to left wall
    if 'left' in room:
        add_window_opening(room['left'])
    
    print(f"Created room with {len(room)} elements")
