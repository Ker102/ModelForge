"""
{
  "title": "Material and Color Management",
  "category": "material",
  "tags": ["material", "color", "bsdf", "shading"],
  "description": "Creating materials, setting base colors, and assigning them to objects using the Principled BSDF shader."
}
"""
import bpy

def create_material(name="NewMaterial", color=(1.0, 1.0, 1.0, 1.0), metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
    
    return mat

def assign_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Example: Create a blue metallic material
# blue_mat = create_material("MetallicBlue", (0.0, 0.0, 1.0, 1.0), metallic=1.0)
# assign_material(bpy.context.active_object, blue_mat)

def create_glass_material(name="Glass", color=(1.0, 1.0, 1.0, 1.0), roughness=0.0, ior=1.45):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Add Glass BSDF
    glass = nodes.new(type="ShaderNodeBsdfGlass")
    glass.inputs['Color'].default_value = color
    glass.inputs['Roughness'].default_value = roughness
    glass.inputs['IOR'].default_value = ior
    
    # Add Output
    output = nodes.new(type="ShaderNodeOutputMaterial")
    
    # Link
    mat.node_tree.links.new(glass.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_emission_material(name="Emission", color=(1.0, 1.0, 1.0, 1.0), strength=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Add Emission
    emission = nodes.new(type="ShaderNodeEmission")
    emission.inputs['Color'].default_value = color
    emission.inputs['Strength'].default_value = strength
    
    # Add Output
    output = nodes.new(type="ShaderNodeOutputMaterial")
    
    # Link
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    return mat
