"""
{
  "title": "Armature and Rigging Utilities",
  "category": "rigging",
  "tags": ["armature", "bones", "rig", "skeleton", "pose", "constraints", "ik"],
  "description": "Functions for creating and manipulating armatures, bones, and rigging setups.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def create_bone(
    armature: bpy.types.Object,
    name: str,
    head: tuple,
    tail: tuple,
    parent_bone: str = None,
    connect: bool = False
) -> bpy.types.EditBone:
    """
    Add a bone to an armature.
    
    Args:
        armature: Armature object
        name: Bone name
        head: Head position (ball joint)
        tail: Tail position (direction)
        parent_bone: Name of parent bone
        connect: Connect to parent (share same position)
    
    Returns:
        The created bone (in edit mode)
    
    Example:
        >>> bone = create_bone(arm, "Spine", (0,0,1), (0,0,1.5))
    """
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    bone = armature.data.edit_bones.new(name)
    bone.head = head
    bone.tail = tail
    
    if parent_bone:
        parent = armature.data.edit_bones.get(parent_bone)
        if parent:
            bone.parent = parent
            bone.use_connect = connect
    
    return bone


def create_bone_chain(
    armature: bpy.types.Object,
    positions: list,
    base_name: str = "Bone",
    parent_bone: str = None
) -> list:
    """
    Create a chain of connected bones.
    
    Args:
        armature: Armature object
        positions: List of XYZ tuples defining joint positions
        base_name: Base name for bones (numbered automatically)
        parent_bone: Name of bone to parent first bone to
    
    Returns:
        List of created bone names
    
    Example:
        >>> positions = [(0,0,0), (0,0,1), (0,0,2), (0,0,3)]
        >>> bones = create_bone_chain(arm, positions, "Spine")
    """
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    bone_names = []
    prev_bone = parent_bone
    
    for i in range(len(positions) - 1):
        name = f"{base_name}.{i:03d}" if len(positions) > 2 else base_name
        
        bone = armature.data.edit_bones.new(name)
        bone.head = positions[i]
        bone.tail = positions[i + 1]
        
        if prev_bone:
            parent = armature.data.edit_bones.get(prev_bone)
            if parent:
                bone.parent = parent
                bone.use_connect = (i > 0 or parent_bone is None)
        
        bone_names.append(name)
        prev_bone = name
    
    return bone_names


def add_bone_constraint(
    armature: bpy.types.Object,
    bone_name: str,
    constraint_type: str,
    target: bpy.types.Object = None,
    subtarget: str = None,
    **kwargs
) -> bpy.types.Constraint:
    """
    Add a constraint to a pose bone.
    
    Args:
        armature: Armature object
        bone_name: Target bone name
        constraint_type: 'IK', 'COPY_ROTATION', 'LIMIT_ROTATION', 'DAMPED_TRACK', etc.
        target: Target object
        subtarget: Target bone name (for armature targets)
        **kwargs: Additional constraint settings
    
    Returns:
        The created constraint
    
    Example:
        >>> add_bone_constraint(arm, "Forearm.L", "IK", arm, "HandTarget.L", chain_count=2)
    """
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_bone = armature.pose.bones.get(bone_name)
    if not pose_bone:
        raise ValueError(f"Bone '{bone_name}' not found")
    
    constraint = pose_bone.constraints.new(constraint_type)
    
    if target:
        constraint.target = target
    if subtarget and hasattr(constraint, 'subtarget'):
        constraint.subtarget = subtarget
    
    for key, value in kwargs.items():
        if hasattr(constraint, key):
            setattr(constraint, key, value)
    
    return constraint


def setup_ik_chain(
    armature: bpy.types.Object,
    tip_bone: str,
    chain_length: int,
    target_name: str = None,
    pole_target_name: str = None,
    pole_angle: float = 0
) -> dict:
    """
    Set up an IK chain on a bone.
    
    Args:
        armature: Armature object
        tip_bone: End bone of IK chain
        chain_length: Number of bones in chain
        target_name: Name for IK target bone (created if None)
        pole_target_name: Name for pole target bone (optional)
        pole_angle: Pole angle in degrees
    
    Returns:
        Dict with 'constraint', 'target', 'pole' keys
    
    Example:
        >>> setup = setup_ik_chain(arm, "Forearm.L", chain_length=2)
    """
    result = {}
    
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Get tip bone position
    edit_bone = armature.data.edit_bones.get(tip_bone)
    if not edit_bone:
        raise ValueError(f"Bone '{tip_bone}' not found")
    
    target_pos = edit_bone.tail.copy()
    
    # Create IK target bone
    if target_name is None:
        target_name = f"{tip_bone}_IK"
    
    target_bone = armature.data.edit_bones.new(target_name)
    target_bone.head = target_pos
    target_bone.tail = (target_pos[0], target_pos[1], target_pos[2] + 0.1)
    result['target'] = target_name
    
    # Create pole target if specified
    if pole_target_name:
        # Position pole in front of the joint
        mid_bone = edit_bone.parent
        if mid_bone:
            pole_pos = (mid_bone.head[0], mid_bone.head[1] - 0.5, mid_bone.head[2])
            pole_bone = armature.data.edit_bones.new(pole_target_name)
            pole_bone.head = pole_pos
            pole_bone.tail = (pole_pos[0], pole_pos[1], pole_pos[2] + 0.1)
            result['pole'] = pole_target_name
    
    bpy.ops.object.mode_set(mode='POSE')
    
    # Add IK constraint
    pose_bone = armature.pose.bones.get(tip_bone)
    ik = pose_bone.constraints.new('IK')
    ik.target = armature
    ik.subtarget = target_name
    ik.chain_count = chain_length
    
    if pole_target_name and pole_target_name in [b.name for b in armature.data.edit_bones]:
        ik.pole_target = armature
        ik.pole_subtarget = pole_target_name
        ik.pole_angle = math.radians(pole_angle)
    
    result['constraint'] = ik
    
    return result


def copy_bone_transforms(armature: bpy.types.Object) -> None:
    """Copy current pose as rest pose."""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.armature_apply()


def reset_pose(armature: bpy.types.Object) -> None:
    """Reset all bones to rest position."""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()


def set_bone_roll(
    armature: bpy.types.Object,
    bone_name: str,
    roll: float
) -> None:
    """
    Set bone roll angle.
    
    Args:
        armature: Armature object
        bone_name: Target bone
        roll: Roll angle in degrees
    """
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    bone = armature.data.edit_bones.get(bone_name)
    if bone:
        bone.roll = math.radians(roll)


def create_simple_rig(
    armature_name: str = "Armature",
    location: tuple = (0, 0, 0)
) -> bpy.types.Object:
    """
    Create a new armature object.
    
    Args:
        armature_name: Name for the armature
        location: Position
    
    Returns:
        The created armature object
    """
    bpy.ops.object.armature_add(location=location)
    armature = bpy.context.active_object
    armature.name = armature_name
    armature.show_in_front = True
    return armature


def parent_mesh_to_armature(
    mesh: bpy.types.Object,
    armature: bpy.types.Object,
    method: str = 'AUTOMATIC'
) -> None:
    """
    Parent mesh to armature with automatic weights.
    
    Args:
        mesh: Mesh object
        armature: Armature object
        method: 'AUTOMATIC', 'ENVELOPE', or 'EMPTY'
    """
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
    type_map = {
        'AUTOMATIC': 'ARMATURE_AUTO',
        'ENVELOPE': 'ARMATURE_ENVELOPE',
        'EMPTY': 'ARMATURE'
    }
    
    bpy.ops.object.parent_set(type=type_map.get(method, 'ARMATURE_AUTO'))
