"""
{
  "title": "NLA Animation Composition",
  "category": "animation",
  "subcategory": "nla",
  "tags": ["nla", "animation", "blend", "layer", "action", "strip", "track", "composition", "overlay", "loop"],
  "difficulty": "advanced",
  "description": "Compose multiple animation actions using NLA tracks, strips, blending modes, and influence control. Supports action layering, NLA transitions, and cyclic loops.",
  "blender_version": "5.0+",
  "estimated_objects": 0
}
"""
import bpy
import math


def create_nla_track(
    obj: bpy.types.Object,
    track_name: str = "Track"
) -> bpy.types.NlaTrack:
    """
    Create a new NLA track on an object.

    Args:
        obj: Any Blender object with animation data
        track_name: Name for the NLA track

    Returns:
        The new NLA track

    Example:
        >>> track = create_nla_track(bpy.data.objects['Armature'], "Base_Movement")
    """
    if not obj.animation_data:
        obj.animation_data_create()

    track = obj.animation_data.nla_tracks.new()
    track.name = track_name
    return track


def add_action_strip(
    track: bpy.types.NlaTrack,
    action: bpy.types.Action,
    strip_name: str = "Strip",
    start_frame: int = 1,
    blend_type: str = 'REPLACE',
    influence: float = 1.0,
    repeat: float = 1.0,
    blend_in: float = 0,
    blend_out: float = 0
) -> bpy.types.NlaStrip:
    """
    Add an action strip to an NLA track.

    Args:
        track: NLA track to add the strip to
        action: Blender action to reference
        strip_name: Display name for the strip
        start_frame: Frame where the strip begins
        blend_type: 'REPLACE', 'ADD', 'MULTIPLY', or 'SUBTRACT'
        influence: Strip influence (0.0 to 1.0)
        repeat: Number of times to repeat the action
        blend_in: Frames to ease in
        blend_out: Frames to ease out

    Returns:
        The new NLA strip

    Example:
        >>> strip = add_action_strip(track, walk_action, "Walk", start_frame=1, repeat=5)
    """
    strip = track.strips.new(
        name=strip_name,
        start=start_frame,
        action=action
    )

    strip.blend_type = blend_type
    strip.influence = influence
    strip.repeat = repeat

    if blend_in > 0:
        strip.blend_in = blend_in
    if blend_out > 0:
        strip.blend_out = blend_out

    return strip


def compose_animation_layers(
    obj: bpy.types.Object,
    actions: list,
    clear_existing: bool = True
) -> list:
    """
    Compose multiple animation actions as layered NLA tracks.
    The first action is the base (REPLACE), subsequent actions overlay (ADD).

    Args:
        obj: Object to animate (typically an armature)
        actions: List of dicts with keys:
            - 'action': bpy.types.Action (required)
            - 'name': str (track/strip name)
            - 'start': int (start frame, default 1)
            - 'blend_type': str (default 'ADD' for overlays)
            - 'influence': float (default 1.0)
            - 'repeat': float (default 1.0)
            - 'blend_in': float (default 0)
            - 'blend_out': float (default 0)
        clear_existing: Remove existing NLA tracks first

    Returns:
        List of created NLA strips

    Example:
        >>> compose_animation_layers(armature, [
        ...     {'action': walk_action, 'name': 'Walk', 'repeat': 5},
        ...     {'action': wave_action, 'name': 'Wave', 'start': 50,
        ...      'influence': 0.85, 'blend_in': 10, 'blend_out': 10},
        ... ])
    """
    if not obj.animation_data:
        obj.animation_data_create()

    anim_data = obj.animation_data

    # Clear existing NLA tracks if requested
    if clear_existing:
        for track in list(anim_data.nla_tracks):
            anim_data.nla_tracks.remove(track)

    # Clear active action so NLA takes full control
    anim_data.action = None

    strips = []
    for i, layer in enumerate(actions):
        action = layer['action']
        name = layer.get('name', action.name)

        # First layer is REPLACE (base), rest are ADD (overlay)
        default_blend = 'REPLACE' if i == 0 else 'ADD'

        track = create_nla_track(obj, f"Track_{name}")
        strip = add_action_strip(
            track=track,
            action=action,
            strip_name=name,
            start_frame=layer.get('start', 1),
            blend_type=layer.get('blend_type', default_blend),
            influence=layer.get('influence', 1.0),
            repeat=layer.get('repeat', 1.0),
            blend_in=layer.get('blend_in', 0),
            blend_out=layer.get('blend_out', 0),
        )
        strips.append(strip)

    return strips


