"""
{
  "title": "Import/Export Utilities",
  "category": "io",
  "tags": ["import", "export", "fbx", "gltf", "obj", "stl", "file"],
  "description": "Functions for importing and exporting 3D file formats.",
  "blender_version": "3.0+"
}
"""
import bpy
import os


def export_gltf(
    filepath: str,
    export_selected: bool = True,
    export_animations: bool = True,
    export_materials: bool = True
) -> None:
    """
    Export to glTF/GLB format.
    
    Args:
        filepath: Output path (.gltf or .glb)
        export_selected: Only export selected objects
        export_animations: Include animations
        export_materials: Include materials
    """
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        use_selection=export_selected,
        export_animations=export_animations,
        export_materials='EXPORT' if export_materials else 'NONE'
    )


def import_gltf(filepath: str) -> list:
    """Import glTF/GLB file. Returns imported objects."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=filepath)
    after = set(bpy.data.objects)
    return list(after - before)


def export_fbx(
    filepath: str,
    export_selected: bool = True,
    apply_modifiers: bool = True,
    include_armature: bool = True
) -> None:
    """Export to FBX format."""
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=export_selected,
        apply_modifiers=apply_modifiers,
        add_leaf_bones=False,
        bake_anim=include_armature
    )


def import_fbx(filepath: str, auto_bone_orientation: bool = True) -> list:
    """Import FBX file."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(
        filepath=filepath,
        automatic_bone_orientation=auto_bone_orientation
    )
    after = set(bpy.data.objects)
    return list(after - before)


def export_obj(
    filepath: str,
    export_selected: bool = True,
    export_materials: bool = True
) -> None:
    """Export to OBJ format."""
    bpy.ops.wm.obj_export(
        filepath=filepath,
        export_selected_objects=export_selected,
        export_materials=export_materials
    )


def import_obj(filepath: str) -> list:
    """Import OBJ file."""
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=filepath)
    after = set(bpy.data.objects)
    return list(after - before)


def export_stl(
    filepath: str,
    export_selected: bool = True,
    ascii_format: bool = False
) -> None:
    """Export to STL format for 3D printing."""
    bpy.ops.export_mesh.stl(
        filepath=filepath,
        use_selection=export_selected,
        ascii=ascii_format
    )


def import_stl(filepath: str) -> list:
    """Import STL file."""
    before = set(bpy.data.objects)
    bpy.ops.import_mesh.stl(filepath=filepath)
    after = set(bpy.data.objects)
    return list(after - before)


def export_usd(
    filepath: str,
    export_selected: bool = True
) -> None:
    """Export to USD/USDA/USDC format."""
    bpy.ops.wm.usd_export(
        filepath=filepath,
        selected_objects_only=export_selected
    )


def import_usd(filepath: str) -> list:
    """Import USD file."""
    before = set(bpy.data.objects)
    bpy.ops.wm.usd_import(filepath=filepath)
    after = set(bpy.data.objects)
    return list(after - before)


def batch_export(
    directory: str,
    format: str = 'GLTF',
    separate_files: bool = True
) -> list:
    """
    Export all/selected objects to directory.
    
    Args:
        directory: Output directory
        format: 'GLTF', 'FBX', 'OBJ', 'STL'
        separate_files: One file per object
    
    Returns:
        List of exported file paths
    """
    os.makedirs(directory, exist_ok=True)
    exported = []
    
    objects = bpy.context.selected_objects or bpy.context.scene.objects
    
    if separate_files:
        for obj in objects:
            if obj.type == 'MESH':
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                
                ext = {'GLTF': '.glb', 'FBX': '.fbx', 'OBJ': '.obj', 'STL': '.stl'}
                filepath = os.path.join(directory, obj.name + ext.get(format, '.glb'))
                
                if format == 'GLTF':
                    export_gltf(filepath, export_selected=True)
                elif format == 'FBX':
                    export_fbx(filepath, export_selected=True)
                elif format == 'OBJ':
                    export_obj(filepath, export_selected=True)
                elif format == 'STL':
                    export_stl(filepath, export_selected=True)
                
                exported.append(filepath)
    
    return exported
