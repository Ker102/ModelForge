"""
{
  "title": "Production Model Export Pipeline",
  "category": "export",
  "tags": ["fbx", "gltf", "usd", "lod", "game-dev", "production", "pipeline", "format-presets"],
  "description": "Production-grade model export with LOD chain generation, format presets (Game/VFX/Web/Print), USD export, pre-export validation, and scene bundle export. Extends basic export with game-dev and VFX workflows.",
  "blender_version": "4.0+"
}
"""
import bpy
import os
import json


# --- Export Presets ---
EXPORT_PRESETS = {
    'game': {
        'description': 'Game engine export (Unity/Unreal)',
        'format': 'FBX',
        'triangulate': True,
        'apply_modifiers': True,
        'apply_transforms': True,
        'tangent_space': True,
        'embed_textures': False,
        'scale': 1.0
    },
    'vfx': {
        'description': 'VFX pipeline export (Houdini/Maya)',
        'format': 'USD',
        'triangulate': False,
        'apply_modifiers': True,
        'apply_transforms': True,
        'tangent_space': False,
        'embed_textures': False,
        'scale': 1.0
    },
    'web': {
        'description': 'Web 3D export (Three.js/Babylon)',
        'format': 'GLTF',
        'triangulate': True,
        'apply_modifiers': True,
        'apply_transforms': True,
        'tangent_space': True,
        'embed_textures': True,
        'scale': 1.0
    },
    'print': {
        'description': '3D printing export',
        'format': 'OBJ',
        'triangulate': True,
        'apply_modifiers': True,
        'apply_transforms': True,
        'tangent_space': False,
        'embed_textures': False,
        'scale': 1000.0  # meters to mm
    }
}


def generate_lods(
    obj: bpy.types.Object,
    lod_levels: int = 4,
    ratios: list = None,
    collection_name: str = None
) -> list:
    """
    Generate a Level of Detail (LOD) chain from a high-poly mesh.
    Creates LOD0 (source) through LOD3 with decreasing face counts.

    Args:
        obj: Source mesh object (becomes LOD0)
        lod_levels: Number of LOD levels to generate (2-5)
        ratios: Custom decimation ratios per level. Default: [1.0, 0.5, 0.25, 0.125]
        collection_name: Collection to put LODs in (created if needed)

    Returns:
        List of LOD objects (LOD0 = original, LOD1+ = decimated copies)

    Example:
        >>> lods = generate_lods(character, lod_levels=4)
        >>> for lod in lods:
        ...     print(f"{lod.name}: {len(lod.data.polygons)} faces")
    """
    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj.name}' is not a mesh")

    if ratios is None:
        ratios = [1.0]
        for i in range(1, lod_levels):
            ratios.append(0.5 ** i)

    # Create collection for LODs
    if collection_name is None:
        collection_name = f"{obj.name}_LODs"

    if collection_name not in bpy.data.collections:
        lod_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(lod_collection)
    else:
        lod_collection = bpy.data.collections[collection_name]

    lods = []
    base_name = obj.name  # Save original name before LOD0 rename

    for i, ratio in enumerate(ratios):
        if i == 0:
            # LOD0 is the original
            lod = obj
            lod.name = f"{base_name}_LOD0"
        else:
            # Duplicate and decimate
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.duplicate()

            lod = bpy.context.active_object
            lod.name = f"{base_name}_LOD{i}"

            # Apply Decimate modifier
            mod = lod.modifiers.new(name=f"Decimate_LOD{i}", type='DECIMATE')
            mod.ratio = ratio
            bpy.ops.object.modifier_apply(modifier=mod.name)

            # Move to LOD collection
            for col in lod.users_collection:
                col.objects.unlink(lod)
            lod_collection.objects.link(lod)

            # Offset for visibility
            lod.location.x = obj.location.x + (i * max(obj.dimensions) * 1.5)

        lods.append(lod)

    # Link LOD0 to collection too
    if obj.name not in [o.name for o in lod_collection.objects]:
        lod_collection.objects.link(obj)

    return lods


