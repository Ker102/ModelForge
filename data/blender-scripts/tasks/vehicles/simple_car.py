"""
{
  "title": "Create Simple Car with Wheels",
  "category": "vehicles",
  "subcategory": "car",
  "tags": ["car", "vehicle", "wheels", "automotive", "game-ready"],
  "difficulty": "intermediate",
  "description": "Creates a complete simple car model with body, four wheels, windows, and headlights. Ideal as a base for vehicle scenes.",
  "blender_version": "3.0+",
  "estimated_objects": 8
}
"""
import bpy
import math


def create_simple_car(
    location: tuple = (0, 0, 0),
    body_color: tuple = (0.8, 0.1, 0.1, 1.0),
    name_prefix: str = "Car"
) -> dict:
    """
    Create a complete simple car with body, wheels, windows, and headlights.
    
    Args:
        location: Base position for the car
        body_color: RGBA color for car body
        name_prefix: Prefix for all created objects
    
    Returns:
        Dictionary containing all created objects
    
    Example:
        >>> car = create_simple_car((0, 0, 0), (0.1, 0.2, 0.8, 1.0), "SportsCar")
        >>> print(car['body'].name)  # "SportsCar_Body"
    """
    created_objects = {}
    bx, by, bz = location
    
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    # === CAR BODY ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, bz + 0.5))
    body = bpy.context.active_object
    body.name = f"{name_prefix}_Body"
    body.scale = (2.0, 0.9, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    
    # Body material
    body_mat = bpy.data.materials.new(name=f"{name_prefix}_Paint")
    bsdf = body_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = body_color
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.2
    body.data.materials.append(body_mat)
    created_objects['body'] = body
    
    # === CABIN/ROOF ===
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx - 0.2, by, bz + 0.95))
    cabin = bpy.context.active_object
    cabin.name = f"{name_prefix}_Cabin"
    cabin.scale = (1.0, 0.85, 0.35)
    bpy.ops.object.transform_apply(scale=True)
    cabin.data.materials.append(body_mat)
    created_objects['cabin'] = cabin
    
    # === WHEELS ===
    wheel_positions = [
        (bx + 0.7, by + 0.55, bz + 0.25),   # Front Right
        (bx + 0.7, by - 0.55, bz + 0.25),   # Front Left
        (bx - 0.7, by + 0.55, bz + 0.25),   # Rear Right
        (bx - 0.7, by - 0.55, bz + 0.25),   # Rear Left
    ]
    wheel_names = ["FR", "FL", "RR", "RL"]
    
    # Wheel material
    wheel_mat = bpy.data.materials.new(name=f"{name_prefix}_Rubber")
    wheel_bsdf = wheel_mat.node_tree.nodes.get("Principled BSDF")
    wheel_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
    wheel_bsdf.inputs['Roughness'].default_value = 0.8
    
    wheels = []
    for pos, wname in zip(wheel_positions, wheel_names):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.15, location=pos)
        wheel = bpy.context.active_object
        wheel.name = f"{name_prefix}_Wheel_{wname}"
        wheel.rotation_euler[0] = math.radians(90)
        wheel.data.materials.append(wheel_mat)
        wheels.append(wheel)
    created_objects['wheels'] = wheels
    
    # === WINDOWS ===
    glass_mat = bpy.data.materials.new(name=f"{name_prefix}_Glass")
    glass_bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
    glass_bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.15, 1.0)
    glass_bsdf.inputs['Metallic'].default_value = 0.0
    glass_bsdf.inputs['Roughness'].default_value = 0.0
    glass_bsdf.inputs['Transmission'].default_value = 0.9
    
    # Front windshield
    bpy.ops.mesh.primitive_plane_add(size=0.8, location=(bx + 0.35, by, bz + 0.95))
    windshield = bpy.context.active_object
    windshield.name = f"{name_prefix}_Windshield"
    windshield.rotation_euler[1] = math.radians(70)
    windshield.scale[1] = 1.0
    windshield.data.materials.append(glass_mat)
    created_objects['windshield'] = windshield
    
    # Rear window
    bpy.ops.mesh.primitive_plane_add(size=0.7, location=(bx - 0.6, by, bz + 0.9))
    rear_window = bpy.context.active_object
    rear_window.name = f"{name_prefix}_RearWindow"
    rear_window.rotation_euler[1] = math.radians(-60)
    rear_window.data.materials.append(glass_mat)
    created_objects['rear_window'] = rear_window
    
    # === HEADLIGHTS ===
    headlight_mat = bpy.data.materials.new(name=f"{name_prefix}_Headlight")
    nodes = headlight_mat.node_tree.nodes
    links = headlight_mat.node_tree.links
    nodes.clear()
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 0.95, 0.8, 1.0)
    emission.inputs['Strength'].default_value = 5.0
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    headlights = []
    for y_offset in [0.35, -0.35]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(bx + 1.0, by + y_offset, bz + 0.45))
        hl = bpy.context.active_object
        hl.name = f"{name_prefix}_Headlight_{'R' if y_offset > 0 else 'L'}"
        hl.data.materials.append(headlight_mat)
        headlights.append(hl)
    created_objects['headlights'] = headlights
    
    # === TAILLIGHTS ===
    taillight_mat = bpy.data.materials.new(name=f"{name_prefix}_Taillight")
    nodes = taillight_mat.node_tree.nodes
    links = taillight_mat.node_tree.links
    nodes.clear()
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 0.0, 0.0, 1.0)
    emission.inputs['Strength'].default_value = 3.0
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    taillights = []
    for y_offset in [0.35, -0.35]:
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(bx - 1.0, by + y_offset, bz + 0.5))
        tl = bpy.context.active_object
        tl.name = f"{name_prefix}_Taillight_{'R' if y_offset > 0 else 'L'}"
        tl.scale = (0.5, 1.5, 1.0)
        tl.data.materials.append(taillight_mat)
        taillights.append(tl)
    created_objects['taillights'] = taillights
    
    return created_objects


# Standalone execution example
if __name__ == "__main__":
    # Clear existing meshes
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create a red sports car
    car = create_simple_car(
        location=(0, 0, 0),
        body_color=(0.7, 0.05, 0.05, 1.0),
        name_prefix="SportsCar"
    )
    
    print(f"Created car with {len(car)} component groups")
