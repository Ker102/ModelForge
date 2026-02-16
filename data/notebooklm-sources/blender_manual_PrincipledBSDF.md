ContentsMenuExpandLight modeDark modeAuto light/dark, in light modeAuto light/dark, in dark mode[Skip to content](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#furo-main-content)

[Back to top](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#)

[Edit this page](https://projects.blender.org/blender/blender-manual/_edit/main/manual/render/shader_nodes/shader/principled.rst "Edit this page")

Toggle Light / Dark / Auto color theme

Toggle table of contents sidebar

# Principled BSDF [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#principled-bsdf "Link to this heading")

![Principled BSDF node.](https://docs.blender.org/manual/en/latest/_images/node-types_ShaderNodeBsdfPrincipled.webp)

The _Principled_ BSDF
that combines multiple layers into a single easy to use node.
It can model a wide variety of materials.

It is based on the OpenPBR Surface shading model, and provides parameters
compatible with similar PBR shaders found in other software,
such as the Disney and Standard Surface models.
Image textures painted or baked from software like Substance Painter
may be directly linked to the corresponding input in this shader.

## Layers [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#layers "Link to this heading")

The base layer is a mix between metal, diffuse, subsurface, and transmission components.
Most materials will use one of these components, though it is possible to smoothly mix
between them.

![../../../_images/render_shader-nodes_principled_layers.svg](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_principled_layers.svg)

The metal component is opaque and only reflect lights. Diffuse is fully opaque, while
subsurface also involves light scattering just below the surface. Both diffuse and
subsurface sit below a specular layer. The transmission component includes both
specular reflection and refraction.

On top of all base layers there is an optional glossy coat. And finally the sheen layer
sits on top of all other layers, to add fuzz or dust.

Light emission can also be added. Light emits from below the coat and sheen layers,
to model for example emissive displays with a coat or dust.

## Inputs [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#inputs "Link to this heading")

Base Color

Overall color of the material used for diffuse, subsurface, metal and transmission.

![../../../_images/render_shader-nodes_shader_principled-base-color.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-base-color.webp)

Same base color for multiple materials types [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id1 "Link to this image")

Roughness

Specifies microfacet roughness of the surface for specular reflection and transmission.
A value of 0.0 gives a perfectly sharp reflection, while 1.0 gives a diffuse reflection.

![../../../_images/render_shader-nodes_shader_principled-roughness.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-roughness.webp)

Roughness from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id2 "Link to this image")

Metallic

Blends between a dielectric and metallic material model.
At 0.0 the material consists of a diffuse or transmissive base layer, with a specular reflection layer on top.
A value of 1.0 gives a fully specular reflection tinted with the base color,
without diffuse reflection or transmission.

![../../../_images/render_shader-nodes_shader_principled-metallic.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-metallic.webp)

Metallic from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id3 "Link to this image")

IOR

Index of refraction ( [IOR](https://docs.blender.org/manual/en/latest/glossary/index.html#term-IOR)) for specular reflection and transmission.
For most materials, the IOR is between 1.0 (vacuum and air) and 4.0 (germanium).
The default value of 1.5 is a good approximation for glass.

![../../../_images/render_shader-nodes_shader_principled-ior.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-ior.webp)

IOR from 1.0 to 2.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id4 "Link to this image")

Alpha

Controls the transparency of the surface, with 1.0 fully opaque.
Usually linked to the Alpha output of an Image Texture node.

![../../../_images/render_shader-nodes_shader_principled-alpha.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-alpha.webp)

Alpha from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id5 "Link to this image")

Normal

Controls the normals of the base layers.

### Diffuse [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#diffuse "Link to this heading")

Roughness Cycles Only

Surface roughness; 0.0 gives standard Lambertian reflection, higher values activate the Oren-Nayar BSDF.

![../../../_images/render_shader-nodes_shader_principled-diffuse-roughness.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-diffuse-roughness.webp)

Roughness from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id6 "Link to this image")

### Subsurface [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#subsurface "Link to this heading")

[Subsurface scattering](https://docs.blender.org/manual/en/latest/glossary/index.html#term-Subsurface-Scattering) is used to render materials such as skin, milk and wax.
Light scatters below the surface to create a soft appearance.

Method

Rendering method to simulate [Subsurface scattering](https://docs.blender.org/manual/en/latest/glossary/index.html#term-Subsurface-Scattering).

Christensen-Burley:

An approximation to physically-based volume scattering.
This method is less accurate than _Random Walk_ however,
in some situations this method will resolve noise faster.

Random Walk:

Cycles Only
Provides accurate results for thin and curved objects.
Random Walk uses true volumetric scattering inside the mesh,
which means that it works best for closed meshes.
Overlapping faces and holes in the mesh can cause problems.

Random Walk (Skin):

Cycles Only
Random walk method optimized for skin rendering. The radius
is automatically adjusted based on the color texture, and
the subsurface entry direction uses a mix of diffuse and
specular transmission with custom [IOR](https://docs.blender.org/manual/en/latest/glossary/index.html#term-IOR). This tends to retain
greater surface detail and color and matches measured skin
more closely.

Weight

Blend between diffuse surface and subsurface scattering.
Typically should be zero or one (either fully diffuse or subsurface).

![../../../_images/render_shader-nodes_shader_principled-subsurface-weight.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-subsurface-weight.webp)

Weight from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id7 "Link to this image")

Radius

Average distance that light scatters below the surface.
Higher radius gives a softer appearance, as light bleeds into shadows and through the object.
The scattering distance is specified separately for the RGB channels,
to render materials such as skin where red light scatters deeper.
The X, Y and Z values are mapped to the R, G and B values, respectively.

![../../../_images/render_shader-nodes_shader_principled-subsurface-radius.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-subsurface-radius.webp)

Radius from white to red [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id8 "Link to this image")

Scale

Scale applied to the radius.

![../../../_images/render_shader-nodes_shader_principled-subsurface-scale.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-subsurface-scale.webp)

Scale from 0 cm to 50 cm [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id9 "Link to this image")

IOR Cycles Only

Index of refraction ( [IOR](https://docs.blender.org/manual/en/latest/glossary/index.html#term-IOR)) used for rays that enter the subsurface component. This may be set to
a different value than the global IOR to simulate different layers of skin.

![../../../_images/render_shader-nodes_shader_principled-subsurface-ior.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-subsurface-ior.webp)

IOR from 1.0 to 2.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id10 "Link to this image")

Anisotropy Cycles Only

Directionality of volume scattering within the subsurface medium. Zero scatters uniformly
in all directions, with higher values scattering more strongly forward.
For example, skin has been measured to have an anisotropy of 0.8.

![../../../_images/render_shader-nodes_shader_principled-subsurface-anisotropy.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-subsurface-anisotropy.webp)

Anisotropy from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id11 "Link to this image")

### Specular [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#specular "Link to this heading")

Controls for both the metallic component and specular layer on top of diffuse and subsurface.

Distribution

Microfacet distribution to use.

GGX:

A method that is faster than _Multiple-scattering GGX_ but is less physically accurate.

Multiscatter GGX:

Takes multiple scattering events between microfacets into account.
This gives more energy conserving results,
which would otherwise be visible as excessive darkening.

IOR Level

Adjustment to the [IOR](https://docs.blender.org/manual/en/latest/glossary/index.html#term-IOR) to increase or decrease intensity of the specular layer.
0.5 means no adjustment, 0 removes all reflections, 1 doubles them at normal incidence.

This input is designed for conveniently texturing the IOR and amount of specular
reflection.

![../../../_images/render_shader-nodes_shader_principled-specular-ior-level.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-specular-ior-level.webp)

IOR level from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id12 "Link to this image")

Tint

Color tint for specular and metallic reflection.

For non-metallic tints provides artistic control over the color specular reflections at normal incidence,
while grazing reflections remain white. In reality non-metallic specular reflection is fully white.

For metallic materials tints the edges to simulate complex IOR as found in materials such as gold or copper.

![../../../_images/render_shader-nodes_shader_principled-specular-tint.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-specular-tint.webp)

Tint from white to orange [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id13 "Link to this image")

Anisotropic Cycles Only

Amount of anisotropy for specular reflection. Higher values give elongated highlights along the tangent direction;
negative values give highlights shaped perpendicular to the tangent direction.

![../../../_images/render_shader-nodes_shader_principled-specular-anisotropic.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-specular-anisotropic.webp)

Anisotropic from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id14 "Link to this image")

Anisotropic Rotation Cycles Only

Rotates the direction of anisotropy, with 1.0 going full circle.

Compared to the _Glossy BSDF_ node, the direction of highlight elongation
is rotated by 90°. Add 0.25 to the value to correct.

![../../../_images/render_shader-nodes_shader_principled-specular-anisotropic-rotation.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-specular-anisotropic-rotation.webp)

Anisotropic rotation from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id15 "Link to this image")

Tangent

Controls the tangent direction for anisotropy.

### Transmission [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#transmission "Link to this heading")

Transmission is used to render materials like glass and liquids, where the surface both
reflects light and transmits it into the interior of the object

Weight

Mix between fully opaque surface at zero and fully transmissive at one.

![../../../_images/render_shader-nodes_shader_principled-transmission-weight.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-transmission-weight.webp)

Weight from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id16 "Link to this image")

