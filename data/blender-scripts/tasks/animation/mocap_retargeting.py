"""
{
  "title": "Motion Capture Retargeting",
  "category": "animation",
  "subcategory": "retarget",
  "tags": ["mocap", "retarget", "motion capture", "armature", "bvh", "fbx", "animation transfer", "bone mapping"],
  "difficulty": "advanced",
  "description": "Import motion capture data (BVH/FBX) and retarget it to a different armature skeleton using bone mapping and constraint-based transfer.",
  "blender_version": "5.0+",
  "estimated_objects": 0
}
"""
import bpy
import math


# Common bone name mappings between different mocap formats
BONE_MAPPINGS = {
    'mixamo_to_rigify': {
        'Hips': 'spine',
        'Spine': 'spine.001',
        'Spine1': 'spine.002',
        'Spine2': 'spine.003',
        'Neck': 'spine.004',
        'Head': 'spine.006',
        'LeftShoulder': 'shoulder.L',
        'LeftArm': 'upper_arm.L',
        'LeftForeArm': 'forearm.L',
        'LeftHand': 'hand.L',
        'RightShoulder': 'shoulder.R',
        'RightArm': 'upper_arm.R',
        'RightForeArm': 'forearm.R',
        'RightHand': 'hand.R',
        'LeftUpLeg': 'thigh.L',
        'LeftLeg': 'shin.L',
        'LeftFoot': 'foot.L',
        'LeftToeBase': 'toe.L',
        'RightUpLeg': 'thigh.R',
        'RightLeg': 'shin.R',
        'RightFoot': 'foot.R',
        'RightToeBase': 'toe.R',
    },
    'cmu_to_rigify': {
        'hip': 'spine',
        'abdomen': 'spine.001',
        'chest': 'spine.003',
        'neck': 'spine.004',
        'head': 'spine.006',
        'lCollar': 'shoulder.L',
        'lShldr': 'upper_arm.L',
        'lForeArm': 'forearm.L',
        'lHand': 'hand.L',
        'rCollar': 'shoulder.R',
        'rShldr': 'upper_arm.R',
        'rForeArm': 'forearm.R',
        'rHand': 'hand.R',
        'lThigh': 'thigh.L',
        'lShin': 'shin.L',
        'lFoot': 'foot.L',
        'rThigh': 'thigh.R',
        'rShin': 'shin.R',
        'rFoot': 'foot.R',
    },
}


def import_bvh(
    filepath: str,
    scale: float = 0.01,
    frame_start: int = 1,
    rotate_mode: str = 'NATIVE',
    update_scene_fps: bool = True
) -> bpy.types.Object:
    """
    Import a BVH motion capture file.

    Args:
        filepath: Path to the BVH file
        scale: Import scale (BVH is usually in cm, Blender in m)
        frame_start: Frame to start the imported animation
        rotate_mode: Rotation mode ('NATIVE', 'XYZ', 'XZY', etc.)
        update_scene_fps: Match scene FPS to BVH framerate

    Returns:
        The imported armature object

    Example:
        >>> arm = import_bvh("C:/mocap/walk.bvh", scale=0.01)
    """
    bpy.ops.import_anim.bvh(
        filepath=filepath,
        filter_glob="*.bvh",
        global_scale=scale,
        frame_start=frame_start,
        rotate_mode=rotate_mode,
        update_scene_fps=update_scene_fps,
        update_scene_duration=True
    )

    return bpy.context.active_object


def auto_detect_bone_mapping(
    source_armature: bpy.types.Object,
    target_armature: bpy.types.Object
) -> dict:
    """
    Automatically detect bone mapping between source and target armatures
    using common naming patterns (case-insensitive fuzzy match).

    Args:
        source_armature: Source armature (mocap)
        target_armature: Target armature (character rig)

    Returns:
        Dict mapping source bone names to target bone names

    Example:
        >>> mapping = auto_detect_bone_mapping(mocap_arm, character_arm)
    """
    mapping = {}
    source_bones = {b.name: b for b in source_armature.data.bones}
    target_bones = {b.name: b for b in target_armature.data.bones}

    # Try exact matches first
    for src_name in source_bones:
        if src_name in target_bones:
            mapping[src_name] = src_name

    # Try known mapping tables
    for preset_name, preset_map in BONE_MAPPINGS.items():
        match_score = sum(1 for k in preset_map if k in source_bones)
        if match_score > len(preset_map) * 0.5:  # >50% match
            for src, tgt in preset_map.items():
                if src in source_bones and tgt in target_bones:
                    mapping[src] = tgt
            break

    # Fuzzy matching for remaining unmatched bones
    unmatched_src = [b for b in source_bones if b not in mapping]
    unmatched_tgt = [b for b in target_bones if b not in mapping.values()]

    keywords = {
        'hip': ['hip', 'pelvis', 'spine'],
        'spine': ['spine', 'chest', 'torso', 'abdomen'],
        'head': ['head'],
        'neck': ['neck'],
        'shoulder': ['shoulder', 'collar', 'clavicle'],
        'arm': ['arm', 'shldr', 'upper'],
        'forearm': ['forearm', 'lower', 'elbow'],
        'hand': ['hand', 'wrist'],
        'thigh': ['thigh', 'upleg', 'upper_leg'],
        'shin': ['shin', 'leg', 'calf', 'lower_leg'],
        'foot': ['foot', 'ankle'],
        'toe': ['toe'],
    }

    for src in unmatched_src:
        src_lower = src.lower()
        for tgt in unmatched_tgt:
            tgt_lower = tgt.lower()
            # Check if both names share body part keywords
            for part, kws in keywords.items():
                src_match = any(kw in src_lower for kw in kws)
                tgt_match = any(kw in tgt_lower for kw in kws)
                # Check side matching
                src_side = 'L' if any(s in src for s in ['.L', '_L', 'Left', 'left', '_l']) else \
                          'R' if any(s in src for s in ['.R', '_R', 'Right', 'right', '_r']) else None
                tgt_side = 'L' if any(s in tgt for s in ['.L', '_L', 'Left', 'left', '_l']) else \
                          'R' if any(s in tgt for s in ['.R', '_R', 'Right', 'right', '_r']) else None

                if src_match and tgt_match and src_side == tgt_side:
                    mapping[src] = tgt
                    unmatched_tgt.remove(tgt)
                    break
            if src in mapping:
                break

    return mapping


