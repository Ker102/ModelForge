"""
{
  "title": "Render Utilities",
  "category": "rendering",
  "tags": ["render", "cycles", "eevee", "output", "compositing", "bake"],
  "description": "Functions for configuring rendering settings, output, and baking.",
  "blender_version": "3.0+"
}
"""
import bpy
import os


def render_image(output_path: str = None, open_result: bool = False) -> str:
    """
    Render current frame.
    
    Args:
        output_path: Save path (uses scene path if None)
        open_result: Open result in image viewer
    
    Returns:
        Path to rendered image
    
    Example:
        >>> render_image("//render_001.png")
    """
    scene = bpy.context.scene
    
    if output_path:
        scene.render.filepath = output_path
    
    bpy.ops.render.render(write_still=True)
    
    if open_result:
        bpy.ops.render.view_show()
    
    return bpy.path.abspath(scene.render.filepath)


def render_animation(
    output_path: str = None,
    frame_start: int = None,
    frame_end: int = None
) -> None:
    """
    Render animation frames.
    
    Args:
        output_path: Output path with frame placeholder (e.g., "//render_####")
        frame_start: Start frame (uses scene value if None)
        frame_end: End frame (uses scene value if None)
    
    Example:
        >>> render_animation("//frames/render_####.png", 1, 120)
    """
    scene = bpy.context.scene
    
    if output_path:
        scene.render.filepath = output_path
    if frame_start is not None:
        scene.frame_start = frame_start
    if frame_end is not None:
        scene.frame_end = frame_end
    
    bpy.ops.render.render(animation=True)


def set_render_engine(engine: str = 'CYCLES') -> None:
    """
    Set render engine.
    
    Args:
        engine: 'CYCLES', 'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'
    
    Example:
        >>> set_render_engine('CYCLES')
    """
    bpy.context.scene.render.engine = engine


def set_render_samples(
    samples: int = 128,
    viewport_samples: int = None
) -> None:
    """
    Set render sample count.
    
    Args:
        samples: Final render samples
        viewport_samples: Viewport preview samples
    """
    scene = bpy.context.scene
    
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = samples
        if viewport_samples:
            scene.cycles.preview_samples = viewport_samples
    elif 'EEVEE' in scene.render.engine:
        scene.eevee.taa_render_samples = samples
        if viewport_samples:
            scene.eevee.taa_samples = viewport_samples


def set_output_format(
    format: str = 'PNG',
    color_mode: str = 'RGBA',
    color_depth: str = '8',
    compression: int = 15
) -> None:
    """
    Set output image format.
    
    Args:
        format: 'PNG', 'JPEG', 'OPEN_EXR', 'TIFF', 'BMP'
        color_mode: 'RGB', 'RGBA', 'BW'
        color_depth: '8', '16', '32' (float for EXR)
        compression: Compression level (0-100 for PNG)
    
    Example:
        >>> set_output_format('PNG', 'RGBA', '16')
    """
    scene = bpy.context.scene
    
    scene.render.image_settings.file_format = format
    scene.render.image_settings.color_mode = color_mode
    
    if format == 'PNG':
        scene.render.image_settings.color_depth = color_depth
        scene.render.image_settings.compression = compression
    elif format == 'OPEN_EXR':
        scene.render.image_settings.color_depth = color_depth
        scene.render.image_settings.exr_codec = 'ZIP'


def set_video_output(
    format: str = 'FFMPEG',
    codec: str = 'H264',
    quality: str = 'HIGH',
    audio: bool = True
) -> None:
    """
    Configure video output settings.
    
    Args:
        format: 'FFMPEG', 'AVI_RAW', 'AVI_JPEG'
        codec: 'H264', 'MPEG4', 'WEBM', 'PNG'
        quality: 'LOWEST', 'LOW', 'MEDIUM', 'HIGH', 'LOSSLESS'
        audio: Include audio track
    
    Example:
        >>> set_video_output('FFMPEG', 'H264', 'HIGH')
    """
    scene = bpy.context.scene
    
    scene.render.image_settings.file_format = format
    
    if format == 'FFMPEG':
        scene.render.ffmpeg.format = 'MPEG4' if codec == 'H264' else codec
        scene.render.ffmpeg.codec = codec
        scene.render.ffmpeg.constant_rate_factor = quality
        
        if audio:
            scene.render.ffmpeg.audio_codec = 'AAC'
        else:
            scene.render.ffmpeg.audio_codec = 'NONE'