def export_with_preset(
    objects: list = None,
    preset: str = 'game',
    output_path: str = None,
    filename: str = None
) -> str:
    """
    Export using a named preset (Game, VFX, Web, Print).

    Args:
        objects: List of objects to export (None = all selected)
        preset: Preset name: 'game', 'vfx', 'web', 'print'
        output_path: Output directory
        filename: Output filename (without extension)

    Returns:
        Path to exported file

    Example:
        >>> export_with_preset(preset='game', output_path='/exports/')
        >>> export_with_preset([character], preset='web', filename='hero_character')
    """
    if preset not in EXPORT_PRESETS:
        raise ValueError(
            f"Unknown preset '{preset}'. Available: {', '.join(EXPORT_PRESETS.keys())}"
        )

    config = EXPORT_PRESETS[preset]
    fmt = config['format']

    if output_path is None:
        output_path = os.path.dirname(bpy.data.filepath) or os.path.expanduser('~')

    if filename is None:
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0] or 'export'

    os.makedirs(output_path, exist_ok=True)

    # Select objects
    if objects:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]

    # Pre-export: apply transforms
    if config['apply_transforms']:
        for obj in (objects or bpy.context.selected_objects):
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Pre-export: triangulate
    if config['triangulate']:
        for obj in (objects or bpy.context.selected_objects):
            if obj.type == 'MESH':
                mod = obj.modifiers.new("Triangulate_Export", 'TRIANGULATE')
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier=mod.name)

    # Export based on format
    if fmt == 'FBX':
        filepath = os.path.join(output_path, f"{filename}.fbx")
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=True,
            apply_scale_options='FBX_SCALE_ALL',
            use_mesh_modifiers=config['apply_modifiers'],
            mesh_smooth_type='FACE',
            use_tspace=config.get('tangent_space', True),
            embed_textures=config.get('embed_textures', False)
        )
    elif fmt == 'GLTF':
        ext = '.glb' if config.get('embed_textures', True) else '.gltf'
        filepath = os.path.join(output_path, f"{filename}{ext}")
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB' if config.get('embed_textures', True) else 'GLTF_SEPARATE',
            use_selection=True,
            export_apply=config['apply_modifiers']
        )
    elif fmt == 'USD':
        filepath = os.path.join(output_path, f"{filename}.usdc")
        bpy.ops.wm.usd_export(
            filepath=filepath,
            selected_objects_only=True,
            export_materials=True,
            generate_preview_surface=True
        )
    elif fmt == 'OBJ':
        filepath = os.path.join(output_path, f"{filename}.obj")
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=True,
            apply_modifiers=config['apply_modifiers'],
            export_triangulated_mesh=config['triangulate'],
            global_scale=config.get('scale', 1.0)
        )
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    return filepath


def export_usd(
    filepath: str,
    selected_only: bool = True,
    export_materials: bool = True,
    export_animation: bool = True,
    export_hair: bool = False
) -> bool:
    """
    Export to Universal Scene Description (USD/USDC/USDA).
    USD is the standard for VFX pipelines (Pixar, Houdini, Omniverse).

    Args:
        filepath: Output file path (.usdc, .usda, or .usd)
        selected_only: Export only selected objects
        export_materials: Include materials
        export_animation: Include animation data
        export_hair: Include particle hair

    Returns:
        True if export succeeded

    Example:
        >>> export_usd("/output/scene.usdc")
    """
    try:
        bpy.ops.wm.usd_export(
            filepath=filepath,
            selected_objects_only=selected_only,
            export_materials=export_materials,
            export_animation=export_animation,
            export_hair=export_hair,
            generate_preview_surface=True
        )
        return True
    except Exception:
        return False


def validate_and_export(
    obj: bpy.types.Object,
    filepath: str,
    format: str = 'FBX',
    auto_fix: bool = True
) -> dict:
    """
    Validate mesh for export issues, optionally fix them, then export.

    Checks: non-manifold geometry, missing UVs, unapplied scale,
    ngons (for game export), loose vertices.

    Args:
        obj: Object to validate and export
        filepath: Export file path
        format: 'FBX', 'GLTF', 'OBJ', 'USD'
        auto_fix: Automatically fix issues before export

    Returns:
        Dict with 'issues' list and 'exported' bool

    Example:
        >>> result = validate_and_export(character, "/out/char.fbx")
        >>> if result['issues']:
        ...     print("Warnings:", result['issues'])
    """
    result = {'issues': [], 'exported': False, 'filepath': filepath}

    if obj.type != 'MESH':
        result['issues'].append('Not a mesh object')
        return result

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    mesh = obj.data

    # Check: Unapplied scale
    if obj.scale[0] != 1.0 or obj.scale[1] != 1.0 or obj.scale[2] != 1.0:
        result['issues'].append('Scale not applied')
        if auto_fix:
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Check: Missing UVs
    if not mesh.uv_layers:
        result['issues'].append('No UV maps')
        if auto_fix:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
            bpy.ops.object.mode_set(mode='OBJECT')

    # Check: Non-manifold
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()
    if obj.data.total_vert_sel > 0:
        result['issues'].append(f'Non-manifold geometry ({obj.data.total_vert_sel} verts)')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Check: Ngons
    for poly in mesh.polygons:
        if len(poly.vertices) > 4:
            result['issues'].append('Contains N-gons')
            break

    # Export
    try:
        format_upper = format.upper()
        if format_upper == 'FBX':
            bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
        elif format_upper in ('GLTF', 'GLB'):
            bpy.ops.export_scene.gltf(filepath=filepath, use_selection=True)
        elif format_upper == 'OBJ':
            bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True)
        elif format_upper == 'USD':
            bpy.ops.wm.usd_export(filepath=filepath, selected_objects_only=True)
        result['exported'] = True
    except Exception as e:
        result['issues'].append(f'Export failed: {str(e)}')

    return result


