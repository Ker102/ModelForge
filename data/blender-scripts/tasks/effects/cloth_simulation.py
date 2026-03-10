"""
{
  "title": "Cloth Simulation",
  "category": "effects",
  "subcategory": "physics",
  "tags": ["cloth", "physics", "simulation", "fabric", "drape", "collision", "pinning", "wind", "softbody"],
  "difficulty": "intermediate",
  "description": "Set up cloth simulations with material presets, vertex pinning, collision objects, and wind effects via Python.",
  "blender_version": "5.0+",
  "estimated_objects": 2
}
"""
import bpy
import math


# Cloth material presets (quality, stiffness, damping)
CLOTH_PRESETS = {
    'silk': {
        'quality': 12,
        'mass': 0.15,
        'tension_stiffness': 5.0,
        'compression_stiffness': 5.0,
        'shear_stiffness': 5.0,
        'bending_stiffness': 0.05,
        'tension_damping': 0.0,
        'compression_damping': 0.0,
        'air_damping': 1.0,
    },
    'cotton': {
        'quality': 7,
        'mass': 0.3,
        'tension_stiffness': 15.0,
        'compression_stiffness': 15.0,
        'shear_stiffness': 15.0,
        'bending_stiffness': 0.5,
        'tension_damping': 5.0,
        'compression_damping': 5.0,
        'air_damping': 1.0,
    },
    'denim': {
        'quality': 12,
        'mass': 0.4,
        'tension_stiffness': 40.0,
        'compression_stiffness': 40.0,
        'shear_stiffness': 40.0,
        'bending_stiffness': 10.0,
        'tension_damping': 25.0,
        'compression_damping': 25.0,
        'air_damping': 1.0,
    },
    'leather': {
        'quality': 15,
        'mass': 0.5,
        'tension_stiffness': 80.0,
        'compression_stiffness': 80.0,
        'shear_stiffness': 80.0,
        'bending_stiffness': 30.0,
        'tension_damping': 25.0,
        'compression_damping': 25.0,
        'air_damping': 1.0,
    },
    'rubber': {
        'quality': 7,
        'mass': 0.3,
        'tension_stiffness': 15.0,
        'compression_stiffness': 15.0,
        'shear_stiffness': 15.0,
        'bending_stiffness': 25.0,
        'tension_damping': 25.0,
        'compression_damping': 25.0,
        'air_damping': 1.0,
    },
}


def add_cloth_simulation(
    obj: bpy.types.Object,
    preset: str = 'cotton',
    custom_settings: dict = None,
    frame_start: int = 1,
    frame_end: int = 250
) -> bpy.types.ClothModifier:
    """
    Add cloth simulation to a mesh object.

    Args:
        obj: Mesh object to simulate as cloth
        preset: Cloth material preset ('silk', 'cotton', 'denim', 'leather', 'rubber')
        custom_settings: Override preset with custom values (dict of setting_name: value)
        frame_start: Simulation start frame
        frame_end: Simulation end frame

    Returns:
        The cloth modifier

    Example:
        >>> add_cloth_simulation(plane, preset='silk')
        >>> add_cloth_simulation(mesh, preset='cotton', custom_settings={'mass': 0.5})
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Add cloth modifier
    bpy.ops.object.modifier_add(type='CLOTH')
    cloth_mod = obj.modifiers[-1]
    cloth = cloth_mod.settings

    # Apply preset
    settings = CLOTH_PRESETS.get(preset, CLOTH_PRESETS['cotton']).copy()
    if custom_settings:
        settings.update(custom_settings)

    cloth.quality = settings['quality']
    cloth.mass = settings['mass']
    cloth.tension_stiffness = settings['tension_stiffness']
    cloth.compression_stiffness = settings['compression_stiffness']
    cloth.shear_stiffness = settings['shear_stiffness']
    cloth.bending_stiffness = settings['bending_stiffness']
    cloth.tension_damping = settings['tension_damping']
    cloth.compression_damping = settings['compression_damping']
    cloth.air_damping = settings['air_damping']

    # Set cache range
    cloth_mod.point_cache.frame_start = frame_start
    cloth_mod.point_cache.frame_end = frame_end

    obj.select_set(False)
    return cloth_mod


def add_cloth_collision(
    obj: bpy.types.Object,
    thickness_outer: float = 0.02,
    thickness_inner: float = 0.01,
    damping: float = 0.5,
    friction: float = 5.0
) -> bpy.types.CollisionModifier:
    """
    Add collision physics to an object so cloth can collide with it.

    Args:
        obj: Object to act as a collision surface
        thickness_outer: Outer collision distance
        thickness_inner: Inner collision distance
        damping: Collision damping
        friction: Surface friction

    Returns:
        The collision modifier

    Example:
        >>> add_cloth_collision(body_mesh, friction=10.0)
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.modifier_add(type='COLLISION')
    col_mod = obj.modifiers[-1]
    col = col_mod.settings

    col.thickness_outer = thickness_outer
    col.thickness_inner = thickness_inner
    col.damping = damping
    col.cloth_friction = friction

    obj.select_set(False)
    return col_mod


