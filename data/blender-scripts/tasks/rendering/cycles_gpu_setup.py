"""
{
  "title": "Cycles GPU Rendering Setup",
  "category": "rendering",
  "subcategory": "cycles",
  "tags": ["cycles", "gpu", "cuda", "optix", "render", "performance", "quality"],
  "difficulty": "beginner",
  "description": "Configures Blender for optimal GPU rendering with Cycles, including device selection and quality settings.",
  "blender_version": "3.0+"
}
"""
import bpy


def setup_cycles_gpu(
    device_type: str = 'OPTIX',
    samples: int = 256,
    use_denoising: bool = True,
    denoiser: str = 'OPTIX',
    use_adaptive_sampling: bool = True,
    noise_threshold: float = 0.01
) -> dict:
    """
    Configure Cycles for optimal GPU rendering.
    
    Args:
        device_type: 'OPTIX' (NVIDIA RTX), 'CUDA' (NVIDIA), 'HIP' (AMD), 'METAL' (Apple)
        samples: Render samples (higher = quality, lower = speed)
        use_denoising: Enable AI denoising
        denoiser: 'OPTIX', 'OPENIMAGEDENOISE', or 'NONE'
        use_adaptive_sampling: Stop early when noise is low
        noise_threshold: Adaptive sampling threshold (lower = higher quality)
    
    Returns:
        Dictionary with current settings
    
    Example:
        >>> setup_cycles_gpu('OPTIX', samples=512, denoiser='OPTIX')
    """
    scene = bpy.context.scene
    
    # Set render engine to Cycles
    scene.render.engine = 'CYCLES'
    
    # Configure compute device
    preferences = bpy.context.preferences
    cycles_prefs = preferences.addons['cycles'].preferences
    
    # Set device type
    cycles_prefs.compute_device_type = device_type
    
    # Get and enable all devices of this type
    cycles_prefs.get_devices()
    for device in cycles_prefs.devices:
        device.use = True
    
    # Set scene to use GPU
    scene.cycles.device = 'GPU'
    
    # Sampling settings
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = use_adaptive_sampling
    if use_adaptive_sampling:
        scene.cycles.adaptive_threshold = noise_threshold
    
    # Denoising
    scene.cycles.use_denoising = use_denoising
    if use_denoising:
        scene.cycles.denoiser = denoiser
    
    return {
        'engine': 'CYCLES',
        'device': 'GPU',
        'device_type': device_type,
        'samples': samples,
        'denoising': use_denoising,
        'adaptive_sampling': use_adaptive_sampling
    }


def setup_cycles_quality(
    preset: str = 'HIGH',
    custom_samples: int = None
) -> dict:
    """
    Apply quality presets for Cycles rendering.
    
    Args:
        preset: 'PREVIEW', 'MEDIUM', 'HIGH', 'ULTRA', or 'CUSTOM'
        custom_samples: Sample count for CUSTOM preset
    
    Returns:
        Applied settings dictionary
    
    Example:
        >>> setup_cycles_quality('HIGH')
    """
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    
    presets = {
        'PREVIEW': {
            'samples': 64,
            'use_denoising': True,
            'max_bounces': 4,
            'diffuse_bounces': 2,
            'glossy_bounces': 2,
            'transmission_bounces': 4,
        },
        'MEDIUM': {
            'samples': 128,
            'use_denoising': True,
            'max_bounces': 8,
            'diffuse_bounces': 4,
            'glossy_bounces': 4,
            'transmission_bounces': 8,
        },
        'HIGH': {
            'samples': 512,
            'use_denoising': True,
            'max_bounces': 12,
            'diffuse_bounces': 6,
            'glossy_bounces': 6,
            'transmission_bounces': 12,
        },
        'ULTRA': {
            'samples': 2048,
            'use_denoising': False,
            'max_bounces': 16,
            'diffuse_bounces': 8,
            'glossy_bounces': 8,
            'transmission_bounces': 16,
        },
        'CUSTOM': {
            'samples': custom_samples or 256,
            'use_denoising': True,
            'max_bounces': 12,
            'diffuse_bounces': 6,
            'glossy_bounces': 6,
            'transmission_bounces': 12,
        }
    }
    
    settings = presets.get(preset.upper(), presets['HIGH'])
    
    scene.cycles.samples = settings['samples']
    scene.cycles.use_denoising = settings['use_denoising']
    scene.cycles.max_bounces = settings['max_bounces']
    scene.cycles.diffuse_bounces = settings['diffuse_bounces']
    scene.cycles.glossy_bounces = settings['glossy_bounces']
    scene.cycles.transmission_bounces = settings['transmission_bounces']
    
    return settings


def setup_transparent_render(
    enable: bool = True,
    format: str = 'PNG'
) -> None:
    """
    Configure render for transparent background.
    
    Args:
        enable: Enable transparent background
        format: Output format (PNG recommended for transparency)
    
    Example:
        >>> setup_transparent_render(True, 'PNG')
    """
    scene = bpy.context.scene
    
    scene.render.film_transparent = enable
    scene.render.image_settings.file_format = format
    
    if format == 'PNG':
        scene.render.image_settings.color_mode = 'RGBA' if enable else 'RGB'
        scene.render.image_settings.color_depth = '16'


def setup_render_output(
    resolution: tuple = (1920, 1080),
    percentage: int = 100,
    output_path: str = "//render_",
    format: str = 'PNG',
    frame_range: tuple = None
) -> None:
    """
    Configure render output settings.
    
    Args:
        resolution: (width, height) in pixels
        percentage: Scale percentage (50 = half resolution)
        output_path: Output file path (// = relative)
        format: 'PNG', 'JPEG', 'EXR', 'FFMPEG'
        frame_range: (start, end) frames for animation
    
    Example:
        >>> setup_render_output((3840, 2160), 100, "//4k_render_", 'PNG')
    """
    scene = bpy.context.scene
    
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = percentage
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = format
    
    if frame_range:
        scene.frame_start = frame_range[0]
        scene.frame_end = frame_range[1]


def get_render_time_estimate(samples: int, resolution: tuple, scene_complexity: str = 'MEDIUM') -> str:
    """
    Estimate render time based on settings (rough estimate).
    
    Args:
        samples: Render samples
        resolution: (width, height)
        scene_complexity: 'LOW', 'MEDIUM', 'HIGH'
    
    Returns:
        Estimated time string
    """
    base_time = 0.001  # ms per pixel per sample
    
    complexity_multipliers = {
        'LOW': 0.5,
        'MEDIUM': 1.0,
        'HIGH': 2.5
    }
    
    pixels = resolution[0] * resolution[1]
    multiplier = complexity_multipliers.get(scene_complexity.upper(), 1.0)
    
    total_ms = pixels * samples * base_time * multiplier
    total_seconds = total_ms / 1000
    
    if total_seconds < 60:
        return f"~{int(total_seconds)} seconds"
    elif total_seconds < 3600:
        return f"~{int(total_seconds / 60)} minutes"
    else:
        return f"~{total_seconds / 3600:.1f} hours"


# Standalone execution
if __name__ == "__main__":
    # Configure for high-quality GPU rendering
    settings = setup_cycles_gpu('OPTIX', samples=512)
    setup_cycles_quality('HIGH')
    setup_render_output((1920, 1080), 100, "//render_")
    
    print(f"Cycles GPU configured: {settings}")
    print(f"Estimated render time: {get_render_time_estimate(512, (1920, 1080), 'MEDIUM')}")
