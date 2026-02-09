"""
{
  "title": "Portal Effect",
  "category": "effects",
  "subcategory": "magic",
  "tags": ["portal", "magic", "ring", "glow", "animated"],
  "difficulty": "intermediate",
  "description": "Creates an animated magic portal effect with rotating rings.",
  "blender_version": "3.0+",
  "estimated_objects": 5
}
"""
import bpy
import math


def create_portal(
    radius: float = 1.0,
    color: tuple = (0.2, 0.5, 1.0),
    inner_color: tuple = (0.8, 0.9, 1.0),
    ring_count: int = 3,
    rotation_speed: float = 1.0,
    location: tuple = (0, 0, 0),
    name: str = "Portal"
) -> dict:
    """
    Create an animated portal effect.
    
    Args:
        radius: Portal radius
        color: RGB outer glow color
        inner_color: RGB inner glow color
        ring_count: Number of rotating rings
        rotation_speed: Ring rotation speed
        location: Position
        name: Object name
    
    Returns:
        Dictionary with portal components
    """
    result = {}
    result['rings'] = []
    
    # === INNER GLOW DISK ===
    bpy.ops.mesh.primitive_circle_add(
        radius=radius * 0.9,
        fill_type='NGON',
        location=location
    )
    inner = bpy.context.active_object
    inner.name = f"{name}_Inner"
    
    inner_mat = bpy.data.materials.new(f"{name}_InnerMat")
    inner_mat.blend_method = 'BLEND'
    nodes = inner_mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*inner_color, 1.0)
    bsdf.inputs['Emission Color'].default_value = (*inner_color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 5.0
    bsdf.inputs['Alpha'].default_value = 0.7
    inner.data.materials.append(inner_mat)
    
    result['inner'] = inner
    
    # === ROTATING RINGS ===
    for i in range(ring_count):
        ring_radius = radius * (0.8 + i * 0.15)
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=ring_radius,
            minor_radius=0.02,
            location=location
        )
        ring = bpy.context.active_object
        ring.name = f"{name}_Ring_{i+1}"
        
        # Ring material
        ring_mat = bpy.data.materials.new(f"{name}_RingMat_{i}")
        nodes = ring_mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        
        # Gradient color based on ring index
        t = i / max(ring_count - 1, 1)
        ring_color = (
            color[0] + (inner_color[0] - color[0]) * t,
            color[1] + (inner_color[1] - color[1]) * t,
            color[2] + (inner_color[2] - color[2]) * t
        )
        
        bsdf.inputs['Base Color'].default_value = (*ring_color, 1.0)
        bsdf.inputs['Emission Color'].default_value = (*ring_color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 10.0 - i * 2
        ring.data.materials.append(ring_mat)
        
        # Animation - different rotation speeds/axes
        _animate_ring_rotation(ring, rotation_speed * (1 + i * 0.3), axis=i % 3)
        
        result['rings'].append(ring)
    
    # === OUTER GLOW RING ===
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=0.05,
        location=location
    )
    outer = bpy.context.active_object
    outer.name = f"{name}_Outer"
    
    outer_mat = bpy.data.materials.new(f"{name}_OuterMat")
    nodes = outer_mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 15.0
    outer.data.materials.append(outer_mat)
    
    result['outer'] = outer
    
    # === LIGHT ===
    bpy.ops.object.light_add(
        type='POINT',
        location=(location[0], location[1] - 0.5, location[2])
    )
    light = bpy.context.active_object
    light.name = f"{name}_Light"
    light.data.energy = 100
    light.data.color = color
    
    result['light'] = light
    
    return result


def _animate_ring_rotation(
    ring: bpy.types.Object,
    speed: float,
    axis: int = 2
) -> None:
    """Animate ring rotation."""
    ring.rotation_euler = (0, 0, 0)
    ring.keyframe_insert(data_path="rotation_euler", frame=1)
    
    # Rotate different axes for variety
    if axis == 0:
        ring.rotation_euler.x = math.radians(360 * speed)
    elif axis == 1:
        ring.rotation_euler.y = math.radians(360 * speed)
    else:
        ring.rotation_euler.z = math.radians(360 * speed)
    
    ring.keyframe_insert(data_path="rotation_euler", frame=250)
    
    # Make cyclic
    if ring.animation_data and ring.animation_data.action:
        for fcurve in ring.animation_data.action.fcurves:
            fcurve.modifiers.new('CYCLES')
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'LINEAR'


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Blue portal
    create_portal(color=(0.2, 0.5, 1.0), location=(0, 0, 1))
    
    # Orange portal
    create_portal(color=(1.0, 0.5, 0.1), location=(3, 0, 1))
    
    bpy.context.scene.render.engine = 'CYCLES'
    print("Created portal effects")
