"""
{
  "title": "Modifier Utilities",
  "category": "modifiers",
  "tags": ["modifier", "subdivision", "mirror", "array", "bevel", "boolean", "solidify"],
  "description": "Functions for adding and configuring mesh modifiers.",
  "blender_version": "3.0+"
}
"""
import bpy


def add_subdivision(
    obj: bpy.types.Object,
    levels: int = 2,
    render_levels: int = None,
    use_limit_surface: bool = True
) -> bpy.types.Modifier:
    """Add subdivision surface modifier."""
    mod = obj.modifiers.new("Subdivision", 'SUBSURF')
    mod.levels = levels
    mod.render_levels = render_levels or levels
    mod.use_limit_surface = use_limit_surface
    return mod


def add_mirror(
    obj: bpy.types.Object,
    axis: str = 'X',
    use_clip: bool = True,
    merge_threshold: float = 0.001
) -> bpy.types.Modifier:
    """Add mirror modifier."""
    mod = obj.modifiers.new("Mirror", 'MIRROR')
    mod.use_axis[0] = 'X' in axis.upper()
    mod.use_axis[1] = 'Y' in axis.upper()
    mod.use_axis[2] = 'Z' in axis.upper()
    mod.use_clip = use_clip
    mod.merge_threshold = merge_threshold
    return mod


def add_array(
    obj: bpy.types.Object,
    count: int = 3,
    offset: tuple = (1.1, 0, 0),
    use_relative: bool = True
) -> bpy.types.Modifier:
    """Add array modifier."""
    mod = obj.modifiers.new("Array", 'ARRAY')
    mod.count = count
    mod.use_relative_offset = use_relative
    if use_relative:
        mod.relative_offset_displace = offset
    else:
        mod.use_constant_offset = True
        mod.constant_offset_displace = offset
    return mod


def add_bevel_modifier(
    obj: bpy.types.Object,
    width: float = 0.02,
    segments: int = 3,
    limit_method: str = 'ANGLE',
    angle_limit: float = 30
) -> bpy.types.Modifier:
    """Add bevel modifier."""
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = limit_method
    if limit_method == 'ANGLE':
        import math
        mod.angle_limit = math.radians(angle_limit)
    return mod


def add_solidify(
    obj: bpy.types.Object,
    thickness: float = 0.05,
    offset: float = -1.0,
    use_even_offset: bool = True
) -> bpy.types.Modifier:
    """Add solidify modifier."""
    mod = obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod.thickness = thickness
    mod.offset = offset
    mod.use_even_offset = use_even_offset
    return mod


def add_boolean(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    operation: str = 'DIFFERENCE',
    solver: str = 'EXACT'
) -> bpy.types.Modifier:
    """Add boolean modifier."""
    mod = obj.modifiers.new("Boolean", 'BOOLEAN')
    mod.operation = operation  # 'DIFFERENCE', 'UNION', 'INTERSECT'
    mod.object = target
    mod.solver = solver
    return mod


def add_displace(
    obj: bpy.types.Object,
    strength: float = 0.5,
    mid_level: float = 0.5,
    texture_type: str = 'CLOUDS'
) -> bpy.types.Modifier:
    """Add displacement modifier with procedural texture."""
    tex = bpy.data.textures.new("DisplaceTex", type=texture_type)
    mod = obj.modifiers.new("Displace", 'DISPLACE')
    mod.texture = tex
    mod.strength = strength
    mod.mid_level = mid_level
    return mod


def add_shrinkwrap(
    obj: bpy.types.Object,
    target: bpy.types.Object,
    wrap_method: str = 'NEAREST_SURFACEPOINT',
    offset: float = 0.0
) -> bpy.types.Modifier:
    """Add shrinkwrap modifier."""
    mod = obj.modifiers.new("Shrinkwrap", 'SHRINKWRAP')
    mod.target = target
    mod.wrap_method = wrap_method
    mod.offset = offset
    return mod


def add_decimate(
    obj: bpy.types.Object,
    ratio: float = 0.5,
    decimate_type: str = 'COLLAPSE'
) -> bpy.types.Modifier:
    """Add decimate modifier."""
    mod = obj.modifiers.new("Decimate", 'DECIMATE')
    mod.decimate_type = decimate_type
    if decimate_type == 'COLLAPSE':
        mod.ratio = ratio
    return mod


def add_edge_split(
    obj: bpy.types.Object,
    split_angle: float = 30,
    use_edge_sharp: bool = True
) -> bpy.types.Modifier:
    """Add edge split modifier."""
    import math
    mod = obj.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    mod.split_angle = math.radians(split_angle)
    mod.use_edge_sharp = use_edge_sharp
    return mod


def add_remesh(
    obj: bpy.types.Object,
    mode: str = 'VOXEL',
    voxel_size: float = 0.1,
    octree_depth: int = 4
) -> bpy.types.Modifier:
    """Add remesh modifier."""
    mod = obj.modifiers.new("Remesh", 'REMESH')
    mod.mode = mode
    if mode == 'VOXEL':
        mod.voxel_size = voxel_size
    else:
        mod.octree_depth = octree_depth
    return mod


def add_smooth(
    obj: bpy.types.Object,
    factor: float = 0.5,
    iterations: int = 1
) -> bpy.types.Modifier:
    """Add smooth modifier."""
    mod = obj.modifiers.new("Smooth", 'SMOOTH')
    mod.factor = factor
    mod.iterations = iterations
    return mod


def add_skin(obj: bpy.types.Object) -> bpy.types.Modifier:
    """Add skin modifier for quick mesh generation."""
    mod = obj.modifiers.new("Skin", 'SKIN')
    return mod


def add_wireframe(
    obj: bpy.types.Object,
    thickness: float = 0.02,
    use_even_offset: bool = True
) -> bpy.types.Modifier:
    """Add wireframe modifier."""
    mod = obj.modifiers.new("Wireframe", 'WIREFRAME')
    mod.thickness = thickness
    mod.use_even_offset = use_even_offset
    return mod


def apply_modifier(obj: bpy.types.Object, modifier_name: str) -> None:
    """Apply a specific modifier."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier_name)


def apply_all_modifiers(obj: bpy.types.Object) -> None:
    """Apply all modifiers on object."""
    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers[:]:
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except:
            pass