### Coat [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#coat "Link to this heading")

Coat on top of the materials, to simulate for example a clearcoat, lacquer or car paint.

Weight

Controls the intensity of the coat layer, both the reflection and the tinting.
Typically should be zero or one for physically-based materials, but may be textured
to vary the amount of coating across the surface.

![../../../_images/render_shader-nodes_shader_principled-coat-weight.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-coat-weight.webp)

Weight from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id17 "Link to this image")

Roughness

Roughness of the coat layer.

![../../../_images/render_shader-nodes_shader_principled-coat-roughness.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-coat-roughness.webp)

Roughness from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id18 "Link to this image")

IOR

Index of refraction ( [IOR](https://docs.blender.org/manual/en/latest/glossary/index.html#term-IOR)) of the coat layer.
Affects its reflectivity as well as the falloff of coat tinting.

![../../../_images/render_shader-nodes_shader_principled-coat-ior.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-coat-ior.webp)

IOR from 1.0 to 2.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id19 "Link to this image")

Tint

Adds a colored tint to the coat layer by modeling absorption in the layer.
Saturation increases at shallower angles, as the light travels farther
through the medium, depending on the IOR.

![../../../_images/render_shader-nodes_shader_principled-coat-tint.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-coat-tint.webp)

Tint from white to blue [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id20 "Link to this image")

Normal

Controls the normals of the _Coat_ layer, for example to add a smooth coating on a rough surface.

### Sheen [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#sheen "Link to this heading")

Sheen simulates very small fibers on the surface.
For cloth this adds a soft velvet like reflection near edges.
It can also be used to simulate dust on arbitrary materials.

Weight

Controls the intensity of the sheen layer.

![../../../_images/render_shader-nodes_shader_principled-sheen-weight.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-sheen-weight.webp)

Weight from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id21 "Link to this image")

