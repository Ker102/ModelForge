"""
{
  "title": "Key Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["key", "lock", "props", "fantasy", "medieval", "game"],
  "difficulty": "beginner",
  "description": "Generates various key styles for game props.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math


def create_key(
    length: float = 0.08,
    style: str = 'SKELETON',
    material: str = 'BRASS',
    location: tuple = (0, 0, 0),
    name: str = "Key"
) -> bpy.types.Object:
    """
    Create a key.
    
    Args:
        length: Total key length
        style: 'SKELETON', 'MODERN', 'ORNATE', 'MASTER'
        material: 'BRASS', 'IRON', 'GOLD', 'SILVER'
        location: Position
        name: Object name
    
    Returns:
        The key object
    """
    parts = []
    
    shaft_length = length * 0.6
    shaft_radius = length * 0.02
    
    # === SHAFT ===
    bpy.ops.mesh.primitive_cylinder_add(
        radius=shaft_radius,
        depth=shaft_length,
        location=(location[0] + shaft_length/2, location[1], location[2])
    )
    shaft = bpy.context.active_object
    shaft.rotation_euler.y = math.radians(90)
    parts.append(shaft)
    
    # === BOW (handle) ===
    bow_size = length * 0.35
    
    if style == 'SKELETON':
        bpy.ops.mesh.primitive_torus_add(
            major_radius=bow_size * 0.5,
            minor_radius=shaft_radius * 1.5,
            location=(location[0] - bow_size * 0.3, location[1], location[2])
        )
    elif style == 'ORNATE':
        bpy.ops.mesh.primitive_circle_add(
            radius=bow_size * 0.5,
            fill_type='NGON',
            location=(location[0] - bow_size * 0.3, location[1], location[2])
        )
        bow = bpy.context.active_object
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bow.modifiers["Solidify"].thickness = shaft_radius * 3
    elif style == 'MODERN':
        bpy.ops.mesh.primitive_cube_add(
            size=bow_size,
            location=(location[0] - bow_size * 0.4, location[1], location[2])
        )
        bow = bpy.context.active_object
        bow.scale = (0.4, 0.1, 1)
        bpy.ops.object.transform_apply(scale=True)
    else:  # MASTER
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=bow_size * 0.4,
            location=(location[0] - bow_size * 0.3, location[1], location[2])
        )
    
    parts.append(bpy.context.active_object)
    
    # === BIT (teeth) ===
    bit_length = length * 0.15
    bit_height = length * 0.1
    
    if style in ['SKELETON', 'ORNATE', 'MASTER']:
        # Create teeth pattern
        teeth_count = 3 if style == 'SKELETON' else 4
        for i in range(teeth_count):
            tooth_h = bit_height * (0.6 + (i % 2) * 0.4)
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=(
                location[0] + shaft_length + bit_length * (i / teeth_count),
                location[1],
                location[2] - tooth_h/2
            ))
            tooth = bpy.context.active_object
            tooth.scale = (bit_length/teeth_count * 0.8, shaft_radius * 1.5, tooth_h/2)
            bpy.ops.object.transform_apply(scale=True)
            parts.append(tooth)
    else:  # MODERN
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + shaft_length,
            location[1],
            location[2] - bit_height/2
        ))
        bit = bpy.context.active_object
        bit.scale = (bit_length, shaft_radius * 2, bit_height)
        bpy.ops.object.transform_apply(scale=True)
        parts.append(bit)
    
    # Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    
    key = bpy.context.active_object
    key.name = name
    
    # Material
    mat = _create_key_material(material, name)
    key.data.materials.append(mat)
    
    bpy.ops.object.shade_smooth()
    
    return key


def _create_key_material(
    material: str,
    name: str
) -> bpy.types.Material:
    """Create key material."""
    colors = {
        'BRASS': (0.8, 0.7, 0.3),
        'IRON': (0.4, 0.4, 0.42),
        'GOLD': (1.0, 0.84, 0.0),
        'SILVER': (0.8, 0.82, 0.85)
    }
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    color = colors.get(material, colors['BRASS'])
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.3 if material == 'GOLD' else 0.4
    
    return mat


def create_key_ring(
    key_count: int = 3,
    location: tuple = (0, 0, 0),
    name: str = "KeyRing"
) -> dict:
    """Create key ring with multiple keys."""
    result = {}
    
    # Ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.03,
        minor_radius=0.003,
        location=location
    )
    ring = bpy.context.active_object
    ring.name = f"{name}_Ring"
    
    ring_mat = bpy.data.materials.new(f"{name}_RingMat")
    ring_mat.use_nodes = True
    bsdf = ring_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.52, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    ring.data.materials.append(ring_mat)
    
    result['ring'] = ring
    
    # Keys
    keys = []
    materials = ['BRASS', 'IRON', 'GOLD']
    styles = ['SKELETON', 'ORNATE', 'MASTER']
    
    for i in range(key_count):
        angle = (i / key_count) * math.pi * 0.5 - 0.3
        
        key = create_key(
            style=styles[i % len(styles)],
            material=materials[i % len(materials)],
            location=(location[0], location[1], location[2] - 0.04),
            name=f"{name}_Key_{i+1}"
        )
        key.rotation_euler.z = angle
        keys.append(key)
    
    result['keys'] = keys
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_key(style='SKELETON', location=(0, 0, 0))
    create_key(style='ORNATE', material='GOLD', location=(0, 0.1, 0))
    create_key_ring(key_count=3, location=(0.2, 0, 0))
    
    print("Created keys")
