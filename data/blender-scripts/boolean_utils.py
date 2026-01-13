"""
{
  "title": "Boolean Operations Utilities",
  "category": "modeling",
  "tags": ["boolean", "csg", "difference", "union", "intersect", "modifier"],
  "description": "Functions for boolean operations and CSG workflows.",
  "blender_version": "3.0+"
}
"""
import bpy


def add_boolean_modifier(
    target: bpy.types.Object,
    cutter: bpy.types.Object,
    operation: str = 'DIFFERENCE',
    solver: str = 'EXACT',
    apply: bool = False
) -> bpy.types.Modifier:
    """
    Add boolean modifier.
    
    Args:
        target: Object to modify
        cutter: Boolean object
        operation: 'DIFFERENCE', 'UNION', 'INTERSECT'
        solver: 'EXACT', 'FAST'
        apply: Apply modifier immediately
    
    Returns:
        The boolean modifier (if not applied)
    """
    mod = target.modifiers.new(f"Boolean_{cutter.name}", 'BOOLEAN')
    mod.operation = operation
    mod.solver = solver
    mod.object = cutter
    
    if apply:
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=mod.name)
        return None
    
    return mod


def boolean_difference(
    target: bpy.types.Object,
    cutter: bpy.types.Object,
    apply: bool = True,
    hide_cutter: bool = True
) -> bpy.types.Modifier:
    """
    Subtract cutter from target.
    
    Args:
        target: Object to cut
        cutter: Cutting object
        apply: Apply modifier
        hide_cutter: Hide cutter after operation
    """
    mod = add_boolean_modifier(target, cutter, 'DIFFERENCE', apply=apply)
    
    if hide_cutter:
        cutter.hide_set(True)
        cutter.hide_render = True
    
    return mod


def boolean_union(
    target: bpy.types.Object,
    other: bpy.types.Object,
    apply: bool = True,
    delete_other: bool = False
) -> bpy.types.Modifier:
    """
    Combine two objects.
    
    Args:
        target: Base object
        other: Object to add
        apply: Apply modifier
        delete_other: Delete the other object after
    """
    mod = add_boolean_modifier(target, other, 'UNION', apply=apply)
    
    if delete_other and apply:
        bpy.data.objects.remove(other)
    
    return mod


def boolean_intersect(
    target: bpy.types.Object,
    other: bpy.types.Object,
    apply: bool = True
) -> bpy.types.Modifier:
    """
    Keep only intersection of two objects.
    
    Args:
        target: Base object
        other: Intersecting object
        apply: Apply modifier
    """
    return add_boolean_modifier(target, other, 'INTERSECT', apply=apply)


def boolean_slice(
    target: bpy.types.Object,
    cutter: bpy.types.Object,
    separate: bool = True
) -> list:
    """
    Slice object into two parts.
    
    Args:
        target: Object to slice
        cutter: Slicing plane/object
        separate: Create separate objects
    
    Returns:
        List of resulting objects
    """
    # Duplicate for second half
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.duplicate()
    copy = bpy.context.active_object
    
    # Boolean difference on original
    boolean_difference(target, cutter, apply=True, hide_cutter=False)
    
    # Boolean intersect on copy
    boolean_intersect(copy, cutter, apply=True)
    
    cutter.hide_set(True)
    
    return [target, copy]


def create_boolean_cutter_cube(
    location: tuple = (0, 0, 0),
    size: tuple = (1, 1, 1),
    name: str = "BoolCutter"
) -> bpy.types.Object:
    """Create cube for boolean operations."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    cutter = bpy.context.active_object
    cutter.name = name
    cutter.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Set display for visibility
    cutter.display_type = 'WIRE'
    
    return cutter


def create_boolean_cutter_cylinder(
    location: tuple = (0, 0, 0),
    radius: float = 0.5,
    depth: float = 1.0,
    vertices: int = 32,
    name: str = "BoolCutter"
) -> bpy.types.Object:
    """Create cylinder for boolean operations."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        vertices=vertices,
        location=location
    )
    cutter = bpy.context.active_object
    cutter.name = name
    cutter.display_type = 'WIRE'
    
    return cutter


def create_boolean_cutter_sphere(
    location: tuple = (0, 0, 0),
    radius: float = 0.5,
    segments: int = 32,
    name: str = "BoolCutter"
) -> bpy.types.Object:
    """Create sphere for boolean operations."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        segments=segments,
        ring_count=segments // 2,
        location=location
    )
    cutter = bpy.context.active_object
    cutter.name = name
    cutter.display_type = 'WIRE'
    
    return cutter


def apply_all_booleans(obj: bpy.types.Object) -> int:
    """
    Apply all boolean modifiers on object.
    
    Returns:
        Number of modifiers applied
    """
    count = 0
    bpy.context.view_layer.objects.active = obj
    
    for mod in obj.modifiers[:]:
        if mod.type == 'BOOLEAN':
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
                count += 1
            except:
                pass
    
    return count


def set_boolean_collection(
    target: bpy.types.Object,
    collection: bpy.types.Collection,
    operation: str = 'DIFFERENCE'
) -> bpy.types.Modifier:
    """
    Use collection as boolean operand.
    
    Args:
        target: Object to modify
        collection: Collection of cutter objects
        operation: Boolean operation
    
    Returns:
        The boolean modifier
    """
    mod = target.modifiers.new(f"Boolean_{collection.name}", 'BOOLEAN')
    mod.operation = operation
    mod.operand_type = 'COLLECTION'
    mod.collection = collection
    mod.solver = 'EXACT'
    
    return mod


def cleanup_boolean_meshes(obj: bpy.types.Object) -> None:
    """Clean up mesh after boolean operations."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Merge close vertices
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    
    # Remove internal faces
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_interior_faces()
    bpy.ops.mesh.delete(type='FACE')
    
    # Recalculate normals
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    
    bpy.ops.object.mode_set(mode='OBJECT')
