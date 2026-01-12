"""
{
  "title": "Mesh Editing Utilities",
  "category": "mesh",
  "tags": ["mesh", "bevel", "extrude", "subdivide", "decimate", "boolean", "edit"],
  "description": "Advanced mesh editing operations including bevel, extrude, bridge, fill, and subdivision.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def bevel_edges(
    offset: float = 0.1,
    segments: int = 3,
    profile: float = 0.5,
    affect: str = 'EDGES',
    clamp_overlap: bool = True,
    harden_normals: bool = False
) -> None:
    """
    Apply bevel to selected edges or vertices.
    
    Args:
        offset: Bevel width
        segments: Number of segments for curved bevel
        profile: Shape profile (0.5 = round, 0 = flat, 1 = pointed)
        affect: 'EDGES' or 'VERTICES'
        clamp_overlap: Prevent overlapping bevels
        harden_normals: Match normals to adjacent faces
    
    Example:
        >>> bpy.ops.object.mode_set(mode='EDIT')
        >>> bpy.ops.mesh.select_all(action='SELECT')
        >>> bevel_edges(offset=0.2, segments=4)
    """
    bpy.ops.mesh.bevel(
        offset=offset,
        segments=segments,
        profile=profile,
        affect=affect,
        clamp_overlap=clamp_overlap,
        harden_normals=harden_normals
    )


def extrude_region(
    direction: tuple = (0, 0, 1),
    amount: float = 1.0
) -> None:
    """
    Extrude selected faces in a direction.
    
    Args:
        direction: XYZ direction vector (normalized)
        amount: Extrusion distance
    
    Example:
        >>> extrude_region((0, 0, 1), 2.0)  # Extrude up
    """
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={
            "value": tuple(d * amount for d in direction)
        }
    )


def bridge_edge_loops(
    segments: int = 0,
    smoothness: float = 1.0,
    interpolation: str = 'PATH'
) -> None:
    """
    Bridge two selected edge loops with faces.
    
    Args:
        segments: Number of intermediate cuts (0 = direct bridge)
        smoothness: Curvature smoothing factor
        interpolation: 'LINEAR', 'PATH', or 'SURFACE'
    
    Example:
        >>> bridge_edge_loops(segments=3, smoothness=0.5)
    """
    bpy.ops.mesh.bridge_edge_loops(
        number_cuts=segments,
        smoothness=smoothness,
        interpolation=interpolation
    )


def fill_holes(max_sides: int = 0) -> None:
    """
    Fill holes in the mesh.
    
    Args:
        max_sides: Maximum hole size to fill (0 = all holes)
    
    Example:
        >>> fill_holes(max_sides=8)
    """
    bpy.ops.mesh.fill_holes(sides=max_sides)


def subdivide_mesh(
    cuts: int = 1,
    smoothness: float = 0.0,
    fractal: float = 0.0
) -> None:
    """
    Subdivide selected mesh faces.
    
    Args:
        cuts: Number of subdivision cuts
        smoothness: Smoothing amount
        fractal: Random displacement for terrain-like results
    
    Example:
        >>> subdivide_mesh(cuts=2, smoothness=0.5)
    """
    bpy.ops.mesh.subdivide(
        number_cuts=cuts,
        smoothness=smoothness,
        fractal=fractal
    )


def decimate_mesh(
    ratio: float = 0.5,
    use_symmetry: bool = False,
    symmetry_axis: str = 'X'
) -> None:
    """
    Reduce polygon count of selected mesh.
    
    Args:
        ratio: Target ratio (0.5 = 50% of original)
        use_symmetry: Maintain symmetry on axis
        symmetry_axis: 'X', 'Y', or 'Z'
    
    Example:
        >>> decimate_mesh(ratio=0.3)  # Reduce to 30%
    """
    bpy.ops.mesh.decimate(
        ratio=ratio,
        use_symmetry=use_symmetry,
        symmetry_axis=symmetry_axis
    )


def inset_faces(
    thickness: float = 0.1,
    depth: float = 0.0,
    use_boundary: bool = True,
    use_individual: bool = False
) -> None:
    """
    Inset selected faces.
    
    Args:
        thickness: Inset distance
        depth: Depth relative to face
        use_boundary: Inset boundary faces
        use_individual: Inset each face individually
    
    Example:
        >>> inset_faces(thickness=0.2, depth=-0.1)
    """
    bpy.ops.mesh.inset(
        thickness=thickness,
        depth=depth,
        use_boundary=use_boundary,
        use_individual=use_individual
    )


def bisect_mesh(
    plane_co: tuple = (0, 0, 0),
    plane_no: tuple = (0, 0, 1),
    use_fill: bool = False,
    clear_inner: bool = False,
    clear_outer: bool = False
) -> None:
    """
    Cut mesh along a plane.
    
    Args:
        plane_co: Point on the plane
        plane_no: Plane normal direction
        use_fill: Fill the cut with faces
        clear_inner: Remove geometry behind plane
        clear_outer: Remove geometry in front of plane
    
    Example:
        >>> bisect_mesh((0, 0, 1), (0, 0, 1), clear_outer=True)  # Cut at Z=1
    """
    bpy.ops.mesh.bisect(
        plane_co=plane_co,
        plane_no=plane_no,
        use_fill=use_fill,
        clear_inner=clear_inner,
        clear_outer=clear_outer
    )


def dissolve_edges(
    use_verts: bool = True,
    angle_threshold: float = None
) -> None:
    """
    Dissolve selected edges, merging adjacent faces.
    
    Args:
        use_verts: Also dissolve resulting 2-edge vertices
        angle_threshold: Preserve sharp edges above this angle (radians)
    
    Example:
        >>> dissolve_edges()
    """
    kwargs = {'use_verts': use_verts}
    if angle_threshold is not None:
        kwargs['angle_threshold'] = angle_threshold
    bpy.ops.mesh.dissolve_edges(**kwargs)


def flip_normals() -> None:
    """Flip normals of selected faces."""
    bpy.ops.mesh.flip_normals()


def recalculate_normals(inside: bool = False) -> None:
    """
    Recalculate normals to point outward (or inward).
    
    Args:
        inside: Point normals inward instead
    """
    bpy.ops.mesh.normals_make_consistent(inside=inside)


def merge_vertices(
    type: str = 'CENTER',
    threshold: float = 0.0001
) -> None:
    """
    Merge selected vertices.
    
    Args:
        type: 'CENTER', 'CURSOR', 'COLLAPSE', 'FIRST', 'LAST'
        threshold: Merge by distance threshold (for auto-merge)
    
    Example:
        >>> merge_vertices('CENTER')
    """
    if type in ('CENTER', 'CURSOR', 'COLLAPSE'):
        bpy.ops.mesh.merge(type=type)
    else:
        bpy.ops.mesh.remove_doubles(threshold=threshold)


def separate_by_selection() -> None:
    """Separate selected geometry into a new object."""
    bpy.ops.mesh.separate(type='SELECTED')


def separate_by_material() -> None:
    """Separate geometry by material into new objects."""
    bpy.ops.mesh.separate(type='MATERIAL')


def separate_by_loose() -> None:
    """Separate disconnected geometry into new objects."""
    bpy.ops.mesh.separate(type='LOOSE')
