"""
{
  "title": "Barrel Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["barrel", "container", "props", "game", "medieval"],
  "difficulty": "beginner",
  "description": "Generates wooden and metal barrels.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math


def create_barrel(
    height: float = 0.8,
    radius: float = 0.25,
    bulge: float = 0.1,
    staves: int = 12,
    bands: int = 3,
    style: str = 'WOODEN',
    location: tuple = (0, 0, 0),
    name: str = "Barrel"
) -> dict:
    """
    Create a barrel.
    
    Args:
        height: Barrel height
        radius: Base radius
        bulge: Middle bulge amount
        staves: Number of wooden staves
        bands: Number of metal bands
        style: 'WOODEN', 'METAL'
        location: Position
        name: Object name
    
    Returns:
        Dictionary with barrel parts
    """
    result = {}
    
    # Main body
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=staves,
        radius=radius,
        depth=height,
        location=(location[0], location[1], location[2] + height/2)
    )
    barrel = bpy.context.active_object
    barrel.name = name
    
    # Add bulge in middle
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for v in barrel.data.vertices:
        # Distance from middle determines bulge
        z_normalized = abs(v.co.z) / (height/2)
        bulge_factor = 1 + bulge * (1 - z_normalized**2)
        
        if v.co.x != 0 or v.co.y != 0:
            angle = math.atan2(v.co.y, v.co.x)
            dist = math.sqrt(v.co.x**2 + v.co.y**2) * bulge_factor
            v.co.x = math.cos(angle) * dist
            v.co.y = math.sin(angle) * dist
    
    bpy.ops.object.shade_smooth()
    
    # Material
    if style == 'WOODEN':
        mat = bpy.data.materials.new(f"{name}_WoodMat")
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.4, 0.28, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.7
    else:  # METAL
        mat = bpy.data.materials.new(f"{name}_MetalMat")
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.55, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.4
    
    barrel.data.materials.append(mat)
    result['barrel'] = barrel
    
    # Metal bands
    if style == 'WOODEN':
        band_objs = _create_barrel_bands(
            radius + bulge, height, bands, location, name
        )
        result['bands'] = band_objs
    
    return result


def _create_barrel_bands(
    radius: float,
    height: float,
    count: int,
    location: tuple,
    name: str
) -> list:
    """Create metal bands around barrel."""
    bands = []
    band_height = 0.03
    
    band_mat = bpy.data.materials.new(f"{name}_BandMat")
    bsdf = band_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.32, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.35
    
    positions = []
    if count == 1:
        positions = [0.5]
    elif count == 2:
        positions = [0.2, 0.8]
    elif count >= 3:
        positions = [0.15, 0.5, 0.85]
        for i in range(3, count):
            positions.append(i / (count + 1))
    
    for i, pos in enumerate(positions):
        z = location[2] + height * pos
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius * 1.02,
            minor_radius=band_height/2,
            location=(location[0], location[1], z)
        )
        band = bpy.context.active_object
        band.name = f"{name}_Band_{i+1}"
        band.data.materials.append(band_mat)
        bands.append(band)
    
    return bands


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_barrel(style='WOODEN', location=(0, 0, 0))
    create_barrel(style='METAL', location=(0.8, 0, 0))
    
    print("Created barrels")
