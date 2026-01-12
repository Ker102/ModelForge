"""
{
  "title": "Product Photography Shot Setup",
  "category": "rendering",
  "subcategory": "product",
  "tags": ["product", "photography", "studio", "e-commerce", "rendering", "backdrop"],
  "difficulty": "intermediate",
  "description": "Complete product photography scene setup with backdrop, lighting, camera, and render settings.",
  "blender_version": "3.0+",
  "estimated_objects": 8
}
"""
import bpy
import math


def create_product_shot_scene(
    product_height: float = 1.0,
    backdrop_color: tuple = (1.0, 1.0, 1.0),
    style: str = 'CLEAN',
    camera_angle: str = 'FRONT',
    resolution: tuple = (1920, 1920),
    name_prefix: str = "ProductShot"
) -> dict:
    """
    Create a complete product photography scene.
    
    Args:
        product_height: Height of product for proper camera framing
        backdrop_color: RGB backdrop color
        style: 'CLEAN' (white), 'DARK' (black), 'GRADIENT', 'STUDIO'
        camera_angle: 'FRONT', 'THREE_QUARTER', 'TOP_DOWN', 'LOW_ANGLE'
        resolution: Render resolution (width, height)
        name_prefix: Prefix for created objects
    
    Returns:
        Dictionary with all created objects
    
    Example:
        >>> scene = create_product_shot_scene(product_height=0.5, style='DARK')
    """
    result = {}
    
    # === BACKDROP ===
    backdrop = _create_backdrop(backdrop_color, style, product_height, name_prefix)
    result['backdrop'] = backdrop
    
    # === LIGHTING ===
    lights = _create_product_lighting(product_height, style, name_prefix)
    result.update(lights)
    
    # === CAMERA ===
    camera = _create_product_camera(product_height, camera_angle, name_prefix)
    result['camera'] = camera
    bpy.context.scene.camera = camera
    
    # === RENDER SETTINGS ===
    _configure_render_settings(resolution, style)
    
    # === WORLD ===
    _setup_world(backdrop_color, style)
    
    return result


def _create_backdrop(
    color: tuple,
    style: str,
    product_height: float,
    name_prefix: str
) -> bpy.types.Object:
    """Create curved backdrop."""
    scale = product_height * 3
    
    # Create base plane
    bpy.ops.mesh.primitive_plane_add(size=scale * 2, location=(0, scale * 0.8, 0))
    backdrop = bpy.context.active_object
    backdrop.name = f"{name_prefix}_Backdrop"
    
    # Rotate to vertical
    backdrop.rotation_euler[0] = math.radians(90)
    
    # Add bend modifier for curved sweep
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    backdrop.modifiers["SimpleDeform"].deform_method = 'BEND'
    backdrop.modifiers["SimpleDeform"].angle = math.radians(-60)
    backdrop.modifiers["SimpleDeform"].deform_axis = 'X'
    
    # Subdivide for smooth curve
    bpy.ops.object.modifier_add(type='SUBSURF')
    backdrop.modifiers["Subdivision"].levels = 3
    backdrop.modifiers["Subdivision"].render_levels = 3
    
    # Material
    mat = bpy.data.materials.new(f"{name_prefix}_BackdropMat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    if style == 'CLEAN':
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.9
    elif style == 'DARK':
        bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8
    elif style == 'GRADIENT':
        # Create gradient with color ramp
        pass
    elif style == 'STUDIO':
        bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.6
        bsdf.inputs['Specular IOR Level'].default_value = 0.2
    
    backdrop.data.materials.append(mat)
    
    return backdrop


def _create_product_lighting(
    product_height: float,
    style: str,
    name_prefix: str
) -> dict:
    """Create product photography lighting."""
    lights = {}
    scale = product_height * 2
    
    # Key light
    bpy.ops.object.light_add(type='AREA', location=(scale * 1.5, -scale, scale * 1.5))
    key = bpy.context.active_object
    key.name = f"{name_prefix}_Key"
    key.data.shape = 'RECTANGLE'
    key.data.size = scale * 1.2
    key.data.size_y = scale * 0.8
    
    if style == 'CLEAN':
        key.data.energy = 800
    elif style == 'DARK':
        key.data.energy = 500
    else:
        key.data.energy = 600
    
    # Point at product center
    direction = (-scale * 1.5, scale, -scale * 0.5)
    key.rotation_euler = _direction_to_euler(direction)
    lights['key'] = key
    
    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-scale * 1.2, -scale * 0.8, scale))
    fill = bpy.context.active_object
    fill.name = f"{name_prefix}_Fill"
    fill.data.shape = 'RECTANGLE'
    fill.data.size = scale * 1.5
    fill.data.size_y = scale
    fill.data.energy = key.data.energy * 0.4
    
    direction = (scale * 1.2, scale * 0.8, -scale * 0.5)
    fill.rotation_euler = _direction_to_euler(direction)
    lights['fill'] = fill
    
    # Rim light (for separation)
    bpy.ops.object.light_add(type='AREA', location=(0, scale * 1.5, scale * 0.5))
    rim = bpy.context.active_object
    rim.name = f"{name_prefix}_Rim"
    rim.data.shape = 'RECTANGLE'
    rim.data.size = scale * 0.8
    rim.data.size_y = scale * 1.2
    rim.data.energy = key.data.energy * 0.3
    
    direction = (0, -scale * 1.5, 0)
    rim.rotation_euler = _direction_to_euler(direction)
    lights['rim'] = rim
    
    # Top bounce (for even illumination)
    if style == 'CLEAN':
        bpy.ops.object.light_add(type='AREA', location=(0, 0, scale * 2.5))
        top = bpy.context.active_object
        top.name = f"{name_prefix}_Top"
        top.data.shape = 'DISK'
        top.data.size = scale * 2
        top.data.energy = key.data.energy * 0.5
        top.rotation_euler = (math.radians(180), 0, 0)
        lights['top'] = top
    
    return lights


