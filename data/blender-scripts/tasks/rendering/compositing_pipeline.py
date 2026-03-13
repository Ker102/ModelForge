"""
{
  "title": "Compositing Pipeline",
  "category": "rendering",
  "subcategory": "compositing",
  "tags": ["compositing", "post-processing", "glare", "bloom", "lens", "color grading", "vignette", "depth of field", "nodes", "render passes"],
  "difficulty": "intermediate",
  "description": "Set up compositor node trees for post-processing effects: glare/bloom, lens distortion, color grading, vignettes, and fog glow. Blender 5.x compatible.",
  "blender_version": "5.0+",
  "estimated_objects": 0
}
"""
import bpy
import math


def enable_compositing(scene: bpy.types.Scene = None) -> bpy.types.NodeTree:
    """
    Enable compositing and return the compositor node tree.
    In Blender 5.0, use scene.compositing_node_group for the node tree.

    Args:
        scene: Target scene

    Returns:
        The compositing node tree

    Example:
        >>> tree = enable_compositing()
    """
    if scene is None:
        scene = bpy.context.scene

    scene.use_nodes = True

    # Blender 5.0+: compositing_node_group replaces node_tree
    tree = getattr(scene, 'compositing_node_group', None) or scene.node_tree
    return tree


def setup_glare_bloom(
    scene: bpy.types.Scene = None,
    glare_type: str = 'FOG_GLOW',
    quality: str = 'HIGH',
    threshold: float = 0.8,
    size: int = 6,
    mix: float = 0.0
) -> bpy.types.Node:
    """
    Add glare/bloom post-processing to the compositor.

    Args:
        scene: Target scene
        glare_type: 'FOG_GLOW' (soft bloom), 'STREAKS' (star pattern),
                   'GHOSTS' (lens ghosts), 'SIMPLE_STAR'
        quality: 'HIGH' or 'MEDIUM'
        threshold: Brightness threshold for bloom (0-10)
        size: Bloom spread size (1-9)
        mix: Mix factor (-1 to 1, 0=add, -1=only glare)

    Returns:
        The Glare node

    Example:
        >>> setup_glare_bloom(threshold=0.5, size=7)
    """
    tree = enable_compositing(scene)
    nodes = tree.nodes
    links = tree.links

    # Find existing render layer and composite output
    render_node = None
    composite_node = None
    for node in nodes:
        if node.type == 'R_LAYERS':
            render_node = node
        elif node.type == 'COMPOSITE':
            composite_node = node

    if not render_node or not composite_node:
        return None

    # Create Glare node
    glare = nodes.new('CompositorNodeGlare')
    glare.glare_type = glare_type
    glare.quality = quality
    glare.threshold = threshold
    glare.size = size
    glare.mix = mix
    glare.location = (render_node.location.x + 300, render_node.location.y)

    # Disconnect existing link and insert glare
    for link in list(links):
        if (link.from_node == render_node and
            link.from_socket.name == 'Image' and
            link.to_node == composite_node):
            links.remove(link)

    links.new(render_node.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], composite_node.inputs['Image'])

    # Move composite node to the right
    composite_node.location = (glare.location.x + 300, glare.location.y)

    return glare


def setup_lens_distortion(
    scene: bpy.types.Scene = None,
    distortion: float = -0.02,
    dispersion: float = 0.01,
    use_jitter: bool = True
) -> bpy.types.Node:
    """
    Add subtle lens distortion for photorealism.

    Args:
        scene: Target scene
        distortion: Barrel/pincushion (-1 to 1, negative=barrel)
        dispersion: Chromatic aberration amount
        use_jitter: Enable jitter for smoother results

    Returns:
        The Lens Distortion node

    Example:
        >>> setup_lens_distortion(distortion=-0.03, dispersion=0.02)
    """
    tree = enable_compositing(scene)
    nodes = tree.nodes
    links = tree.links

    composite_node = None
    prev_node = None
    for node in nodes:
        if node.type == 'COMPOSITE':
            composite_node = node
        elif node.type in ('GLARE', 'R_LAYERS'):
            prev_node = node

    if not composite_node or not prev_node:
        return None

    # Insert lens distortion before composite
    lens = nodes.new('CompositorNodeLensdist')
    lens.use_jitter = use_jitter
    lens.inputs['Distort'].default_value = distortion
    lens.inputs['Dispersion'].default_value = dispersion
    lens.location = (composite_node.location.x - 300, composite_node.location.y)

    # Reconnect
    for link in list(links):
        if link.to_node == composite_node and link.to_socket.name == 'Image':
            from_socket = link.from_socket
            links.remove(link)
            links.new(from_socket, lens.inputs['Image'])

    links.new(lens.outputs['Image'], composite_node.inputs['Image'])
    composite_node.location.x += 300

    return lens


