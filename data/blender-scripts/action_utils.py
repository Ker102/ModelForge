"""
{
  "title": "Action & NLA Utilities (Blender 5.0+)",
  "category": "animation",
  "tags": ["action", "animation", "nla", "keyframe", "clip", "slotted-actions", "channelbag", "slot", "bake"],
  "description": "Functions for managing animation actions, NLA tracks, and the Blender 5.0+ Slotted Actions system. Uses channelbag-based F-Curve access, slot-aware action assignment, and the new BakeOptions class.",
  "blender_version": "5.0+"
}
"""
import bpy
from bpy_extras import anim_utils


# =============================================================================
# BLENDER 5.0+ SLOTTED ACTIONS
# =============================================================================
# In Blender 5.0, the Action architecture changed fundamentally:
#
#   OLD (removed):  action.fcurves, action.groups, action.id_root
#   NEW:            action → layers → strips → channelbag(slot) → fcurves
#
# Key concepts:
#   - ActionSlot: Identifies which data-block the animation targets
#   - ActionLayer: Contains strips (multiple layers = animation blending)
#   - ActionKeyframeStrip: Contains channelbags
#   - ActionChannelbag: Per-slot container with fcurves & groups
#
# Helper functions:
#   anim_utils.action_get_channelbag_for_slot(action, slot)   → read
#   anim_utils.action_ensure_channelbag_for_slot(action, slot) → create
# =============================================================================


def create_action(name: str) -> bpy.types.Action:
    """Create a new action."""
    return bpy.data.actions.new(name)


def assign_action(
    obj: bpy.types.Object,
    action: bpy.types.Action,
    slot_name: str = None
) -> None:
    """
    Assign action to object with proper slot binding (Blender 5.0+).
    
    In Blender 5.0, assigning an action also requires binding to a slot.
    The slot identifies which channels in the action belong to this object.
    
    Args:
        obj: Object to animate
        action: Action to assign
        slot_name: Optional slot name to bind to. If None, auto-assigns.
    
    Example:
        >>> assign_action(cube, walk_action)
        >>> assign_action(cube, multi_action, slot_name='OBCube')
    """
    if not obj.animation_data:
        obj.animation_data_create()
    
    obj.animation_data.action = action
    
    # In 5.0+, we need to assign a slot as well
    if slot_name:
        # Find slot by name
        for slot in action.slots:
            if slot.name == slot_name:
                obj.animation_data.action_slot = slot
                return
    
    # Auto-assign a suitable slot
    if hasattr(obj.animation_data, 'action_suitable_slots') and obj.animation_data.action_suitable_slots:
        obj.animation_data.action_slot = obj.animation_data.action_suitable_slots[0]


def create_action_with_slot(
    name: str,
    obj: bpy.types.Object
) -> tuple:
    """
    Create a new action and a slot bound to the given object.
    
    Returns:
        Tuple of (Action, ActionSlot)
    
    Example:
        >>> action, slot = create_action_with_slot("WalkCycle", character)
    """
    action = bpy.data.actions.new(name)
    slot = action.slots.new(id_type=obj.id_type, name=obj.name)
    
    if not obj.animation_data:
        obj.animation_data_create()
    
    obj.animation_data.action = action
    obj.animation_data.action_slot = slot
    
    return action, slot


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
    """
    Push action to NLA track (Blender 5.0+ slot-aware).
    
    In 5.0+, NLA strips have action_slot property for slot binding.
    """
    if not obj.animation_data:
        obj.animation_data_create()
    
    action = action or obj.animation_data.action
    if not action:
        return None
    
    track = obj.animation_data.nla_tracks.new()
    track.name = track_name
    
    # Get frame range from channelbag instead of action.frame_range
    start_frame = 1
    slot = obj.animation_data.action_slot
    if slot:
        cb = anim_utils.action_get_channelbag_for_slot(action, slot)
        if cb and cb.fcurves:
            # Find earliest keyframe
            min_frame = float('inf')
            for fc in cb.fcurves:
                if fc.keyframe_points:
                    min_frame = min(min_frame, fc.keyframe_points[0].co.x)
            if min_frame != float('inf'):
                start_frame = int(min_frame)
    
    strip = track.strips.new(action.name, start_frame, action)
    
    # Auto-assign slot for the strip (5.0+)
    if hasattr(strip, 'action_suitable_slots') and strip.action_suitable_slots:
        strip.action_slot = strip.action_suitable_slots[0]
    
    return strip


