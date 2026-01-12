"""
{
  "title": "Mask Utilities",
  "category": "compositing",
  "tags": ["mask", "matte", "alpha", "selection", "compositing"],
  "description": "Functions for creating and managing masks for compositing.",
  "blender_version": "3.0+"
}
"""
import bpy


def create_object_mask(
    obj: bpy.types.Object,
    pass_index: int = 1
) -> None:
    """
    Set up object for mask pass rendering.
    
    Args:
        obj: Object to mask
        pass_index: Unique pass index for the object
    """
    obj.pass_index = pass_index
    bpy.context.view_layer.use_pass_object_index = True


def create_material_mask(
    material: bpy.types.Material,
    pass_index: int = 1
) -> None:
    """
    Set up material for mask pass rendering.
    
    Args:
        material: Material to mask
        pass_index: Unique pass index
    """
    material.pass_index = pass_index
    bpy.context.view_layer.use_pass_material_index = True


def setup_id_mask_compositing(pass_index: int = 1) -> dict:
    """
    Set up ID mask in compositor.
    
    Args:
        pass_index: Object/material pass index to mask
    
    Returns:
        Dictionary with compositor nodes
    """
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    nodes = tree.nodes
    links = tree.links
    
    # Render layers
    render = None
    for node in nodes:
        if node.type == 'R_LAYERS':
            render = node
            break
    
    if not render:
        render = nodes.new('CompositorNodeRLayers')
        render.location = (0, 0)
    
    # ID Mask node
    id_mask = nodes.new('CompositorNodeIDMask')
    id_mask.location = (200, -100)
    id_mask.index = pass_index
    id_mask.use_antialiasing = True
    
    links.new(render.outputs['IndexOB'], id_mask.inputs['ID value'])
    
    return {
        'render': render,
        'id_mask': id_mask
    }


def create_holdout_material(name: str = "HoldoutMat") -> bpy.types.Material:
    """Create holdout material for masking."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    holdout = nodes.new('ShaderNodeHoldout')
    holdout.location = (0, 0)
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    links.new(holdout.outputs['Holdout'], output.inputs['Surface'])
    
    return mat


def add_cryptomatte_setup() -> dict:
    """
    Enable and configure Cryptomatte passes.
    
    Returns:
        Dictionary with settings applied
    """
    view_layer = bpy.context.view_layer
    view_layer.use_pass_cryptomatte_object = True
    view_layer.use_pass_cryptomatte_material = True
    view_layer.use_pass_cryptomatte_asset = True
    
    # Add cryptomatte node in compositor
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    nodes = tree.nodes
    
    crypto = nodes.new('CompositorNodeCryptomatteV2')
    crypto.location = (200, -200)
    
    return {
        'object_pass': True,
        'material_pass': True,
        'asset_pass': True,
        'cryptomatte_node': crypto
    }


def enable_render_passes() -> None:
    """Enable common render passes for compositing."""
    view_layer = bpy.context.view_layer
    
    # Standard passes
    view_layer.use_pass_combined = True
    view_layer.use_pass_z = True
    view_layer.use_pass_mist = True
    view_layer.use_pass_normal = True
    
    # Light passes
    view_layer.use_pass_diffuse_color = True
    view_layer.use_pass_glossy_color = True
    view_layer.use_pass_emit = True
    
    # Index passes
    view_layer.use_pass_object_index = True
    view_layer.use_pass_material_index = True


def setup_mist_pass(
    start: float = 5.0,
    depth: float = 25.0,
    falloff: str = 'QUADRATIC'
) -> None:
    """
    Configure mist pass for depth effects.
    
    Args:
        start: Mist start distance
        depth: Mist depth
        falloff: 'LINEAR', 'QUADRATIC', 'INVERSE_QUADRATIC'
    """
    bpy.context.view_layer.use_pass_mist = True
    
    world = bpy.context.scene.world
    if world:
        world.mist_settings.start = start
        world.mist_settings.depth = depth
        world.mist_settings.falloff = falloff