def setup_color_grading(
    scene: bpy.types.Scene = None,
    lift: tuple = (1.0, 1.0, 1.0),
    gamma: tuple = (1.0, 1.0, 1.0),
    gain: tuple = (1.0, 1.0, 1.0),
    offset: float = 0.0
) -> bpy.types.Node:
    """
    Add color grading via Color Balance node (ASC-CDL mode).

    Args:
        scene: Target scene
        lift: Shadow tint (RGB multiplier, 1.0 = neutral)
        gamma: Midtone tint (RGB multiplier)
        gain: Highlight tint (RGB multiplier)
        offset: Overall brightness offset

    Returns:
        The Color Balance node

    Example:
        >>> setup_color_grading(lift=(0.95, 0.95, 1.05), gain=(1.1, 1.0, 0.9))
    """
    tree = enable_compositing(scene)
    nodes = tree.nodes
    links = tree.links

    composite_node = None
    for node in nodes:
        if node.type == 'COMPOSITE':
            composite_node = node

    if not composite_node:
        return None

    # Create Color Balance
    cb = nodes.new('CompositorNodeColorBalance')
    cb.correction_method = 'LIFT_GAMMA_GAIN'
    cb.lift = (*lift, 1.0) if len(lift) == 3 else lift
    cb.gamma = (*gamma, 1.0) if len(gamma) == 3 else gamma
    cb.gain = (*gain, 1.0) if len(gain) == 3 else gain
    cb.location = (composite_node.location.x - 300, composite_node.location.y)

    # Insert before composite
    for link in list(links):
        if link.to_node == composite_node and link.to_socket.name == 'Image':
            from_socket = link.from_socket
            links.remove(link)
            links.new(from_socket, cb.inputs['Image'])

    links.new(cb.outputs['Image'], composite_node.inputs['Image'])
    composite_node.location.x += 300

    return cb


def setup_vignette(
    scene: bpy.types.Scene = None,
    amount: float = 0.3
) -> list:
    """
    Add a vignette effect using Ellipse Mask + Blur + Mix.

    Args:
        scene: Target scene
        amount: Vignette darkness (0-1, higher=darker edges)

    Returns:
        List of created nodes

    Example:
        >>> setup_vignette(amount=0.4)
    """
    tree = enable_compositing(scene)
    nodes = tree.nodes
    links = tree.links

    composite_node = None
    for node in nodes:
        if node.type == 'COMPOSITE':
            composite_node = node

    if not composite_node:
        return []

    # Get the socket feeding into composite
    prev_socket = None
    for link in list(links):
        if link.to_node == composite_node and link.to_socket.name == 'Image':
            prev_socket = link.from_socket
            links.remove(link)

    if not prev_socket:
        return []

    x_base = composite_node.location.x - 600

    # Ellipse mask
    mask = nodes.new('CompositorNodeEllipseMask')
    mask.x = 0.5
    mask.y = 0.5
    mask.width = 0.75
    mask.height = 0.75
    mask.location = (x_base, composite_node.location.y - 200)

    # Blur the mask edges
    blur = nodes.new('CompositorNodeBlur')
    blur.size_x = 200
    blur.size_y = 200
    blur.use_relative = True
    blur.location = (x_base + 200, composite_node.location.y - 200)
    links.new(mask.outputs['Mask'], blur.inputs['Image'])

    # Mix: multiply image with blurred mask
    mix = nodes.new('CompositorNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = amount
    mix.location = (x_base + 400, composite_node.location.y)

    links.new(prev_socket, mix.inputs[1])  # Image
    links.new(blur.outputs['Image'], mix.inputs[2])  # Mask
    links.new(mix.outputs['Image'], composite_node.inputs['Image'])

    composite_node.location.x = x_base + 700

    return [mask, blur, mix]


def setup_cinematic_post_processing(
    scene: bpy.types.Scene = None,
    bloom: bool = True,
    lens_distortion: bool = True,
    color_grade: bool = True,
    vignette: bool = True,
    bloom_threshold: float = 0.7,
    vignette_amount: float = 0.3
) -> dict:
    """
    Apply a complete cinematic post-processing stack.

    Args:
        scene: Target scene
        bloom: Enable bloom/glare
        lens_distortion: Enable lens distortion
        color_grade: Enable color grading (warm tone)
        vignette: Enable vignette
        bloom_threshold: Bloom brightness threshold
        vignette_amount: Vignette darkness amount

    Returns:
        Dict of created nodes

    Example:
        >>> setup_cinematic_post_processing(bloom_threshold=0.5, vignette_amount=0.4)
    """
    result = {}

    if bloom:
        result['glare'] = setup_glare_bloom(
            scene, threshold=bloom_threshold, size=7
        )

    if lens_distortion:
        result['lens'] = setup_lens_distortion(
            scene, distortion=-0.02, dispersion=0.01
        )

    if color_grade:
        result['color_balance'] = setup_color_grading(
            scene,
            lift=(0.97, 0.97, 1.02),   # Slightly cool shadows
            gamma=(1.0, 1.0, 1.0),      # Neutral midtones
            gain=(1.05, 1.02, 0.95),     # Warm highlights
        )

    if vignette:
        result['vignette'] = setup_vignette(scene, amount=vignette_amount)

    return result


# Standalone execution
if __name__ == "__main__":
    result = setup_cinematic_post_processing()
    print(f"Applied cinematic post-processing: {list(result.keys())}")
