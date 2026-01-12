"""
{
  "title": "Eevee Optimized Setup",
  "category": "rendering",
  "subcategory": "optimization",
  "tags": ["eevee", "realtime", "optimization", "performance", "rendering"],
  "difficulty": "intermediate",
  "description": "Optimized Eevee render settings for fast previews and final renders.",
  "blender_version": "3.0+",
  "estimated_objects": 0
}
"""
import bpy


def setup_eevee_quality(quality: str = 'MEDIUM') -> dict:
    """
    Configure Eevee quality preset.
    
    Args:
        quality: 'LOW', 'MEDIUM', 'HIGH', 'ULTRA'
    
    Returns:
        Dictionary with applied settings
    """
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
    eevee = bpy.context.scene.eevee
    
    presets = {
        'LOW': {
            'samples': 16,
            'shadows': '512',
            'ssr': False,
            'ao': True,
            'bloom': False
        },
        'MEDIUM': {
            'samples': 32,
            'shadows': '1024',
            'ssr': True,
            'ao': True,
            'bloom': True
        },
        'HIGH': {
            'samples': 64,
            'shadows': '2048',
            'ssr': True,
            'ao': True,
            'bloom': True
        },
        'ULTRA': {
            'samples': 128,
            'shadows': '4096',
            'ssr': True,
            'ao': True,
            'bloom': True
        }
    }
    
    preset = presets.get(quality, presets['MEDIUM'])
    
    eevee.taa_render_samples = preset['samples']
    eevee.shadow_cascade_size = preset['shadows']
    eevee.use_ssr = preset['ssr']
    eevee.use_gtao = preset['ao']
    eevee.use_bloom = preset['bloom']
    
    return preset


def enable_eevee_reflections(
    quality: str = 'MEDIUM',
    thickness: float = 0.5
) -> None:
    """Enable screen-space reflections."""
    eevee = bpy.context.scene.eevee
    eevee.use_ssr = True
    eevee.use_ssr_refraction = True
    eevee.ssr_thickness = thickness
    
    if quality == 'HIGH':
        eevee.ssr_quality = 1.0
        eevee.ssr_max_roughness = 0.5
    else:
        eevee.ssr_quality = 0.5
        eevee.ssr_max_roughness = 0.3


def enable_eevee_shadows(soft: bool = True, contact: bool = True) -> None:
    """Configure shadow settings."""
    eevee = bpy.context.scene.eevee
    eevee.shadow_soft_max = 50 if soft else 0
    eevee.use_shadow_contact = contact


def enable_eevee_ambient_occlusion(
    distance: float = 0.5,
    factor: float = 1.0
) -> None:
    """Enable ambient occlusion."""
    eevee = bpy.context.scene.eevee
    eevee.use_gtao = True
    eevee.gtao_distance = distance
    eevee.gtao_factor = factor


def enable_eevee_bloom(
    threshold: float = 0.8,
    intensity: float = 0.05,
    radius: float = 6.5
) -> None:
    """Enable bloom/glow effect."""
    eevee = bpy.context.scene.eevee
    eevee.use_bloom = True
    eevee.bloom_threshold = threshold
    eevee.bloom_intensity = intensity
    eevee.bloom_radius = radius


def add_reflection_probe(
    location: tuple = (0, 0, 1),
    influence_distance: float = 2.5,
    probe_type: str = 'SPHERE',
    name: str = "ReflectionProbe"
) -> bpy.types.Object:
    """
    Add reflection/light probe.
    
    Args:
        location: Probe position
        influence_distance: Influence radius
        probe_type: 'SPHERE' or 'BOX'
        name: Object name
    
    Returns:
        The probe object
    """
    bpy.ops.object.lightprobe_add(
        type='SPHERE' if probe_type == 'SPHERE' else 'BOX',
        location=location
    )
    probe = bpy.context.active_object
    probe.name = name
    probe.data.influence_distance = influence_distance
    
    return probe


def add_irradiance_volume(
    location: tuple = (0, 0, 1),
    size: tuple = (5, 5, 3),
    resolution: tuple = (4, 4, 2),
    name: str = "IrradianceVolume"
) -> bpy.types.Object:
    """
    Add irradiance volume for indirect lighting.
    
    Args:
        location: Volume center
        size: XYZ size
        resolution: XYZ probe count
        name: Object name
    
    Returns:
        The volume object
    """
    bpy.ops.object.lightprobe_add(type='VOLUME', location=location)
    volume = bpy.context.active_object
    volume.name = name
    volume.scale = (size[0]/2, size[1]/2, size[2]/2)
    volume.data.grid_resolution_x = resolution[0]
    volume.data.grid_resolution_y = resolution[1]
    volume.data.grid_resolution_z = resolution[2]
    
    return volume


def bake_lighting() -> None:
    """Bake indirect lighting for Eevee."""
    bpy.ops.scene.light_cache_bake()


if __name__ == "__main__":
    setup_eevee_quality('HIGH')
    enable_eevee_reflections()
    enable_eevee_bloom()
    
    print("Configured Eevee for high quality rendering")