def pin_cloth_vertex_group(
    obj: bpy.types.Object,
    vertex_group_name: str = "Pin",
    create_top_row: bool = True
) -> str:
    """
    Create a vertex group for cloth pinning.
    Pin vertices are held in place while the rest simulates.

    Args:
        obj: Cloth mesh object
        vertex_group_name: Name for the pin vertex group
        create_top_row: If True, automatically assign top-row vertices

    Returns:
        Name of the vertex group

    Example:
        >>> pin_cloth_vertex_group(curtain, "Pin", create_top_row=True)
    """
    # Create vertex group
    if vertex_group_name in obj.vertex_groups:
        vg = obj.vertex_groups[vertex_group_name]
    else:
        vg = obj.vertex_groups.new(name=vertex_group_name)

    if create_top_row:
        # Find the highest vertices and pin them
        mesh = obj.data
        if mesh.vertices:
            max_z = max(v.co.z for v in mesh.vertices)
            threshold = max_z - 0.01  # small tolerance

            top_verts = [v.index for v in mesh.vertices if v.co.z >= threshold]
            vg.add(top_verts, 1.0, 'REPLACE')

    # Assign to cloth modifier
    for mod in obj.modifiers:
        if mod.type == 'CLOTH':
            mod.settings.vertex_group_mass = vertex_group_name
            break

    return vertex_group_name


def create_cloth_curtain(
    width: float = 2.0,
    height: float = 3.0,
    subdivisions: int = 30,
    location: tuple = (0, 0, 3),
    preset: str = 'cotton',
    name: str = "Curtain"
) -> bpy.types.Object:
    """
    Create a cloth curtain that drapes with gravity.
    Top row is pinned, rest is simulated.

    Args:
        width: Curtain width
        height: Curtain height
        subdivisions: Mesh resolution
        location: World position (top-center)
        preset: Cloth material preset
        name: Object name

    Returns:
        The curtain object

    Example:
        >>> curtain = create_cloth_curtain(width=3, height=4, preset='silk')
    """
    bpy.ops.mesh.primitive_plane_add(size=1, location=location)
    curtain = bpy.context.active_object
    curtain.name = name

    # Scale to curtain dimensions
    curtain.scale = (width, height, 1)
    bpy.ops.object.transform_apply(scale=True)

    # Rotate to hang vertically (plane starts horizontal)
    curtain.rotation_euler.x = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)

    # Subdivide for cloth resolution
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=subdivisions)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add cloth sim
    add_cloth_simulation(curtain, preset=preset)

    # Pin top row
    pin_cloth_vertex_group(curtain, "Pin", create_top_row=True)

    # Add material
    mat = bpy.data.materials.new(f"{name}_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.6, 0.15, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8
    curtain.data.materials.append(mat)

    return curtain


def bake_cloth_simulation(
    obj: bpy.types.Object,
    frame_start: int = 1,
    frame_end: int = 250
) -> bool:
    """
    Bake a cloth simulation for stable playback and rendering.

    Args:
        obj: Object with cloth modifier
        frame_start: Start frame
        frame_end: End frame

    Returns:
        True if successful

    Example:
        >>> bake_cloth_simulation(curtain, frame_end=200)
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Find cloth modifier
    cloth_mod = None
    for mod in obj.modifiers:
        if mod.type == 'CLOTH':
            cloth_mod = mod
            break

    if not cloth_mod:
        print(f"No cloth modifier on '{obj.name}'")
        return False

    # Set cache range and bake
    cloth_mod.point_cache.frame_start = frame_start
    cloth_mod.point_cache.frame_end = frame_end

    # Use override to bake specific cache
    override = bpy.context.copy()
    override['point_cache'] = cloth_mod.point_cache
    bpy.ops.ptcache.bake(override, bake=True)

    return True


# Standalone execution
if __name__ == "__main__":
    # Create a curtain demo
    curtain = create_cloth_curtain(width=2.5, height=3.0, preset='silk')
    print(f"Created cloth curtain '{curtain.name}' with silk preset")
    print("Press Alt+A or play to see the simulation")
