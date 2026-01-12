"""
{
  "title": "Book Generator",
  "category": "modeling",
  "subcategory": "props",
  "tags": ["book", "props", "interior", "library", "procedural"],
  "difficulty": "beginner",
  "description": "Generates books and book stacks with customizable covers.",
  "blender_version": "3.0+",
  "estimated_objects": 1
}
"""
import bpy
import random


def create_book(
    width: float = 0.15,
    height: float = 0.22,
    depth: float = 0.03,
    cover_color: tuple = None,
    with_pages: bool = True,
    location: tuple = (0, 0, 0),
    name: str = "Book"
) -> bpy.types.Object:
    """
    Create a simple book.
    
    Args:
        width: Book width (spine to edge)
        height: Book height
        depth: Book thickness
        cover_color: RGB cover color (random if None)
        with_pages: Add visible page edges
        location: Position
        name: Object name
    
    Returns:
        The book object
    """
    if cover_color is None:
        cover_color = (
            random.uniform(0.2, 0.8),
            random.uniform(0.2, 0.8),
            random.uniform(0.2, 0.8)
        )
    
    # Main book body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        location[0] + width/2,
        location[1],
        location[2] + height/2
    ))
    book = bpy.context.active_object
    book.name = name
    book.scale = (width/2, depth/2, height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Cover material
    cover_mat = bpy.data.materials.new(f"{name}_CoverMat")
    cover_mat.use_nodes = True
    bsdf = cover_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*cover_color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    book.data.materials.append(cover_mat)
    
    # Page edges
    if with_pages:
        page_inset = 0.005
        page_height = height - 0.01
        
        # Pages material (cream/white)
        page_mat = bpy.data.materials.new(f"{name}_PageMat")
        page_mat.use_nodes = True
        bsdf = page_mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.95, 0.93, 0.88, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.9
        
        # Top edge
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + width/2,
            location[1],
            location[2] + height - page_inset
        ))
        pages_top = bpy.context.active_object
        pages_top.scale = ((width - 0.01)/2, (depth - 0.01)/2, page_inset/2)
        bpy.ops.object.transform_apply(scale=True)
        pages_top.data.materials.append(page_mat)
        pages_top.parent = book
        
        # Front edge
        bpy.ops.mesh.primitive_cube_add(size=1, location=(
            location[0] + width - page_inset,
            location[1],
            location[2] + height/2
        ))
        pages_front = bpy.context.active_object
        pages_front.scale = (page_inset/2, (depth - 0.01)/2, page_height/2)
        bpy.ops.object.transform_apply(scale=True)
        pages_front.data.materials.append(page_mat)
        pages_front.parent = book
    
    return book


def create_book_stack(
    count: int = 5,
    min_height: float = 0.18,
    max_height: float = 0.28,
    random_rotation: bool = True,
    location: tuple = (0, 0, 0),
    seed: int = 42,
    name: str = "BookStack"
) -> list:
    """
    Create a stack of books.
    
    Args:
        count: Number of books
        min_height: Minimum book height
        max_height: Maximum book height
        random_rotation: Slightly rotate books
        location: Stack position
        seed: Random seed
        name: Stack name
    
    Returns:
        List of book objects
    """
    random.seed(seed)
    books = []
    current_z = location[2]
    
    for i in range(count):
        height = random.uniform(min_height, max_height)
        width = random.uniform(0.12, 0.18)
        depth = random.uniform(0.02, 0.05)
        
        book = create_book(
            width=width,
            height=height,
            depth=depth,
            location=(location[0], location[1], current_z),
            name=f"{name}_{i+1}"
        )
        
        # Rotate book to lay flat
        book.rotation_euler.x = 1.5708
        
        if random_rotation:
            book.rotation_euler.z = random.uniform(-0.15, 0.15)
            book.location.x += random.uniform(-0.02, 0.02)
            book.location.y += random.uniform(-0.02, 0.02)
        
        current_z += depth
        books.append(book)
    
    return books


if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    create_book(location=(0, 0, 0))
    create_book_stack(count=6, location=(0.5, 0, 0))
    
    print("Created book and book stack")
