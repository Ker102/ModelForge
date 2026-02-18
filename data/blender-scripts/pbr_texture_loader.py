"""
{
  "title": "PBR Texture Loader and Baker",
  "category": "materials",
  "tags": ["pbr", "texture", "Principled BSDF", "material", "bake", "normal-map", "roughness", "metallic", "displacement"],
  "description": "Load and apply PBR texture maps (albedo, roughness, metallic, normal, AO, displacement) to Blender's Principled BSDF shader. Also supports auto-discovery from folders, displacement setup, and texture baking.",
  "blender_version": "4.0+"
}
"""
import bpy
import os


def apply_pbr_textures(
    obj: bpy.types.Object,
    albedo_path: str = None,
    roughness_path: str = None,
    metallic_path: str = None,
    normal_path: str = None,
    ao_path: str = None,
    displacement_path: str = None,
    material_name: str = "PBR_Material",
    uv_scale: tuple = (1.0, 1.0, 1.0)
) -> bpy.types.Material:
    """
    Create and apply a full PBR material from texture map files.
    Connects all maps to the correct Principled BSDF inputs with
    proper colorspace settings.

    Args:
        obj: Mesh object to apply material to
        albedo_path: Path to albedo/base color texture
        roughness_path: Path to roughness map
        metallic_path: Path to metallic map
        normal_path: Path to normal map
        ao_path: Path to ambient occlusion map
        displacement_path: Path to displacement/height map
        material_name: Name for the created material
        uv_scale: UV tiling scale (x, y, z)

    Returns:
        The created material

    Example:
        >>> mat = apply_pbr_textures(
        ...     character_mesh,
        ...     albedo_path="/textures/skin_albedo.png",
        ...     normal_path="/textures/skin_normal.png",
        ...     roughness_path="/textures/skin_roughness.png"
        ... )
    """
    mat = bpy.data.materials.new(name=material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create Principled BSDF and Output
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Create shared UV mapping node for tiling control
    mapping = None
    tex_coord = None
    if uv_scale != (1.0, 1.0, 1.0):
        tex_coord = nodes.new('ShaderNodeTexCoord')
        tex_coord.location = (-1000, 0)
        mapping = nodes.new('ShaderNodeMapping')
        mapping.location = (-800, 0)
        mapping.inputs['Scale'].default_value = uv_scale
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    x_offset = -500
    y_pos = 300

    # Helper to add a texture node
    def add_texture(filepath, colorspace='sRGB', y=0):
        nonlocal x_offset
        if not filepath or not os.path.isfile(filepath):
            return None
        tex = nodes.new('ShaderNodeTexImage')
        tex.location = (x_offset, y)
        tex.image = bpy.data.images.load(filepath)
        tex.image.colorspace_settings.name = colorspace
        if mapping:
            links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
        return tex

    # Albedo / Base Color
    if albedo_path:
        tex = add_texture(albedo_path, 'sRGB', y_pos)
        if tex:
            links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        y_pos -= 300

    # Roughness
    if roughness_path:
        tex = add_texture(roughness_path, 'Non-Color', y_pos)
        if tex:
            links.new(tex.outputs['Color'], bsdf.inputs['Roughness'])
        y_pos -= 300

    # Metallic
    if metallic_path:
        tex = add_texture(metallic_path, 'Non-Color', y_pos)
        if tex:
            links.new(tex.outputs['Color'], bsdf.inputs['Metallic'])
        y_pos -= 300

    # Normal Map
    if normal_path:
        tex = add_texture(normal_path, 'Non-Color', y_pos)
        if tex:
            normal_map = nodes.new('ShaderNodeNormalMap')
            normal_map.location = (-200, y_pos)
            links.new(tex.outputs['Color'], normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
        y_pos -= 300

    # Ambient Occlusion (multiply with Base Color if both exist)
    if ao_path:
        tex = add_texture(ao_path, 'Non-Color', y_pos)
        if tex and albedo_path:
            mix = nodes.new('ShaderNodeMix')
            mix.data_type = 'RGBA'
            mix.location = (-200, y_pos)
            mix.blend_type = 'MULTIPLY'
            mix.inputs[0].default_value = 1.0  # Factor

            # Reconnect: albedo → mix A, AO → mix B, mix → Base Color
            for link in list(links):
                if link.to_socket == bsdf.inputs['Base Color']:
                    links.new(link.from_socket, mix.inputs[6])  # A
                    links.remove(link)
                    break
            links.new(tex.outputs['Color'], mix.inputs[7])  # B
            links.new(mix.outputs[2], bsdf.inputs['Base Color'])  # Result
        y_pos -= 300

    # Displacement
    if displacement_path:
        tex = add_texture(displacement_path, 'Non-Color', y_pos)
        if tex:
            disp = nodes.new('ShaderNodeDisplacement')
            disp.location = (0, y_pos)
            disp.inputs['Scale'].default_value = 0.1
            disp.inputs['Midlevel'].default_value = 0.5
            links.new(tex.outputs['Color'], disp.inputs['Height'])
            links.new(disp.outputs['Displacement'], output.inputs['Displacement'])
            mat.cycles.displacement_method = 'BOTH'

    # Assign to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return mat


def create_pbr_material_from_folder(
    obj: bpy.types.Object,
    folder_path: str,
    material_name: str = None
) -> bpy.types.Material:
    """
    Auto-discover PBR texture maps in a folder by naming convention
    and apply them. Recognizes common suffixes:
    _albedo, _basecolor, _diffuse, _color → Base Color
    _roughness, _rough → Roughness
    _metallic, _metal, _metalness → Metallic
    _normal, _norm, _nrm → Normal
    _ao, _occlusion, _ambient → AO
    _displacement, _disp, _height → Displacement

    Args:
        obj: Mesh object to apply material to
        folder_path: Directory containing texture files
        material_name: Material name (default: folder name)

    Returns:
        The created material

    Example:
        >>> mat = create_pbr_material_from_folder(mesh, "/textures/wood_planks/")
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"Directory not found: {folder_path}")

    if material_name is None:
        material_name = os.path.basename(folder_path.rstrip('/\\'))

    # Map suffixes to their roles
    suffix_map = {
        'albedo': 'albedo', 'basecolor': 'albedo', 'base_color': 'albedo',
        'diffuse': 'albedo', 'color': 'albedo', 'col': 'albedo',
        'roughness': 'roughness', 'rough': 'roughness',
        'metallic': 'metallic', 'metal': 'metallic', 'metalness': 'metallic',
        'normal': 'normal', 'norm': 'normal', 'nrm': 'normal', 'nor': 'normal',
        'ao': 'ao', 'occlusion': 'ao', 'ambient_occlusion': 'ao',
        'displacement': 'displacement', 'disp': 'displacement', 'height': 'displacement',
    }

    image_extensions = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.exr', '.hdr', '.bmp'}

    discovered = {}

    for filename in os.listdir(folder_path):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in image_extensions:
            continue

        name_lower = os.path.splitext(filename)[0].lower()
        for suffix, role in suffix_map.items():
            if suffix in name_lower.split('_'):
                discovered[role] = os.path.join(folder_path, filename)
                break

    return apply_pbr_textures(
        obj,
        albedo_path=discovered.get('albedo'),
        roughness_path=discovered.get('roughness'),
        metallic_path=discovered.get('metallic'),
        normal_path=discovered.get('normal'),
        ao_path=discovered.get('ao'),
        displacement_path=discovered.get('displacement'),
        material_name=material_name
    )


def apply_displacement_from_texture(
    obj: bpy.types.Object,
    height_map_path: str,
    strength: float = 0.5,
    subdivision_levels: int = 3
) -> None:
    """
    Apply displacement modifier driven by a height/displacement texture.
    Adds Subdivision Surface + Displace modifiers for real geometry displacement.

    Args:
        obj: Mesh object
        height_map_path: Path to height map image (grayscale)
        strength: Displacement intensity
        subdivision_levels: Subdivision level for detail (2-4 recommended)

    Example:
        >>> apply_displacement_from_texture(terrain, "/maps/terrain_height.png", strength=2.0)
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    # Add subdivision for geometry detail
    subsurf = obj.modifiers.new(name="Subsurf_Disp", type='SUBSURF')
    subsurf.levels = subdivision_levels
    subsurf.render_levels = subdivision_levels

    # Load height map as texture
    img = bpy.data.images.load(height_map_path)
    img.colorspace_settings.name = 'Non-Color'

    tex = bpy.data.textures.new(name="Displacement_Tex", type='IMAGE')
    tex.image = img

    # Add Displace modifier
    displace = obj.modifiers.new(name="Displace_Map", type='DISPLACE')
    displace.texture = tex
    displace.strength = strength
    displace.mid_level = 0.5
    displace.texture_coords = 'UV'


def setup_texture_mapping(
    material: bpy.types.Material,
    scale: tuple = (1.0, 1.0, 1.0),
    rotation: tuple = (0.0, 0.0, 0.0),
    offset: tuple = (0.0, 0.0, 0.0)
) -> None:
    """
    Configure UV mapping for all texture nodes in a material.
    Adds or updates a shared Mapping node connected to all image textures.

    Args:
        material: Material to update
        scale: UV tiling scale
        rotation: UV rotation in radians
        offset: UV offset

    Example:
        >>> setup_texture_mapping(wood_material, scale=(2, 2, 1), rotation=(0, 0, 0.785))
    """
    if not material.use_nodes:
        return

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find or create TexCoord and Mapping nodes
    tex_coord = None
    mapping = None
    for node in nodes:
        if node.type == 'TEX_COORD':
            tex_coord = node
        elif node.type == 'MAPPING':
            mapping = node

    if not tex_coord:
        tex_coord = nodes.new('ShaderNodeTexCoord')
        tex_coord.location = (-1000, 0)

    if not mapping:
        mapping = nodes.new('ShaderNodeMapping')
        mapping.location = (-800, 0)

    mapping.inputs['Scale'].default_value = scale
    mapping.inputs['Rotation'].default_value = rotation
    mapping.inputs['Location'].default_value = offset

    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    # Connect mapping to all image texture nodes
    for node in nodes:
        if node.type == 'TEX_IMAGE':
            links.new(mapping.outputs['Vector'], node.inputs['Vector'])


def bake_textures(
    obj: bpy.types.Object,
    output_dir: str,
    bake_types: list = None,
    resolution: int = 1024,
    margin: int = 16
) -> dict:
    """
    Bake Cycles render data to texture maps.

    Args:
        obj: Object to bake from
        output_dir: Directory to save baked textures
        bake_types: List of bake types. Options: 'DIFFUSE', 'ROUGHNESS',
                    'NORMAL', 'AO', 'EMIT', 'COMBINED', 'SHADOW'
        resolution: Texture resolution in pixels
        margin: Bleed margin in pixels

    Returns:
        Dict mapping bake type to output file path

    Example:
        >>> paths = bake_textures(character, "/output/bakes/", ['DIFFUSE', 'NORMAL', 'AO'])
    """
    if bake_types is None:
        bake_types = ['DIFFUSE', 'NORMAL', 'AO']

    os.makedirs(output_dir, exist_ok=True)

    # Ensure Cycles is active
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.samples = 128

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    results = {}

    for bake_type in bake_types:
        # Create bake target image
        img_name = f"{obj.name}_{bake_type.lower()}"
        img = bpy.data.images.new(img_name, resolution, resolution)

        # Create temporary image texture node in material
        mat = obj.active_material
        if not mat:
            continue

        nodes = mat.node_tree.nodes
        bake_node = nodes.new('ShaderNodeTexImage')
        bake_node.image = img
        bake_node.select = True
        nodes.active = bake_node

        # Bake
        try:
            bpy.ops.object.bake(
                type=bake_type,
                margin=margin,
                use_clear=True
            )

            # Save image
            filepath = os.path.join(output_dir, f"{img_name}.png")
            img.filepath_raw = filepath
            img.file_format = 'PNG'
            img.save()
            results[bake_type] = filepath

        except RuntimeError as e:
            results[bake_type] = f"ERROR: {str(e)}"

        # Cleanup temp node
        nodes.remove(bake_node)

    return results
