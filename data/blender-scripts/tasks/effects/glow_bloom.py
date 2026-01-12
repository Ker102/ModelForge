"""
{
  "title": "Glow and Bloom Effect",
  "category": "effects",
  "subcategory": "visual",
  "tags": ["glow", "bloom", "emission", "neon", "effects"],
  "difficulty": "intermediate",
  "description": "Creates glowing objects with bloom compositing setup.",
  "blender_version": "3.0+",
  "estimated_objects": 2
}
"""
import bpy


def create_glow_material(
    name: str = "GlowMat",
    color: tuple = (0, 0.8, 1),
    emission_strength: float = 10.0,
    base_color: tuple = None
) -> bpy.types.Material:
    """
    Create a glowing material.
    
    Args:
        name: Material name
        color: RGB glow color
        emission_strength: Emission intensity
        base_color: Optional base color (uses glow color if None)
    
    Returns:
        The glowing material
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*(base_color or color), 1.0)
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = emission_strength
    bsdf.inputs['Roughness'].default_value = 0.3
    
    return mat


def create_neon_tube(
    length: float = 1.0,
    radius: float = 0.02,
    color: tuple = (1, 0, 0.5),
    intensity: float = 20.0,
    location: tuple = (0, 0, 0),
    name: str = "NeonTube"
) -> bpy.types.Object:
    """
    Create a neon tube light.
    
    Args:
        length: Tube length
        radius: Tube radius
        color: RGB glow color
        intensity: Emission strength
        location: Position
        name: Object name
    
    Returns:
        The neon tube object
    """
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        location=location
    )
    tube = bpy.context.active_object
    tube.name = name
    
    mat = create_glow_material(f"{name}_Mat", color, intensity)
    tube.data.materials.append(mat)
    
    bpy.ops.object.shade_smooth()
    
    return tube


def setup_bloom_compositing(
    threshold: float = 0.8,
    intensity: float = 1.0,
    size: int = 8
) -> dict:
    """
    Set up bloom/glow compositing.
    
    Args:
        threshold: Brightness threshold for glow
        intensity: Glow intensity
        size: Glow size
    
    Returns:
        Dictionary with compositing nodes
    """
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    nodes = tree.nodes
    links = tree.links
    
    nodes.clear()
    
    # Render layers
    render = nodes.new('CompositorNodeRLayers')
    render.location = (0, 0)
    
    # Glare for bloom
    glare = nodes.new('CompositorNodeGlare')
    glare.location = (200, 0)
    glare.glare_type = 'FOG_GLOW'
    glare.threshold = threshold
    glare.size = size
    glare.mix = intensity * -0.9  # Negative = additive
    
    # Color correction
    color = nodes.new('CompositorNodeColorCorrection')
    color.location = (400, 0)
    
    # Output
    composite = nodes.new('CompositorNodeComposite')
    composite.location = (600, 0)
    
    viewer = nodes.new('CompositorNodeViewer')
    viewer.location = (600, -200)
    
    # Connect
    links.new(render.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], color.inputs['Image'])
    links.new(color.outputs['Image'], composite.inputs['Image'])
    links.new(color.outputs['Image'], viewer.inputs['Image'])
    
    return {
        'render': render,
        'glare': glare,
        'color': color,
        'composite': composite
    }


def create_energy_orb(
    radius: float = 0.3,
    color: tuple = (0.2, 0.6, 1),
    intensity: float = 30.0,
    location: tuple = (0, 0, 0),
    name: str = "EnergyOrb"
) -> dict:
    """
    Create a glowing energy orb with inner core.
    
    Args:
        radius: Orb radius
        color: RGB glow color
        intensity: Glow strength
        location: Position
        name: Object name
    
    Returns:
        Dictionary with orb parts
    """
    result = {}
    
    # Outer glow sphere
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=radius,
        subdivisions=3,
        location=location
    )
    outer = bpy.context.active_object
    outer.name = f"{name}_Outer"
    
    outer_mat = create_glow_material(f"{name}_OuterMat", color, intensity * 0.5)
    outer_mat.blend_method = 'BLEND'
    outer_mat.node_tree.nodes.get("Principled BSDF").inputs['Alpha'].default_value = 0.3
    outer.data.materials.append(outer_mat)
    
    bpy.ops.object.shade_smooth()
    result['outer'] = outer
    
    # Inner bright core
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=radius * 0.4,
        subdivisions=2,
        location=location
    )
    inner = bpy.context.active_object
    inner.name = f"{name}_Core"
    
    inner_mat = create_glow_material(f"{name}_CoreMat", (1, 1, 1), intensity)
    inner.data.materials.append(inner_mat)
    
    bpy.ops.object.shade_smooth()
    result['core'] = inner
    
    return result


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create neon tubes
    create_neon_tube(color=(1, 0, 0.5), location=(0, 0, 0))
    create_neon_tube(color=(0, 1, 0.5), location=(0.5, 0, 0))
    create_neon_tube(color=(0, 0.5, 1), location=(-0.5, 0, 0))
    
    # Create energy orb
    create_energy_orb(location=(0, 2, 0.5))
    
    # Set up bloom
    setup_bloom_compositing(threshold=0.5)
    
    # Use Cycles for emission
    bpy.context.scene.render.engine = 'CYCLES'
    
    print("Created glow effects with bloom compositing")
