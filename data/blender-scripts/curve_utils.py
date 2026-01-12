"""
{
  "title": "Curve and Path Utilities",
  "category": "curves",
  "tags": ["curve", "bezier", "nurbs", "path", "spline", "handles"],
  "description": "Functions for creating and manipulating curves, paths, and splines.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def create_bezier_curve(
    points: list,
    cyclic: bool = False,
    resolution: int = 12,
    name: str = "BezierCurve"
) -> bpy.types.Object:
    """
    Create a bezier curve from points.
    
    Args:
        points: List of (x, y, z) tuples
        cyclic: Close the curve
        resolution: Curve smoothness
        name: Object name
    
    Returns:
        The created curve object
    
    Example:
        >>> pts = [(0,0,0), (1,0,1), (2,0,0), (3,0,1)]
        >>> curve = create_bezier_curve(pts)
    """
    curve_data = bpy.data.curves.new(name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = resolution
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    
    for i, point in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = point
        bp.handle_type_left = 'AUTO'
        bp.handle_type_right = 'AUTO'
    
    spline.use_cyclic_u = cyclic
    
    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    return curve_obj


def create_nurbs_curve(
    points: list,
    order: int = 4,
    cyclic: bool = False,
    name: str = "NurbsCurve"
) -> bpy.types.Object:
    """
    Create a NURBS curve from points.
    
    Args:
        points: List of (x, y, z) tuples
        order: NURBS order (2-6)
        cyclic: Close the curve
        name: Object name
    
    Returns:
        The created curve object
    """
    curve_data = bpy.data.curves.new(name, type='CURVE')
    curve_data.dimensions = '3D'
    
    spline = curve_data.splines.new('NURBS')
    spline.points.add(len(points) - 1)
    
    for i, point in enumerate(points):
        spline.points[i].co = (*point, 1.0)  # w=1
    
    spline.order_u = order
    spline.use_cyclic_u = cyclic
    spline.use_endpoint_u = True
    
    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    return curve_obj


def create_circle_curve(
    radius: float = 1.0,
    location: tuple = (0, 0, 0),
    name: str = "Circle"
) -> bpy.types.Object:
    """Create a circle curve."""
    bpy.ops.curve.primitive_bezier_circle_add(
        radius=radius,
        location=location
    )
    circle = bpy.context.active_object
    circle.name = name
    return circle


def create_path(
    length: float = 5.0,
    location: tuple = (0, 0, 0),
    name: str = "Path"
) -> bpy.types.Object:
    """Create a straight path curve for animation."""
    bpy.ops.curve.primitive_nurbs_path_add(location=location)
    path = bpy.context.active_object
    path.name = name
    path.data.path_duration = 100
    
    # Scale to length
    path.scale.x = length / 5
    bpy.ops.object.transform_apply(scale=True)
    
    return path


def curve_to_mesh(curve: bpy.types.Object) -> bpy.types.Object:
    """Convert curve to mesh."""
    bpy.context.view_layer.objects.active = curve
    curve.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return bpy.context.active_object


def add_bevel_to_curve(
    curve: bpy.types.Object,
    depth: float = 0.1,
    resolution: int = 4
) -> None:
    """Add bevel/thickness to curve."""
    curve.data.bevel_depth = depth
    curve.data.bevel_resolution = resolution


def add_taper_to_curve(
    curve: bpy.types.Object,
    taper_curve: bpy.types.Object
) -> None:
    """Add taper object to control curve thickness."""
    curve.data.taper_object = taper_curve


def extrude_curve(curve: bpy.types.Object, amount: float = 0.5) -> None:
    """Extrude curve in Z direction."""
    curve.data.extrude = amount


def set_curve_fill(curve: bpy.types.Object, fill_mode: str = 'FULL') -> None:
    """Set curve fill mode: 'NONE', 'BACK', 'FRONT', 'FULL'."""
    curve.data.fill_mode = fill_mode


def create_spiral(
    turns: int = 5,
    height: float = 2.0,
    start_radius: float = 1.0,
    end_radius: float = 0.5,
    points_per_turn: int = 16,
    name: str = "Spiral"
) -> bpy.types.Object:
    """
    Create a spiral curve.
    
    Args:
        turns: Number of complete rotations
        height: Total height
        start_radius: Starting radius
        end_radius: Ending radius
        points_per_turn: Resolution
        name: Object name
    
    Returns:
        Spiral curve object
    """
    total_points = turns * points_per_turn
    points = []
    
    for i in range(total_points + 1):
        t = i / total_points
        angle = t * turns * 2 * math.pi
        radius = start_radius + (end_radius - start_radius) * t
        z = t * height
        
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        
        points.append((x, y, z))
    
    return create_bezier_curve(points, name=name)


def create_helix(
    radius: float = 1.0,
    height: float = 3.0,
    turns: int = 5,
    name: str = "Helix"
) -> bpy.types.Object:
    """Create a helix (constant radius spiral)."""
    return create_spiral(
        turns=turns,
        height=height,
        start_radius=radius,
        end_radius=radius,
        name=name
    )
