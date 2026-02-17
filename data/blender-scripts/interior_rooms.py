"""
Interior Room & Architecture Recipes — Blender 4.0/5.0
======================================================
Category: utility
Blender: 4.0+ / 5.0

Recipes for creating enclosed interior rooms, walls, doorways, and
architectural structures. Essential for interior scene prompts
(taverns, houses, dungeons, offices, etc.).

INTERIOR SCENE RULES:
1. ALWAYS create a proper enclosed room FIRST before placing furniture
2. Use separate mesh objects for each wall (easier to edit/remove for camera)
3. Floor + 4 walls + optional ceiling = minimum room shell
4. Scale to real-world units: wall height ~2.5-3m, door ~2m, table ~0.75m
5. Leave one wall open or use camera clipping for interior shots

REAL-WORLD SCALE REFERENCE (for interiors):
| Element         | Typical Size          |
|-----------------|-----------------------|
| Room height     | 2.5 – 3.0 m          |
| Door            | 2.0m H × 0.9m W      |
| Window          | 1.2m H × 1.0m W      |
| Table           | 0.75m H               |
| Chair seat      | 0.45m H               |
| Person          | 1.7 – 1.8m            |
| Barrel          | 0.9m H × 0.5m Ø      |
"""

import bpy
import bmesh
import math


def create_room(name="Room", width=6, depth=8, height=3,
                wall_thickness=0.2, open_front=False):
    """Create an enclosed room with floor, 4 walls, and ceiling.

    Creates separate objects for floor, walls, and ceiling so individual
    pieces can be hidden for camera placement.

    Args:
        name: Base name for room objects
        width: Room width (X axis) in meters
        depth: Room depth (Y axis) in meters
        height: Wall height in meters
        wall_thickness: Thickness of walls
        open_front: If True, omit front wall for camera access
    Returns:
        dict with 'floor', 'ceiling', 'walls' keys
    """
    parts = {}

    # Floor
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = f"{name}_Floor"
    floor.scale = (width / 2, depth / 2, 1)
    parts['floor'] = floor

    # Ceiling
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, height))
    ceiling = bpy.context.active_object
    ceiling.name = f"{name}_Ceiling"
    ceiling.scale = (width / 2, depth / 2, 1)
    parts['ceiling'] = ceiling

    walls = []

    # Back wall (Y+)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, depth / 2, height / 2))
    back = bpy.context.active_object
    back.name = f"{name}_Wall_Back"
    back.scale = (width / 2, wall_thickness / 2, height / 2)
    walls.append(back)

    # Left wall (X-)
    bpy.ops.mesh.primitive_cube_add(
        size=1, location=(-width / 2, 0, height / 2))
    left = bpy.context.active_object
    left.name = f"{name}_Wall_Left"
    left.scale = (wall_thickness / 2, depth / 2, height / 2)
    walls.append(left)

    # Right wall (X+)
    bpy.ops.mesh.primitive_cube_add(
        size=1, location=(width / 2, 0, height / 2))
    right = bpy.context.active_object
    right.name = f"{name}_Wall_Right"
    right.scale = (wall_thickness / 2, depth / 2, height / 2)
    walls.append(right)

    # Front wall (Y-) — optional
    if not open_front:
        bpy.ops.mesh.primitive_cube_add(
            size=1, location=(0, -depth / 2, height / 2))
        front = bpy.context.active_object
        front.name = f"{name}_Wall_Front"
        front.scale = (width / 2, wall_thickness / 2, height / 2)
        walls.append(front)

    parts['walls'] = walls
    return parts


