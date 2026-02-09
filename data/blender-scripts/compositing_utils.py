"""
{
  "title": "Compositing Utilities",
  "category": "compositing",
  "tags": ["compositing", "nodes", "post", "effects", "color", "blur"],
  "description": "Functions for setting up compositing node setups.",
  "blender_version": "3.0+"
}
"""
import bpy


def enable_compositing() -> bpy.types.NodeTree:
    """Enable compositing and return node tree."""
    return bpy.context.scene.node_tree


def clear_compositing_nodes() -> None:
    """Clear all compositing nodes."""
    tree = enable_compositing()
    tree.nodes.clear()


def setup_basic_composite() -> dict:
    """Set up basic render layers to composite output."""
    tree = enable_compositing()
    tree.nodes.clear()
    
    render = tree.nodes.new('CompositorNodeRLayers')
    render.location = (0, 0)
    
    composite = tree.nodes.new('CompositorNodeComposite')
    composite.location = (400, 0)
    
    viewer = tree.nodes.new('CompositorNodeViewer')
    viewer.location = (400, -200)
    
    tree.links.new(render.outputs['Image'], composite.inputs['Image'])
    tree.links.new(render.outputs['Image'], viewer.inputs['Image'])
    
    return {'render': render, 'composite': composite, 'viewer': viewer}


def add_glare(
    input_socket,
    glare_type: str = 'FOG_GLOW',
    threshold: float = 1.0,
    size: int = 8
) -> bpy.types.Node:
    """Add glare/glow effect."""
    tree = enable_compositing()
    
    glare = tree.nodes.new('CompositorNodeGlare')
    glare.glare_type = glare_type  # 'GHOSTS', 'STREAKS', 'FOG_GLOW', 'SIMPLE_STAR'
    glare.threshold = threshold
    glare.size = size
    
    tree.links.new(input_socket, glare.inputs['Image'])
    
    return glare


def add_blur(
    input_socket,
    blur_type: str = 'FLAT',
    size_x: float = 5,
    size_y: float = 5
) -> bpy.types.Node:
    """Add blur effect."""
    tree = enable_compositing()
    
    blur = tree.nodes.new('CompositorNodeBlur')
    blur.filter_type = blur_type  # 'FLAT', 'TENT', 'QUAD', 'GAUSS'
    blur.size_x = size_x
    blur.size_y = size_y
    
    tree.links.new(input_socket, blur.inputs['Image'])
    
    return blur


def add_color_correction(
    input_socket,
    brightness: float = 0.0,
    contrast: float = 0.0,
    saturation: float = 1.0
) -> bpy.types.Node:
    """Add brightness/contrast adjustment."""
    tree = enable_compositing()
    
    bc = tree.nodes.new('CompositorNodeBrightContrast')
    bc.inputs['Bright'].default_value = brightness
    bc.inputs['Contrast'].default_value = contrast
    
    tree.links.new(input_socket, bc.inputs['Image'])
    
    return bc


def add_vignette(input_socket, strength: float = 0.5) -> bpy.types.Node:
    """Add vignette effect."""
    tree = enable_compositing()
    
    # Ellipse mask
    mask = tree.nodes.new('CompositorNodeEllipseMask')
    mask.width = 1.0
    mask.height = 1.0
    
    # Blur the mask
    blur = tree.nodes.new('CompositorNodeBlur')
    blur.size_x = 200
    blur.size_y = 200
    
    tree.links.new(mask.outputs['Mask'], blur.inputs['Image'])
    
    # Mix
    mix = tree.nodes.new('CompositorNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = strength
    
    tree.links.new(input_socket, mix.inputs[1])
    tree.links.new(blur.outputs['Image'], mix.inputs[2])
    
    return mix


def add_lens_distortion(
    input_socket,
    distortion: float = 0.0,
    dispersion: float = 0.0
) -> bpy.types.Node:
    """Add lens distortion effect."""
    tree = enable_compositing()
    
    lens = tree.nodes.new('CompositorNodeLensdist')
    lens.inputs['Distort'].default_value = distortion
    lens.inputs['Dispersion'].default_value = dispersion
    
    tree.links.new(input_socket, lens.inputs['Image'])
    
    return lens


def add_film_grain(input_socket, strength: float = 0.1) -> bpy.types.Node:
    """Add film grain effect."""
    tree = enable_compositing()
    
    # Noise texture
    tex = tree.nodes.new('CompositorNodeTexture')
    noise_tex = bpy.data.textures.new("GrainNoise", 'NOISE')
    tex.texture = noise_tex
    
    # Mix with image
    mix = tree.nodes.new('CompositorNodeMixRGB')
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = strength
    
    tree.links.new(input_socket, mix.inputs[1])
    tree.links.new(tex.outputs['Color'], mix.inputs[2])
    
    return mix


def setup_depth_of_field_composite(
    focus_distance: float = 5.0,
    fstop: float = 2.8
) -> dict:
    """Set up depth of field in compositing."""
    tree = enable_compositing()
    
    # Enable Z pass
    bpy.context.view_layer.use_pass_z = True
    
    nodes = setup_basic_composite()
    
    defocus = tree.nodes.new('CompositorNodeDefocus')
    defocus.use_zbuffer = True
    defocus.z_scale = 1.0
    defocus.f_stop = fstop
    
    tree.links.new(nodes['render'].outputs['Image'], defocus.inputs['Image'])
    tree.links.new(nodes['render'].outputs['Depth'], defocus.inputs['Z'])
    tree.links.new(defocus.outputs['Image'], nodes['composite'].inputs['Image'])
    
    nodes['defocus'] = defocus
    return nodes
