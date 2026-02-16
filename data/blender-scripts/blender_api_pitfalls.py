"""
Blender Python API — Common Pitfalls & Correct Solutions
========================================================
Category: utility
Blender: 4.0+ / 5.0
Source: NotebookLM (89-source Blender knowledge base)

This module documents the most common Python scripting pitfalls in Blender
with specific code patterns, error messages, and correct solutions.
"""

import bpy
import bmesh
import numpy as np
from mathutils import Vector


# =============================================================================
# PITFALL 1: The Context Trap — bpy.ops vs bpy.data
# =============================================================================
# Problem: bpy.ops operators rely on the active context (3D Viewport, selection).
#          They FAIL in headless/background mode or when wrong panel is active.
# Solution: Use the "Factory Pattern" via bpy.data for all creation operations.

def create_object_WRONG():
    """INCORRECT — relies on context, fails headlessly."""
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    return bpy.context.active_object  # Fragile!

def create_object_CORRECT(name="MyObject"):
    """CORRECT — Factory Pattern via bpy.data. Always works."""
    mesh = bpy.data.meshes.new(name=f"{name}_Mesh")
    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def create_light_CORRECT(name, light_type, energy, color=(1, 1, 1)):
    """CORRECT — Factory Pattern for lights. No context dependency."""
    light_data = bpy.data.lights.new(name=name, type=light_type)
    light_data.energy = energy
    light_data.color = color  # 3-tuple RGB, NOT 4-tuple RGBA!
    light_obj = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    return light_obj


# =============================================================================
# PITFALL 2: Mesh Validation — Missing validate() and calc_edges
# =============================================================================
# Problem: from_pydata with invalid indices (face references vertex #5 when
#          only 4 exist) can CRASH Blender. Missing calc_edges = invisible edges.
# Solution: ALWAYS call mesh.validate() and mesh.update(calc_edges=True).

def create_mesh_CORRECT(name, verts, edges, faces):
    """CORRECT — Always validate after from_pydata."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.validate(verbose=True)        # Auto-corrects invalid geometry
    mesh.update(calc_edges=True)       # Recalculates internal edge data
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


# =============================================================================
# PITFALL 3: Light Color — 3-tuple RGB, NOT 4-tuple RGBA
# =============================================================================
# Problem: bpy.types.Light strictly accepts 3-item RGB arrays.
#          Providing 4 values (RGBA) raises an error or is silently ignored.
# Solution: Always use (R, G, B) for light colors.

def set_light_color_WRONG(light_obj):
    """INCORRECT — 4 values for light color."""
    light_obj.data.color = (1.0, 0.0, 0.0, 1.0)  # FAILS!

def set_light_color_CORRECT(light_obj):
    """CORRECT — 3 values for light color."""
    light_obj.data.color = (1.0, 0.0, 0.0)  # Red, 3-tuple only


# =============================================================================
# PITFALL 4: Light Energy Units — Watts vs W/m²
# =============================================================================
# - Point, Spot, Area lights: energy in WATTS (e.g., 500W)
# - Sun lights: energy in WATTS PER SQUARE METER (e.g., 5 W/m²)
# - Real sunlight ≈ 441 W/m² — DO NOT set sun to 1000 (apocalyptic!)
# - Emission shaders on meshes: also in W/m²

def create_sun_CORRECT():
    """CORRECT — Sun uses W/m², not Watts. Typical value: 3-10 W/m²."""
    sun = create_light_CORRECT("Sun", 'SUN', energy=5.0)  # 5 W/m²
    return sun

def create_area_light_CORRECT():
    """CORRECT — Area light uses Watts. Typical value: 200-1000W."""
    area = create_light_CORRECT("AreaLight", 'AREA', energy=500)  # 500 Watts
    area.data.size = 2.0  # Larger = softer shadows
    return area


# =============================================================================
# PITFALL 5: ShaderNodeMix — Must Set data_type Explicitly
# =============================================================================
# Problem: ShaderNodeMixRGB was REMOVED in Blender 4.0.
#          ShaderNodeMix defaults to FLOAT, not color mixing.
# Solution: Set data_type = 'RGBA' explicitly after creation.

def create_mix_node_WRONG(nodes):
    """INCORRECT — defaults to FLOAT, won't mix colors."""
    mix = nodes.new('ShaderNodeMix')  # data_type defaults to 'FLOAT'!
    return mix

def create_mix_node_CORRECT(nodes):
    """CORRECT — explicitly set RGBA for color mixing."""
    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'       # CRITICAL: Must be set explicitly
    mix.blend_type = 'MIX'       # Or 'MULTIPLY', 'ADD', etc.
    # Inputs: mix.inputs[0] = Factor, mix.inputs[6] = A, mix.inputs[7] = B
    # Output: mix.outputs[2] = Result Color
    return mix


# =============================================================================
# PITFALL 6: Principled BSDF Socket Renaming (4.0+)
# =============================================================================
# Problem: Scripts using old socket names get KeyError.
# Solution: Use the new OpenPBR-compliant names.
#
# SOCKET NAME MAPPING:
# | OLD (3.x)           | NEW (4.0/5.0)            |
# |---------------------|--------------------------|
# | "Subsurface"        | "Subsurface Weight"      |
# | "Subsurface Color"  | REMOVED (use Base Color) |
# | "Specular"          | "Specular IOR Level"     |
# | "Transmission"      | "Transmission Weight"    |
# | "Clearcoat"         | "Coat Weight"            |
# | "Sheen"             | "Sheen Weight"           |
# | "Emission"          | "Emission Color"         |
# | "Base Color"        | "Base Color" (unchanged) |
# | "Metallic"          | "Metallic" (unchanged)   |
# | "Roughness"         | "Roughness" (unchanged)  |


