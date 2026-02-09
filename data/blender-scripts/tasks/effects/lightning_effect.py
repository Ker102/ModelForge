"""
{
  "title": "Lightning Effect Generator",
  "category": "effects",
  "subcategory": "weather",
  "tags": ["lightning", "storm", "weather", "effect", "electricity"],
  "difficulty": "intermediate",
  "description": "Generates lightning bolt effects for storm scenes.",
  "blender_version": "3.0+",
  "estimated_objects": 2
}
"""
import bpy
import random
import math


def create_lightning_bolt(
    start: tuple = (0, 0, 10),
    end: tuple = (0, 0, 0),
    branches: int = 4,
    segment_count: int = 10,
    jitter: float = 0.5,
    thickness: float = 0.05,
    glow_color: tuple = (0.5, 0.7, 1.0),
    seed: int = 42,
    name: str = "Lightning"
) -> dict:
    """
    Create a lightning bolt effect.
    
    Args:
        start: Start point (usually sky)
        end: End point (usually ground)
        branches: Number of branches
        segment_count: Segments per bolt
        jitter: Zigzag amount
        thickness: Bolt thickness
        glow_color: RGB glow color
        seed: Random seed
        name: Object name
    
    Returns:
        Dictionary with lightning parts
    """
    random.seed(seed)
    result = {}
    
    # Main bolt
    main_bolt = _create_bolt_curve(
        start, end, segment_count, jitter, thickness, glow_color, name
    )
    result['main_bolt'] = main_bolt
    
    # Branches
    branch_bolts = []
    for i in range(branches):
        # Branch from random point on main bolt
        t = random.uniform(0.2, 0.7)
        branch_start = (
            start[0] + (end[0] - start[0]) * t + random.uniform(-jitter, jitter),
            start[1] + (end[1] - start[1]) * t + random.uniform(-jitter, jitter),
            start[2] + (end[2] - start[2]) * t
        )
        branch_end = (
            branch_start[0] + random.uniform(-2, 2),
            branch_start[1] + random.uniform(-2, 2),
            branch_start[2] - random.uniform(1, 3)
        )
        
        branch = _create_bolt_curve(
            branch_start, branch_end,
            segment_count // 2, jitter * 0.7, thickness * 0.5, glow_color,
            f"{name}_Branch_{i}"
        )
        branch_bolts.append(branch)
    
    result['branches'] = branch_bolts
    
    # Impact light
    bpy.ops.object.light_add(type='POINT', location=end)
    light = bpy.context.active_object
    light.name = f"{name}_Light"
    light.data.energy = 5000
    light.data.color = glow_color
    light.data.shadow_soft_size = 2
    result['light'] = light
    
    return result


def _create_bolt_curve(
    start: tuple,
    end: tuple,
    segments: int,
    jitter: float,
    thickness: float,
    color: tuple,
    name: str
) -> bpy.types.Object:
    """Create zigzag bolt curve."""
    curve_data = bpy.data.curves.new(f"{name}_Curve", 'CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = thickness
    curve_data.bevel_resolution = 2
    
    spline = curve_data.splines.new('POLY')
    spline.points.add(segments - 1)
    
    for i in range(segments):
        t = i / (segments - 1)
        
        # Interpolate with jitter
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        z = start[2] + (end[2] - start[2]) * t
        
        if i > 0 and i < segments - 1:
            x += random.uniform(-jitter, jitter)
            y += random.uniform(-jitter, jitter)
        
        spline.points[i].co = (x, y, z, 1)
    
    bolt = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(bolt)
    
    # Emission material
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 50.0
    bolt.data.materials.append(mat)
    
    return bolt


def animate_lightning_flash(
    light: bpy.types.Object,
    start_frame: int = 1,
    duration: int = 5
) -> None:
    """Animate lightning flash on/off."""
    light.data.energy = 0
    light.data.keyframe_insert('energy', frame=start_frame)
    
    # Flash on
    light.data.energy = 5000
    light.data.keyframe_insert('energy', frame=start_frame + 1)
    
    # Flash off
    light.data.energy = 0
    light.data.keyframe_insert('energy', frame=start_frame + 2)
    
    # Secondary flash
    light.data.energy = 3000
    light.data.keyframe_insert('energy', frame=start_frame + 3)
    
    light.data.energy = 0
    light.data.keyframe_insert('energy', frame=start_frame + duration)


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    lightning = create_lightning_bolt(
        start=(0, 0, 10),
        end=(1, 0.5, 0),
        branches=3
    )
    
    bpy.context.scene.render.engine = 'CYCLES'
    print("Created lightning bolt")