Roughness

Roughness of the sheen reflection.

![../../../_images/render_shader-nodes_shader_principled-sheen-roughness.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-sheen-roughness.webp)

Roughness from 0.0 to 1.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id22 "Link to this image")

Tint

The color of the sheen reflection.

![../../../_images/render_shader-nodes_shader_principled-sheen-tint.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-sheen-tint.webp)

Tint from white to green. [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id23 "Link to this image")

### Emission [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#emission "Link to this heading")

Light emission from the surface.

Color

Color of light emission from the surface.

![../../../_images/render_shader-nodes_shader_principled-emission-color.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-emission-color.webp)

Emission color variations [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id24 "Link to this image")

Strength

Strength of the emitted light. A value of 1.0 ensures that the object
in the image has the exact same color as the _Emission Color_, i.e. make it ‘shadeless’.

![../../../_images/render_shader-nodes_shader_principled-emission-strength.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-emission-strength.webp)

Strength from 0.0 to 10.0 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id25 "Link to this image")

### Thin Film Cycles Only [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#thin-film-cycles-only "Link to this heading")

Thin Film simulates the effect of interference in a thin film sitting on top of the material.
This causes the specular reflection to be colored in a way which strongly depends on the view
angle as well as the film thickness and the index of refraction ( [IOR](https://docs.blender.org/manual/en/latest/glossary/index.html#term-IOR)) of the film and
the material itself.

This effect is commonly seen on e.g. oil films, soap bubbles or glass coatings. While its
influence is more obvious in specular highlights, it also affects transmission.

Thickness

The thickness of the film in nanometers. A value of 0 disables the simulation.
The interference effect is strongest between roughly 100 and 1000 nanometers, since this is
near the wavelengths of visible light.

![../../../_images/render_shader-nodes_shader_principled-thin-film-thickness.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-thin-film-thickness.webp)

Thickness from 400 to 800 nanometers [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id26 "Link to this image")

IOR

Index of refraction ( [IOR](https://docs.blender.org/manual/en/latest/glossary/index.html#term-IOR)) of the thin film.
The common range for this value is between 1.0 (vacuum and air) and roughly 2.0,
though some materials can reach higher values.
The default value of 1.33 is a good approximation for water.
Note that when the value is set to 1.0 or to the main IOR of the material, the thin film
effect disappears since the film optically blends into the air or the material.

![../../../_images/render_shader-nodes_shader_principled-thin-film-ior.webp](https://docs.blender.org/manual/en/latest/_images/render_shader-nodes_shader_principled-thin-film-ior.webp)

IOR from 1.0 to 1.5 [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html#id27 "Link to this image")

## Outputs [¶](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html\#outputs "Link to this heading")

BSDF

Standard shader output.