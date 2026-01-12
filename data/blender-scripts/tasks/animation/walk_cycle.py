"""
{
  "title": "Walk Cycle Animation",
  "category": "animation",
  "subcategory": "character",
  "tags": ["walk", "cycle", "character", "loop", "armature", "animation"],
  "difficulty": "advanced",
  "description": "Creates a procedural walk cycle animation for a humanoid armature.",
  "blender_version": "3.0+",
  "estimated_objects": 0
}
"""
import bpy
import math


def create_walk_cycle(
    armature: bpy.types.Object,
    step_length: float = 0.5,
    step_height: float = 0.15,
    cycle_frames: int = 24,
    hip_sway: float = 0.05,
    arm_swing: float = 0.4,
    start_frame: int = 1
) -> dict:
    """
    Create a basic walk cycle animation.
    
    Args:
        armature: Armature object with standard bone names
        step_length: Distance of each step
        step_height: How high feet lift
        cycle_frames: Frames per complete cycle
        hip_sway: Side-to-side hip movement
        arm_swing: Arm swing amplitude
        start_frame: Starting frame
    
    Returns:
        Dictionary with animation info
    
    Example:
        >>> create_walk_cycle(bpy.data.objects['Armature'])
    """
    if armature.type != 'ARMATURE':
        raise ValueError("Object must be an armature")
    
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    result = {
        'armature': armature.name,
        'start_frame': start_frame,
        'end_frame': start_frame + cycle_frames - 1,
        'cycle_frames': cycle_frames
    }
    
    # Get pose bones - try common naming conventions
    bone_mapping = _find_bones(armature)
    
    if not bone_mapping.get('spine'):
        print("Warning: Could not find standard bone naming. Animation may not work.")
        return result
    
    # Create keyframes
    half = cycle_frames // 2
    quarter = cycle_frames // 4
    
    for frame_offset in range(cycle_frames):
        frame = start_frame + frame_offset
        bpy.context.scene.frame_set(frame)
        
        # Normalized position in cycle (0-1)
        t = frame_offset / cycle_frames
        
        # === SPINE/HIP MOVEMENT ===
        if bone_mapping.get('spine'):
            spine = armature.pose.bones.get(bone_mapping['spine'])
            if spine:
                # Up/down bob
                spine.location.z = 0.03 * math.sin(t * 4 * math.pi)
                # Side to side sway
                spine.location.x = hip_sway * math.sin(t * 2 * math.pi)
                # Slight rotation
                spine.rotation_euler.y = math.radians(3) * math.sin(t * 2 * math.pi)
                spine.keyframe_insert(data_path="location", frame=frame)
                spine.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        # === LEG MOVEMENT ===
        _animate_leg(
            armature, bone_mapping, 'left', 
            t, step_length, step_height, frame, phase=0
        )
        _animate_leg(
            armature, bone_mapping, 'right', 
            t, step_length, step_height, frame, phase=0.5
        )
        
        # === ARM SWING ===
        _animate_arm(armature, bone_mapping, 'left', t, arm_swing, frame, phase=0.5)
        _animate_arm(armature, bone_mapping, 'right', t, arm_swing, frame, phase=0)
    
    # Make cyclic
    _make_cyclic(armature)
    
    return result


def _find_bones(armature: bpy.types.Object) -> dict:
    """Find bones using common naming conventions."""
    mapping = {}
    bones = armature.pose.bones
    
    # Common naming patterns
    patterns = {
        'spine': ['spine', 'spine.001', 'Spine', 'hips', 'Hips', 'pelvis'],
        'thigh_l': ['thigh.L', 'Thigh.L', 'upperleg.L', 'UpperLeg.L', 'leg_upper.L'],
        'thigh_r': ['thigh.R', 'Thigh.R', 'upperleg.R', 'UpperLeg.R', 'leg_upper.R'],
        'shin_l': ['shin.L', 'Shin.L', 'lowerleg.L', 'LowerLeg.L', 'leg_lower.L', 'calf.L'],
        'shin_r': ['shin.R', 'Shin.R', 'lowerleg.R', 'LowerLeg.R', 'leg_lower.R', 'calf.R'],
        'foot_l': ['foot.L', 'Foot.L', 'ankle.L', 'Ankle.L'],
        'foot_r': ['foot.R', 'Foot.R', 'ankle.R', 'Ankle.R'],
        'upper_arm_l': ['upperarm.L', 'UpperArm.L', 'arm_upper.L', 'shoulder.L'],
        'upper_arm_r': ['upperarm.R', 'UpperArm.R', 'arm_upper.R', 'shoulder.R'],
        'forearm_l': ['forearm.L', 'Forearm.L', 'arm_lower.L', 'lowerarm.L'],
        'forearm_r': ['forearm.R', 'Forearm.R', 'arm_lower.R', 'lowerarm.R'],
    }
    
    for bone_type, names in patterns.items():
        for name in names:
            if name in bones:
                mapping[bone_type] = name
                break
    
    return mapping


