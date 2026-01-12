"""
{
  "title": "Treasure Chest Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["chest", "treasure", "props", "fantasy", "game", "loot"],
  "difficulty": "intermediate",
  "description": "Generates treasure chests with lids and decorations.",
  "blender_version": "3.0+",
  "estimated_objects": 4
}
"""
import bpy
import math


def create_chest(
    size: tuple = (0.5, 0.35, 0.35),
    lid_open: float = 0,
    style: str = 'WOODEN',
    with_treasure: bool = False,
    location: tuple = (0, 0, 0),
    name: str = "Chest"
) -> dict:
    """
    Create a treasure chest.
    
    Args:
        size: XYZ dimensions
        lid_open: Lid angle 0-90 degrees
        style: 'WOODEN', 'METAL', 'ORNATE'
        with_treasure: Add gold inside
        location: Position
        name: Object name
    
    Returns:
        Dictionary with chest parts
    """
    result = {}
    
    w, d, h = size
    body_height = h * 0.6
    lid_height = h * 0.4
    
    # === BODY ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1],
        location[2] + body_height/2
    ))
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    body.scale = (w/2, d/2, body_height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    body_mat = _create_chest_material(style, name, "Body")
    body.data.materials.append(body_mat)
    result['body'] = body
    
    # === LID ===
    # Create curved lid
    bpy.ops.mesh.primitive_cylinder_add(
        radius=d/2,
        depth=w,
        location=(location[0], location[1], location[2] + body_height)
    )
    lid = bpy.context.active_object
    lid.name = f"{name}_Lid"
    lid.rotation_euler.y = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    
    # Cut in half
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(
        plane_co=(0, 0, location[2] + body_height),
        plane_no=(0, 0, 1),
        clear_inner=True
    )
    bpy.ops.object.mode_set(mode='OBJECT')
    
    lid.data.materials.append(body_mat)
    
    # Set lid pivot at hinge
    bpy.context.scene.cursor.location = (
        location[0],
        location[1] - d/2,
        location[2] + body_height
    )
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    # Open lid
    lid.rotation_euler.x = math.radians(-lid_open)
    
    result['lid'] = lid
    
    # === BANDS ===
    if style in ['WOODEN', 'ORNATE']:
        bands = _create_chest_bands(w, d, body_height, location, name)
        result['bands'] = bands
    
    # === LOCK ===
    lock = _create_chest_lock(d, body_height, location, name)
    result['lock'] = lock
    
    # === TREASURE ===
    if with_treasure and lid_open > 30:
        treasure = _create_treasure_fill(w, d, body_height, location, name)
        result['treasure'] = treasure
    
    return result


def _create_chest_material(
    style: str,
    name: str,
    part: str
) -> bpy.types.Material:
    """Create chest material."""
    mat = bpy.data.materials.new(f"{name}_{part}Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    if style == 'WOODEN':
        bsdf.inputs['Base Color'].default_value = (0.35, 0.22, 0.1, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.7
    elif style == 'METAL':
        bsdf.inputs['Base Color'].default_value = (0.4, 0.35, 0.3, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.8
        bsdf.inputs['Roughness'].default_value = 0.4
    else:  # ORNATE
        bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.12, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.6
    
    return mat


def _create_chest_bands(
    w: float, d: float, h: float,
    location: tuple, name: str
) -> list:
    """Create metal bands."""
    bands = []
    band_mat = bpy.data.materials.new(f"{name}_BandMat")
    band_mat.use_nodes = True
    bsdf = band_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.28, 0.25, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.4
    
    for i, x_pos in enumerate([-w*0.35, 0, w*0.35]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + x_pos,
            location[1],
            location[2] + h/2
        ))
        band = bpy.context.active_object
        band.name = f"{name}_Band_{i}"
        band.scale = (0.015, d/2 + 0.01, h/2 + 0.01)
        bpy.ops.object.transform_apply(scale=True)
        band.data.materials.append(band_mat)
        bands.append(band)
    
    return bands


def _create_chest_lock(
    d: float, h: float,
    location: tuple, name: str
) -> bpy.types.Object:
    """Create chest lock."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0],
        location[1] - d/2 - 0.01,
        location[2] + h * 0.7
    ))
    lock = bpy.context.active_object
    lock.name = f"{name}_Lock"
    lock.scale = (0.04, 0.015, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    
    mat = bpy.data.materials.new(f"{name}_LockMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.7, 0.6, 0.3, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.25
    lock.data.materials.append(mat)
    
    return lock


def _create_treasure_fill(
    w: float, d: float, h: float,
    location: tuple, name: str
) -> list:
    """Create gold coins inside chest."""
    import random
    items = []
    
    gold_mat = bpy.data.materials.new(f"{name}_GoldMat")
    gold_mat.use_nodes = True
    bsdf = gold_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (1.0, 0.84, 0.0, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.2
    
    for i in range(15):
        pos = (
            location[0] + random.uniform(-w*0.35, w*0.35),
            location[1] + random.uniform(-d*0.35, d*0.35),
            location[2] + random.uniform(h*0.3, h*0.6)
        )
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.015,
            depth=0.003,
            location=pos
        )
        coin = bpy.context.active_object
        coin.name = f"{name}_Coin_{i}"
        coin.rotation_euler = (
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5),
            random.uniform(0, math.pi)
        )
        coin.data.materials.append(gold_mat)
        items.append(coin)
    
    return items


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_chest(lid_open=0, location=(0, 0, 0))
    create_chest(lid_open=60, with_treasure=True, location=(0.8, 0, 0))
    
    print("Created treasure chests")
