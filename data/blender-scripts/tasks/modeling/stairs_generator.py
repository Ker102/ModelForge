"""
{
  "title": "Stairs Generator",
  "category": "modeling",
  "subcategory": "architecture",
  "tags": ["stairs", "steps", "architecture", "building", "interior"],
  "difficulty": "intermediate",
  "description": "Generates straight and spiral staircases.",
  "blender_version": "3.0+",
  "estimated_objects": 15
}
"""
import bpy
import math


def create_stairs(
    steps: int = 12,
    step_width: float = 1.0,
    step_depth: float = 0.28,
    step_height: float = 0.18,
    style: str = 'STRAIGHT',
    with_railings: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Stairs"
) -> dict:
    """
    Create a staircase.
    
    Args:
        steps: Number of steps
        step_width: Width of steps
        step_depth: Depth/tread of steps
        step_height: Height/rise of steps
        style: 'STRAIGHT', 'L_TURN', 'U_TURN'
        with_railings: Add handrails
        location: Position
        name: Object name
    
    Returns:
        Dictionary with staircase parts
    """
    result = {}
    step_objs = []
    
    # Material
    step_mat = bpy.data.materials.new(f"{name}_Mat")
    step_mat.use_nodes = True
    bsdf = step_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.4, 0.3, 0.2, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    
    for i in range(steps):
        # Position
        x = location[0]
        y = location[1] - i * step_depth
        z = location[2] + i * step_height
        
        # Step tread
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            x, y - step_depth/2, z + step_height/2
        ))
        step = bpy.context.active_object
        step.name = f"{name}_Step_{i+1}"
        step.scale = (step_width/2, step_depth/2, step_height/2)
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(step_mat)
        step_objs.append(step)
    
    result['steps'] = step_objs
    
    # === STRINGERS (side supports) ===
    total_run = steps * step_depth
    total_rise = steps * step_height
    stringer_length = math.sqrt(total_run**2 + total_rise**2)
    stringer_angle = math.atan2(total_rise, total_run)
    
    for side, offset in [('L', -step_width/2 - 0.03), ('R', step_width/2 + 0.03)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + offset,
            location[1] - total_run/2,
            location[2] + total_rise/2
        ))
        stringer = bpy.context.active_object
        stringer.name = f"{name}_Stringer_{side}"
        stringer.scale = (0.03, stringer_length/2, 0.15)
        stringer.rotation_euler.x = -stringer_angle
        bpy.ops.object.transform_apply(scale=True)
        stringer.data.materials.append(step_mat)
    
    # === RAILINGS ===
    if with_railings:
        railings = _create_stair_railings(
            steps, step_width, step_depth, step_height,
            location, name
        )
        result['railings'] = railings
    
    return result


def _create_stair_railings(
    steps: int,
    step_width: float,
    step_depth: float,
    step_height: float,
    location: tuple,
    name: str
) -> list:
    """Create stair railings."""
    railings = []
    railing_height = 0.9
    
    rail_mat = bpy.data.materials.new(f"{name}_RailMat")
    rail_mat.use_nodes = True
    bsdf = rail_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.2, 0.18, 0.15, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.4
    
    total_run = steps * step_depth
    total_rise = steps * step_height
    stringer_angle = math.atan2(total_rise, total_run)
    
    for side, offset in [('L', -step_width/2), ('R', step_width/2)]:
        # Handrail
        rail_length = math.sqrt(total_run**2 + total_rise**2)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.025,
            depth=rail_length,
            location=(
                location[0] + offset,
                location[1] - total_run/2,
                location[2] + total_rise/2 + railing_height
            )
        )
        rail = bpy.context.active_object
        rail.name = f"{name}_Rail_{side}"
        rail.rotation_euler.x = math.pi/2 - stringer_angle
        rail.data.materials.append(rail_mat)
        railings.append(rail)
        
        # Posts
        post_interval = 3
        for i in range(0, steps, post_interval):
            y = location[1] - i * step_depth
            z = location[2] + i * step_height
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.02,
                depth=railing_height,
                location=(offset + location[0], y, z + railing_height/2)
            )
            post = bpy.context.active_object
            post.name = f"{name}_Post_{side}_{i}"
            post.data.materials.append(rail_mat)
            railings.append(post)
    
    return railings


def create_spiral_stairs(
    steps: int = 16,
    inner_radius: float = 0.3,
    outer_radius: float = 1.2,
    total_height: float = 3.0,
    total_rotation: float = 360,
    location: tuple = (0, 0, 0),
    name: str = "SpiralStairs"
) -> dict:
    """Create spiral staircase."""
    result = {}
    step_objs = []
    
    step_mat = bpy.data.materials.new(f"{name}_Mat")
    step_mat.use_nodes = True
    bsdf = step_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.35, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.3
    
    step_height = total_height / steps
    angle_per_step = math.radians(total_rotation) / steps
    
    for i in range(steps):
        angle = i * angle_per_step
        z = location[2] + i * step_height
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + math.cos(angle) * (inner_radius + outer_radius) / 2,
            location[1] + math.sin(angle) * (inner_radius + outer_radius) / 2,
            z
        ))
        step = bpy.context.active_object
        step.name = f"{name}_Step_{i+1}"
        step.scale = ((outer_radius - inner_radius)/2, 0.15, step_height/2)
        step.rotation_euler.z = angle
        bpy.ops.object.transform_apply(scale=True)
        step.data.materials.append(step_mat)
        step_objs.append(step)
    
    result['steps'] = step_objs
    
    # Center pole
    bpy.ops.mesh.primitive_cylinder_add(
        radius=inner_radius * 0.8,
        depth=total_height,
        location=(location[0], location[1], location[2] + total_height/2)
    )
    pole = bpy.context.active_object
    pole.name = f"{name}_Pole"
    pole.data.materials.append(step_mat)
    result['pole'] = pole
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_stairs(steps=10, location=(0, 0, 0))
    create_spiral_stairs(steps=16, location=(3, 0, 0))
    
    print("Created straight and spiral stairs")