def _animate_leg(
    armature: bpy.types.Object,
    mapping: dict,
    side: str,
    t: float,
    step_length: float,
    step_height: float,
    frame: int,
    phase: float = 0
) -> None:
    """Animate one leg."""
    suffix = 'l' if side == 'left' else 'r'
    
    # Adjust phase
    t_adj = (t + phase) % 1.0
    
    thigh = armature.pose.bones.get(mapping.get(f'thigh_{suffix}'))
    shin = armature.pose.bones.get(mapping.get(f'shin_{suffix}'))
    foot = armature.pose.bones.get(mapping.get(f'foot_{suffix}'))
    
    if thigh:
        # Thigh rotation (forward/back swing)
        swing = math.sin(t_adj * 2 * math.pi) * 0.4
        thigh.rotation_euler.x = swing
        thigh.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if shin:
        # Knee bend (more bent during middle of step)
        bend = abs(math.sin(t_adj * 2 * math.pi)) * 0.6
        shin.rotation_euler.x = bend
        shin.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if foot:
        # Foot rotation (toe-off and heel-strike)
        foot_rot = math.sin((t_adj + 0.25) * 2 * math.pi) * 0.3
        foot.rotation_euler.x = foot_rot
        foot.keyframe_insert(data_path="rotation_euler", frame=frame)


def _animate_arm(
    armature: bpy.types.Object,
    mapping: dict,
    side: str,
    t: float,
    amplitude: float,
    frame: int,
    phase: float = 0
) -> None:
    """Animate one arm."""
    suffix = 'l' if side == 'left' else 'r'
    
    t_adj = (t + phase) % 1.0
    
    upper_arm = armature.pose.bones.get(mapping.get(f'upper_arm_{suffix}'))
    forearm = armature.pose.bones.get(mapping.get(f'forearm_{suffix}'))
    
    if upper_arm:
        # Arm swing opposite to leg
        swing = math.sin(t_adj * 2 * math.pi) * amplitude
        upper_arm.rotation_euler.x = swing
        upper_arm.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if forearm:
        # Forearm bend
        bend = 0.3 + abs(math.sin(t_adj * 2 * math.pi)) * 0.3
        forearm.rotation_euler.x = bend
        forearm.keyframe_insert(data_path="rotation_euler", frame=frame)


def _make_cyclic(armature: bpy.types.Object) -> None:
    """Make animation cyclic."""
    if armature.animation_data and armature.animation_data.action:
        action = armature.animation_data.action
        for fcurve in action.fcurves:
            for mod in fcurve.modifiers:
                if mod.type == 'CYCLES':
                    return  # Already cyclic
            
            mod = fcurve.modifiers.new('CYCLES')
            mod.mode_before = 'REPEAT'
            mod.mode_after = 'REPEAT'


def create_idle_animation(
    armature: bpy.types.Object,
    cycle_frames: int = 60,
    breath_amount: float = 0.02,
    sway_amount: float = 0.01,
    start_frame: int = 1
) -> dict:
    """
    Create a subtle idle breathing/swaying animation.
    
    Args:
        armature: Character armature
        cycle_frames: Frames per breath cycle
        breath_amount: Chest expansion amount
        sway_amount: Body sway amount
        start_frame: Starting frame
    
    Returns:
        Dictionary with animation info
    """
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    bone_mapping = _find_bones(armature)
    
    for frame_offset in range(cycle_frames):
        frame = start_frame + frame_offset
        bpy.context.scene.frame_set(frame)
        
        t = frame_offset / cycle_frames
        
        # Breathing (slow sine wave)
        breath = math.sin(t * 2 * math.pi) * breath_amount
        
        # Subtle sway
        sway = math.sin((t + 0.5) * 2 * math.pi) * sway_amount
        
        if bone_mapping.get('spine'):
            spine = armature.pose.bones.get(bone_mapping['spine'])
            if spine:
                spine.location.z = breath
                spine.location.x = sway
                spine.keyframe_insert(data_path="location", frame=frame)
    
    _make_cyclic(armature)
    
    return {
        'armature': armature.name,
        'start_frame': start_frame,
        'end_frame': start_frame + cycle_frames - 1,
        'type': 'idle'
    }


# Standalone execution
if __name__ == "__main__":
    # Find armature in scene
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
    
    if armatures:
        result = create_walk_cycle(armatures[0], cycle_frames=24)
        print(f"Created walk cycle: frames {result['start_frame']}-{result['end_frame']}")
    else:
        print("No armature found in scene. Add an armature first.")
