"""
{
  "title": "Idempotent Mesh Factory Pattern",
  "category": "modeling",
  "subcategory": "utility",
  "tags": ["mesh", "factory", "from_pydata", "bmesh", "idempotent", "cleanup", "foreach_set", "numpy", "vertex", "face"],
  "difficulty": "intermediate",
  "description": "Factory pattern for creating mesh objects idempotently: removes existing objects with same name, creates mesh via from_pydata or BMesh, and applies materials. Includes NumPy foreach_set optimization for large meshes.",
  "blender_version": "5.0+",
  "estimated_objects": 1
}
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix


def create_mesh_object(
    name: str,
    vertices: list,
    edges: list = None,
    faces: list = None,
    location: tuple = (0, 0, 0),
    collection: str = None,
    replace_existing: bool = True
) -> bpy.types.Object:
    """
    Idempotent mesh factory: creates a mesh object from vertex/face data.
    If an object with the same name exists, it is removed first.

    This is the canonical way to create mesh objects in Blender 5.x scripts.
    Use this instead of bpy.ops.mesh.primitive_* when you need precise geometry.

    Args:
        name: Object name (also used for mesh datablock)
        vertices: List of (x, y, z) vertex positions
        edges: List of (v1, v2) edge index pairs (optional)
        faces: List of (v1, v2, v3, ...) face index tuples
        location: World position
        collection: Collection name (None = active collection)
        replace_existing: Remove existing object with same name

    Returns:
        The new mesh object

    Example:
        >>> verts = [(0,0,0), (1,0,0), (1,1,0), (0,1,0)]
        >>> faces = [(0,1,2,3)]
        >>> obj = create_mesh_object("MyPlane", verts, faces=faces)
    """
    if edges is None:
        edges = []
    if faces is None:
        faces = []

    # Idempotent: remove existing object with same name
    if replace_existing:
        remove_object_by_name(name)

    # Create mesh data
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()
    mesh.validate()

    # Create object
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location

    # Link to collection
    if collection:
        col = bpy.data.collections.get(collection)
        if not col:
            col = bpy.data.collections.new(collection)
            bpy.context.scene.collection.children.link(col)
        col.objects.link(obj)
    else:
        bpy.context.collection.objects.link(obj)

    # Make active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    return obj


def remove_object_by_name(name: str) -> bool:
    """
    Safely remove an object and its mesh data by name.
    Used for idempotent object creation.

    Args:
        name: Object name to remove

    Returns:
        True if object was found and removed

    Example:
        >>> remove_object_by_name("OldSword")
    """
    obj = bpy.data.objects.get(name)
    if obj:
        # Remove from all collections
        for col in obj.users_collection:
            col.objects.unlink(obj)

        # Remove mesh data
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)

        # Clean up orphan mesh
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)

        return True
    return False


def create_mesh_with_bmesh(
    name: str,
    build_fn: callable,
    location: tuple = (0, 0, 0),
    replace_existing: bool = True,
    apply_smooth: bool = False
) -> bpy.types.Object:
    """
    Create a mesh object using BMesh for complex procedural geometry.
    Pass a build function that receives the bmesh instance.

    Args:
        name: Object name
        build_fn: Function that takes a bmesh.types.BMesh and adds geometry
        location: World position
        replace_existing: Remove existing object
        apply_smooth: Auto-smooth the mesh

    Returns:
        The new mesh object

    Example:
        >>> def build(bm):
        ...     bmesh.ops.create_cube(bm, size=1.0)
        ...     bmesh.ops.bevel(bm, geom=bm.edges, offset=0.05, segments=2)
        >>> obj = create_mesh_with_bmesh("BevelCube", build)
    """
    if replace_existing:
        remove_object_by_name(name)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    try:
        # Call the build function
        build_fn(bm)

        # Recalculate normals
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        # Write to mesh
        bm.to_mesh(mesh)
    finally:
        bm.free()

    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)

    if apply_smooth:
        obj.data.shade_smooth()

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    return obj


def apply_material(
    obj: bpy.types.Object,
    base_color: tuple = (0.8, 0.8, 0.8, 1.0),
    metallic: float = 0.0,
    roughness: float = 0.5,
    material_name: str = None
) -> bpy.types.Material:
    """
    Apply a Principled BSDF material to an object.

    Args:
        obj: Target object
        base_color: RGBA color
        metallic: Metallic factor (0-1)
        roughness: Roughness factor (0-1)
        material_name: Material name (auto-generated if None)

    Returns:
        The material

    Example:
        >>> apply_material(sword, base_color=(0.7, 0.7, 0.72, 1.0), metallic=1.0, roughness=0.3)
    """
    name = material_name or f"{obj.name}_Material"
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness

    obj.data.materials.clear()
    obj.data.materials.append(mat)

    return mat


def create_mesh_numpy(
    name: str,
    vertices,
    faces,
    normals=None,
    location: tuple = (0, 0, 0),
    replace_existing: bool = True
) -> bpy.types.Object:
    """
    High-performance mesh creation using NumPy foreach_set.
    10-100x faster than from_pydata for large meshes (>10K vertices).

    Args:
        name: Object name
        vertices: numpy array of shape (N, 3) — vertex positions
        faces: numpy array — flat loop indices, or list of face tuples
        normals: numpy array of shape (N, 3) — custom normals (optional)
        location: World position
        replace_existing: Remove existing object

    Returns:
        The new mesh object

    Example:
        >>> import numpy as np
        >>> verts = np.random.randn(10000, 3).astype(np.float32)
        >>> obj = create_mesh_numpy("PointCloud", verts, [])
    """
    try:
        import numpy as np
    except ImportError:
        # Fallback: convert to lists and use from_pydata
        return create_mesh_object(
            name,
            vertices.tolist() if hasattr(vertices, 'tolist') else list(vertices),
            faces=faces.tolist() if hasattr(faces, 'tolist') else list(faces),
            location=location,
            replace_existing=replace_existing
        )

    if replace_existing:
        remove_object_by_name(name)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")

    vert_count = len(vertices)

    # Handle faces: convert list of tuples to flat arrays
    if isinstance(faces, np.ndarray) and faces.ndim == 2:
        face_count = len(faces)
        loop_total = faces.shape[1]  # verts per face
        loop_starts = np.arange(0, face_count * loop_total, loop_total, dtype=np.int32)
        loop_totals = np.full(face_count, loop_total, dtype=np.int32)
        loop_verts = faces.flatten().astype(np.int32)
        total_loops = face_count * loop_total
    elif isinstance(faces, (list, tuple)) and len(faces) > 0:
        # List of tuples with possibly varying lengths
        loop_verts_list = []
        loop_starts_list = []
        loop_totals_list = []
        offset = 0
        for face in faces:
            loop_starts_list.append(offset)
            loop_totals_list.append(len(face))
            loop_verts_list.extend(face)
            offset += len(face)

        face_count = len(faces)
        total_loops = len(loop_verts_list)
        loop_starts = np.array(loop_starts_list, dtype=np.int32)
        loop_totals = np.array(loop_totals_list, dtype=np.int32)
        loop_verts = np.array(loop_verts_list, dtype=np.int32)
    else:
        face_count = 0
        total_loops = 0
        loop_starts = np.array([], dtype=np.int32)
        loop_totals = np.array([], dtype=np.int32)
        loop_verts = np.array([], dtype=np.int32)

    # Allocate mesh data
    mesh.vertices.add(vert_count)
    mesh.loops.add(total_loops)
    mesh.polygons.add(face_count)

    # Set vertex positions (flatten to 1D: x0,y0,z0,x1,y1,z1,...)
    flat_verts = np.asarray(vertices, dtype=np.float32).reshape(-1)
    mesh.vertices.foreach_set("co", flat_verts)

    if face_count > 0:
        mesh.loops.foreach_set("vertex_index", loop_verts)
        mesh.polygons.foreach_set("loop_start", loop_starts)
        mesh.polygons.foreach_set("loop_total", loop_totals)

    if normals is not None:
        flat_normals = np.asarray(normals, dtype=np.float32).reshape(-1)
        mesh.vertices.foreach_set("normal", flat_normals)

    mesh.update()
    mesh.validate()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    return obj


def add_smooth_shading(
    obj: bpy.types.Object,
    auto_smooth_angle: float = 30.0
) -> None:
    """
    Apply smooth shading with auto-smooth normals.

    Args:
        obj: Mesh object
        auto_smooth_angle: Angle threshold in degrees for auto-smooth

    Example:
        >>> add_smooth_shading(sword_blade, auto_smooth_angle=45)
    """
    obj.data.shade_smooth()
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = math.radians(auto_smooth_angle)


def set_origin_to_geometry(obj: bpy.types.Object) -> None:
    """
    Set the object's origin to its geometry center.

    Args:
        obj: Target object

    Example:
        >>> set_origin_to_geometry(my_mesh)
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    obj.select_set(False)


# Standalone execution
if __name__ == "__main__":
    # Demo: create a simple pyramid using from_pydata
    verts = [
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),  # base
        (0.5, 0.5, 1.0),  # apex
    ]
    faces = [
        (0, 1, 2, 3),  # base
        (0, 1, 4),     # front
        (1, 2, 4),     # right
        (2, 3, 4),     # back
        (3, 0, 4),     # left
    ]
    obj = create_mesh_object("Pyramid", verts, faces=faces)
    apply_material(obj, base_color=(0.8, 0.6, 0.2, 1.0), roughness=0.4)
    print(f"Created '{obj.name}' with {len(verts)} verts and {len(faces)} faces")