def stash_action_to_nla(
    obj: bpy.types.Object,
    action: bpy.types.Action = None,
    track_name: str = None
) -> bpy.types.NlaStrip:
    """
    Stash (push down) an action to the NLA, freeing the active action slot.
    This is the non-operator equivalent of the 'Push Down' button in the Action Editor.

    Args:
        obj: Object with animation data
        action: Action to stash (defaults to current active action)
        track_name: Optional track name

    Returns:
        The stashed NLA strip

    Example:
        >>> stash_action_to_nla(armature)  # stash current active action
    """
    if not obj.animation_data:
        obj.animation_data_create()

    anim_data = obj.animation_data

    if action is None:
        action = anim_data.action
        if not action:
            raise ValueError("No active action to stash")

    name = track_name or action.name
    track = anim_data.nla_tracks.new()
    track.name = name

    strip = track.strips.new(
        name=action.name,
        start=int(action.frame_range[0]),
        action=action
    )

    # Clear active action
    anim_data.action = None

    return strip


def create_nla_transition(
    obj: bpy.types.Object,
    action_a: bpy.types.Action,
    action_b: bpy.types.Action,
    transition_frames: int = 10,
    start_frame: int = 1
) -> dict:
    """
    Create a smooth transition between two actions using NLA strip blending.
    Places action_a first, then action_b with a crossfade overlap.

    Args:
        obj: Object to animate
        action_a: First action (plays first)
        action_b: Second action (blends in)
        transition_frames: Duration of crossfade overlap
        start_frame: Frame where the sequence begins

    Returns:
        Dict with strip references and timing info

    Example:
        >>> create_nla_transition(armature, idle_action, run_action, transition_frames=15)
    """
    if not obj.animation_data:
        obj.animation_data_create()

    anim_data = obj.animation_data
    anim_data.action = None

    # Calculate timing
    a_duration = int(action_a.frame_range[1] - action_a.frame_range[0])
    b_start = start_frame + a_duration - transition_frames

    # Track for action A
    track_a = create_nla_track(obj, f"Trans_{action_a.name}")
    strip_a = add_action_strip(
        track_a, action_a, action_a.name,
        start_frame=start_frame,
        blend_out=transition_frames
    )

    # Track for action B (on top, with blend-in)
    track_b = create_nla_track(obj, f"Trans_{action_b.name}")
    strip_b = add_action_strip(
        track_b, action_b, action_b.name,
        start_frame=b_start,
        blend_in=transition_frames
    )

    return {
        'strip_a': strip_a,
        'strip_b': strip_b,
        'transition_start': b_start,
        'transition_end': b_start + transition_frames,
        'total_frames': a_duration + int(action_b.frame_range[1] - action_b.frame_range[0]) - transition_frames
    }


def bake_nla_to_action(
    obj: bpy.types.Object,
    frame_start: int = 1,
    frame_end: int = 250,
    action_name: str = "BakedNLA"
) -> bpy.types.Action:
    """
    Bake the entire NLA stack into a single action.
    Essential before export — other software cannot read NLA data.

    Args:
        obj: Object with NLA tracks
        frame_start: Start frame to bake
        frame_end: End frame to bake
        action_name: Name for the baked action

    Returns:
        The baked action

    Example:
        >>> baked = bake_nla_to_action(armature, 1, 240, "FinalAnimation")
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.nla.bake(
        frame_start=frame_start,
        frame_end=frame_end,
        only_selected=False,
        visual_keying=True,
        clear_constraints=False,
        bake_types={'POSE'} if obj.type == 'ARMATURE' else {'OBJECT'}
    )

    # Rename the baked action
    if obj.animation_data and obj.animation_data.action:
        obj.animation_data.action.name = action_name
        return obj.animation_data.action

    return None


# Standalone execution
if __name__ == "__main__":
    # Demo: create two simple actions and compose them via NLA
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']

    if armatures:
        arm = armatures[0]
        actions = list(bpy.data.actions)
        if len(actions) >= 2:
            strips = compose_animation_layers(arm, [
                {'action': actions[0], 'name': 'Base', 'repeat': 3},
                {'action': actions[1], 'name': 'Overlay',
                 'start': 20, 'influence': 0.8, 'blend_in': 10, 'blend_out': 10},
            ])
            print(f"Composed {len(strips)} NLA layers")
        else:
            print("Need at least 2 actions in the file for NLA composition demo")
    else:
        print("No armature found in scene")
