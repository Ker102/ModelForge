"""
{
  "title": "Vertex Group Utilities",
  "category": "mesh",
  "tags": ["vertex", "group", "weight", "paint", "deform", "selection"],
  "description": "Functions for creating and managing vertex groups for mesh deformation.",
  "blender_version": "3.0+"
}
"""
import bpy


def create_vertex_group(
    obj: bpy.types.Object,
    name: str
) -> bpy.types.VertexGroup:
    """Create a new vertex group."""
    return obj.vertex_groups.new(name=name)


def add_vertices_to_group(
    obj: bpy.types.Object,
    group_name: str,
    vertex_indices: list,
    weight: float = 1.0
) -> None:
    """
    Add vertices to a vertex group.
    
    Args:
        obj: Mesh object
        group_name: Vertex group name
        vertex_indices: List of vertex indices
        weight: Weight value (0-1)
    """
    if group_name not in obj.vertex_groups:
        create_vertex_group(obj, group_name)
    
    group = obj.vertex_groups[group_name]
    group.add(vertex_indices, weight, 'REPLACE')


def set_vertex_weight(
    obj: bpy.types.Object,
    group_name: str,
    vertex_index: int,
    weight: float
) -> None:
    """Set weight for single vertex."""
    if group_name in obj.vertex_groups:
        group = obj.vertex_groups[group_name]
        group.add([vertex_index], weight, 'REPLACE')


def get_vertex_weight(
    obj: bpy.types.Object,
    group_name: str,
    vertex_index: int
) -> float:
    """Get weight of vertex in group."""
    if group_name in obj.vertex_groups:
        group = obj.vertex_groups[group_name]
        try:
            return group.weight(vertex_index)
        except RuntimeError:
            return 0.0
    return 0.0


def remove_vertices_from_group(
    obj: bpy.types.Object,
    group_name: str,
    vertex_indices: list
) -> None:
    """Remove vertices from group."""
    if group_name in obj.vertex_groups:
        group = obj.vertex_groups[group_name]
        group.remove(vertex_indices)


def create_group_from_selection(
    obj: bpy.types.Object,
    group_name: str,
    weight: float = 1.0
) -> bpy.types.VertexGroup:
    """Create vertex group from selected vertices."""
    bpy.ops.object.mode_set(mode='OBJECT')
    
    selected_verts = [v.index for v in obj.data.vertices if v.select]
    
    group = create_vertex_group(obj, group_name)
    group.add(selected_verts, weight, 'REPLACE')
    
    return group


def create_group_by_position(
    obj: bpy.types.Object,
    group_name: str,
    axis: str = 'Z',
    threshold: float = 0.0,
    above: bool = True,
    weight: float = 1.0
) -> bpy.types.VertexGroup:
    """
    Create vertex group from vertices above/below threshold on axis.
    
    Args:
        obj: Mesh object
        group_name: Group name
        axis: 'X', 'Y', or 'Z'
        threshold: Position threshold
        above: Select above (True) or below (False)
        weight: Weight value
    """
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[axis.upper()]
    
    indices = []
    for v in obj.data.vertices:
        pos = v.co[axis_index]
        if (above and pos >= threshold) or (not above and pos <= threshold):
            indices.append(v.index)
    
    group = create_vertex_group(obj, group_name)
    group.add(indices, weight, 'REPLACE')
    
    return group


def create_gradient_weight(
    obj: bpy.types.Object,
    group_name: str,
    axis: str = 'Z',
    start: float = 0.0,
    end: float = 1.0
) -> bpy.types.VertexGroup:
    """
    Create vertex group with gradient weights along axis.
    
    Args:
        obj: Mesh object
        group_name: Group name
        axis: 'X', 'Y', or 'Z'
        start: Position for weight 0
        end: Position for weight 1
    """
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[axis.upper()]
    
    group = create_vertex_group(obj, group_name)
    
    for v in obj.data.vertices:
        pos = v.co[axis_index]
        t = (pos - start) / (end - start) if end != start else 0
        weight = max(0, min(1, t))
        group.add([v.index], weight, 'REPLACE')
    
    return group


def normalize_weights(obj: bpy.types.Object) -> None:
    """Normalize all vertex group weights."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.vertex_group_normalize_all()
    bpy.ops.object.mode_set(mode='OBJECT')


def mirror_vertex_groups(obj: bpy.types.Object) -> None:
    """Mirror vertex groups (L/R naming)."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.vertex_group_mirror(use_topology=False)


def remove_vertex_group(obj: bpy.types.Object, name: str) -> None:
    """Remove vertex group by name."""
    if name in obj.vertex_groups:
        obj.vertex_groups.remove(obj.vertex_groups[name])


def list_vertex_groups(obj: bpy.types.Object) -> list:
    """Return list of vertex group names."""
    return [g.name for g in obj.vertex_groups]
