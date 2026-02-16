- [Home](https://docs.blender.org/api/4.0/index.html)
- [Types (bpy.types)](https://docs.blender.org/api/4.0/bpy.types.html)
- PointLight(Light)

* * *

# PointLight(Light) [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html\#pointlight-light "Permalink to this heading")

base classes — [`bpy_struct`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID "bpy.types.ID"), [`Light`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light "bpy.types.Light")

_class_ bpy.types.PointLight( _Light_) [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight "Permalink to this definition")

Omnidirectional point Light

contact\_shadow\_bias [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.contact_shadow_bias "Permalink to this definition")

Bias to avoid self shadowing

Type:

float in \[0.001, 9999\], default 0.03

contact\_shadow\_distance [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.contact_shadow_distance "Permalink to this definition")

World space distance in which to search for screen space occluder

Type:

float in \[0, 9999\], default 0.2

contact\_shadow\_thickness [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.contact_shadow_thickness "Permalink to this definition")

Pixel thickness used to detect occlusion

Type:

float in \[0, 9999\], default 0.2

energy [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.energy "Permalink to this definition")

Light energy emitted over the entire area of the light in all directions

Type:

float in \[-inf, inf\], default 10.0

shadow\_buffer\_bias [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.shadow_buffer_bias "Permalink to this definition")

Bias for reducing self shadowing

Type:

float in \[0, inf\], default 1.0

shadow\_buffer\_clip\_start [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.shadow_buffer_clip_start "Permalink to this definition")

Shadow map clip start, below which objects will not generate shadows

Type:

float in \[1e-06, inf\], default 0.05

shadow\_color [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.shadow_color "Permalink to this definition")

Color of shadows cast by the light

Type:

[`mathutils.Color`](https://docs.blender.org/api/4.0/mathutils.html#mathutils.Color "mathutils.Color") of 3 items in \[0, inf\], default (0.0, 0.0, 0.0)

shadow\_soft\_size [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.shadow_soft_size "Permalink to this definition")

Light size for ray shadow sampling (Raytraced shadows)

Type:

float in \[0, inf\], default 0.0

shadow\_softness\_factor [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.shadow_softness_factor "Permalink to this definition")

Scale light shape for smaller penumbra

Type:

float in \[0, 1\], default 1.0

use\_contact\_shadow [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.use_contact_shadow "Permalink to this definition")

Use screen space ray-tracing to have correct shadowing near occluder, or for small features that does not appear in shadow maps

Type:

boolean, default False

use\_shadow [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.use_shadow "Permalink to this definition")Type:

boolean, default True

_classmethod_ bl\_rna\_get\_subclass( _id_, _default=None_) [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.bl_rna_get_subclass "Permalink to this definition")Parameters:

**id** ( _string_) – The RNA type identifier.

Returns:

The RNA type or default when not found.

Return type:

[`bpy.types.Struct`](https://docs.blender.org/api/4.0/bpy.types.Struct.html#bpy.types.Struct "bpy.types.Struct") subclass

_classmethod_ bl\_rna\_get\_subclass\_py( _id_, _default=None_) [](https://docs.blender.org/api/4.0/bpy.types.PointLight.html#bpy.types.PointLight.bl_rna_get_subclass_py "Permalink to this definition")Parameters:

**id** ( _string_) – The RNA type identifier.

Returns:

The class or default when not found.

Return type:

type

Inherited Properties

|     |     |
| --- | --- |
| - [`bpy_struct.id_data`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data "bpy.types.bpy_struct.id_data")<br>  <br>- [`ID.name`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.name "bpy.types.ID.name")<br>  <br>- [`ID.name_full`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.name_full "bpy.types.ID.name_full")<br>  <br>- [`ID.is_evaluated`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.is_evaluated "bpy.types.ID.is_evaluated")<br>  <br>- [`ID.original`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.original "bpy.types.ID.original")<br>  <br>- [`ID.users`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.users "bpy.types.ID.users")<br>  <br>- [`ID.use_fake_user`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.use_fake_user "bpy.types.ID.use_fake_user")<br>  <br>- [`ID.use_extra_user`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.use_extra_user "bpy.types.ID.use_extra_user")<br>  <br>- [`ID.is_embedded_data`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.is_embedded_data "bpy.types.ID.is_embedded_data")<br>  <br>- [`ID.is_missing`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.is_missing "bpy.types.ID.is_missing")<br>  <br>- [`ID.is_runtime_data`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.is_runtime_data "bpy.types.ID.is_runtime_data")<br>  <br>- [`ID.tag`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.tag "bpy.types.ID.tag")<br>  <br>- [`ID.is_library_indirect`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.is_library_indirect "bpy.types.ID.is_library_indirect")<br>  <br>- [`ID.library`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.library "bpy.types.ID.library")<br>  <br>- [`ID.library_weak_reference`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.library_weak_reference "bpy.types.ID.library_weak_reference") | - [`ID.asset_data`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.asset_data "bpy.types.ID.asset_data")<br>  <br>- [`ID.override_library`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.override_library "bpy.types.ID.override_library")<br>  <br>- [`ID.preview`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.preview "bpy.types.ID.preview")<br>  <br>- [`Light.type`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.type "bpy.types.Light.type")<br>  <br>- [`Light.color`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.color "bpy.types.Light.color")<br>  <br>- [`Light.specular_factor`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.specular_factor "bpy.types.Light.specular_factor")<br>  <br>- [`Light.diffuse_factor`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.diffuse_factor "bpy.types.Light.diffuse_factor")<br>  <br>- [`Light.volume_factor`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.volume_factor "bpy.types.Light.volume_factor")<br>  <br>- [`Light.use_custom_distance`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.use_custom_distance "bpy.types.Light.use_custom_distance")<br>  <br>- [`Light.cutoff_distance`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.cutoff_distance "bpy.types.Light.cutoff_distance")<br>  <br>- [`Light.node_tree`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.node_tree "bpy.types.Light.node_tree")<br>  <br>- [`Light.use_nodes`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.use_nodes "bpy.types.Light.use_nodes")<br>  <br>- [`Light.animation_data`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.animation_data "bpy.types.Light.animation_data")<br>  <br>- [`Light.cycles`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.cycles "bpy.types.Light.cycles") |

Inherited Functions

|     |     |
| --- | --- |
| - [`bpy_struct.as_pointer`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.as_pointer "bpy.types.bpy_struct.as_pointer")<br>  <br>- [`bpy_struct.driver_add`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_add "bpy.types.bpy_struct.driver_add")<br>  <br>- [`bpy_struct.driver_remove`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_remove "bpy.types.bpy_struct.driver_remove")<br>  <br>- [`bpy_struct.get`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.get "bpy.types.bpy_struct.get")<br>  <br>- [`bpy_struct.id_properties_clear`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_clear "bpy.types.bpy_struct.id_properties_clear")<br>  <br>- [`bpy_struct.id_properties_ensure`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ensure "bpy.types.bpy_struct.id_properties_ensure")<br>  <br>- [`bpy_struct.id_properties_ui`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ui "bpy.types.bpy_struct.id_properties_ui")<br>  <br>- [`bpy_struct.is_property_hidden`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_hidden "bpy.types.bpy_struct.is_property_hidden")<br>  <br>- [`bpy_struct.is_property_overridable_library`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_overridable_library "bpy.types.bpy_struct.is_property_overridable_library")<br>  <br>- [`bpy_struct.is_property_readonly`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_readonly "bpy.types.bpy_struct.is_property_readonly")<br>  <br>- [`bpy_struct.is_property_set`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_set "bpy.types.bpy_struct.is_property_set")<br>  <br>- [`bpy_struct.items`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.items "bpy.types.bpy_struct.items")<br>  <br>- [`bpy_struct.keyframe_delete`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_delete "bpy.types.bpy_struct.keyframe_delete")<br>  <br>- [`bpy_struct.keyframe_insert`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert "bpy.types.bpy_struct.keyframe_insert")<br>  <br>- [`bpy_struct.keys`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keys "bpy.types.bpy_struct.keys")<br>  <br>- [`bpy_struct.path_from_id`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_id "bpy.types.bpy_struct.path_from_id")<br>  <br>- [`bpy_struct.path_resolve`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_resolve "bpy.types.bpy_struct.path_resolve")<br>  <br>- [`bpy_struct.pop`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.pop "bpy.types.bpy_struct.pop")<br>  <br>- [`bpy_struct.property_overridable_library_set`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_overridable_library_set "bpy.types.bpy_struct.property_overridable_library_set")<br>  <br>- [`bpy_struct.property_unset`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_unset "bpy.types.bpy_struct.property_unset")<br>  <br>- [`bpy_struct.type_recast`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.type_recast "bpy.types.bpy_struct.type_recast") | - [`bpy_struct.values`](https://docs.blender.org/api/4.0/bpy.types.bpy_struct.html#bpy.types.bpy_struct.values "bpy.types.bpy_struct.values")<br>  <br>- [`ID.evaluated_get`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.evaluated_get "bpy.types.ID.evaluated_get")<br>  <br>- [`ID.copy`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.copy "bpy.types.ID.copy")<br>  <br>- [`ID.asset_mark`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.asset_mark "bpy.types.ID.asset_mark")<br>  <br>- [`ID.asset_clear`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.asset_clear "bpy.types.ID.asset_clear")<br>  <br>- [`ID.asset_generate_preview`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.asset_generate_preview "bpy.types.ID.asset_generate_preview")<br>  <br>- [`ID.override_create`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.override_create "bpy.types.ID.override_create")<br>  <br>- [`ID.override_hierarchy_create`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.override_hierarchy_create "bpy.types.ID.override_hierarchy_create")<br>  <br>- [`ID.override_template_create`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.override_template_create "bpy.types.ID.override_template_create")<br>  <br>- [`ID.user_clear`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.user_clear "bpy.types.ID.user_clear")<br>  <br>- [`ID.user_remap`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.user_remap "bpy.types.ID.user_remap")<br>  <br>- [`ID.make_local`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.make_local "bpy.types.ID.make_local")<br>  <br>- [`ID.user_of_id`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.user_of_id "bpy.types.ID.user_of_id")<br>  <br>- [`ID.animation_data_create`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.animation_data_create "bpy.types.ID.animation_data_create")<br>  <br>- [`ID.animation_data_clear`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.animation_data_clear "bpy.types.ID.animation_data_clear")<br>  <br>- [`ID.update_tag`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.update_tag "bpy.types.ID.update_tag")<br>  <br>- [`ID.preview_ensure`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.preview_ensure "bpy.types.ID.preview_ensure")<br>  <br>- [`ID.bl_rna_get_subclass`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass "bpy.types.ID.bl_rna_get_subclass")<br>  <br>- [`ID.bl_rna_get_subclass_py`](https://docs.blender.org/api/4.0/bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass_py "bpy.types.ID.bl_rna_get_subclass_py")<br>  <br>- [`Light.bl_rna_get_subclass`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.bl_rna_get_subclass "bpy.types.Light.bl_rna_get_subclass")<br>  <br>- [`Light.bl_rna_get_subclass_py`](https://docs.blender.org/api/4.0/bpy.types.Light.html#bpy.types.Light.bl_rna_get_subclass_py "bpy.types.Light.bl_rna_get_subclass_py") |

- 4.0







Versions



  - Loading...