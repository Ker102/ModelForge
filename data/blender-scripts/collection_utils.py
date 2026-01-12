"""
{
  "title": "Collection Management Utilities",
  "category": "organization",
  "tags": ["collection", "organize", "layer", "visibility", "hierarchy"],
  "description": "Functions for organizing objects into collections.",
  "blender_version": "3.0+"
}
"""
import bpy


def create_collection(
    name: str,
    parent: bpy.types.Collection = None
) -> bpy.types.Collection:
    """
    Create a new collection.
    
    Args:
        name: Collection name
        parent: Parent collection (uses scene collection if None)
    
    Returns:
        The created collection
    """
    collection = bpy.data.collections.new(name)
    
    if parent:
        parent.children.link(collection)
    else:
        bpy.context.scene.collection.children.link(collection)
    
    return collection


def move_to_collection(
    obj: bpy.types.Object,
    collection: bpy.types.Collection,
    unlink_others: bool = True
) -> None:
    """Move object to collection."""
    if unlink_others:
        for coll in obj.users_collection:
            coll.objects.unlink(obj)
    
    if obj.name not in collection.objects:
        collection.objects.link(obj)


def move_selected_to_collection(
    collection: bpy.types.Collection,
    unlink_others: bool = True
) -> None:
    """Move all selected objects to collection."""
    for obj in bpy.context.selected_objects:
        move_to_collection(obj, collection, unlink_others)


def get_or_create_collection(name: str) -> bpy.types.Collection:
    """Get existing or create new collection."""
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    return create_collection(name)


def set_collection_visibility(
    collection: bpy.types.Collection,
    visible: bool = True,
    viewport: bool = True,
    render: bool = True
) -> None:
    """Set collection visibility."""
    # Find layer collection
    def find_layer_collection(layer_coll, name):
        if layer_coll.name == name:
            return layer_coll
        for child in layer_coll.children:
            result = find_layer_collection(child, name)
            if result:
                return result
        return None
    
    layer_coll = find_layer_collection(
        bpy.context.view_layer.layer_collection,
        collection.name
    )
    
    if layer_coll:
        layer_coll.exclude = not visible
    
    collection.hide_viewport = not viewport
    collection.hide_render = not render


def delete_collection(
    collection: bpy.types.Collection,
    delete_objects: bool = False
) -> None:
    """Delete collection."""
    if delete_objects:
        for obj in collection.objects[:]:
            bpy.data.objects.remove(obj)
    
    bpy.data.collections.remove(collection)


def organize_by_type() -> dict:
    """Organize scene objects by type into collections."""
    collections = {}
    
    type_names = {
        'MESH': 'Meshes',
        'CURVE': 'Curves',
        'LIGHT': 'Lights',
        'CAMERA': 'Cameras',
        'ARMATURE': 'Armatures',
        'EMPTY': 'Empties'
    }
    
    for obj in bpy.context.scene.objects:
        type_name = type_names.get(obj.type, 'Other')
        
        if type_name not in collections:
            collections[type_name] = get_or_create_collection(type_name)
        
        move_to_collection(obj, collections[type_name])
    
    return collections


def select_collection_objects(collection: bpy.types.Collection) -> None:
    """Select all objects in collection."""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.objects:
        obj.select_set(True)


def get_collection_bounds(collection: bpy.types.Collection) -> tuple:
    """Get bounding box of all objects in collection."""
    min_co = [float('inf')] * 3
    max_co = [float('-inf')] * 3
    
    for obj in collection.objects:
        if obj.type == 'MESH':
            for corner in obj.bound_box:
                world_co = obj.matrix_world @ corner
                for i in range(3):
                    min_co[i] = min(min_co[i], world_co[i])
                    max_co[i] = max(max_co[i], world_co[i])
    
    return tuple(min_co), tuple(max_co)
