"""
{
  "title": "Driver Utilities",
  "category": "animation",
  "tags": ["driver", "expression", "variable", "animation", "procedural"],
  "description": "Functions for creating and managing property drivers.",
  "blender_version": "3.0+"
}
"""
import bpy


def add_driver(
    obj: bpy.types.Object,
    data_path: str,
    expression: str,
    index: int = -1
) -> bpy.types.Driver:
    """
    Add a driver with expression.
    
    Args:
        obj: Object to add driver to
        data_path: Property path (e.g., 'location', 'rotation_euler')
        expression: Python expression
        index: Array index (-1 for non-array)
    
    Returns:
        The created driver
    
    Example:
        >>> add_driver(cube, 'location', 'sin(frame/10)', index=2)
    """
    if index >= 0:
        fcurve = obj.driver_add(data_path, index)
    else:
        fcurve = obj.driver_add(data_path)
    
    driver = fcurve.driver
    driver.type = 'SCRIPTED'
    driver.expression = expression
    
    return driver


def add_driver_variable(
    driver: bpy.types.Driver,
    name: str,
    target: bpy.types.Object,
    data_path: str,
    var_type: str = 'SINGLE_PROP'
) -> bpy.types.DriverVariable:
    """
    Add a variable to a driver.
    
    Args:
        driver: Target driver
        name: Variable name
        target: Source object
        data_path: Property path on target
        var_type: 'SINGLE_PROP', 'TRANSFORMS', 'ROTATION_DIFF', 'LOC_DIFF'
    
    Returns:
        The created variable
    """
    var = driver.variables.new()
    var.name = name
    var.type = var_type
    
    if var_type == 'SINGLE_PROP':
        var.targets[0].id = target
        var.targets[0].data_path = data_path
    elif var_type == 'TRANSFORMS':
        var.targets[0].id = target
        var.targets[0].transform_type = 'LOC_X'
        var.targets[0].transform_space = 'WORLD_SPACE'
    
    return var


def add_frame_driver(
    obj: bpy.types.Object,
    data_path: str,
    expression: str,
    index: int = -1
) -> bpy.types.Driver:
    """
    Add driver using frame number.
    
    Args:
        obj: Target object
        data_path: Property path
        expression: Expression using 'frame' variable
        index: Array index
    
    Example:
        >>> add_frame_driver(cube, 'rotation_euler', 'frame * 0.05', index=2)
    """
    driver = add_driver(obj, data_path, expression, index)
    return driver


def add_oscillation_driver(
    obj: bpy.types.Object,
    data_path: str,
    amplitude: float = 1.0,
    frequency: float = 1.0,
    offset: float = 0.0,
    index: int = -1
) -> bpy.types.Driver:
    """
    Add sine wave oscillation driver.
    
    Args:
        obj: Target object
        data_path: Property path
        amplitude: Wave amplitude
        frequency: Wave frequency
        offset: Base value offset
        index: Array index
    """
    expression = f"sin(frame * {frequency} * 0.1) * {amplitude} + {offset}"
    return add_driver(obj, data_path, expression, index)


def add_noise_driver(
    obj: bpy.types.Object,
    data_path: str,
    scale: float = 1.0,
    strength: float = 1.0,
    index: int = -1
) -> bpy.types.Driver:
    """
    Add noise-based driver.
    
    Args:
        obj: Target object
        data_path: Property path
        scale: Noise scale
        strength: Effect strength
        index: Array index
    """
    expression = f"noise.random() * {strength}"
    return add_driver(obj, data_path, expression, index)


def copy_property_driver(
    source_obj: bpy.types.Object,
    target_obj: bpy.types.Object,
    source_path: str,
    target_path: str,
    multiplier: float = 1.0,
    offset: float = 0.0,
    index: int = -1
) -> bpy.types.Driver:
    """
    Create driver that copies property from another object.
    
    Args:
        source_obj: Object to read from
        target_obj: Object to drive
        source_path: Property to read
        target_path: Property to drive
        multiplier: Value multiplier
        offset: Value offset
        index: Array index
    """
    driver = add_driver(target_obj, target_path, f"var * {multiplier} + {offset}", index)
    add_driver_variable(driver, 'var', source_obj, source_path)
    return driver


def remove_driver(
    obj: bpy.types.Object,
    data_path: str,
    index: int = -1
) -> None:
    """Remove driver from property."""
    if index >= 0:
        obj.driver_remove(data_path, index)
    else:
        obj.driver_remove(data_path)


def remove_all_drivers(obj: bpy.types.Object) -> None:
    """Remove all drivers from object."""
    if obj.animation_data:
        for driver in obj.animation_data.drivers[:]:
            obj.driver_remove(driver.data_path, driver.array_index)
