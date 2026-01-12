"""
{
  "title": "Humanoid Armature Generator",
  "category": "characters",
  "subcategory": "rigging",
  "tags": ["armature", "skeleton", "rig", "humanoid", "character", "bones", "animation-ready"],
  "difficulty": "intermediate",
  "description": "Creates a basic humanoid armature/skeleton suitable for character animation.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math


def create_humanoid_armature(
    location: tuple = (0, 0, 0),
    height: float = 1.8,
    name: str = "Humanoid"
) -> bpy.types.Object:
    """
    Create a basic humanoid armature with proper bone hierarchy.
    
    The armature includes:
    - Spine chain (hips, spine, chest, neck, head)
    - Arms (shoulder, upper_arm, forearm, hand)
    - Legs (thigh, shin, foot, toe)
    
    Args:
        location: Base position (feet level)
        height: Total height in meters
        name: Armature name
    
    Returns:
        The created armature object
    
    Example:
        >>> armature = create_humanoid_armature(height=1.75, name="Hero")
    """
    # Proportions (relative to height)
    scale = height / 1.8
    
    # Create armature
    bpy.ops.object.armature_add(location=location)
    armature = bpy.context.active_object
    armature.name = name
    armature.show_in_front = True
    
    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    arm_data = armature.data
    
    # Remove default bone
    for bone in arm_data.edit_bones:
        arm_data.edit_bones.remove(bone)
    
    # Bone positions (relative to base, scaled)
    def pos(x, y, z):
        return (x * scale, y * scale, z * scale + location[2])
    
    # === SPINE ===
    hips = arm_data.edit_bones.new("Hips")
    hips.head = pos(0, 0, 0.95)
    hips.tail = pos(0, 0, 1.05)
    
    spine = arm_data.edit_bones.new("Spine")
    spine.head = pos(0, 0, 1.05)
    spine.tail = pos(0, 0, 1.25)
    spine.parent = hips
    
    chest = arm_data.edit_bones.new("Chest")
    chest.head = pos(0, 0, 1.25)
    chest.tail = pos(0, 0, 1.45)
    chest.parent = spine
    
    neck = arm_data.edit_bones.new("Neck")
    neck.head = pos(0, 0, 1.45)
    neck.tail = pos(0, 0, 1.55)
    neck.parent = chest
    
    head = arm_data.edit_bones.new("Head")
    head.head = pos(0, 0, 1.55)
    head.tail = pos(0, 0, 1.8)
    head.parent = neck
    
    # === LEFT ARM ===
    shoulder_l = arm_data.edit_bones.new("Shoulder.L")
    shoulder_l.head = pos(0, 0, 1.42)
    shoulder_l.tail = pos(0.15, 0, 1.42)
    shoulder_l.parent = chest
    
    upper_arm_l = arm_data.edit_bones.new("UpperArm.L")
    upper_arm_l.head = pos(0.15, 0, 1.42)
    upper_arm_l.tail = pos(0.42, 0, 1.42)
    upper_arm_l.parent = shoulder_l
    upper_arm_l.use_connect = True
    
    forearm_l = arm_data.edit_bones.new("Forearm.L")
    forearm_l.head = pos(0.42, 0, 1.42)
    forearm_l.tail = pos(0.67, 0, 1.42)
    forearm_l.parent = upper_arm_l
    forearm_l.use_connect = True
    
    hand_l = arm_data.edit_bones.new("Hand.L")
    hand_l.head = pos(0.67, 0, 1.42)
    hand_l.tail = pos(0.77, 0, 1.42)
    hand_l.parent = forearm_l
    hand_l.use_connect = True
    
    # === RIGHT ARM ===
    shoulder_r = arm_data.edit_bones.new("Shoulder.R")
    shoulder_r.head = pos(0, 0, 1.42)
    shoulder_r.tail = pos(-0.15, 0, 1.42)
    shoulder_r.parent = chest
    
    upper_arm_r = arm_data.edit_bones.new("UpperArm.R")
    upper_arm_r.head = pos(-0.15, 0, 1.42)
    upper_arm_r.tail = pos(-0.42, 0, 1.42)
    upper_arm_r.parent = shoulder_r
    upper_arm_r.use_connect = True
    
    forearm_r = arm_data.edit_bones.new("Forearm.R")
    forearm_r.head = pos(-0.42, 0, 1.42)
    forearm_r.tail = pos(-0.67, 0, 1.42)
    forearm_r.parent = upper_arm_r
    forearm_r.use_connect = True
    
    hand_r = arm_data.edit_bones.new("Hand.R")
    hand_r.head = pos(-0.67, 0, 1.42)
    hand_r.tail = pos(-0.77, 0, 1.42)
    hand_r.parent = forearm_r
    hand_r.use_connect = True
    
    # === LEFT LEG ===
    thigh_l = arm_data.edit_bones.new("Thigh.L")
    thigh_l.head = pos(0.1, 0, 0.95)
    thigh_l.tail = pos(0.1, 0, 0.5)
    thigh_l.parent = hips
    
    shin_l = arm_data.edit_bones.new("Shin.L")
    shin_l.head = pos(0.1, 0, 0.5)
    shin_l.tail = pos(0.1, 0, 0.08)
    shin_l.parent = thigh_l
    shin_l.use_connect = True
    
    foot_l = arm_data.edit_bones.new("Foot.L")
    foot_l.head = pos(0.1, 0, 0.08)
    foot_l.tail = pos(0.1, -0.12, 0)
    foot_l.parent = shin_l
    foot_l.use_connect = True
    
    toe_l = arm_data.edit_bones.new("Toe.L")
    toe_l.head = pos(0.1, -0.12, 0)
    toe_l.tail = pos(0.1, -0.20, 0)
    toe_l.parent = foot_l
    toe_l.use_connect = True
    
    # === RIGHT LEG ===
    thigh_r = arm_data.edit_bones.new("Thigh.R")
    thigh_r.head = pos(-0.1, 0, 0.95)
    thigh_r.tail = pos(-0.1, 0, 0.5)
    thigh_r.parent = hips
    
    shin_r = arm_data.edit_bones.new("Shin.R")
    shin_r.head = pos(-0.1, 0, 0.5)
    shin_r.tail = pos(-0.1, 0, 0.08)
    shin_r.parent = thigh_r
    shin_r.use_connect = True
    
    foot_r = arm_data.edit_bones.new("Foot.R")
    foot_r.head = pos(-0.1, 0, 0.08)
    foot_r.tail = pos(-0.1, -0.12, 0)
    foot_r.parent = shin_r
    foot_r.use_connect = True
    
    toe_r = arm_data.edit_bones.new("Toe.R")
    toe_r.head = pos(-0.1, -0.12, 0)
    toe_r.tail = pos(-0.1, -0.20, 0)
    toe_r.parent = foot_r
    toe_r.use_connect = True
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return armature


def parent_mesh_to_armature(
    mesh_object: bpy.types.Object,
    armature_object: bpy.types.Object,
    parenting_type: str = 'AUTOMATIC'
) -> None:
    """
    Parent a mesh to an armature with automatic or manual weights.
    
    Args:
        mesh_object: The mesh to parent
        armature_object: The target armature
        parenting_type: 'AUTOMATIC', 'ENVELOPE', or 'EMPTY' (manual weight painting)
    
    Example:
        >>> parent_mesh_to_armature(body_mesh, humanoid_rig, 'AUTOMATIC')
    """
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select mesh first, then armature (armature must be active)
    mesh_object.select_set(True)
    armature_object.select_set(True)
    bpy.context.view_layer.objects.active = armature_object
    
    # Parent with weights
    if parenting_type == 'AUTOMATIC':
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    elif parenting_type == 'ENVELOPE':
        bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
    else:
        bpy.ops.object.parent_set(type='ARMATURE')


def add_ik_constraint(
    armature: bpy.types.Object,
    bone_name: str,
    target_bone: str = None,
    chain_length: int = 2,
    pole_bone: str = None
) -> bpy.types.Constraint:
    """
    Add an Inverse Kinematics constraint to a bone.
    
    Args:
        armature: The armature object
        bone_name: Bone to add IK to (e.g., 'Forearm.L')
        target_bone: Target bone name (creates if None)
        chain_length: Number of bones in IK chain
        pole_bone: Pole target bone name (optional)
    
    Returns:
        The created IK constraint
    
    Example:
        >>> add_ik_constraint(rig, 'Forearm.L', chain_length=2)
    """
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_bone = armature.pose.bones.get(bone_name)
    if not pose_bone:
        raise ValueError(f"Bone '{bone_name}' not found")
    
    # Add IK constraint
    ik = pose_bone.constraints.new('IK')
    ik.chain_count = chain_length
    
    if target_bone:
        ik.target = armature
        ik.subtarget = target_bone
    
    if pole_bone:
        ik.pole_target = armature
        ik.pole_subtarget = pole_bone
        ik.pole_angle = math.radians(90)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return ik


# Standalone execution
if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create humanoid armature
    armature = create_humanoid_armature(height=1.8, name="Character")
    
    print(f"Created armature with {len(armature.data.bones)} bones")
