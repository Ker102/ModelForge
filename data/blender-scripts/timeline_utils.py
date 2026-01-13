"""
{
  "title": "Timeline and Playback Utilities",
  "category": "animation",
  "tags": ["timeline", "playback", "frame", "keyframe", "preview"],
  "description": "Functions for controlling timeline and playback settings.",
  "blender_version": "3.0+"
}
"""
import bpy


def set_frame_range(start: int, end: int) -> None:
    """Set scene frame range."""
    scene = bpy.context.scene
    scene.frame_start = start
    scene.frame_end = end


def set_fps(fps: float, base: int = 1) -> None:
    """
    Set scene framerate.
    
    Args:
        fps: Frames per second
        base: Frame base (usually 1)
    """
    scene = bpy.context.scene
    scene.render.fps = int(fps)
    scene.render.fps_base = base


def set_current_frame(frame: int) -> None:
    """Jump to specific frame."""
    bpy.context.scene.frame_set(frame)


def get_current_frame() -> int:
    """Get current frame number."""
    return bpy.context.scene.frame_current


def play_animation() -> None:
    """Start animation playback."""
    bpy.ops.screen.animation_play()


def stop_animation() -> None:
    """Stop animation playback."""
    bpy.ops.screen.animation_cancel()


def toggle_playback() -> None:
    """Toggle animation playback."""
    if bpy.context.screen.is_animation_playing:
        stop_animation()
    else:
        play_animation()


def jump_to_start() -> None:
    """Jump to start frame."""
    bpy.context.scene.frame_set(bpy.context.scene.frame_start)


def jump_to_end() -> None:
    """Jump to end frame."""
    bpy.context.scene.frame_set(bpy.context.scene.frame_end)


def set_preview_range(start: int, end: int) -> None:
    """Set preview range for playback."""
    scene = bpy.context.scene
    scene.use_preview_range = True
    scene.frame_preview_start = start
    scene.frame_preview_end = end


def clear_preview_range() -> None:
    """Clear preview range."""
    bpy.context.scene.use_preview_range = False


def set_playback_sync(mode: str = 'AUDIO_SYNC') -> None:
    """
    Set playback sync mode.
    
    Args:
        mode: 'NONE', 'FRAME_DROP', 'AUDIO_SYNC'
    """
    bpy.context.scene.sync_mode = mode


def enable_audio_scrubbing(enabled: bool = True) -> None:
    """Enable/disable audio scrubbing."""
    bpy.context.scene.use_audio_scrub = enabled


def set_audio_volume(volume: float = 1.0) -> None:
    """Set scene audio volume (0-1)."""
    bpy.context.scene.audio_volume = volume


def mute_audio(mute: bool = True) -> None:
    """Mute/unmute scene audio."""
    bpy.context.scene.use_audio = not mute


def go_to_next_keyframe() -> None:
    """Jump to next keyframe."""
    bpy.ops.screen.keyframe_jump(next=True)


def go_to_prev_keyframe() -> None:
    """Jump to previous keyframe."""
    bpy.ops.screen.keyframe_jump(next=False)


def go_to_next_marker() -> None:
    """Jump to next marker."""
    bpy.ops.screen.marker_jump(next=True)


def go_to_prev_marker() -> None:
    """Jump to previous marker."""
    bpy.ops.screen.marker_jump(next=False)


def add_marker(name: str = "", frame: int = None) -> bpy.types.TimelineMarker:
    """
    Add timeline marker.
    
    Args:
        name: Marker name
        frame: Frame number (current if None)
    
    Returns:
        Created marker
    """
    if frame is None:
        frame = bpy.context.scene.frame_current
    
    marker = bpy.context.scene.timeline_markers.new(name, frame=frame)
    return marker


def remove_marker(name: str) -> bool:
    """Remove marker by name."""
    marker = bpy.context.scene.timeline_markers.get(name)
    if marker:
        bpy.context.scene.timeline_markers.remove(marker)
        return True
    return False


def list_markers() -> list:
    """List all markers with their frames."""
    return [(m.name, m.frame) for m in bpy.context.scene.timeline_markers]


def clear_all_markers() -> None:
    """Remove all timeline markers."""
    bpy.context.scene.timeline_markers.clear()


def set_frame_step(step: int = 1) -> None:
    """Set frame step for stepping through animation."""
    bpy.context.scene.frame_step = step


def bind_camera_to_marker(
    marker: bpy.types.TimelineMarker,
    camera: bpy.types.Object
) -> None:
    """Bind camera to marker for camera switching."""
    marker.camera = camera
