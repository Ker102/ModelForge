"""
{
  "title": "Studio Three-Point Lighting Setup",
  "category": "lighting",
  "subcategory": "studio",
  "tags": ["studio", "three-point", "key", "fill", "rim", "professional", "product"],
  "difficulty": "beginner",
  "description": "Creates a professional three-point lighting setup with key, fill, and rim lights for product or character rendering.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy
import math


def create_three_point_lighting(
    target_location: tuple = (0, 0, 0),
    key_energy: float = 1000,
    fill_ratio: float = 0.5,
    rim_energy: float = 800,
    key_color: tuple = (1.0, 0.98, 0.95),
    fill_color: tuple = (0.9, 0.95, 1.0),
    rim_color: tuple = (1.0, 1.0, 1.0),
    distance: float = 5.0,
    name_prefix: str = "Studio"
) -> dict:
    """
    Create a professional three-point lighting setup.
    
    The three-point lighting system consists of:
    - Key Light: Main light source, brightest, creates primary shadows
    - Fill Light: Softer light to fill in shadows from key light
    - Rim/Back Light: Creates edge highlights and separates subject from background
    
    Args:
        target_location: Center point the lights will illuminate
        key_energy: Key light intensity in watts
        fill_ratio: Fill light as ratio of key light (0.3-0.7 typical)
        rim_energy: Rim light intensity
        key_color: RGB color for key light (warm recommended)
        fill_color: RGB color for fill light (slightly cool for contrast)
        rim_color: RGB color for rim light
        distance: Distance of lights from target
        name_prefix: Prefix for light names
    
    Returns:
        Dictionary with 'key', 'fill', 'rim' light objects
    
    Example:
        >>> lights = create_three_point_lighting(target_location=(0, 0, 1), key_energy=1500)
        >>> lights['key'].data.energy = 2000  # Adjust key light
    """
    tx, ty, tz = target_location
    lights = {}
    
    # === KEY LIGHT ===
    # Positioned high, to the front-right of subject
    key_x = tx + distance * 0.7
    key_y = ty - distance * 0.7
    key_z = tz + distance * 0.6
    
    bpy.ops.object.light_add(type='AREA', location=(key_x, key_y, key_z))
    key_light = bpy.context.active_object
    key_light.name = f"{name_prefix}_KeyLight"
    key_light.data.energy = key_energy
    key_light.data.color = key_color
    key_light.data.shape = 'RECTANGLE'
    key_light.data.size = 2.0
    key_light.data.size_y = 1.5
    
    # Point at target
    direction = (tx - key_x, ty - key_y, tz - key_z)
    key_light.rotation_euler = _direction_to_euler(direction)
    lights['key'] = key_light
    
    # === FILL LIGHT ===
    # Positioned to the front-left, lower and softer
    fill_x = tx - distance * 0.6
    fill_y = ty - distance * 0.5
    fill_z = tz + distance * 0.3
    
    bpy.ops.object.light_add(type='AREA', location=(fill_x, fill_y, fill_z))
    fill_light = bpy.context.active_object
    fill_light.name = f"{name_prefix}_FillLight"
    fill_light.data.energy = key_energy * fill_ratio
    fill_light.data.color = fill_color
    fill_light.data.shape = 'RECTANGLE'
    fill_light.data.size = 3.0  # Larger = softer
    fill_light.data.size_y = 2.5
    
    direction = (tx - fill_x, ty - fill_y, tz - fill_z)
    fill_light.rotation_euler = _direction_to_euler(direction)
    lights['fill'] = fill_light
    
    # === RIM LIGHT ===
    # Positioned behind and above the subject
    rim_x = tx - distance * 0.3
    rim_y = ty + distance * 0.8
    rim_z = tz + distance * 0.8
    
    bpy.ops.object.light_add(type='AREA', location=(rim_x, rim_y, rim_z))
    rim_light = bpy.context.active_object
    rim_light.name = f"{name_prefix}_RimLight"
    rim_light.data.energy = rim_energy
    rim_light.data.color = rim_color
    rim_light.data.shape = 'RECTANGLE'
    rim_light.data.size = 1.5
    rim_light.data.size_y = 1.0
    
    direction = (tx - rim_x, ty - rim_y, tz - rim_z)
    rim_light.rotation_euler = _direction_to_euler(direction)
    lights['rim'] = rim_light
    
    return lights


def _direction_to_euler(direction: tuple) -> tuple:
    """Convert direction vector to euler rotation."""
    from mathutils import Vector
    vec = Vector(direction).normalized()
    # Point -Z axis towards target (standard for lights/cameras)
    rot_quat = vec.to_track_quat('-Z', 'Y')
    return rot_quat.to_euler()


def create_product_lighting(
    target_location: tuple = (0, 0, 0),
    backdrop_color: tuple = (1.0, 1.0, 1.0),
    name_prefix: str = "Product"
) -> dict:
    """
    Create a complete product photography lighting setup with backdrop.
    
    Args:
        target_location: Product center location
        backdrop_color: RGB color for the background
        name_prefix: Prefix for created objects
    
    Returns:
        Dictionary with lights and backdrop objects
    
    Example:
        >>> setup = create_product_lighting((0, 0, 0.5))
    """
    result = {}
    tx, ty, tz = target_location
    
    # Create three-point lighting
    result['lights'] = create_three_point_lighting(
        target_location=target_location,
        key_energy=800,
        fill_ratio=0.6,
        rim_energy=500,
        distance=4.0,
        name_prefix=name_prefix
    )
    
    # Create backdrop (curved plane)
    bpy.ops.mesh.primitive_plane_add(size=10, location=(tx, ty + 5, tz - 0.5))
    backdrop = bpy.context.active_object
    backdrop.name = f"{name_prefix}_Backdrop"
    backdrop.rotation_euler[0] = math.radians(90)
    
    # Add bend modifier for curved backdrop
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    backdrop.modifiers["SimpleDeform"].deform_method = 'BEND'
    backdrop.modifiers["SimpleDeform"].angle = math.radians(-45)
    backdrop.modifiers["SimpleDeform"].deform_axis = 'X'
    
    # Backdrop material
    backdrop_mat = bpy.data.materials.new(name=f"{name_prefix}_BackdropMat")
    backdrop_mat.use_nodes = True
    bsdf = backdrop_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*backdrop_color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    backdrop.data.materials.append(backdrop_mat)
    result['backdrop'] = backdrop
    
    # Set world to white for clean reflections
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (*backdrop_color, 1.0)
        bg.inputs['Strength'].default_value = 0.5
    
    return result


# Standalone execution
if __name__ == "__main__":
    # Create a three-point lighting setup
    lights = create_three_point_lighting(
        target_location=(0, 0, 1),
        key_energy=1200,
        fill_ratio=0.4,
        rim_energy=800
    )
    print(f"Created {len(lights)} lights: {list(lights.keys())}")