def create_wall_with_doorway(name="DoorWall", width=6, height=3,
                              door_width=1.0, door_height=2.1,
                              door_offset=0.0, thickness=0.2):
    """Create a wall with a rectangular doorway cut out.

    Uses BMesh to create a wall plane with a hole for the door.
    The door is centered on door_offset from center of wall.

    Args:
        door_width: Width of doorway opening
        door_height: Height of doorway (standard: 2.1m)
        door_offset: Horizontal offset from wall center (0 = centered)
        thickness: Wall thickness
    """
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()

    half_w = width / 2
    half_d = door_width / 2

    # Create wall as 4 faces around the doorway opening
    # Bottom-left section (below door isn't needed, door starts at floor)
    # Left of door
    if door_offset - half_d > -half_w:
        verts_left = [
            bm.verts.new((-half_w, 0, 0)),
            bm.verts.new((door_offset - half_d, 0, 0)),
            bm.verts.new((door_offset - half_d, 0, height)),
            bm.verts.new((-half_w, 0, height)),
        ]
        bm.faces.new(verts_left)

    # Right of door
    if door_offset + half_d < half_w:
        verts_right = [
            bm.verts.new((door_offset + half_d, 0, 0)),
            bm.verts.new((half_w, 0, 0)),
            bm.verts.new((half_w, 0, height)),
            bm.verts.new((door_offset + half_d, 0, height)),
        ]
        bm.faces.new(verts_right)

    # Above door
    verts_top = [
        bm.verts.new((door_offset - half_d, 0, door_height)),
        bm.verts.new((door_offset + half_d, 0, door_height)),
        bm.verts.new((door_offset + half_d, 0, height)),
        bm.verts.new((door_offset - half_d, 0, height)),
    ]
    bm.faces.new(verts_top)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update(calc_edges=True)

    # Add Solidify modifier for wall thickness
    solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = thickness
    solidify.offset = 0  # Center thickness on face

    return obj


def create_wall_with_window(name="WindowWall", width=6, height=3,
                             win_width=1.2, win_height=1.0,
                             win_bottom=1.0, win_offset=0.0,
                             thickness=0.2):
    """Create a wall with a rectangular window opening.

    Args:
        win_width: Window width
        win_height: Window height
        win_bottom: Height from floor to bottom of window (sill height)
        win_offset: Horizontal offset from center
        thickness: Wall thickness
    """
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()

    half_w = width / 2
    half_win = win_width / 2
    win_top = win_bottom + win_height
    wo = win_offset  # shorthand

    # Below window (full width)
    v_below = [
        bm.verts.new((-half_w, 0, 0)),
        bm.verts.new((half_w, 0, 0)),
        bm.verts.new((half_w, 0, win_bottom)),
        bm.verts.new((-half_w, 0, win_bottom)),
    ]
    bm.faces.new(v_below)

    # Above window (full width)
    v_above = [
        bm.verts.new((-half_w, 0, win_top)),
        bm.verts.new((half_w, 0, win_top)),
        bm.verts.new((half_w, 0, height)),
        bm.verts.new((-half_w, 0, height)),
    ]
    bm.faces.new(v_above)

    # Left of window
    if wo - half_win > -half_w:
        v_left = [
            bm.verts.new((-half_w, 0, win_bottom)),
            bm.verts.new((wo - half_win, 0, win_bottom)),
            bm.verts.new((wo - half_win, 0, win_top)),
            bm.verts.new((-half_w, 0, win_top)),
        ]
        bm.faces.new(v_left)

    # Right of window
    if wo + half_win < half_w:
        v_right = [
            bm.verts.new((wo + half_win, 0, win_bottom)),
            bm.verts.new((half_w, 0, win_bottom)),
            bm.verts.new((half_w, 0, win_top)),
            bm.verts.new((wo + half_win, 0, win_top)),
        ]
        bm.faces.new(v_right)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update(calc_edges=True)

    solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = thickness

    return obj


def create_stone_wall_material(name="StoneMaterial"):
    """Quick stone/masonry material for walls."""
    mat = bpy.data.materials.new(name=name)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.45, 0.42, 0.38, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    return mat


def create_wood_material(name="WoodMaterial"):
    """Quick warm wood material for floors and furniture."""
    mat = bpy.data.materials.new(name=name)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.35, 0.22, 0.12, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    return mat
