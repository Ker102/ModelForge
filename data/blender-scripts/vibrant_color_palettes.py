"""
{
  "title": "Vibrant Color Palettes for Blender Materials",
  "category": "materials",
  "tags": ["color", "palette", "vibrant", "RGB", "material", "reference", "nature", "space", "metal"],
  "description": "Ready-to-use vibrant RGB color tuples for Blender materials. Organized by category with recommended roughness and metallic values. Use these instead of picking muted, desaturated colors.",
  "blender_version": "3.0+"
}
"""
import bpy

# =============================================================================
# VIBRANT COLOR PALETTE REFERENCE
# =============================================================================
# Use these tuples directly as Base Color (R, G, B, A) values.
# IMPORTANT: Always prefer saturated, vivid colors over muted/gray tones.
# These are LINEAR color space values — Blender expects linear, not sRGB.
# =============================================================================


# --- NATURE COLORS ---
# For outdoor scenes, landscapes, vegetation, water

GRASS_GREEN = (0.08, 0.52, 0.12, 1.0)          # Lush grass, roughness=0.85
DARK_GRASS = (0.05, 0.35, 0.08, 1.0)           # Deep forest grass, roughness=0.9
FOREST_GREEN = (0.02, 0.28, 0.05, 1.0)         # Pine trees, roughness=0.8
LEAF_GREEN = (0.15, 0.65, 0.1, 1.0)            # Fresh spring leaves, roughness=0.7
OCEAN_BLUE = (0.0, 0.15, 0.65, 1.0)            # Deep ocean, roughness=0.05, transmission=0.8
SKY_BLUE = (0.3, 0.55, 0.9, 1.0)               # Clear sky, roughness=0.5
WATER_BLUE = (0.05, 0.3, 0.7, 1.0)             # Rivers/lakes, roughness=0.05
SUNSET_ORANGE = (0.95, 0.45, 0.05, 1.0)        # Warm sunset, roughness=0.5
SUNRISE_PINK = (0.9, 0.35, 0.4, 1.0)           # Dawn sky, roughness=0.5
EARTH_BROWN = (0.35, 0.2, 0.08, 1.0)           # Soil/dirt, roughness=0.9
SAND_BEIGE = (0.75, 0.62, 0.38, 1.0)           # Desert sand, roughness=0.85
CLAY_RED = (0.6, 0.22, 0.1, 1.0)               # Red clay, roughness=0.9
SNOW_WHITE = (0.95, 0.95, 0.97, 1.0)           # Fresh snow, roughness=0.6


# --- SPACE COLORS ---
# For celestial objects, planets, sci-fi scenes

SUN_YELLOW = (1.0, 0.85, 0.2, 1.0)             # Star/sun emission, emission_strength=5
SUN_ORANGE = (1.0, 0.6, 0.1, 1.0)              # Warm star, emission_strength=5
EARTH_BLUE_GREEN = (0.1, 0.45, 0.65, 1.0)      # Earth from space, roughness=0.6
MARS_RUST = (0.7, 0.2, 0.05, 1.0)              # Mars surface, roughness=0.85
MOON_GRAY = (0.45, 0.45, 0.42, 1.0)            # Lunar surface, roughness=0.9
JUPITER_TAN = (0.7, 0.55, 0.35, 1.0)           # Gas giant, roughness=0.6
SATURN_GOLD = (0.75, 0.65, 0.4, 1.0)           # Saturn surface, roughness=0.6
NEBULA_PURPLE = (0.5, 0.1, 0.7, 1.0)           # Space nebula, emission_strength=3
NEBULA_BLUE = (0.15, 0.25, 0.8, 1.0)           # Blue nebula, emission_strength=2
ASTEROID_DARK = (0.12, 0.1, 0.08, 1.0)         # Dark rock, roughness=0.95
DEEP_SPACE_BG = (0.002, 0.002, 0.01, 1.0)      # World background for space


# --- METAL COLORS (always use metallic=1.0) ---

GOLD = (1.0, 0.84, 0.0, 1.0)                   # Pure gold, metallic=1.0, roughness=0.2
COPPER = (0.88, 0.47, 0.3, 1.0)                # Polished copper, metallic=1.0, roughness=0.25
BRONZE = (0.72, 0.47, 0.15, 1.0)               # Ancient bronze, metallic=1.0, roughness=0.35
CHROME = (0.85, 0.85, 0.88, 1.0)               # Mirror chrome, metallic=1.0, roughness=0.05
IRON = (0.42, 0.42, 0.42, 1.0)                 # Raw iron, metallic=1.0, roughness=0.5
BRUSHED_STEEL = (0.65, 0.65, 0.7, 1.0)         # Brushed finish, metallic=1.0, roughness=0.4
DARK_METAL = (0.18, 0.18, 0.2, 1.0)            # Dark anodized, metallic=1.0, roughness=0.3
ROSE_GOLD = (0.9, 0.6, 0.5, 1.0)               # Rose gold, metallic=1.0, roughness=0.2


# --- ARCHITECTURAL / BUILDING COLORS ---

