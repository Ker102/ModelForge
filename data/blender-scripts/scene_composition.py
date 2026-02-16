"""
{
  "title": "Scene Composition and Professional Layout",
  "category": "scene",
  "tags": ["composition", "layout", "scale", "proportion", "grounding", "arrangement", "floor", "backdrop", "pedestal", "skybox"],
  "description": "Professional scene composition techniques for Blender. Covers real-world scale references, object grounding (floor planes), backdrop creation, pedestal/display stands, object arrangement patterns (circular, grid, shelf), and skybox setup. Essential for creating polished, realistic scenes that look professional.",
  "blender_version": "4.0+"
}
"""
import bpy
import math


# =============================================================================
# PROFESSIONAL SCENE COMPOSITION
# =============================================================================
#
# KEY PRINCIPLES FOR PROFESSIONAL SCENES:
#
# 1. GROUNDING: Objects MUST sit on a surface (floor, pedestal, ground plane).
#    Floating objects look amateurish. Always add a floor or ground plane.
#
# 2. SCALE: Use real-world dimensions. Blender units = meters by default.
#    - Human height:   1.75m
#    - Table height:   0.75m
#    - Chair height:   0.45m (seat)
#    - Door height:    2.0m
#    - Room height:    2.5m
#    - Car length:     4.5m
#
# 3. COMPOSITION: Don't center everything. Use asymmetry and negative space.
#    - Place the main subject slightly off-center
#    - Group objects in odd numbers (1, 3, 5)
#    - Create depth with foreground, midground, background elements
#
# 4. CONTEXT: Add environmental details (floor, walls, lighting, props)
#    to make scenes feel lived-in and realistic.
#
# 5. SPACING: Leave breathing room between objects. Crowded scenes feel chaotic.
# =============================================================================


# --- REAL-WORLD SCALE REFERENCE ---
SCALE_REFERENCE = {
    # Architecture
    'door_width':    0.9,    # meters
    'door_height':   2.1,
    'room_height':   2.5,
    'wall_thickness': 0.15,
    'window_sill':   0.9,    # height from floor
    'stair_rise':    0.18,   # per step
    'stair_run':     0.28,   # per step depth
    
    # Furniture
    'table_height':  0.75,
    'desk_height':   0.73,
    'desk_width':    1.4,
    'desk_depth':    0.7,
    'chair_seat':    0.45,
    'chair_back':    0.9,
    'sofa_height':   0.4,
    'sofa_depth':    0.9,
    'bed_height':    0.5,
    'bookshelf_h':   1.8,
    
    # Human
    'human_height':  1.75,
    'eye_level':     1.6,
    'shoulder_w':    0.45,
    
    # Objects
    'mug_height':    0.1,
    'monitor_h':     0.35,
    'keyboard_w':    0.44,
    'lamp_height':   0.5,
    'book_thickness': 0.03,
    
    # Vehicles
    'car_length':    4.5,
    'car_width':     1.8,
    'car_height':    1.45,
    'wheel_radius':  0.35,
}


