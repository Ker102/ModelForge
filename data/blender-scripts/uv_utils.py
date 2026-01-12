"""
{
  "title": "UV Mapping Utilities",
  "category": "uv",
  "tags": ["uv", "unwrap", "texture", "mapping", "projection", "seams"],
  "description": "Utility functions for UV unwrapping and texture coordinate management in Blender.",
  "blender_version": "3.0+"
}
"""
import bpy
import bmesh
import math


def smart_uv_project(
    obj: bpy.types.Object,
    angle_limit: float = 66.0,
    island_margin: float = 0.02,
    scale_to_bounds: bool = True
) -> None:
    """
    Apply smart UV projection to an object.
    
    Args:
        obj: Object to unwrap
        angle_limit: Angle for splitting in degrees
        island_margin: Space between UV islands
        scale_to_bounds: Scale UVs to fit 0-1 space
    
    Example:
        >>> smart_uv_project(complex_mesh, angle_limit=45)
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(angle_limit),
        island_margin=island_margin,
        scale_to_bounds=scale_to_bounds
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')


def cube_project(
    obj: bpy.types.Object,
    cube_size: float = 1.0,
    correct_aspect: bool = True
) -> None:
    """
    Apply cube projection UV mapping.
    
    Best for: Box-like objects, buildings, rooms
    
    Args:
        obj: Object to unwrap
        cube_size: Scale of the projection
        correct_aspect: Correct for non-square faces
    
    Example:
        >>> cube_project(building_mesh, cube_size=2.0)
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.uv.cube_project(
        cube_size=cube_size,
        correct_aspect=correct_aspect
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')


def cylinder_project(
    obj: bpy.types.Object,
    direction: str = 'Z',
    radius: float = 1.0
) -> None:
    """
    Apply cylindrical projection UV mapping.
    
    Best for: Cylindrical objects, bottles, poles
    
    Args:
        obj: Object to unwrap
        direction: Cylinder axis ('X', 'Y', 'Z')
        radius: Cylinder radius
    
    Example:
        >>> cylinder_project(bottle_mesh, direction='Z')
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.uv.cylinder_project(
        direction=direction,
        radius=radius
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')


def sphere_project(
    obj: bpy.types.Object,
    direction: str = 'VIEW_ON_EQUATOR'
) -> None:
    """
    Apply spherical projection UV mapping.
    
    Best for: Spheres, planets, globes
    
    Args:
        obj: Object to unwrap
        direction: Projection direction
    
    Example:
        >>> sphere_project(planet_mesh)
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.uv.sphere_project(direction=direction)
    
    bpy.ops.object.mode_set(mode='OBJECT')


def unwrap_with_seams(
    obj: bpy.types.Object,
    seam_angle: float = 30.0,
    margin: float = 0.02
) -> None:
    """
    Automatically mark seams based on sharp edges and unwrap.
    
    Args:
        obj: Object to unwrap
        seam_angle: Minimum angle for seam (degrees)
        margin: UV island margin
    
    Example:
        >>> unwrap_with_seams(character_mesh, seam_angle=45)
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Clear existing seams
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.mark_seam(clear=True)
    
    # Mark seams from sharp edges
    bpy.ops.mesh.edges_select_sharp(sharpness=math.radians(seam_angle))
    bpy.ops.mesh.mark_seam()
    
    # Unwrap
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=margin)
    
    bpy.ops.object.mode_set(mode='OBJECT')


def pack_islands(
    obj: bpy.types.Object,
    margin: float = 0.02,
    rotate: bool = True
) -> None:
    """
    Pack UV islands to minimize unused space.
    
    Args:
        obj: Object with UVs to pack
        margin: Space between islands
        rotate: Allow rotation for better packing
    
    Example:
        >>> pack_islands(model, margin=0.01)
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.uv.pack_islands(margin=margin, rotate=rotate)
    
    bpy.ops.object.mode_set(mode='OBJECT')


def average_islands_scale(obj: bpy.types.Object) -> None:
    """
    Equalize the scale of all UV islands for consistent texel density.
    
    Args:
        obj: Object with UVs to adjust
    
    Example:
        >>> average_islands_scale(game_asset)
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.uv.average_islands_scale()
    
    bpy.ops.object.mode_set(mode='OBJECT')


def add_uv_layer(
    obj: bpy.types.Object,
    name: str = "UVMap_Alt"
) -> bpy.types.MeshUVLoopLayer:
    """
    Add a new UV layer to an object.
    
    Args:
        obj: Target object
        name: UV layer name
    
    Returns:
        The created UV layer
    
    Example:
        >>> lightmap_uv = add_uv_layer(model, "Lightmap")
    """
    mesh = obj.data
    uv_layer = mesh.uv_layers.new(name=name)
    return uv_layer


def set_active_uv_layer(
    obj: bpy.types.Object,
    layer_name: str
) -> bool:
    """
    Set the active UV layer by name.
    
    Args:
        obj: Target object
        layer_name: Name of UV layer to activate
    
    Returns:
        True if layer was found and activated
    """
    mesh = obj.data
    for uv_layer in mesh.uv_layers:
        if uv_layer.name == layer_name:
            mesh.uv_layers.active = uv_layer
            return True
    return False
