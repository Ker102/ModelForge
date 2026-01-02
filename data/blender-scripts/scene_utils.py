"""
{
  "title": "Lighting and Camera Setup",
  "category": "scene",
  "tags": ["lighting", "camera", "setup", "render"],
  "description": "Standard setup for lights (Point, Sun, Area) and cameras in a Blender scene."
}
"""
import bpy

def add_light(type='POINT', location=(5, -5, 5), energy=1000, name="Light"):
    bpy.ops.object.light_add(type=type, location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    return light

def add_camera(location=(7, -7, 5), rotation=(1.109, 0, 0.814), name="Camera"):
    bpy.ops.object.camera_add(location=location, rotation=rotation)
    cam = bpy.context.active_object
    cam.name = name
    bpy.context.scene.camera = cam
    return cam

# Common Three-Point Lighting Setup
def setup_three_point_lighting():
    add_light('AREA', location=(5, -5, 5), energy=1000, name="KeyLight")
    add_light('AREA', location=(-5, -5, 3), energy=500, name="FillLight")
    add_light('POINT', location=(0, 5, 4), energy=300, name="BackLight")

def set_background_color(color=(0.05, 0.05, 0.05, 1.0)):
    bpy.context.scene.world.use_nodes = True
    bg = bpy.context.scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value = color

def set_render_engine(engine='CYCLES', samples=128):
    bpy.context.scene.render.engine = engine
    if engine == 'CYCLES':
        bpy.context.scene.cycles.samples = samples
    elif engine == 'BLENDER_EEVEE':
        bpy.context.scene.eevee.taa_render_samples = samples

def set_render_resolution(x=1920, y=1080, percentage=100):
    bpy.context.scene.render.resolution_x = x
    bpy.context.scene.render.resolution_y = y
    bpy.context.scene.render.resolution_percentage = percentage