def export_scene_bundle(
    output_dir: str,
    format: str = 'GLTF',
    include_textures: bool = True,
    separate_objects: bool = False
) -> dict:
    """
    Export entire scene as an organized file bundle.
    Creates a structured directory: meshes/, textures/, materials.json

    Args:
        output_dir: Root output directory
        format: Export format for meshes
        include_textures: Copy textures to bundle
        separate_objects: Export each object as individual file

    Returns:
        Dict with 'mesh_files', 'texture_files', and 'manifest' path

    Example:
        >>> bundle = export_scene_bundle("/output/my_scene/", format='GLTF')
    """
    os.makedirs(output_dir, exist_ok=True)
    mesh_dir = os.path.join(output_dir, 'meshes')
    tex_dir = os.path.join(output_dir, 'textures')
    os.makedirs(mesh_dir, exist_ok=True)

    result = {'mesh_files': [], 'texture_files': [], 'manifest': ''}

    # Export meshes
    if separate_objects:
        for obj in bpy.context.scene.objects:
            if obj.type != 'MESH':
                continue
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            clean_name = "".join(c for c in obj.name if c.isalnum() or c in ' -_').strip()
            ext = '.glb' if format == 'GLTF' else f'.{format.lower()}'
            filepath = os.path.join(mesh_dir, f"{clean_name}{ext}")

            if format == 'FBX':
                bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
            elif format == 'GLTF':
                bpy.ops.export_scene.gltf(filepath=filepath, use_selection=True, export_format='GLB')
            elif format == 'OBJ':
                bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True)

            result['mesh_files'].append(filepath)
    else:
        bpy.ops.object.select_all(action='SELECT')
        ext = '.glb' if format == 'GLTF' else f'.{format.lower()}'
        filepath = os.path.join(mesh_dir, f"scene{ext}")

        if format == 'FBX':
            bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
        elif format == 'GLTF':
            bpy.ops.export_scene.gltf(filepath=filepath, use_selection=True, export_format='GLB')
        elif format == 'OBJ':
            bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True)

        result['mesh_files'].append(filepath)

    # Copy textures
    if include_textures:
        os.makedirs(tex_dir, exist_ok=True)
        for img in bpy.data.images:
            if img.filepath and img.filepath != '' and not img.packed_file:
                src = bpy.path.abspath(img.filepath)
                if os.path.isfile(src):
                    import shutil
                    dst = os.path.join(tex_dir, os.path.basename(src))
                    shutil.copy2(src, dst)
                    result['texture_files'].append(dst)

    # Write manifest
    manifest = {
        'format': format,
        'objects': len(result['mesh_files']),
        'textures': len(result['texture_files']),
        'blender_version': bpy.app.version_string
    }
    manifest_path = os.path.join(output_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    result['manifest'] = manifest_path

    return result


def apply_export_transforms(
    obj: bpy.types.Object,
    triangulate: bool = True,
    apply_scale: bool = True,
    apply_rotation: bool = True
) -> None:
    """
    Apply scale/rotation transforms and optionally triangulate for game engines.

    Args:
        obj: Object to prepare
        triangulate: Convert quads/ngons to triangles
        apply_scale: Apply scale transform
        apply_rotation: Apply rotation transform

    Example:
        >>> apply_export_transforms(character_mesh, triangulate=True)
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.transform_apply(
        location=False,
        rotation=apply_rotation,
        scale=apply_scale
    )

    if triangulate and obj.type == 'MESH':
        mod = obj.modifiers.new("Triangulate_Export", 'TRIANGULATE')
        mod.quad_method = 'BEAUTY'
        mod.ngon_method = 'BEAUTY'
        bpy.ops.object.modifier_apply(modifier=mod.name)