STONE_GRAY = (0.45, 0.43, 0.4, 1.0)            # Castle stone, roughness=0.85
DARK_STONE = (0.3, 0.28, 0.25, 1.0)            # Dungeon stone, roughness=0.9
BRICK_RED = (0.6, 0.18, 0.1, 1.0)              # Red brick, roughness=0.85
TERRACOTTA = (0.75, 0.38, 0.18, 1.0)           # Roof tiles, roughness=0.8
SLATE_BLUE = (0.3, 0.35, 0.42, 1.0)            # Roofing slate, roughness=0.7
MARBLE_WHITE = (0.9, 0.88, 0.85, 1.0)          # Polished marble, roughness=0.15
DARK_WOOD = (0.25, 0.13, 0.05, 1.0)            # Dark timber, roughness=0.6
LIGHT_OAK = (0.55, 0.38, 0.18, 1.0)            # Light oak, roughness=0.55
MAHOGANY = (0.35, 0.1, 0.05, 1.0)              # Rich mahogany, roughness=0.5


# --- VIVID / ACCENT COLORS ---

PURE_RED = (0.8, 0.05, 0.02, 1.0)              # Bright red, roughness=0.4
PURE_BLUE = (0.05, 0.1, 0.85, 1.0)             # Bright blue, roughness=0.4
PURE_GREEN = (0.05, 0.7, 0.1, 1.0)             # Bright green, roughness=0.4
BRIGHT_YELLOW = (0.95, 0.85, 0.05, 1.0)        # Vivid yellow, roughness=0.3
BRIGHT_ORANGE = (0.95, 0.45, 0.02, 1.0)        # Vivid orange, roughness=0.4
PURPLE = (0.45, 0.05, 0.7, 1.0)                # Rich purple, roughness=0.4
CYAN = (0.0, 0.75, 0.8, 1.0)                   # Electric cyan, roughness=0.3
MAGENTA = (0.8, 0.05, 0.5, 1.0)                # Hot magenta, roughness=0.3
CORAL = (0.9, 0.35, 0.3, 1.0)                  # Warm coral, roughness=0.4
TEAL = (0.0, 0.55, 0.55, 1.0)                  # Deep teal, roughness=0.4


# --- EMISSIVE COLORS (use with emission_strength 3–8) ---
# IMPORTANT: For emissive materials, set BOTH Base Color AND Emission Color
# to the same value. This keeps the color visible even in Material Preview.

NEON_RED = (1.0, 0.1, 0.05, 1.0)               # emission_strength=5
NEON_BLUE = (0.1, 0.3, 1.0, 1.0)               # emission_strength=5
NEON_GREEN = (0.1, 1.0, 0.2, 1.0)              # emission_strength=5
NEON_PINK = (1.0, 0.1, 0.5, 1.0)               # emission_strength=5
LAVA_ORANGE = (1.0, 0.35, 0.0, 1.0)            # emission_strength=6
FIRE_YELLOW = (1.0, 0.7, 0.1, 1.0)             # emission_strength=5
ICE_BLUE = (0.5, 0.8, 1.0, 1.0)                # emission_strength=3


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_vibrant_material(
    name: str,
    color: tuple,
    roughness: float = 0.5,
    metallic: float = 0.0,
    emission_strength: float = 0.0
) -> bpy.types.Material:
    """
    Create a material with vibrant, saturated colors.
    
    For emissive materials, this sets BOTH Base Color and Emission Color
    to the same value, preventing the white-washing effect in Material Preview.
    
    Args:
        name: Material name
        color: RGBA tuple like (R, G, B, 1.0) — use the palette constants above
        roughness: Surface roughness (0.0 = mirror, 1.0 = matte)
        metallic: Metallic value (0.0 = dielectric, 1.0 = metal)
        emission_strength: Glow intensity (0 = none, 3–8 recommended for visibility)
    
    Example:
        # Glowing sun
        sun_mat = create_vibrant_material("Sun", SUN_YELLOW, emission_strength=5)
        
        # Metallic gold
        gold_mat = create_vibrant_material("Gold", GOLD, roughness=0.2, metallic=1.0)
        
        # Matte grass
        grass_mat = create_vibrant_material("Grass", GRASS_GREEN, roughness=0.85)
    """
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    if bsdf:
        # Always set a vibrant base color
        bsdf.inputs['Base Color'].default_value = color if len(color) == 4 else (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        
        # For emissive materials: set BOTH base color AND emission color
        # This prevents the object from looking white in Material Preview
        if emission_strength > 0:
            bsdf.inputs['Emission Color'].default_value = color if len(color) == 4 else (*color, 1.0)
            bsdf.inputs['Emission Strength'].default_value = emission_strength
    
    return mat


def apply_vibrant_material(obj, name: str, color: tuple, **kwargs):
    """Create and assign a vibrant material to an object in one call."""
    mat = create_vibrant_material(name, color, **kwargs)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return mat


# =============================================================================
# USAGE EXAMPLES — Copy these patterns for vibrant materials
# =============================================================================

# --- Example: Vivid planet Earth ---
# earth_mat = create_vibrant_material("Earth", EARTH_BLUE_GREEN, roughness=0.6)
# bpy.context.active_object.data.materials.append(earth_mat)

# --- Example: Glowing yellow sun (NOT white) ---
# sun_mat = create_vibrant_material("Sun", SUN_YELLOW, emission_strength=5)
# Note: emission_strength=5   keeps the yellow visible
#       emission_strength=15  would wash it out to white in viewport

# --- Example: Polished gold ring ---
# gold_mat = create_vibrant_material("Gold", GOLD, roughness=0.2, metallic=1.0)

# --- Example: Rusty Mars surface ---
# mars_mat = create_vibrant_material("Mars", MARS_RUST, roughness=0.85)
