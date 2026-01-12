"""
{
  "title": "Simple Character Body",
  "category": "characters",
  "subcategory": "humanoid",
  "tags": ["character", "humanoid", "body", "mesh", "stylized", "lowpoly"],
  "difficulty": "intermediate",
  "description": "Creates a simple stylized humanoid character mesh suitable for animation.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math


def create_simple_character(
    height: float = 1.8,
    style: str = 'CAPSULE',
    proportions: str = 'REALISTIC',
    location: tuple = (0, 0, 0),
    name: str = "Character"
) -> bpy.types.Object:
    """
    Create a simple humanoid character.
    
    Args:
        height: Character height
        style: 'CAPSULE' (pill-shaped), 'BLOCKY', 'ROUND'
        proportions: 'REALISTIC', 'CHIBI', 'HEROIC'
        location: Character base position
        name: Object name
    
    Returns:
        The created character mesh
    
    Example:
        >>> char = create_simple_character(height=2.0, style='BLOCKY')
    """
    # Proportion presets
    props = {
        'REALISTIC': {
            'head_ratio': 0.13,
            'torso_ratio': 0.30,
            'leg_ratio': 0.45,
            'shoulder_width': 0.25,
            'hip_width': 0.22
        },
        'CHIBI': {
            'head_ratio': 0.35,
            'torso_ratio': 0.25,
            'leg_ratio': 0.25,
            'shoulder_width': 0.30,
            'hip_width': 0.25
        },
        'HEROIC': {
            'head_ratio': 0.11,
            'torso_ratio': 0.35,
            'leg_ratio': 0.45,
            'shoulder_width': 0.35,
            'hip_width': 0.20
        }
    }
    
    p = props.get(proportions, props['REALISTIC'])
    
    # Calculate sizes
    head_h = height * p['head_ratio']
    torso_h = height * p['torso_ratio']
    leg_h = height * p['leg_ratio']
    arm_h = height * 0.35
    
    # Join all parts
    parts = []
    
    # === HEAD ===
    head_z = location[2] + height - head_h / 2
    
    if style == 'CAPSULE':
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=head_h * 0.5,
            location=(location[0], location[1], head_z)
        )
    elif style == 'BLOCKY':
        bpy.ops.mesh.primitive_cube_add(
            size=head_h,
            location=(location[0], location[1], head_z)
        )
    else:  # ROUND
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=head_h * 0.5,
            subdivisions=2,
            location=(location[0], location[1], head_z)
        )
    
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    parts.append(head)
    
    # === TORSO ===
    torso_z = location[2] + leg_h + torso_h / 2
    
    if style == 'CAPSULE':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=p['shoulder_width'] / 2 * height,
            depth=torso_h,
            location=(location[0], location[1], torso_z)
        )
        torso = bpy.context.active_object
        # Taper toward hips
        torso.scale.y = 0.5
        bpy.ops.object.transform_apply(scale=True)
    elif style == 'BLOCKY':
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(location[0], location[1], torso_z)
        )
        torso = bpy.context.active_object
        torso.scale = (
            p['shoulder_width'] * height / 2,
            height * 0.15 / 2,
            torso_h / 2
        )
        bpy.ops.object.transform_apply(scale=True)
    else:  # ROUND
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=p['shoulder_width'] / 2 * height,
            location=(location[0], location[1], torso_z)
        )
        torso = bpy.context.active_object
        torso.scale = (1, 0.7, torso_h / (p['shoulder_width'] * height))
        bpy.ops.object.transform_apply(scale=True)
    
    torso.name = f"{name}_Torso"
    parts.append(torso)
    
    # === LEGS ===
    leg_radius = height * 0.05
    leg_offset = p['hip_width'] * height / 2 * 0.5
    
    for side, offset in [('L', -leg_offset), ('R', leg_offset)]:
        if style == 'CAPSULE':
            bpy.ops.mesh.primitive_cylinder_add(
                radius=leg_radius * 1.5,
                depth=leg_h,
                location=(
                    location[0] + offset,
                    location[1],
                    location[2] + leg_h / 2
                )
            )
        elif style == 'BLOCKY':
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(
                    location[0] + offset,
                    location[1],
                    location[2] + leg_h / 2
                )
            )
            bpy.context.active_object.scale = (
                leg_radius * 1.5,
                leg_radius * 1.5,
                leg_h / 2
            )
            bpy.ops.object.transform_apply(scale=True)
        else:  # ROUND
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=leg_radius * 2,
                location=(
                    location[0] + offset,
                    location[1],
                    location[2] + leg_h / 2
                )
            )
            bpy.context.active_object.scale = (1, 1, leg_h / (leg_radius * 4))
            bpy.ops.object.transform_apply(scale=True)
        
        leg = bpy.context.active_object
        leg.name = f"{name}_Leg_{side}"
        parts.append(leg)
    
    # === ARMS ===
    arm_radius = height * 0.04
    arm_z = location[2] + leg_h + torso_h * 0.85
    arm_offset = p['shoulder_width'] * height / 2
    
    for side, offset in [('L', -arm_offset - arm_h/2), ('R', arm_offset + arm_h/2)]:
        if style == 'CAPSULE':
            bpy.ops.mesh.primitive_cylinder_add(
                radius=arm_radius * 1.2,
                depth=arm_h,
                location=(
                    location[0] + offset,
                    location[1],
                    arm_z
                )
            )
        elif style == 'BLOCKY':
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(
                    location[0] + offset,
                    location[1],
                    arm_z
                )
            )
            bpy.context.active_object.scale = (
                arm_h / 2,
                arm_radius * 1.2,
                arm_radius * 1.2
            )
            bpy.ops.object.transform_apply(scale=True)
        else:  # ROUND
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=arm_radius * 1.5,
                location=(
                    location[0] + offset,
                    location[1],
                    arm_z
                )
            )
            bpy.context.active_object.scale = (arm_h / (arm_radius * 3), 1, 1)
            bpy.ops.object.transform_apply(scale=True)
        
        arm = bpy.context.active_object
        arm.rotation_euler.y = math.radians(90) if side == 'L' else math.radians(-90)
        bpy.ops.object.transform_apply(rotation=True)
        arm.name = f"{name}_Arm_{side}"
        parts.append(arm)
    
    # Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    
    character = bpy.context.active_object
    character.name = name
    
    # Apply smooth shading for non-blocky styles
    if style != 'BLOCKY':
        bpy.ops.object.shade_smooth()
    
    # Create simple material
    mat = bpy.data.materials.new(f"{name}_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.5, 1.0)  # Skin tone
    bsdf.inputs['Roughness'].default_value = 0.6
    character.data.materials.append(mat)
    
    # Set origin to base
    bpy.context.scene.cursor.location = location
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    return character


def add_face_features(
    character: bpy.types.Object,
    eye_size: float = 0.03,
    add_mouth: bool = True
) -> dict:
    """
    Add simple face features to character head.
    
    Args:
        character: Character object
        eye_size: Size of eyes
        add_mouth: Whether to add a mouth
    
    Returns:
        Dictionary of created feature objects
    """
    result = {}
    
    # Find approximate head position
    # (assumes head is at top of character)
    bounds = character.bound_box
    top_z = max(v[2] for v in bounds)
    head_center = (0, 0, top_z - 0.1)
    
    # Eyes
    for side, offset in [('L', -eye_size * 2), ('R', eye_size * 2)]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=eye_size,
            location=(
                offset,
                -0.12,  # Forward
                head_center[2] + 0.02
            )
        )
        eye = bpy.context.active_object
        eye.name = f"Eye_{side}"
        
        # Eye material (white with black pupil effect)
        mat = bpy.data.materials.new(f"EyeMat_{side}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)  # Dark pupil
        eye.data.materials.append(mat)
        
        result[f'eye_{side.lower()}'] = eye
    
    if add_mouth:
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, -0.12, head_center[2] - 0.05)
        )
        mouth = bpy.context.active_object
        mouth.name = "Mouth"
        mouth.scale = (eye_size * 2, eye_size * 0.3, eye_size * 0.5)
        bpy.ops.object.transform_apply(scale=True)
        
        mat = bpy.data.materials.new("MouthMat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.3, 0.1, 0.1, 1.0)
        mouth.data.materials.append(mat)
        
        result['mouth'] = mouth
    
    return result


# Standalone execution
if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create different character styles
    char1 = create_simple_character(
        height=1.8,
        style='CAPSULE',
        proportions='REALISTIC',
        location=(0, 0, 0),
        name="RealisticChar"
    )
    
    char2 = create_simple_character(
        height=1.0,
        style='ROUND',
        proportions='CHIBI',
        location=(3, 0, 0),
        name="ChibiChar"
    )
    
    char3 = create_simple_character(
        height=2.2,
        style='BLOCKY',
        proportions='HEROIC',
        location=(-3, 0, 0),
        name="HeroChar"
    )
    
    print("Created 3 character variations")