def retarget_with_constraints(
    source_armature: bpy.types.Object,
    target_armature: bpy.types.Object,
    bone_mapping: dict = None,
    use_rotation: bool = True,
    use_location: bool = True,
    influence: float = 1.0
) -> int:
    """
    Retarget animation from source to target using Copy Rotation/Location constraints.

    Args:
        source_armature: Source armature (mocap data)
        target_armature: Target armature (character rig)
        bone_mapping: Dict of source→target bone names (auto-detected if None)
        use_rotation: Copy rotation
        use_location: Copy location (root/hip bone only recommended)
        influence: Constraint influence (0-1)

    Returns:
        Number of constraints created

    Example:
        >>> count = retarget_with_constraints(mocap_arm, char_arm)
    """
    if bone_mapping is None:
        bone_mapping = auto_detect_bone_mapping(source_armature, target_armature)

    bpy.context.view_layer.objects.active = target_armature
    bpy.ops.object.mode_set(mode='POSE')

    constraint_count = 0

    for src_bone_name, tgt_bone_name in bone_mapping.items():
        tgt_bone = target_armature.pose.bones.get(tgt_bone_name)
        if not tgt_bone:
            continue

        if use_rotation:
            # Add Copy Rotation constraint
            con = tgt_bone.constraints.new('COPY_ROTATION')
            con.name = f"Retarget_Rot_{src_bone_name}"
            con.target = source_armature
            con.subtarget = src_bone_name
            con.influence = influence
            con.target_space = 'LOCAL'
            con.owner_space = 'LOCAL'
            constraint_count += 1

        # Only copy location for root bone to avoid stretching
        is_root = tgt_bone_name in ['spine', 'hip', 'Hips', 'pelvis']
        if use_location and is_root:
            con = tgt_bone.constraints.new('COPY_LOCATION')
            con.name = f"Retarget_Loc_{src_bone_name}"
            con.target = source_armature
            con.subtarget = src_bone_name
            con.influence = influence
            constraint_count += 1

    bpy.ops.object.mode_set(mode='OBJECT')
    return constraint_count


def bake_retargeted_animation(
    target_armature: bpy.types.Object,
    frame_start: int = 1,
    frame_end: int = 250,
    action_name: str = "Retargeted",
    remove_constraints: bool = True
) -> bpy.types.Action:
    """
    Bake retargeted constraints into keyframes, then optionally remove constraints.
    Essential before export or NLA usage.

    Args:
        target_armature: Target armature with retarget constraints
        frame_start: Bake start frame
        frame_end: Bake end frame
        action_name: Name for the baked action
        remove_constraints: Remove retarget constraints after baking

    Returns:
        The baked action

    Example:
        >>> action = bake_retargeted_animation(char_arm, 1, 200, "WalkCycle")
    """
    bpy.context.view_layer.objects.active = target_armature
    target_armature.select_set(True)

    bpy.ops.nla.bake(
        frame_start=frame_start,
        frame_end=frame_end,
        only_selected=False,
        visual_keying=True,
        clear_constraints=remove_constraints,
        bake_types={'POSE'}
    )

    if target_armature.animation_data and target_armature.animation_data.action:
        target_armature.animation_data.action.name = action_name
        return target_armature.animation_data.action

    return None


def cleanup_retarget_constraints(
    armature: bpy.types.Object,
    prefix: str = "Retarget_"
) -> int:
    """
    Remove all retarget constraints from an armature.

    Args:
        armature: Armature to clean up
        prefix: Constraint name prefix to match

    Returns:
        Number of constraints removed

    Example:
        >>> removed = cleanup_retarget_constraints(char_arm)
    """
    removed = 0
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    for bone in armature.pose.bones:
        for con in list(bone.constraints):
            if con.name.startswith(prefix):
                bone.constraints.remove(con)
                removed += 1

    bpy.ops.object.mode_set(mode='OBJECT')
    return removed


# Standalone execution
if __name__ == "__main__":
    armatures = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    if len(armatures) >= 2:
        mapping = auto_detect_bone_mapping(armatures[0], armatures[1])
        count = retarget_with_constraints(armatures[0], armatures[1], mapping)
        print(f"Retargeted {count} constraints from '{armatures[0].name}' to '{armatures[1].name}'")
    else:
        print("Need at least 2 armatures in scene for retargeting")
