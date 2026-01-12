"""
{
  "title": "Ground Plane Generator",
  "category": "environment",
  "subcategory": "terrain",
  "tags": ["ground", "floor", "terrain", "environment", "base"],
  "difficulty": "beginner",
  "description": "Creates ground planes with various materials and textures.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy


def create_ground_plane(
    size: float = 10.0,
    material_type: str = 'CONCRETE',
    subdivisions: int = 0,
    location: tuple = (0, 0, 0),
    name: str = "Ground"
) -> bpy.types.Object:
    """
    Create a ground plane with material.
    
    Args:
        size: Plane size
        material_type: 'CONCRETE', 'GRASS', 'DIRT', 'WOOD', 'TILE'
        subdivisions: Subdivision level (for displacement)
        location: Position
        name: Object name
    
    Returns:
        The ground plane object
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    ground = bpy.context.active_object
    ground.name = name
    
    if subdivisions > 0:
        bpy.ops.object.modifier_add(type='SUBSURF')
        ground.modifiers["Subdivision"].levels = subdivisions
        ground.modifiers["Subdivision"].render_levels = subdivisions
    
    # Create material based on type
    mat = _create_ground_material(material_type, name)
    ground.data.materials.append(mat)
    
    return ground


def _create_ground_material(material_type: str, name: str) -> bpy.types.Material:
    """Create ground material based on type."""
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    bsdf = nodes.get("Principled BSDF")
    
    if material_type == 'CONCRETE':
        bsdf.inputs['Base Color'].default_value = (0.45, 0.45, 0.42, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.9
        
        # Add noise for texture
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 50.0
        
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (0.4, 0.4, 0.38, 1.0)
        ramp.color_ramp.elements[1].color = (0.5, 0.5, 0.47, 1.0)
        
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        
    elif material_type == 'GRASS':
        bsdf.inputs['Base Color'].default_value = (0.15, 0.4, 0.1, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8
        bsdf.inputs['Sheen Weight'].default_value = 0.2
        
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 30.0
        
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (0.12, 0.35, 0.08, 1.0)
        ramp.color_ramp.elements[1].color = (0.2, 0.5, 0.15, 1.0)
        
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        
    elif material_type == 'DIRT':
        bsdf.inputs['Base Color'].default_value = (0.35, 0.25, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.95
        
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 20.0
        
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (0.3, 0.2, 0.12, 1.0)
        ramp.color_ramp.elements[1].color = (0.4, 0.3, 0.18, 1.0)
        
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        
    elif material_type == 'WOOD':
        bsdf.inputs['Base Color'].default_value = (0.4, 0.28, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.6
        
        wave = nodes.new('ShaderNodeTexWave')
        wave.wave_type = 'BANDS'
        wave.inputs['Scale'].default_value = 8.0
        wave.inputs['Distortion'].default_value = 5.0
        
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (0.35, 0.22, 0.1, 1.0)
        ramp.color_ramp.elements[1].color = (0.45, 0.32, 0.18, 1.0)
        
        links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        
    elif material_type == 'TILE':
        bsdf.inputs['Base Color'].default_value = (0.85, 0.85, 0.82, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.3
        
        brick = nodes.new('ShaderNodeTexBrick')
        brick.inputs['Scale'].default_value = 5.0
        brick.inputs['Color1'].default_value = (0.85, 0.85, 0.82, 1.0)
        brick.inputs['Color2'].default_value = (0.8, 0.8, 0.78, 1.0)
        brick.inputs['Mortar'].default_value = (0.5, 0.5, 0.48, 1.0)
        brick.inputs['Mortar Size'].default_value = 0.01
        
        links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    
    return mat


def create_curved_backdrop(
    width: float = 10.0,
    height: float = 6.0,
    curve_radius: float = 2.0,
    color: tuple = (0.9, 0.9, 0.9),
    location: tuple = (0, 0, 0),
    name: str = "Backdrop"
) -> bpy.types.Object:
    """
    Create curved studio backdrop.
    
    Args:
        width: Backdrop width
        height: Backdrop height
        curve_radius: Curve at bottom
        color: Background color
        location: Position
        name: Object name
    """
    bpy.ops.mesh.primitive_plane_add(size=1, location=location)
    backdrop = bpy.context.active_object
    backdrop.name = name
    backdrop.scale = (width/2, height/2, 1)
    backdrop.rotation_euler.x = 1.5708
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    
    # Subdivide for bending
    bpy.ops.object.modifier_add(type='SUBSURF')
    backdrop.modifiers["Subdivision"].levels = 4
    bpy.ops.object.modifier_apply(modifier="Subdivision")
    
    # Bend bottom
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    backdrop.modifiers["SimpleDeform"].deform_method = 'BEND'
    backdrop.modifiers["SimpleDeform"].angle = 1.5708
    backdrop.modifiers["SimpleDeform"].deform_axis = 'X'
    
    bpy.ops.object.shade_smooth()
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    backdrop.data.materials.append(mat)
    
    return backdrop


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_ground_plane(material_type='GRASS', location=(0, 0, 0))
    create_ground_plane(material_type='TILE', size=5, location=(0, 8, 0))
    
    print("Created ground planes")
