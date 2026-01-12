"""
{
  "title": "Smoke and Fire Effects",
  "category": "effects",
  "tags": ["smoke", "fire", "simulation", "effects"],
  "description": "Creates smoke and fire simulation effects.",
  "blender_version": "3.0+",
  "estimated_objects": 3
}
"""
import bpy


def create_smoke_effect(
    location: tuple = (0, 0, 0),
    domain_size: tuple = (4, 4, 6),
    resolution: int = 64,
    smoke_color: tuple = (0.5, 0.5, 0.5),
    name_prefix: str = "Smoke"
) -> dict:
    """Create a smoke simulation."""
    result = {}
    
    # Domain
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    domain = bpy.context.active_object
    domain.name = f"{name_prefix}_Domain"
    domain.scale = [s/2 for s in domain_size]
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.object.modifier_add(type='FLUID')
    domain.modifiers["Fluid"].fluid_type = 'DOMAIN'
    settings = domain.modifiers["Fluid"].domain_settings
    settings.domain_type = 'GAS'
    settings.resolution_max = resolution
    
    result['domain'] = domain
    
    # Flow
    flow_loc = (location[0], location[1], location[2] - domain_size[2]/2 + 0.5)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.3, location=flow_loc)
    flow = bpy.context.active_object
    flow.name = f"{name_prefix}_Flow"
    
    bpy.ops.object.modifier_add(type='FLUID')
    flow.modifiers["Fluid"].fluid_type = 'FLOW'
    flow.modifiers["Fluid"].flow_settings.flow_type = 'SMOKE'
    flow.modifiers["Fluid"].flow_settings.smoke_color = smoke_color
    
    result['flow'] = flow
    return result


def create_fire_effect(
    location: tuple = (0, 0, 0),
    domain_size: tuple = (3, 3, 5),
    resolution: int = 64,
    name_prefix: str = "Fire"
) -> dict:
    """Create a fire simulation."""
    result = {}
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    domain = bpy.context.active_object
    domain.name = f"{name_prefix}_Domain"
    domain.scale = [s/2 for s in domain_size]
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.object.modifier_add(type='FLUID')
    domain.modifiers["Fluid"].fluid_type = 'DOMAIN'
    settings = domain.modifiers["Fluid"].domain_settings
    settings.domain_type = 'GAS'
    settings.resolution_max = resolution
    settings.beta = 2.0
    
    result['domain'] = domain
    
    flow_loc = (location[0], location[1], location[2] - domain_size[2]/2 + 0.3)
    bpy.ops.mesh.primitive_plane_add(size=1, location=flow_loc)
    flow = bpy.context.active_object
    flow.name = f"{name_prefix}_Flow"
    
    bpy.ops.object.modifier_add(type='FLUID')
    flow.modifiers["Fluid"].fluid_type = 'FLOW'
    flow.modifiers["Fluid"].flow_settings.flow_type = 'BOTH'
    flow.modifiers["Fluid"].flow_settings.fuel_amount = 1.0
    
    result['flow'] = flow
    return result


if __name__ == "__main__":
    smoke = create_smoke_effect()
    fire = create_fire_effect(location=(5, 0, 0))
    print("Created smoke and fire effects")