# =============================================================================
# PITFALL 7: use_nodes Deprecation (5.0)
# =============================================================================
# Problem: material.use_nodes = True is deprecated. Always returns True.
#          Harmless now but will be REMOVED in Blender 6.0.
# Solution: Remove use_nodes from scripts, proceed directly to node_tree.

def create_material_CORRECT(name):
    """CORRECT — Skip use_nodes, go straight to node_tree."""
    mat = bpy.data.materials.new(name=name)
    # mat.use_nodes = True  # DEPRECATED in 5.0, always True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    return mat, nodes, links


# =============================================================================
# PITFALL 8: BMesh — ensure_lookup_table() Required
# =============================================================================
# Problem: After creating/deleting geometry in BMesh, internal index table
#          becomes outdated. Accessing by index causes IndexError.
# Solution: Call ensure_lookup_table() after geometry changes.

def bmesh_example_CORRECT(mesh):
    """CORRECT — ensure lookup tables after changes, free when done."""
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Create geometry...
    bmesh.ops.create_cube(bm, size=1.0)

    # CRITICAL: Update lookup tables after geometry changes
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Now safe to access by index
    first_vert = bm.verts[0]

    # Write back and ALWAYS free
    bm.to_mesh(mesh)
    bm.free()  # CRITICAL: Prevent memory leaks


# =============================================================================
# PITFALL 9: NumPy foreach_set — Must Flatten Arrays
# =============================================================================
# Problem: foreach_set expects a flat 1D array. Passing Nx3 array fails.
# Solution: Always .flatten() before passing to Blender.

def set_vertices_numpy_CORRECT(mesh, positions_nx3):
    """CORRECT — Flatten Nx3 array before foreach_set."""
    flat = positions_nx3.flatten()  # CRITICAL: Must be 1D
    mesh.vertices.foreach_set("co", flat)
    mesh.update()


# =============================================================================
# PITFALL 10: Boolean Solver — "FAST" Renamed to "FLOAT" in 5.0
# =============================================================================
# Problem: FAST solver doesn't exist in 5.0. Only EXACT, FLOAT, MANIFOLD.
# Solution: Use FLOAT for speed, EXACT for precision.

def add_boolean_modifier_CORRECT(obj, cutter, operation='DIFFERENCE'):
    """CORRECT — Use FLOAT solver (not FAST) in Blender 5.0."""
    mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = operation
    mod.object = cutter
    mod.solver = 'FLOAT'  # Was 'FAST' pre-5.0, now 'FLOAT'
    return mod


# =============================================================================
# PITFALL 11: Grease Pencil → Annotation (5.0)
# =============================================================================
# Problem: GreasePencil types renamed to Annotation in 5.0.
# Solution: Use new names:
#   bpy.types.GreasePencil → bpy.types.Annotation
#   bpy.data.grease_pencils → bpy.types.annotations
#   GPencilStroke → AnnotationStroke
#   GPencilLayer → AnnotationLayer


# =============================================================================
# PITFALL 12: EEVEE Engine Rename (5.0)
# =============================================================================
# Problem: BLENDER_EEVEE_NEXT renamed to BLENDER_EEVEE in 5.0.
# Solution: Use 'BLENDER_EEVEE' for the render engine enum.

def set_eevee_CORRECT():
    """CORRECT — EEVEE engine name for Blender 5.0."""
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'


# =============================================================================
# PITFALL 13: Dictionary Property Access Removed (5.0)
# =============================================================================
# Problem: scene['cycles'] no longer works. Properties defined via bpy.props
#          are no longer accessible via dictionary syntax.
# Solution: Use attribute access directly.

def access_cycles_WRONG():
    """INCORRECT — dict access removed in 5.0."""
    val = bpy.context.scene['cycles']  # TypeError in 5.0!

def access_cycles_CORRECT():
    """CORRECT — Use attribute access."""
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128


# =============================================================================
# PITFALL 14: Mathutils Float Precision (5.0)
# =============================================================================
# Problem: mathutils.Vector now uses float32 (was float64).
#          Scientific scripts relying on double precision may see drift.
# Solution: Be aware; cast to float64 if precision matters.

def precision_aware_calculation():
    """Note: Blender 5.0 mathutils uses float32 by default."""
    v = Vector((0.1, 0.2, 0.3))  # float32 in 5.0
    # For high-precision: convert to numpy float64
    precise = np.array(v, dtype=np.float64)
    return precise


# =============================================================================
# PITFALL 15: Context Overrides — Use temp_override (3.2+)
# =============================================================================
# Problem: Old dict-based context overrides are deprecated.
# Solution: Use bpy.context.temp_override() for Blender 3.2+.

def apply_modifier_CORRECT(obj, modifier_name):
    """CORRECT — Use temp_override for operator context."""
    with bpy.context.temp_override(object=obj):
        bpy.ops.object.modifier_apply(modifier=modifier_name)