def create_floor_plane(
    size=20.0,
    location=(0, 0, 0),
    color=(0.3, 0.3, 0.32),
    roughness=0.8,
    name="Floor"
):
    """
    Create a ground plane for objects to sit on.
    
    ALWAYS add a floor plane unless the scene explicitly doesn't need one
    (e.g., space scenes). Objects floating in void look unprofessional.
    
    Args:
        size: Plane size in meters 
        location: Floor position (default at origin)
        color: Floor color (dark gray default)
        roughness: Surface roughness (0.8 = matte, 0.1 = glossy)
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    floor = bpy.context.active_object
    floor.name = name
    
    # Apply material
    mat = bpy.data.materials.new(name=f"{name}_Material")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    floor.data.materials.append(mat)
    
    return floor


def create_backdrop(
    width=15.0,
    height=8.0,
    curve_radius=3.0,
    color=(0.85, 0.85, 0.87),
    name="Backdrop"
):
    """
    Create a seamless backdrop (cyclorama) for studio-style renders.
    
    Creates a curved floor-to-wall transition that eliminates the
    visible seam between floor and background. Professional product
    photography standard.
    
    Args:
        width: Backdrop width
        height: Wall height
        curve_radius: Radius of the floor-to-wall curve
        color: Backdrop color (light gray default for studio)
    """
    # Create with a bezier curve profile + extrude
    verts = []
    segments = 12
    
    # Floor section
    verts.append((-width/2, -5, 0))
    verts.append((-width/2, 0, 0))
    
    # Curved transition
    for i in range(segments + 1):
        angle = (math.pi / 2) * (i / segments)
        y = -curve_radius * math.cos(angle)
        z = curve_radius * math.sin(angle)
        verts.append((-width/2, y, z))
    
    # Wall section
    verts.append((-width/2, -curve_radius, curve_radius + height))
    
    # Create mesh
    mesh = bpy.data.meshes.new(name)
    
    # Use simple plane approach for reliability
    bpy.ops.mesh.primitive_plane_add(size=width, location=(0, -2, 0))
    backdrop = bpy.context.active_object
    backdrop.name = name
    backdrop.scale = (1, 1.5, 1)
    
    # Apply material
    mat = bpy.data.materials.new(name=f"{name}_Material")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    backdrop.data.materials.append(mat)
    
    return backdrop


def create_pedestal(
    location=(0, 0, 0),
    radius=0.5,
    height=0.8,
    color=(0.15, 0.15, 0.17),
    name="Pedestal"
):
    """
    Create a display pedestal/plinth for showcasing objects.
    
    Professional product and museum display standard.
    Objects should be placed on TOP of the pedestal (at Z = height).
    
    Args:
        location: Base position
        radius: Pedestal radius
        height: Pedestal height
        color: Surface color (dark for contrast)
    """
    x, y, z = location
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, 
        depth=height, 
        location=(x, y, z + height/2)
    )
    pedestal = bpy.context.active_object
    pedestal.name = name
    bpy.ops.object.shade_smooth()
    
    mat = bpy.data.materials.new(name=f"{name}_Material")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.3
    bsdf.inputs['Metallic'].default_value = 0.1
    pedestal.data.materials.append(mat)
    
    return pedestal


def arrange_circular(
    objects_data,
    center=(0, 0, 0),
    radius=5.0,
    start_angle=0
):
    """
    Arrange objects in a circular pattern around a center point.
    
    Args:
        objects_data: List of (name, create_func) tuples
        center: Center of the circle
        radius: Circle radius
        start_angle: Starting angle in degrees
    
    Example:
        # Arrange 6 columns around a center point
        for i in range(6):
            angle = math.radians(i * 60)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            bpy.ops.mesh.primitive_cylinder_add(location=(x, y, 0))
    """
    cx, cy, cz = center
    n = len(objects_data)
    positions = []
    
    for i in range(n):
        angle = math.radians(start_angle + (360 / n) * i)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions.append((x, y, cz))
    
    return positions


def arrange_grid(
    rows=3,
    cols=3,
    spacing=2.0,
    center=(0, 0, 0),
    z_offset=0
):
    """
    Calculate grid positions for arranging objects.
    
    Args:
        rows: Number of rows
        cols: Number of columns
        spacing: Distance between objects
        center: Grid center point
        z_offset: Height offset for all positions
    
    Returns:
        List of (x, y, z) positions
    """
    cx, cy, cz = center
    positions = []
    
    for row in range(rows):
        for col in range(cols):
            x = cx + (col - (cols - 1) / 2) * spacing
            y = cy + (row - (rows - 1) / 2) * spacing
            positions.append((x, y, cz + z_offset))
    
    return positions


# =============================================================================
# COMPLETE SCENE SETUP EXAMPLES
# =============================================================================

# --- Example: Product showcase (object on pedestal + studio setup) ---
#
# import bpy
#
# # Floor
# create_floor_plane(size=20, color=(0.1, 0.1, 0.12))
#
# # Pedestal
# pedestal = create_pedestal(location=(0, 0, 0), radius=0.4, height=0.6)
#
# # Place product on top of pedestal
# bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0.6 + 0.3))
# product = bpy.context.active_object
# product.name = "Product"
# bpy.ops.object.shade_smooth()
#
# # Add gold material
# mat = bpy.data.materials.new("Gold")
# bsdf = mat.node_tree.nodes.get("Principled BSDF")
# bsdf.inputs['Base Color'].default_value = (1.0, 0.84, 0.0, 1.0)
# bsdf.inputs['Metallic'].default_value = 1.0
# bsdf.inputs['Roughness'].default_value = 0.2
# product.data.materials.append(mat)

# --- Example: Room interior with furniture ---
#
# # Floor
# create_floor_plane(size=8, color=(0.55, 0.38, 0.18), roughness=0.55, name="WoodFloor")
#
# # Objects at real-world scale
# # Table at 0.75m height
# bpy.ops.mesh.primitive_cube_add(scale=(0.6, 0.4, 0.375), location=(0, 0, 0.375))
# # Chair at 0.45m seat height  
# bpy.ops.mesh.primitive_cube_add(scale=(0.2, 0.2, 0.225), location=(0.8, 0, 0.225))
