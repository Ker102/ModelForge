"""
{
  "title": "Action/Animation Utilities",
  "category": "animation",
  "tags": ["action", "animation", "nla", "keyframe", "clip"],
  "description": "Functions for managing animation actions and NLA.",
  "blender_version": "3.0+"
}
"""
import bpy


def create_action(name: str) -> bpy.types.Action:
    """Create a new action."""
    return bpy.data.actions.new(name)


def assign_action(
    obj: bpy.types.Object,
    action: bpy.types.Action
) -> None:
    """Assign action to object."""
    if not obj.animation_data:
        obj.animation_data_create()
    obj.animation_data.action = action


def duplicate_action(
    action: bpy.types.Action,
    new_name: str = None
) -> bpy.types.Action:
    """Duplicate an action."""
    new_action = action.copy()
    if new_name:
        new_action.name = new_name
    return new_action


def push_action_to_nla(
    obj: bpy.types.Object,
    action: bpy.types.Action = None,
    track_name: str = "NLATrack"
) -> bpy.types.NlaStrip:
    """Push action to NLA track."""
    if not obj.animation_data:
        obj.animation_data_create()
    
    action = action or obj.animation_data.action
    if not action:
        return None
    
    track = obj.animation_data.nla_tracks.new()
    track.name = track_name
    
    strip = track.strips.new(action.name, int(action.frame_range[0]), action)
    
    return strip


def create_nla_strip(
    obj: bpy.types.Object,
    action: bpy.types.Action,
    start_frame: int,
    track_name: str = "Track"
) -> bpy.types.NlaStrip:
    """Create NLA strip from action."""
    if not obj.animation_data:
        obj.animation_data_create()
    
    track = None
    for t in obj.animation_data.nla_tracks:
        if t.name == track_name:
            track = t
            break
    
    if not track:
        track = obj.animation_data.nla_tracks.new()
        track.name = track_name
    
    strip = track.strips.new(action.name, start_frame, action)
    return strip


def set_strip_blend_mode(
    strip: bpy.types.NlaStrip,
    blend_type: str = 'REPLACE'
) -> None:
    """Set NLA strip blend mode."""
    strip.blend_type = blend_type  # REPLACE, ADD, SUBTRACT, MULTIPLY


def set_strip_extrapolation(
    strip: bpy.types.NlaStrip,
    extrapolation: str = 'HOLD'
) -> None:
    """Set NLA strip extrapolation."""
    strip.extrapolation = extrapolation  # NOTHING, HOLD, HOLD_FORWARD


def scale_action(
    action: bpy.types.Action,
    scale: float
) -> None:
    """Scale action keyframes."""
    for fcurve in action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.co.x *= scale
            keyframe.handle_left.x *= scale
            keyframe.handle_right.x *= scale


def offset_action(
    action: bpy.types.Action,
    offset: float
) -> None:
    """Offset action keyframes."""
    for fcurve in action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.co.x += offset
            keyframe.handle_left.x += offset
            keyframe.handle_right.x += offset


def list_actions() -> list:
    """Return list of all action names."""
    return [a.name for a in bpy.data.actions]


def delete_action(name: str) -> None:
    """Delete action by name."""
    if name in bpy.data.actions:
        bpy.data.actions.remove(bpy.data.actions[name])


def clear_animation(obj: bpy.types.Object) -> None:
    """Clear all animation from object."""
    if obj.animation_data:
        obj.animation_data.action = None
        for track in obj.animation_data.nla_tracks:
            obj.animation_data.nla_tracks.remove(track)