def _create_product_camera(
    product_height: float,
    angle: str,
    name_prefix: str
) -> bpy.types.Object:
    """Create product camera with proper framing."""
    scale = product_height * 2
    
    angles = {
        'FRONT': (scale * 2, 0, product_height * 0.6),
        'THREE_QUARTER': (scale * 1.8, -scale * 1.5, product_height * 0.8),
        'TOP_DOWN': (0, 0, scale * 3),
        'LOW_ANGLE': (scale * 2.5, -scale * 0.5, product_height * 0.2)
    }
    
    position = angles.get(angle, angles['THREE_QUARTER'])
    
    bpy.ops.object.camera_add(location=position)
    camera = bpy.context.active_object
    camera.name = f"{name_prefix}_Camera"
    
    # Point at product center
    from mathutils import Vector
    target = Vector((0, 0, product_height / 2))
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    # Camera settings
    camera.data.lens = 85  # Portrait lens
    camera.data.sensor_width = 36
    
    # DOF
    camera.data.dof.use_dof = True
    camera.data.dof.aperture_fstop = 4.0
    camera.data.dof.focus_distance = direction.length
    
    return camera


def _configure_render_settings(resolution: tuple, style: str) -> None:
    """Configure render settings for product photography."""
    scene = bpy.context.scene
    
    # Resolution
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    
    # Use Cycles for best quality
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 256
    scene.cycles.use_denoising = True
    
    # Transparent background
    scene.render.film_transparent = style != 'STUDIO'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'


def _setup_world(color: tuple, style: str) -> None:
    """Set up world environment."""
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("ProductWorld")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    background = nodes.new('ShaderNodeBackground')
    
    if style == 'CLEAN':
        background.inputs['Color'].default_value = (*color, 1.0)
        background.inputs['Strength'].default_value = 0.5
    elif style == 'DARK':
        background.inputs['Color'].default_value = (0.01, 0.01, 0.01, 1.0)
        background.inputs['Strength'].default_value = 0.2
    else:
        background.inputs['Color'].default_value = (0.8, 0.8, 0.8, 1.0)
        background.inputs['Strength'].default_value = 0.3
    
    output = nodes.new('ShaderNodeOutputWorld')
    links.new(background.outputs['Background'], output.inputs['Surface'])


def _direction_to_euler(direction: tuple) -> tuple:
    """Convert direction to euler rotation."""
    from mathutils import Vector
    vec = Vector(direction).normalized()
    rot_quat = vec.to_track_quat('-Z', 'Y')
    return rot_quat.to_euler()


# Standalone execution
if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create test product
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0, 0, 0.25))
    
    # Create product shot scene
    scene = create_product_shot_scene(
        product_height=0.5,
        style='CLEAN',
        camera_angle='THREE_QUARTER'
    )
    
    print(f"Created product shot with {len(scene)} elements")
