"""
{
  "title": "Image and Texture Utilities",
  "category": "texturing",
  "tags": ["image", "texture", "load", "save", "pack", "generate"],
  "description": "Functions for loading, creating, and managing images.",
  "blender_version": "3.0+"
}
"""
import bpy
import os


def load_image(
    filepath: str,
    check_existing: bool = True
) -> bpy.types.Image:
    """
    Load image from file.
    
    Args:
        filepath: Path to image file
        check_existing: Reuse if already loaded
    
    Returns:
        The loaded image
    """
    return bpy.data.images.load(filepath, check_existing=check_existing)


def create_image(
    name: str,
    width: int = 1024,
    height: int = 1024,
    color: tuple = (0, 0, 0, 1),
    alpha: bool = True,
    float_buffer: bool = False
) -> bpy.types.Image:
    """
    Create new image.
    
    Args:
        name: Image name
        width: Width in pixels
        height: Height in pixels
        color: Fill color (RGBA)
        alpha: Include alpha channel
        float_buffer: Use 32-bit float
    
    Returns:
        The created image
    """
    img = bpy.data.images.new(
        name,
        width=width,
        height=height,
        alpha=alpha,
        float_buffer=float_buffer
    )
    
    # Fill with color
    pixels = list(color) * (width * height)
    img.pixels = pixels
    
    return img


def save_image(
    image: bpy.types.Image,
    filepath: str,
    file_format: str = 'PNG'
) -> bool:
    """
    Save image to file.
    
    Args:
        image: Image to save
        filepath: Output path
        file_format: 'PNG', 'JPEG', 'TIFF', 'OPEN_EXR', 'TARGA'
    
    Returns:
        Success status
    """
    try:
        image.filepath_raw = filepath
        image.file_format = file_format
        image.save()
        return True
    except:
        return False


def pack_image(image: bpy.types.Image) -> None:
    """Pack image into blend file."""
    if not image.packed_file:
        image.pack()


def unpack_image(
    image: bpy.types.Image,
    method: str = 'USE_ORIGINAL'
) -> None:
    """
    Unpack image to external file.
    
    Args:
        method: 'USE_ORIGINAL', 'WRITE_ORIGINAL', 'USE_LOCAL', 'WRITE_LOCAL'
    """
    if image.packed_file:
        image.unpack(method=method)


def reload_image(image: bpy.types.Image) -> None:
    """Reload image from disk."""
    image.reload()


def get_image(name: str) -> bpy.types.Image:
    """Get image by name."""
    return bpy.data.images.get(name)


def set_color_space(
    image: bpy.types.Image,
    color_space: str = 'sRGB'
) -> None:
    """
    Set image color space.
    
    Args:
        color_space: 'sRGB', 'Linear', 'Non-Color', 'Raw', etc.
    """
    image.colorspace_settings.name = color_space


def resize_image(
    image: bpy.types.Image,
    width: int,
    height: int
) -> None:
    """Resize image."""
    image.scale(width, height)


def flip_image(
    image: bpy.types.Image,
    horizontal: bool = False,
    vertical: bool = True
) -> None:
    """Flip image pixels."""
    width = image.size[0]
    height = image.size[1]
    pixels = list(image.pixels)
    
    if vertical:
        for y in range(height // 2):
            for x in range(width):
                idx1 = (y * width + x) * 4
                idx2 = ((height - 1 - y) * width + x) * 4
                
                for c in range(4):
                    pixels[idx1 + c], pixels[idx2 + c] = pixels[idx2 + c], pixels[idx1 + c]
    
    if horizontal:
        for y in range(height):
            for x in range(width // 2):
                idx1 = (y * width + x) * 4
                idx2 = (y * width + (width - 1 - x)) * 4
                
                for c in range(4):
                    pixels[idx1 + c], pixels[idx2 + c] = pixels[idx2 + c], pixels[idx1 + c]
    
    image.pixels = pixels


def create_solid_color_image(
    name: str,
    color: tuple,
    size: int = 8
) -> bpy.types.Image:
    """Create small solid color image for materials."""
    return create_image(name, size, size, color)


def create_checker_image(
    name: str,
    size: int = 512,
    squares: int = 8,
    color1: tuple = (0.2, 0.2, 0.2, 1),
    color2: tuple = (0.8, 0.8, 0.8, 1)
) -> bpy.types.Image:
    """Create checker pattern image."""
    img = bpy.data.images.new(name, width=size, height=size)
    
    pixels = []
    square_size = size // squares
    
    for y in range(size):
        for x in range(size):
            checker = ((x // square_size) + (y // square_size)) % 2
            color = color1 if checker == 0 else color2
            pixels.extend(color)
    
    img.pixels = pixels
    return img


def create_gradient_image(
    name: str,
    width: int = 256,
    height: int = 256,
    direction: str = 'VERTICAL',
    color1: tuple = (0, 0, 0, 1),
    color2: tuple = (1, 1, 1, 1)
) -> bpy.types.Image:
    """
    Create gradient image.
    
    Args:
        direction: 'VERTICAL', 'HORIZONTAL', 'RADIAL'
    """
    img = bpy.data.images.new(name, width=width, height=height)
    
    pixels = []
    
    for y in range(height):
        for x in range(width):
            if direction == 'VERTICAL':
                t = y / height
            elif direction == 'HORIZONTAL':
                t = x / width
            else:  # RADIAL
                cx, cy = width/2, height/2
                dx, dy = x - cx, y - cy
                dist = (dx*dx + dy*dy) ** 0.5
                max_dist = min(cx, cy)
                t = min(1, dist / max_dist)
            
            # Lerp colors
            color = tuple(c1 * (1 - t) + c2 * t for c1, c2 in zip(color1, color2))
            pixels.extend(color)
    
    img.pixels = pixels
    return img


def get_image_resolution(image: bpy.types.Image) -> tuple:
    """Get image dimensions."""
    return (image.size[0], image.size[1])


def list_loaded_images() -> list:
    """List all loaded image names."""
    return [img.name for img in bpy.data.images]
