ContentsMenuExpandLight modeDark modeAuto light/dark, in light modeAuto light/dark, in dark mode[Skip to content](https://docs.blender.org/api/current/bpy.types.Material.html#furo-main-content)

[Back to top](https://docs.blender.org/api/current/bpy.types.Material.html#)

Toggle Light / Dark / Auto color theme

Toggle table of contents sidebar

# Material(ID) [¶](https://docs.blender.org/api/current/bpy.types.Material.html\#material-id "Link to this heading")

base classes — [`bpy_struct`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID "bpy.types.ID")

_class_ bpy.types.Material( _ID_) [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material "Link to this definition")

Material data-block to define the appearance of geometric objects for rendering

alpha\_threshold [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.alpha_threshold "Link to this definition")

A pixel is rendered only if its alpha value is above this threshold

Type:

float in \[0, 1\], default 0.5

animation\_data [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.animation_data "Link to this definition")

Animation data for this data-block

Type:

[`AnimData`](https://docs.blender.org/api/current/bpy.types.AnimData.html#bpy.types.AnimData "bpy.types.AnimData"), (readonly)

blend\_method [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.blend_method "Link to this definition")

Blend Mode for Transparent Faces (Deprecated: use ‘surface\_render\_method’)

- `OPAQUE`
Opaque – Render surface without transparency.

- `CLIP`
Alpha Clip – Use the alpha threshold to clip the visibility (binary visibility).

- `HASHED`
Alpha Hashed – Use noise to dither the binary visibility (works well with multi-samples).

- `BLEND`
Alpha Blend – Render polygon transparent, depending on alpha channel of the texture.


Type:

enum in \[`'OPAQUE'`, `'CLIP'`, `'HASHED'`, `'BLEND'`\], default `'OPAQUE'`

cycles [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.cycles "Link to this definition")

Cycles material settings

Type:

`CyclesMaterialSettings`, (readonly)

diffuse\_color [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.diffuse_color "Link to this definition")

Diffuse color of the material

Type:

float array of 4 items in \[0, inf\], default (0.8, 0.8, 0.8, 1.0)

displacement\_method [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.displacement_method "Link to this definition")

Method to use for the displacement

- `BUMP`
Bump Only – Bump mapping to simulate the appearance of displacement.

- `DISPLACEMENT`
Displacement Only – Use true displacement of surface only, requires fine subdivision.

- `BOTH`
Displacement and Bump – Combination of true displacement and bump mapping for finer detail.


Type:

enum in \[`'BUMP'`, `'DISPLACEMENT'`, `'BOTH'`\], default `'BUMP'`

grease\_pencil [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.grease_pencil "Link to this definition")

Grease Pencil color settings for material

Type:

[`MaterialGPencilStyle`](https://docs.blender.org/api/current/bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle "bpy.types.MaterialGPencilStyle"), (readonly)

is\_grease\_pencil [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.is_grease_pencil "Link to this definition")

True if this material has Grease Pencil data

Type:

boolean, default False, (readonly)

line\_color [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.line_color "Link to this definition")

Line color used for Freestyle line rendering

Type:

float array of 4 items in \[0, inf\], default (0.0, 0.0, 0.0, 0.0)

line\_priority [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.line_priority "Link to this definition")

The line color of a higher priority is used at material boundaries

Type:

int in \[0, 32767\], default 0

lineart [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.lineart "Link to this definition")

Line Art settings for material

Type:

[`MaterialLineArt`](https://docs.blender.org/api/current/bpy.types.MaterialLineArt.html#bpy.types.MaterialLineArt "bpy.types.MaterialLineArt"), (readonly)

max\_vertex\_displacement [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.max_vertex_displacement "Link to this definition")

The max distance a vertex can be displaced. Displacements over this threshold may cause visibility issues.

Type:

float in \[0, inf\], default 0.0

metallic [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.metallic "Link to this definition")

Amount of mirror reflection for raytrace

Type:

float in \[0, 1\], default 0.0

node\_tree [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.node_tree "Link to this definition")

Node tree for node based materials

Type:

[`NodeTree`](https://docs.blender.org/api/current/bpy.types.NodeTree.html#bpy.types.NodeTree "bpy.types.NodeTree"), (readonly)

paint\_active\_slot [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.paint_active_slot "Link to this definition")

Index of active texture paint slot

Type:

int in \[0, 32767\], default 0

paint\_clone\_slot [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.paint_clone_slot "Link to this definition")

Index of clone texture paint slot

Type:

int in \[0, 32767\], default 0

pass\_index [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.pass_index "Link to this definition")

Index number for the “Material Index” render pass

Type:

int in \[0, 32767\], default 0

preview\_render\_type [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.preview_render_type "Link to this definition")

Type of preview render

- `FLAT`
Flat – Flat XY plane.

- `SPHERE`
Sphere – Sphere.

- `CUBE`
Cube – Cube.

- `HAIR`
Hair – Hair strands.

- `SHADERBALL`
Shader Ball – Shader ball.

- `CLOTH`
Cloth – Cloth.

- `FLUID`
Fluid – Fluid.


Type:

enum in \[`'FLAT'`, `'SPHERE'`, `'CUBE'`, `'HAIR'`, `'SHADERBALL'`, `'CLOTH'`, `'FLUID'`\], default `'SPHERE'`

refraction\_depth [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.refraction_depth "Link to this definition")

Approximate the thickness of the object to compute two refraction events (0 is disabled) (Deprecated)

Type:

float in \[0, inf\], default 0.0

roughness [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.roughness "Link to this definition")

Roughness of the material

Type:

float in \[0, 1\], default 0.4

show\_transparent\_back [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.show_transparent_back "Link to this definition")

Render multiple transparent layers (may introduce transparency sorting problems) (Deprecated: use ‘use\_tranparency\_overlap’)

Type:

boolean, default True

specular\_color [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.specular_color "Link to this definition")

Specular color of the material

Type:

[`mathutils.Color`](https://docs.blender.org/api/current/mathutils.html#mathutils.Color "mathutils.Color") of 3 items in \[0, inf\], default (1.0, 1.0, 1.0)

specular\_intensity [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.specular_intensity "Link to this definition")

How intense (bright) the specular reflection is

Type:

float in \[0, 1\], default 0.5

surface\_render\_method [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.surface_render_method "Link to this definition")

Controls the blending and the compatibility with certain features

- `DITHERED`
Dithered – Allows for grayscale hashed transparency, and compatible with render passes and raytracing. Also known as deferred rendering..

- `BLENDED`
Blended – Allows for colored transparency, but incompatible with render passes and raytracing. Also known as forward rendering..


Type:

enum in \[`'DITHERED'`, `'BLENDED'`\], default `'DITHERED'`

texture\_paint\_images [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.texture_paint_images "Link to this definition")

Texture images used for texture painting

Type:

[`bpy_prop_collection`](https://docs.blender.org/api/current/bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection") of [`Image`](https://docs.blender.org/api/current/bpy.types.Image.html#bpy.types.Image "bpy.types.Image"), (readonly)

texture\_paint\_slots [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.texture_paint_slots "Link to this definition")

Texture slots defining the mapping and influence of textures

Type:

[`bpy_prop_collection`](https://docs.blender.org/api/current/bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection") of [`TexPaintSlot`](https://docs.blender.org/api/current/bpy.types.TexPaintSlot.html#bpy.types.TexPaintSlot "bpy.types.TexPaintSlot"), (readonly)

thickness\_mode [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.thickness_mode "Link to this definition")

Approximation used to model the light interactions inside the object

- `SPHERE`
Sphere – Approximate the object as a sphere whose diameter is equal to the thickness defined by the node tree.

- `SLAB`
Slab – Approximate the object as an infinite slab of thickness defined by the node tree.


Type:

enum in \[`'SPHERE'`, `'SLAB'`\], default `'SPHERE'`

use\_backface\_culling [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_backface_culling "Link to this definition")

Use back face culling to hide the back side of faces

Type:

boolean, default False

use\_backface\_culling\_lightprobe\_volume [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_backface_culling_lightprobe_volume "Link to this definition")

Consider material single sided for light probe volume capture. Additionally helps rejecting probes inside the object to avoid light leaks.

Type:

boolean, default True

use\_backface\_culling\_shadow [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_backface_culling_shadow "Link to this definition")

Use back face culling when casting shadows

Type:

boolean, default False

use\_nodes [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_nodes "Link to this definition")

Use shader nodes to render the material

Deprecated since version 5.0: removal planned in version 6.0

Unused but kept for compatibility reasons. Setting the property has no effect, and getting it always returns True.

Type:

boolean, default False

use\_preview\_world [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_preview_world "Link to this definition")

Use the current world background to light the preview render

Type:

boolean, default False

use\_raytrace\_refraction [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_raytrace_refraction "Link to this definition")

Use raytracing to determine transmitted color instead of using only light probes. This prevents the surface from contributing to the lighting of surfaces not using this setting.

Type:

boolean, default False

use\_screen\_refraction [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_screen_refraction "Link to this definition")

Use raytracing to determine transmitted color instead of using only light probes. This prevents the surface from contributing to the lighting of surfaces not using this setting. Deprecated: use ‘use\_raytrace\_refraction’.

Type:

boolean, default False

use\_sss\_translucency [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_sss_translucency "Link to this definition")

Add translucency effect to subsurface (Deprecated)

Type:

boolean, default False

use\_thickness\_from\_shadow [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_thickness_from_shadow "Link to this definition")

Use the shadow maps from shadow casting lights to refine the thickness defined by the material node tree

Type:

boolean, default False

use\_transparency\_overlap [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_transparency_overlap "Link to this definition")

Render multiple transparent layers (may introduce transparency sorting problems)

Type:

boolean, default True

use\_transparent\_shadow [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.use_transparent_shadow "Link to this definition")

Use transparent shadows for this material if it contains a Transparent BSDF, disabling will render faster but not give accurate shadows

Type:

boolean, default True

volume\_intersection\_method [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.volume_intersection_method "Link to this definition")

Determines which inner part of the mesh will produce volumetric effect

- `FAST`
Fast – Each face is considered as a medium interface. Gives correct results for manifold geometry that contains no inner parts..

- `ACCURATE`
Accurate – Faces are considered as medium interface only when they have different consecutive facing. Gives correct results as long as the max ray depth is not exceeded. Have significant memory overhead compared to the fast method..


Type:

enum in \[`'FAST'`, `'ACCURATE'`\], default `'FAST'`

inline\_shader\_nodes() [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.inline_shader_nodes "Link to this definition")

Get the inlined shader nodes of this material. This preprocesses the node tree
to remove nested groups, repeat zones and more.

Returns:

The inlined shader nodes.

Return type:

[`bpy.types.InlineShaderNodes`](https://docs.blender.org/api/current/bpy.types.InlineShaderNodes.html#bpy.types.InlineShaderNodes "bpy.types.InlineShaderNodes")

_classmethod_ bl\_rna\_get\_subclass( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.bl_rna_get_subclass "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The RNA type or default when not found.

Return type:

[`bpy.types.Struct`](https://docs.blender.org/api/current/bpy.types.Struct.html#bpy.types.Struct "bpy.types.Struct") subclass

_classmethod_ bl\_rna\_get\_subclass\_py( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material.bl_rna_get_subclass_py "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The class or default when not found.

Return type:

type

## Inherited Properties [¶](https://docs.blender.org/api/current/bpy.types.Material.html\#inherited-properties "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.id_data`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data "bpy.types.bpy_struct.id_data")<br>  <br>- [`ID.name`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.name "bpy.types.ID.name")<br>  <br>- [`ID.name_full`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.name_full "bpy.types.ID.name_full")<br>  <br>- [`ID.id_type`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.id_type "bpy.types.ID.id_type")<br>  <br>- [`ID.session_uid`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.session_uid "bpy.types.ID.session_uid")<br>  <br>- [`ID.is_evaluated`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_evaluated "bpy.types.ID.is_evaluated")<br>  <br>- [`ID.original`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.original "bpy.types.ID.original")<br>  <br>- [`ID.users`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.users "bpy.types.ID.users")<br>  <br>- [`ID.use_fake_user`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.use_fake_user "bpy.types.ID.use_fake_user")<br>  <br>- [`ID.use_extra_user`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.use_extra_user "bpy.types.ID.use_extra_user")<br>  <br>- [`ID.is_embedded_data`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_embedded_data "bpy.types.ID.is_embedded_data") | - [`ID.is_linked_packed`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_linked_packed "bpy.types.ID.is_linked_packed")<br>  <br>- [`ID.is_missing`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_missing "bpy.types.ID.is_missing")<br>  <br>- [`ID.is_runtime_data`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_runtime_data "bpy.types.ID.is_runtime_data")<br>  <br>- [`ID.is_editable`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_editable "bpy.types.ID.is_editable")<br>  <br>- [`ID.tag`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.tag "bpy.types.ID.tag")<br>  <br>- [`ID.is_library_indirect`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_library_indirect "bpy.types.ID.is_library_indirect")<br>  <br>- [`ID.library`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.library "bpy.types.ID.library")<br>  <br>- [`ID.library_weak_reference`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.library_weak_reference "bpy.types.ID.library_weak_reference")<br>  <br>- [`ID.asset_data`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_data "bpy.types.ID.asset_data")<br>  <br>- [`ID.override_library`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.override_library "bpy.types.ID.override_library")<br>  <br>- [`ID.preview`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.preview "bpy.types.ID.preview") |

## Inherited Functions [¶](https://docs.blender.org/api/current/bpy.types.Material.html\#inherited-functions "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.as_pointer`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.as_pointer "bpy.types.bpy_struct.as_pointer")<br>  <br>- [`bpy_struct.driver_add`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_add "bpy.types.bpy_struct.driver_add")<br>  <br>- [`bpy_struct.driver_remove`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_remove "bpy.types.bpy_struct.driver_remove")<br>  <br>- [`bpy_struct.get`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.get "bpy.types.bpy_struct.get")<br>  <br>- [`bpy_struct.id_properties_clear`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_clear "bpy.types.bpy_struct.id_properties_clear")<br>  <br>- [`bpy_struct.id_properties_ensure`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ensure "bpy.types.bpy_struct.id_properties_ensure")<br>  <br>- [`bpy_struct.id_properties_ui`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ui "bpy.types.bpy_struct.id_properties_ui")<br>  <br>- [`bpy_struct.is_property_hidden`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_hidden "bpy.types.bpy_struct.is_property_hidden")<br>  <br>- [`bpy_struct.is_property_overridable_library`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_overridable_library "bpy.types.bpy_struct.is_property_overridable_library")<br>  <br>- [`bpy_struct.is_property_readonly`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_readonly "bpy.types.bpy_struct.is_property_readonly")<br>  <br>- [`bpy_struct.is_property_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_set "bpy.types.bpy_struct.is_property_set")<br>  <br>- [`bpy_struct.items`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.items "bpy.types.bpy_struct.items")<br>  <br>- [`bpy_struct.keyframe_delete`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_delete "bpy.types.bpy_struct.keyframe_delete")<br>  <br>- [`bpy_struct.keyframe_insert`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert "bpy.types.bpy_struct.keyframe_insert")<br>  <br>- [`bpy_struct.keys`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keys "bpy.types.bpy_struct.keys")<br>  <br>- [`bpy_struct.path_from_id`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_id "bpy.types.bpy_struct.path_from_id")<br>  <br>- [`bpy_struct.path_from_module`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_module "bpy.types.bpy_struct.path_from_module")<br>  <br>- [`bpy_struct.path_resolve`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_resolve "bpy.types.bpy_struct.path_resolve")<br>  <br>- [`bpy_struct.pop`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.pop "bpy.types.bpy_struct.pop")<br>  <br>- [`bpy_struct.property_overridable_library_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_overridable_library_set "bpy.types.bpy_struct.property_overridable_library_set")<br>  <br>- [`bpy_struct.property_unset`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_unset "bpy.types.bpy_struct.property_unset")<br>  <br>- [`bpy_struct.rna_ancestors`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.rna_ancestors "bpy.types.bpy_struct.rna_ancestors") | - [`bpy_struct.type_recast`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.type_recast "bpy.types.bpy_struct.type_recast")<br>  <br>- [`bpy_struct.values`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.values "bpy.types.bpy_struct.values")<br>  <br>- [`ID.bl_system_properties_get`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.bl_system_properties_get "bpy.types.ID.bl_system_properties_get")<br>  <br>- [`ID.rename`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.rename "bpy.types.ID.rename")<br>  <br>- [`ID.evaluated_get`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.evaluated_get "bpy.types.ID.evaluated_get")<br>  <br>- [`ID.copy`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.copy "bpy.types.ID.copy")<br>  <br>- [`ID.asset_mark`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_mark "bpy.types.ID.asset_mark")<br>  <br>- [`ID.asset_clear`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_clear "bpy.types.ID.asset_clear")<br>  <br>- [`ID.asset_generate_preview`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_generate_preview "bpy.types.ID.asset_generate_preview")<br>  <br>- [`ID.override_create`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.override_create "bpy.types.ID.override_create")<br>  <br>- [`ID.override_hierarchy_create`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.override_hierarchy_create "bpy.types.ID.override_hierarchy_create")<br>  <br>- [`ID.user_clear`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.user_clear "bpy.types.ID.user_clear")<br>  <br>- [`ID.user_remap`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.user_remap "bpy.types.ID.user_remap")<br>  <br>- [`ID.make_local`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.make_local "bpy.types.ID.make_local")<br>  <br>- [`ID.user_of_id`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.user_of_id "bpy.types.ID.user_of_id")<br>  <br>- [`ID.animation_data_create`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.animation_data_create "bpy.types.ID.animation_data_create")<br>  <br>- [`ID.animation_data_clear`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.animation_data_clear "bpy.types.ID.animation_data_clear")<br>  <br>- [`ID.update_tag`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.update_tag "bpy.types.ID.update_tag")<br>  <br>- [`ID.preview_ensure`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.preview_ensure "bpy.types.ID.preview_ensure")<br>  <br>- [`ID.bl_rna_get_subclass`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass "bpy.types.ID.bl_rna_get_subclass")<br>  <br>- [`ID.bl_rna_get_subclass_py`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass_py "bpy.types.ID.bl_rna_get_subclass_py") |

## References [¶](https://docs.blender.org/api/current/bpy.types.Material.html\#references "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy.context.material`](https://docs.blender.org/api/current/bpy.context.html#bpy.context.material "bpy.context.material")<br>  <br>- [`BlendData.materials`](https://docs.blender.org/api/current/bpy.types.BlendData.html#bpy.types.BlendData.materials "bpy.types.BlendData.materials")<br>  <br>- [`BlendDataMaterials.create_gpencil_data`](https://docs.blender.org/api/current/bpy.types.BlendDataMaterials.html#bpy.types.BlendDataMaterials.create_gpencil_data "bpy.types.BlendDataMaterials.create_gpencil_data")<br>  <br>- [`BlendDataMaterials.new`](https://docs.blender.org/api/current/bpy.types.BlendDataMaterials.html#bpy.types.BlendDataMaterials.new "bpy.types.BlendDataMaterials.new")<br>  <br>- [`BlendDataMaterials.remove`](https://docs.blender.org/api/current/bpy.types.BlendDataMaterials.html#bpy.types.BlendDataMaterials.remove "bpy.types.BlendDataMaterials.remove")<br>  <br>- [`BlendDataMaterials.remove_gpencil_data`](https://docs.blender.org/api/current/bpy.types.BlendDataMaterials.html#bpy.types.BlendDataMaterials.remove_gpencil_data "bpy.types.BlendDataMaterials.remove_gpencil_data")<br>  <br>- [`BrushGpencilSettings.material`](https://docs.blender.org/api/current/bpy.types.BrushGpencilSettings.html#bpy.types.BrushGpencilSettings.material "bpy.types.BrushGpencilSettings.material")<br>  <br>- [`BrushGpencilSettings.material_alt`](https://docs.blender.org/api/current/bpy.types.BrushGpencilSettings.html#bpy.types.BrushGpencilSettings.material_alt "bpy.types.BrushGpencilSettings.material_alt")<br>  <br>- [`Curve.materials`](https://docs.blender.org/api/current/bpy.types.Curve.html#bpy.types.Curve.materials "bpy.types.Curve.materials")<br>  <br>- [`Curves.materials`](https://docs.blender.org/api/current/bpy.types.Curves.html#bpy.types.Curves.materials "bpy.types.Curves.materials")<br>  <br>- [`GeometryNodeInputMaterial.material`](https://docs.blender.org/api/current/bpy.types.GeometryNodeInputMaterial.html#bpy.types.GeometryNodeInputMaterial.material "bpy.types.GeometryNodeInputMaterial.material")<br>  <br>- [`GreasePencil.materials`](https://docs.blender.org/api/current/bpy.types.GreasePencil.html#bpy.types.GreasePencil.materials "bpy.types.GreasePencil.materials")<br>  <br>- [`GreasePencilArrayModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilArrayModifier.html#bpy.types.GreasePencilArrayModifier.material_filter "bpy.types.GreasePencilArrayModifier.material_filter")<br>  <br>- [`GreasePencilBuildModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilBuildModifier.html#bpy.types.GreasePencilBuildModifier.material_filter "bpy.types.GreasePencilBuildModifier.material_filter")<br>  <br>- [`GreasePencilColorModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilColorModifier.html#bpy.types.GreasePencilColorModifier.material_filter "bpy.types.GreasePencilColorModifier.material_filter")<br>  <br>- [`GreasePencilDashModifierData.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilDashModifierData.html#bpy.types.GreasePencilDashModifierData.material_filter "bpy.types.GreasePencilDashModifierData.material_filter")<br>  <br>- [`GreasePencilEnvelopeModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilEnvelopeModifier.html#bpy.types.GreasePencilEnvelopeModifier.material_filter "bpy.types.GreasePencilEnvelopeModifier.material_filter")<br>  <br>- [`GreasePencilHookModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilHookModifier.html#bpy.types.GreasePencilHookModifier.material_filter "bpy.types.GreasePencilHookModifier.material_filter")<br>  <br>- [`GreasePencilLatticeModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilLatticeModifier.html#bpy.types.GreasePencilLatticeModifier.material_filter "bpy.types.GreasePencilLatticeModifier.material_filter")<br>  <br>- [`GreasePencilLengthModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilLengthModifier.html#bpy.types.GreasePencilLengthModifier.material_filter "bpy.types.GreasePencilLengthModifier.material_filter")<br>  <br>- [`GreasePencilLineartModifier.target_material`](https://docs.blender.org/api/current/bpy.types.GreasePencilLineartModifier.html#bpy.types.GreasePencilLineartModifier.target_material "bpy.types.GreasePencilLineartModifier.target_material")<br>  <br>- [`GreasePencilMirrorModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilMirrorModifier.html#bpy.types.GreasePencilMirrorModifier.material_filter "bpy.types.GreasePencilMirrorModifier.material_filter")<br>  <br>- [`GreasePencilMultiplyModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilMultiplyModifier.html#bpy.types.GreasePencilMultiplyModifier.material_filter "bpy.types.GreasePencilMultiplyModifier.material_filter")<br>  <br>- [`GreasePencilNoiseModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilNoiseModifier.html#bpy.types.GreasePencilNoiseModifier.material_filter "bpy.types.GreasePencilNoiseModifier.material_filter") | - [`GreasePencilOffsetModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilOffsetModifier.html#bpy.types.GreasePencilOffsetModifier.material_filter "bpy.types.GreasePencilOffsetModifier.material_filter")<br>  <br>- [`GreasePencilOpacityModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilOpacityModifier.html#bpy.types.GreasePencilOpacityModifier.material_filter "bpy.types.GreasePencilOpacityModifier.material_filter")<br>  <br>- [`GreasePencilOutlineModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilOutlineModifier.html#bpy.types.GreasePencilOutlineModifier.material_filter "bpy.types.GreasePencilOutlineModifier.material_filter")<br>  <br>- [`GreasePencilOutlineModifier.outline_material`](https://docs.blender.org/api/current/bpy.types.GreasePencilOutlineModifier.html#bpy.types.GreasePencilOutlineModifier.outline_material "bpy.types.GreasePencilOutlineModifier.outline_material")<br>  <br>- [`GreasePencilShrinkwrapModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilShrinkwrapModifier.html#bpy.types.GreasePencilShrinkwrapModifier.material_filter "bpy.types.GreasePencilShrinkwrapModifier.material_filter")<br>  <br>- [`GreasePencilSimplifyModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilSimplifyModifier.html#bpy.types.GreasePencilSimplifyModifier.material_filter "bpy.types.GreasePencilSimplifyModifier.material_filter")<br>  <br>- [`GreasePencilSmoothModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilSmoothModifier.html#bpy.types.GreasePencilSmoothModifier.material_filter "bpy.types.GreasePencilSmoothModifier.material_filter")<br>  <br>- [`GreasePencilSubdivModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilSubdivModifier.html#bpy.types.GreasePencilSubdivModifier.material_filter "bpy.types.GreasePencilSubdivModifier.material_filter")<br>  <br>- [`GreasePencilTextureModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilTextureModifier.html#bpy.types.GreasePencilTextureModifier.material_filter "bpy.types.GreasePencilTextureModifier.material_filter")<br>  <br>- [`GreasePencilThickModifierData.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilThickModifierData.html#bpy.types.GreasePencilThickModifierData.material_filter "bpy.types.GreasePencilThickModifierData.material_filter")<br>  <br>- [`GreasePencilTintModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilTintModifier.html#bpy.types.GreasePencilTintModifier.material_filter "bpy.types.GreasePencilTintModifier.material_filter")<br>  <br>- [`GreasePencilWeightAngleModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilWeightAngleModifier.html#bpy.types.GreasePencilWeightAngleModifier.material_filter "bpy.types.GreasePencilWeightAngleModifier.material_filter")<br>  <br>- [`GreasePencilWeightProximityModifier.material_filter`](https://docs.blender.org/api/current/bpy.types.GreasePencilWeightProximityModifier.html#bpy.types.GreasePencilWeightProximityModifier.material_filter "bpy.types.GreasePencilWeightProximityModifier.material_filter")<br>  <br>- [`IDMaterials.append`](https://docs.blender.org/api/current/bpy.types.IDMaterials.html#bpy.types.IDMaterials.append "bpy.types.IDMaterials.append")<br>  <br>- [`IDMaterials.pop`](https://docs.blender.org/api/current/bpy.types.IDMaterials.html#bpy.types.IDMaterials.pop "bpy.types.IDMaterials.pop")<br>  <br>- [`MaterialSlot.material`](https://docs.blender.org/api/current/bpy.types.MaterialSlot.html#bpy.types.MaterialSlot.material "bpy.types.MaterialSlot.material")<br>  <br>- [`Mesh.materials`](https://docs.blender.org/api/current/bpy.types.Mesh.html#bpy.types.Mesh.materials "bpy.types.Mesh.materials")<br>  <br>- [`MetaBall.materials`](https://docs.blender.org/api/current/bpy.types.MetaBall.html#bpy.types.MetaBall.materials "bpy.types.MetaBall.materials")<br>  <br>- [`NodeSocketMaterial.default_value`](https://docs.blender.org/api/current/bpy.types.NodeSocketMaterial.html#bpy.types.NodeSocketMaterial.default_value "bpy.types.NodeSocketMaterial.default_value")<br>  <br>- [`NodeTreeInterfaceSocketMaterial.default_value`](https://docs.blender.org/api/current/bpy.types.NodeTreeInterfaceSocketMaterial.html#bpy.types.NodeTreeInterfaceSocketMaterial.default_value "bpy.types.NodeTreeInterfaceSocketMaterial.default_value")<br>  <br>- [`Object.active_material`](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object.active_material "bpy.types.Object.active_material")<br>  <br>- [`PointCloud.materials`](https://docs.blender.org/api/current/bpy.types.PointCloud.html#bpy.types.PointCloud.materials "bpy.types.PointCloud.materials")<br>  <br>- [`ViewLayer.material_override`](https://docs.blender.org/api/current/bpy.types.ViewLayer.html#bpy.types.ViewLayer.material_override "bpy.types.ViewLayer.material_override")<br>  <br>- [`Volume.materials`](https://docs.blender.org/api/current/bpy.types.Volume.html#bpy.types.Volume.materials "bpy.types.Volume.materials") |