def bake_textures(
    bake_type: str = 'DIFFUSE',
    output_size: tuple = (1024, 1024),
    margin: int = 16,
    use_clear: bool = True,
    filepath: str = None
) -> None:
    """
    Bake textures from objects.
    
    Args:
        bake_type: 'DIFFUSE', 'NORMAL', 'AO', 'COMBINED', 'EMIT', 'ROUGHNESS'
        output_size: Texture size (width, height)
        margin: Edge margin in pixels
        use_clear: Clear image before baking
        filepath: Output file path
    
    Example:
        >>> bake_textures('NORMAL', (2048, 2048))
    """
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    
    bpy.ops.object.bake(
        type=bake_type,
        width=output_size[0],
        height=output_size[1],
        margin=margin,
        use_clear=use_clear,
        filepath=filepath if filepath else ''
    )


def setup_transparent_background(enable: bool = True) -> None:
    """
    Enable/disable transparent background.
    
    Args:
        enable: True for transparent, False for solid
    """
    bpy.context.scene.render.film_transparent = enable
    
    if enable:
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'


def setup_motion_blur(
    enable: bool = True,
    shutter: float = 0.5,
    position: str = 'CENTER'
) -> None:
    """
    Configure motion blur.
    
    Args:
        enable: Enable motion blur
        shutter: Shutter time (0-2, where 1 = full frame)
        position: 'START', 'CENTER', 'END'
    
    Example:
        >>> setup_motion_blur(True, shutter=0.3)
    """
    scene = bpy.context.scene
    
    if scene.render.engine == 'CYCLES':
        scene.render.use_motion_blur = enable
        scene.render.motion_blur_shutter = shutter
        scene.render.motion_blur_position = position
    elif 'EEVEE' in scene.render.engine:
        scene.eevee.use_motion_blur = enable
        scene.eevee.motion_blur_shutter = shutter


def add_render_layer_pass(pass_type: str) -> None:
    """
    Enable a render pass for compositing.
    
    Args:
        pass_type: 'diffuse_color', 'specular_color', 'ambient_occlusion',
                   'emission', 'environment', 'shadow', 'normal', 'uv', etc.
    """
    view_layer = bpy.context.view_layer
    
    pass_attrs = {
        'diffuse_color': 'use_pass_diffuse_color',
        'specular_color': 'use_pass_glossy_color',
        'ambient_occlusion': 'use_pass_ambient_occlusion',
        'emission': 'use_pass_emit',
        'environment': 'use_pass_environment',
        'shadow': 'use_pass_shadow',
        'normal': 'use_pass_normal',
        'uv': 'use_pass_uv',
        'z': 'use_pass_z',
        'mist': 'use_pass_mist',
        'object_index': 'use_pass_object_index',
        'material_index': 'use_pass_material_index'
    }
    
    attr = pass_attrs.get(pass_type.lower())
    if attr and hasattr(view_layer, attr):
        setattr(view_layer, attr, True)


def setup_overscan(percentage: int = 10) -> None:
    """
    Add border around render for edge effects.
    
    Args:
        percentage: Extra render area as percentage
    """
    scene = bpy.context.scene
    
    # Enable border render
    scene.render.use_border = True
    scene.render.use_crop_to_border = False
    
    # Set border with overscan
    margin = percentage / 100 / 2
    scene.render.border_min_x = -margin
    scene.render.border_max_x = 1 + margin
    scene.render.border_min_y = -margin
    scene.render.border_max_y = 1 + margin
