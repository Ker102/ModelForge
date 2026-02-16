# Emission Shader - Blender 5.0 Manual

The Emission node is used to add Lambertian emission shader.
This can for example, be used for material and light surface outputs.

Light strength for point, spot and area lights is specified in Watts.
Sun lights are specified in Watts/m2, which require much smaller values like 1 W/m2.
Emission shaders on meshes are also in Watts/m2.

## Inputs
- **Color**: Color of the emitted light.
- **Strength**: Strength of the emitted light. For point and area lights, the unit is Watts.
  For materials, a value of 1.0 will ensure that the object in the image has
  the exact same color as the Color input, i.e. make it 'shadeless'.

## Properties
This node has no properties.

## Outputs
- **Emission**: Can be plugged into both Surface Input and Volume Input of the Material Output node.

## Key Notes
- Point/spot/area lights: strength in **Watts**
- Sun lights: strength in **Watts/m2** (much smaller values like 1 W/m2)
- Mesh emission: also in **Watts/m2**
- Strength 1.0 = exact same color as Color input (shadeless)
- Strength 3.0+ = visible bloom/glow effect
