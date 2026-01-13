"""
{
  "title": "Export Pipeline Utilities",
  "category": "io",
  "tags": ["export", "fbx", "gltf", "obj", "batch", "pipeline"],
  "description": "Functions for batch export and pipeline operations.",
  "blender_version": "3.0+"
}
"""
import bpy
import os


def export_selected_fbx(
    filepath: str,
    apply_modifiers: bool = True,
    apply_transforms: bool = True,
    mesh_only: bool = False,
    include_armature: bool = True,
    use_mesh_edges: bool = False
) -> bool:
    """
    Export selected objects to FBX.
    
    Args:
        filepath: Output path
        apply_modifiers: Apply modifiers on export
        apply_transforms: Apply transforms
        mesh_only: Export only mesh data
        include_armature: Include armature if present
        use_mesh_edges: Include edge data
    
    Returns:
        Success status
    """
    object_types = {'MESH'}
    if include_armature:
        object_types.add('ARMATURE')
    
    try:
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=True,
            apply_scale_options='FBX_SCALE_ALL',
            use_mesh_modifiers=apply_modifiers,
            mesh_smooth_type='FACE',
            use_mesh_edges=use_mesh_edges,
            object_types=object_types,
            bake_space_transform=apply_transforms
        )
        return True
    except:
        return False


def export_selected_gltf(
    filepath: str,
    format: str = 'GLB',
    apply_modifiers: bool = True,
    export_materials: str = 'EXPORT',
    export_animations: bool = True,
    export_textures: bool = True
) -> bool:
    """
    Export selected objects to glTF/GLB.
    
    Args:
        filepath: Output path
        format: 'GLB', 'GLTF_SEPARATE', 'GLTF_EMBEDDED'
        apply_modifiers: Apply modifiers
        export_materials: 'NONE', 'PLACEHOLDER', 'EXPORT'
        export_animations: Include animations
        export_textures: Include textures
    
    Returns:
        Success status
    """
    try:
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format=format,
            use_selection=True,
            export_apply=apply_modifiers,
            export_materials=export_materials,
            export_animations=export_animations,
            export_image_format='AUTO' if export_textures else 'NONE'
        )
        return True
    except:
        return False


def export_selected_obj(
    filepath: str,
    apply_modifiers: bool = True,
    include_normals: bool = True,
    include_uvs: bool = True,
    include_materials: bool = True,
    triangulate: bool = False
) -> bool:
    """
    Export selected objects to OBJ.
    
    Returns:
        Success status
    """
    try:
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=True,
            apply_modifiers=apply_modifiers,
            export_normals=include_normals,
            export_uv=include_uvs,
            export_materials=include_materials,
            export_triangulated_mesh=triangulate
        )
        return True
    except:
        return False


def batch_export_objects(
    output_dir: str,
    format: str = 'FBX',
    each_object: bool = True,
    naming: str = 'OBJECT'
) -> list:
    """
    Export multiple objects to individual files.
    
    Args:
        output_dir: Output directory
        format: 'FBX', 'GLTF', 'OBJ'
        each_object: Export each object separately
        naming: 'OBJECT' (use object name) or 'COLLECTION' (use collection name)
    
    Returns:
        List of exported file paths
    """
    exported = []
    os.makedirs(output_dir, exist_ok=True)
    
    objects = bpy.context.selected_objects
    
    bpy.ops.object.select_all(action='DESELECT')
    
    for obj in objects:
        if obj.type != 'MESH':
            continue
        
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Determine filename
        if naming == 'COLLECTION' and obj.users_collection:
            name = obj.users_collection[0].name
        else:
            name = obj.name
        
        # Clean filename
        name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        
        if format == 'FBX':
            filepath = os.path.join(output_dir, f"{name}.fbx")
            export_selected_fbx(filepath)
        elif format == 'GLTF':
            filepath = os.path.join(output_dir, f"{name}.glb")
            export_selected_gltf(filepath)
        else:
            filepath = os.path.join(output_dir, f"{name}.obj")
            export_selected_obj(filepath)
        
        exported.append(filepath)
        obj.select_set(False)
    
    return exported


def prepare_for_export(
    obj: bpy.types.Object,
    apply_modifiers: bool = True,
    apply_transforms: bool = True,
    triangulate: bool = False
) -> None:
    """
    Prepare object for export.
    
    Args:
        obj: Object to prepare
        apply_modifiers: Apply all modifiers
        apply_transforms: Apply location/rotation/scale
        triangulate: Convert to triangles
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    if apply_transforms:
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    if apply_modifiers:
        for mod in obj.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except:
                pass
    
    if triangulate:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.mode_set(mode='OBJECT')


def export_uv_layout(
    obj: bpy.types.Object,
    filepath: str,
    size: tuple = (1024, 1024),
    opacity: float = 0.25
) -> bool:
    """
    Export UV layout as image.
    
    Args:
        obj: Object with UVs
        filepath: Output image path
        size: Image dimensions
        opacity: Fill opacity
    
    Returns:
        Success status
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    try:
        bpy.ops.uv.export_layout(
            filepath=filepath,
            size=size,
            opacity=opacity,
            export_all=True
        )
        return True
    except:
        return False


def validate_mesh_for_export(obj: bpy.types.Object) -> dict:
    """
    Validate mesh for common export issues.
    
    Returns:
        Dictionary with validation results
    """
    issues = {
        'has_ngons': False,
        'has_loose_verts': False,
        'has_loose_edges': False,
        'has_non_manifold': False,
        'missing_uvs': False,
        'scale_not_applied': False
    }
    
    if obj.type != 'MESH':
        return issues
    
    mesh = obj.data
    
    # Check for ngons
    for poly in mesh.polygons:
        if len(poly.vertices) > 4:
            issues['has_ngons'] = True
            break
    
    # Check UVs
    if not mesh.uv_layers:
        issues['missing_uvs'] = True
    
    # Check scale
    if obj.scale != (1, 1, 1):
        issues['scale_not_applied'] = True
    
    # Check topology
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    bpy.ops.mesh.select_loose()
    if bpy.context.object.data.total_vert_sel > 0:
        issues['has_loose_verts'] = True
    
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()
    if bpy.context.object.data.total_vert_sel > 0:
        issues['has_non_manifold'] = True
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return issues