def create_nla_strip(
    obj: bpy.types.Object,
    action: bpy.types.Action,
    start_frame: int,
    track_name: str = "Track"
) -> bpy.types.NlaStrip:
    """Create NLA strip from action on a specific track."""
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
    
    # Auto-assign slot (5.0+)
    if hasattr(strip, 'action_suitable_slots') and strip.action_suitable_slots:
        strip.action_slot = strip.action_suitable_slots[0]
    
    return strip


def set_strip_blend_mode(
    strip: bpy.types.NlaStrip,
    blend_type: str = 'REPLACE'
) -> None:
    """Set NLA strip blend mode."""
    strip.blend_type = blend_type  # REPLACE, ADD, SUBTRACT, MULTIPLY, COMBINE


def set_strip_extrapolation(
    strip: bpy.types.NlaStrip,
    extrapolation: str = 'HOLD'
) -> None:
    """Set NLA strip extrapolation."""
    strip.extrapolation = extrapolation  # NOTHING, HOLD, HOLD_FORWARD


def scale_action(
    action: bpy.types.Action,
    scale: float,
    obj: bpy.types.Object = None
) -> None:
    """
    Scale action keyframes using channelbag API (Blender 5.0+).
    
    Args:
        action: Action to scale
        scale: Scale factor for frame positions
        obj: Object to get slot from (needed for channelbag access).
             If None, attempts to find any slot in the action.
    """
    slot = None
    if obj and obj.animation_data:
        slot = obj.animation_data.action_slot
    
    if not slot and action.slots:
        slot = action.slots[0]
    
    if not slot:
        return
    
    cb = anim_utils.action_get_channelbag_for_slot(action, slot)
    if not cb:
        return
    
    for fcurve in cb.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.co.x *= scale
            keyframe.handle_left.x *= scale
            keyframe.handle_right.x *= scale


def offset_action(
    action: bpy.types.Action,
    offset: float,
    obj: bpy.types.Object = None
) -> None:
    """
    Offset action keyframes using channelbag API (Blender 5.0+).
    
    Args:
        action: Action to offset
        offset: Frame offset to apply
        obj: Object to get slot from. If None, uses first slot.
    """
    slot = None
    if obj and obj.animation_data:
        slot = obj.animation_data.action_slot
    
    if not slot and action.slots:
        slot = action.slots[0]
    
    if not slot:
        return
    
    cb = anim_utils.action_get_channelbag_for_slot(action, slot)
    if not cb:
        return
    
    for fcurve in cb.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.co.x += offset
            keyframe.handle_left.x += offset
            keyframe.handle_right.x += offset


def list_actions() -> list:
    """Return list of all action names."""
    return [a.name for a in bpy.data.actions]


def list_action_slots(action: bpy.types.Action) -> list:
    """
    List all slots in an action (Blender 5.0+).
    
    Returns:
        List of dicts with slot name, target_id_type, and handle
    """
    return [
        {
            'name': slot.name,
            'target_id_type': slot.target_id_type,
            'handle': slot.handle
        }
        for slot in action.slots
    ]


def delete_action(name: str) -> None:
    """Delete action by name."""
    if name in bpy.data.actions:
        bpy.data.actions.remove(bpy.data.actions[name])


def clear_animation(obj: bpy.types.Object) -> None:
    """Clear all animation from object."""
    if obj.animation_data:
        obj.animation_data.action = None
        # Remove NLA tracks safely (iterate in reverse)
        tracks = list(obj.animation_data.nla_tracks)
        for track in reversed(tracks):
            obj.animation_data.nla_tracks.remove(track)


def get_action_info(action: bpy.types.Action) -> dict:
    """
    Get detailed information about an action's structure (5.0+).
    Useful for debugging the new layered action hierarchy.
    
    Returns:
        Dict with layers, strips, channelbags, slots info
    """
    info = {
        'name': action.name,
        'slots': [],
        'layers': [],
        'total_fcurves': 0
    }
    
    for slot in action.slots:
        info['slots'].append({
            'name': slot.name,
            'target_id_type': slot.target_id_type
        })
    
    for layer in action.layers:
        layer_info = {'name': layer.name, 'strips': []}
        for strip in layer.strips:
            strip_info = {'type': strip.type, 'channelbags': []}
            if hasattr(strip, 'channelbag'):
                for slot in action.slots:
                    cb = strip.channelbag(slot)
                    if cb:
                        cb_info = {
                            'slot': slot.name,
                            'fcurve_count': len(cb.fcurves),
                            'group_count': len(cb.groups)
                        }
                        info['total_fcurves'] += len(cb.fcurves)
                        strip_info['channelbags'].append(cb_info)
            layer_info['strips'].append(strip_info)
        info['layers'].append(layer_info)
    
    return info
