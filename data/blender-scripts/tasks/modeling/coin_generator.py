"""
{
  "title": "Coin Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["coin", "money", "gold", "props", "game"],
  "difficulty": "beginner",
  "description": "Generates coins and coin stacks for game assets.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import math
import random


def create_coin(
    radius: float = 0.02,
    thickness: float = 0.003,
    material: str = 'GOLD',
    location: tuple = (0, 0, 0),
    name: str = "Coin"
) -> bpy.types.Object:
    """
    Create a coin.
    
    Args:
        radius: Coin radius
        thickness: Coin thickness
        material: 'GOLD', 'SILVER', 'BRONZE', 'COPPER'
        location: Position
        name: Object name
    
    Returns:
        The coin object
    """
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=thickness,
        location=(location[0], location[1], location[2] + thickness/2)
    )
    coin = bpy.context.active_object
    coin.name = name
    
    # Add edge bevel for realism
    bpy.ops.object.modifier_add(type='BEVEL')
    coin.modifiers["Bevel"].width = radius * 0.05
    coin.modifiers["Bevel"].segments = 2
    
    bpy.ops.object.shade_smooth()
    
    # Material colors
    colors = {
        'GOLD': (1.0, 0.84, 0.0),
        'SILVER': (0.8, 0.8, 0.85),
        'BRONZE': (0.8, 0.5, 0.2),
        'COPPER': (0.95, 0.64, 0.54)
    }
    
    mat = bpy.data.materials.new(f"{name}_Mat")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    color = colors.get(material, colors['GOLD'])
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.25
    coin.data.materials.append(mat)
    
    return coin


def create_coin_stack(
    count: int = 8,
    radius: float = 0.02,
    material: str = 'GOLD',
    messy: bool = True,
    location: tuple = (0, 0, 0),
    seed: int = 42,
    name: str = "CoinStack"
) -> list:
    """
    Create a stack of coins.
    
    Args:
        count: Number of coins
        radius: Coin radius
        material: Metal type
        messy: Add randomness to positions
        location: Stack position
        seed: Random seed
        name: Stack name
    
    Returns:
        List of coin objects
    """
    random.seed(seed)
    coins = []
    thickness = 0.003
    
    for i in range(count):
        offset_x = 0
        offset_y = 0
        rotation = 0
        
        if messy:
            offset_x = random.uniform(-radius * 0.2, radius * 0.2)
            offset_y = random.uniform(-radius * 0.2, radius * 0.2)
            rotation = random.uniform(-0.1, 0.1)
        
        pos = (
            location[0] + offset_x,
            location[1] + offset_y,
            location[2] + i * thickness
        )
        
        coin = create_coin(
            radius=radius,
            thickness=thickness,
            material=material,
            location=pos,
            name=f"{name}_{i+1}"
        )
        coin.rotation_euler.z = rotation
        coins.append(coin)
    
    return coins


def create_coin_pile(
    count: int = 20,
    spread: float = 0.1,
    material: str = 'GOLD',
    location: tuple = (0, 0, 0),
    seed: int = 123,
    name: str = "CoinPile"
) -> list:
    """Create a scattered pile of coins."""
    random.seed(seed)
    coins = []
    thickness = 0.003
    radius = 0.02
    
    for i in range(count):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, spread)
        
        pos = (
            location[0] + math.cos(angle) * dist,
            location[1] + math.sin(angle) * dist,
            location[2] + random.uniform(0, thickness * 5)
        )
        
        coin = create_coin(
            radius=radius * random.uniform(0.8, 1.0),
            material=material,
            location=pos,
            name=f"{name}_{i+1}"
        )
        
        # Random rotation for scattered look
        coin.rotation_euler = (
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5),
            random.uniform(0, math.pi * 2)
        )
        
        coins.append(coin)
    
    return coins


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_coin(material='GOLD', location=(0, 0, 0))
    create_coin_stack(count=10, location=(0.1, 0, 0))
    create_coin_pile(count=15, location=(0, 0.2, 0))
    
    print("Created coins")
