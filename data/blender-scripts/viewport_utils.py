"""
{
  "title": "Viewport Utilities",
  "category": "interface",
  "tags": ["viewport", "3d", "view", "camera", "navigation"],
  "description": "Functions for controlling 3D viewport settings.",
  "blender_version": "3.0+"
}
"""
import bpy


def frame_selected() -> None:
    """Frame selected objects in viewport."""
    bpy.ops.view3d.view_selected()


def frame_all() -> None:
    """Frame all objects in viewport."""
    bpy.ops.view3d.view_all()


def set_view(view: str) -> None:
    """
    Set viewport to preset view.
    
    Args:
        view: 'FRONT', 'BACK', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM', 'CAMERA'
    """
    views = {
        'FRONT': 'FRONT',
        'BACK': 'BACK',
        'LEFT': 'LEFT',
        'RIGHT': 'RIGHT',
        'TOP': 'TOP',
        'BOTTOM': 'BOTTOM',
        'CAMERA': 'CAMERA'
    }
    
    if view in views:
        bpy.ops.view3d.view_axis(type=views[view])


def toggle_orthographic() -> None:
    """Toggle orthographic/perspective view."""
    bpy.ops.view3d.view_persportho()


def set_shading_mode(mode: str) -> None:
    """
    Set viewport shading mode.
    
    Args:
        mode: 'WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED'
    """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = mode


def set_solid_shading_options(
    color_type: str = 'MATERIAL',
    light: str = 'STUDIO',
    show_shadows: bool = True
) -> None:
    """Configure solid shading."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    shading = space.shading
                    shading.color_type = color_type
                    shading.light = light
                    shading.show_shadows = show_shadows


def show_overlays(show: bool) -> None:
    """Toggle viewport overlays."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.show_overlays = show


def show_grid(show: bool) -> None:
    """Toggle floor grid visibility."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.show_floor = show


def show_axes(show: bool) -> None:
    """Toggle axes visibility."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.show_axis_x = show
                    space.overlay.show_axis_y = show
                    space.overlay.show_axis_z = show


def set_clip_distances(near: float, far: float) -> None:
    """Set viewport clip start/end."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_start = near
                    space.clip_end = far


def toggle_xray() -> None:
    """Toggle X-Ray mode."""
    bpy.context.space_data.shading.show_xray = not bpy.context.space_data.shading.show_xray


def set_focal_length(length: float) -> None:
    """Set viewport camera focal length."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.lens = length
