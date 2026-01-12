"""
{
  "title": "Bone Helper Utilities",
  "category": "rigging",
  "tags": ["bone", "ik", "fk", "rigging", "helper", "animation"],
  "description": "Helper functions for bone manipulation and rigging.",
  "blender_version": "3.0+"
}
"""
import bpy
import math


def get_bone_chain(
    armature: bpy.types.Object,
    start_bone: str,
    end_bone: str
) -> list:
    """Get list of bones from start to end (following parent chain)."""
    bones = armature.data.bones
    chain = []
    
    current = bones.get(end_bone)
    while current:
        chain.insert(0, current.name)
        if current.name == start_bone:
            break
        current = current.parent
    
    return chain


def set_bone_roll(
    armature: bpy.types.Object,
    bone_name: str,
    roll: float
) -> None:
    """Set bone roll angle in degrees."""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    bone = armature.data.edit_bones.get(bone_name)
    if bone:
        bone.roll = math.radians(roll)
    
    bpy.ops.object.mode_set(mode='OBJECT')


def align_bone_to_world(
    armature: bpy.types.Object,
    bone_name: str,
    axis: str = 'Y'
) -> None:
    """Align bone to world axis."""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    bone = armature.data.edit_bones.get(bone_name)
    if bone:
        length = bone.length
        head = bone.head.copy()
        
        if axis == 'X':
            bone.tail = head + (length, 0, 0)
        elif axis == 'Y':
            bone.tail = head + (0, length, 0)
        elif axis == 'Z':
            bone.tail = head + (0, 0, length)
    
    bpy.ops.object.mode_set(mode='OBJECT')


def create_bone_group(
    armature: bpy.types.Object,
    group_name: str,
    bone_names: list,
    color_set: str = 'THEME01'
) -> None:
    """Create bone group with color."""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # In Blender 4.0+, use bone_collections
    if hasattr(armature.data, 'collections'):
        coll = armature.data.collections.new(group_name)
        for name in bone_names:
            if name in armature.pose.bones:
                coll.assign(armature.pose.bones[name])
    else:
        # Legacy bone groups
        group = armature.pose.bone_groups.new(name=group_name)
        group.color_set = color_set
        
        for name in bone_names:
            if name in armature.pose.bones:
                armature.pose.bones[name].bone_group = group
    
    bpy.ops.object.mode_set(mode='OBJECT')


def add_stretch_to(
    armature: bpy.types.Object,
    bone_name: str,
    target_bone: str
) -> bpy.types.Constraint:
    """Add stretch-to constraint."""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    bone = armature.pose.bones.get(bone_name)
    if bone:
        constraint = bone.constraints.new('STRETCH_TO')
        constraint.target = armature
        constraint.subtarget = target_bone
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return constraint
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return None


def add_copy_bone_constraint(
    armature: bpy.types.Object,
    bone_name: str,
    target_bone: str,
    constraint_type: str = 'COPY_ROTATION'
) -> bpy.types.Constraint:
    """Add copy constraint between bones."""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    bone = armature.pose.bones.get(bone_name)
    if bone:
        constraint = bone.constraints.new(constraint_type)
        constraint.target = armature
        constraint.subtarget = target_bone
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return constraint
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return None


def set_bone_layer(
    armature: bpy.types.Object,
    bone_name: str,
    layer: int
) -> None:
    """Move bone to specific layer (deprecated in 4.0+)."""
    if hasattr(armature.data.bones[bone_name], 'layers'):
        layers = [False] * 32
        layers[layer] = True
        armature.data.bones[bone_name].layers = layers


def mirror_bone_pose(
    armature: bpy.types.Object,
    bone_name: str
) -> None:
    """Mirror pose bone to opposite side."""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    bone = armature.pose.bones.get(bone_name)
    if bone:
        bone.bone.select = True
        bpy.ops.pose.copy()
        bpy.ops.pose.paste(flipped=True)
    
    bpy.ops.object.mode_set(mode='OBJECT')
