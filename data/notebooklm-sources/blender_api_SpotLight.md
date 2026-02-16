ContentsMenuExpandLight modeDark modeAuto light/dark, in light modeAuto light/dark, in dark mode[Skip to content](https://docs.blender.org/api/current/bpy.types.SpotLight.html#furo-main-content)

[Back to top](https://docs.blender.org/api/current/bpy.types.SpotLight.html#)

Toggle Light / Dark / Auto color theme

Toggle table of contents sidebar

# SpotLight(Light) [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html\#spotlight-light "Link to this heading")

base classes — [`bpy_struct`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID "bpy.types.ID"), [`Light`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light "bpy.types.Light")

_class_ bpy.types.SpotLight( _Light_) [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight "Link to this definition")

Directional cone Light

energy [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.energy "Link to this definition")

The energy this light would emit over its entire area if it wasn’t limited by the spot angle, in units of radiant power (W)

Type:

float in \[-inf, inf\], default 10.0

shadow\_buffer\_clip\_start [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.shadow_buffer_clip_start "Link to this definition")

Shadow map clip start, below which objects will not generate shadows

Type:

float in \[1e-06, inf\], default 0.05

shadow\_filter\_radius [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.shadow_filter_radius "Link to this definition")

Blur shadow aliasing using Percentage Closer Filtering

Type:

float in \[0, inf\], default 1.0

shadow\_jitter\_overblur [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.shadow_jitter_overblur "Link to this definition")

Apply shadow tracing to each jittered sample to reduce under-sampling artifacts

Type:

float in \[0, 100\], default 10.0

shadow\_maximum\_resolution [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.shadow_maximum_resolution "Link to this definition")

Minimum size of a shadow map pixel. Higher values use less memory at the cost of shadow quality.

Type:

float in \[0, inf\], default 0.001

shadow\_soft\_size [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.shadow_soft_size "Link to this definition")

Light size for ray shadow sampling (Raytraced shadows)

Type:

float in \[0, inf\], default 0.0

show\_cone [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.show_cone "Link to this definition")

Display transparent cone in 3D view to visualize which objects are contained in it

Type:

boolean, default False

spot\_blend [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.spot_blend "Link to this definition")

The softness of the spotlight edge

Type:

float in \[0, 1\], default 0.15

spot\_size [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.spot_size "Link to this definition")

Angular diameter of the spotlight beam

Type:

float in \[0.0174533, 3.14159\], default 0.785398

use\_absolute\_resolution [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.use_absolute_resolution "Link to this definition")

Limit the resolution at 1 unit from the light origin instead of relative to the shadowed pixel

Type:

boolean, default False

use\_shadow\_jitter [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.use_shadow_jitter "Link to this definition")

Enable jittered soft shadows to increase shadow precision (disabled in viewport unless enabled in the render settings). Has a high performance impact.

Type:

boolean, default False

use\_soft\_falloff [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.use_soft_falloff "Link to this definition")

Apply falloff to avoid sharp edges when the light geometry intersects with other objects

Type:

boolean, default True

use\_square [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.use_square "Link to this definition")

Cast a square spot light shape

Type:

boolean, default False

inline\_shader\_nodes() [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.inline_shader_nodes "Link to this definition")

Get the inlined shader nodes of this light. This preprocesses the node tree
to remove nested groups, repeat zones and more.

Returns:

The inlined shader nodes.

Return type:

[`bpy.types.InlineShaderNodes`](https://docs.blender.org/api/current/bpy.types.InlineShaderNodes.html#bpy.types.InlineShaderNodes "bpy.types.InlineShaderNodes")

_classmethod_ bl\_rna\_get\_subclass( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.bl_rna_get_subclass "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The RNA type or default when not found.

Return type:

[`bpy.types.Struct`](https://docs.blender.org/api/current/bpy.types.Struct.html#bpy.types.Struct "bpy.types.Struct") subclass

_classmethod_ bl\_rna\_get\_subclass\_py( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html#bpy.types.SpotLight.bl_rna_get_subclass_py "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The class or default when not found.

Return type:

type

## Inherited Properties [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html\#inherited-properties "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.id_data`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data "bpy.types.bpy_struct.id_data")<br>  <br>- [`ID.name`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.name "bpy.types.ID.name")<br>  <br>- [`ID.name_full`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.name_full "bpy.types.ID.name_full")<br>  <br>- [`ID.id_type`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.id_type "bpy.types.ID.id_type")<br>  <br>- [`ID.session_uid`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.session_uid "bpy.types.ID.session_uid")<br>  <br>- [`ID.is_evaluated`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_evaluated "bpy.types.ID.is_evaluated")<br>  <br>- [`ID.original`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.original "bpy.types.ID.original")<br>  <br>- [`ID.users`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.users "bpy.types.ID.users")<br>  <br>- [`ID.use_fake_user`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.use_fake_user "bpy.types.ID.use_fake_user")<br>  <br>- [`ID.use_extra_user`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.use_extra_user "bpy.types.ID.use_extra_user")<br>  <br>- [`ID.is_embedded_data`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_embedded_data "bpy.types.ID.is_embedded_data")<br>  <br>- [`ID.is_linked_packed`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_linked_packed "bpy.types.ID.is_linked_packed")<br>  <br>- [`ID.is_missing`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_missing "bpy.types.ID.is_missing")<br>  <br>- [`ID.is_runtime_data`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_runtime_data "bpy.types.ID.is_runtime_data")<br>  <br>- [`ID.is_editable`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_editable "bpy.types.ID.is_editable")<br>  <br>- [`ID.tag`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.tag "bpy.types.ID.tag")<br>  <br>- [`ID.is_library_indirect`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_library_indirect "bpy.types.ID.is_library_indirect")<br>  <br>- [`ID.library`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.library "bpy.types.ID.library")<br>  <br>- [`ID.library_weak_reference`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.library_weak_reference "bpy.types.ID.library_weak_reference")<br>  <br>- [`ID.asset_data`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_data "bpy.types.ID.asset_data") | - [`ID.override_library`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.override_library "bpy.types.ID.override_library")<br>  <br>- [`ID.preview`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.preview "bpy.types.ID.preview")<br>  <br>- [`Light.type`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.type "bpy.types.Light.type")<br>  <br>- [`Light.use_temperature`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.use_temperature "bpy.types.Light.use_temperature")<br>  <br>- [`Light.color`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.color "bpy.types.Light.color")<br>  <br>- [`Light.temperature`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.temperature "bpy.types.Light.temperature")<br>  <br>- [`Light.temperature_color`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.temperature_color "bpy.types.Light.temperature_color")<br>  <br>- [`Light.specular_factor`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.specular_factor "bpy.types.Light.specular_factor")<br>  <br>- [`Light.diffuse_factor`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.diffuse_factor "bpy.types.Light.diffuse_factor")<br>  <br>- [`Light.transmission_factor`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.transmission_factor "bpy.types.Light.transmission_factor")<br>  <br>- [`Light.volume_factor`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.volume_factor "bpy.types.Light.volume_factor")<br>  <br>- [`Light.use_custom_distance`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.use_custom_distance "bpy.types.Light.use_custom_distance")<br>  <br>- [`Light.cutoff_distance`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.cutoff_distance "bpy.types.Light.cutoff_distance")<br>  <br>- [`Light.use_shadow`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.use_shadow "bpy.types.Light.use_shadow")<br>  <br>- [`Light.exposure`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.exposure "bpy.types.Light.exposure")<br>  <br>- [`Light.normalize`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.normalize "bpy.types.Light.normalize")<br>  <br>- [`Light.node_tree`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.node_tree "bpy.types.Light.node_tree")<br>  <br>- [`Light.use_nodes`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.use_nodes "bpy.types.Light.use_nodes")<br>  <br>- [`Light.animation_data`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.animation_data "bpy.types.Light.animation_data")<br>  <br>- [`Light.cycles`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.cycles "bpy.types.Light.cycles") |

## Inherited Functions [¶](https://docs.blender.org/api/current/bpy.types.SpotLight.html\#inherited-functions "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.as_pointer`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.as_pointer "bpy.types.bpy_struct.as_pointer")<br>  <br>- [`bpy_struct.driver_add`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_add "bpy.types.bpy_struct.driver_add")<br>  <br>- [`bpy_struct.driver_remove`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_remove "bpy.types.bpy_struct.driver_remove")<br>  <br>- [`bpy_struct.get`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.get "bpy.types.bpy_struct.get")<br>  <br>- [`bpy_struct.id_properties_clear`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_clear "bpy.types.bpy_struct.id_properties_clear")<br>  <br>- [`bpy_struct.id_properties_ensure`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ensure "bpy.types.bpy_struct.id_properties_ensure")<br>  <br>- [`bpy_struct.id_properties_ui`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ui "bpy.types.bpy_struct.id_properties_ui")<br>  <br>- [`bpy_struct.is_property_hidden`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_hidden "bpy.types.bpy_struct.is_property_hidden")<br>  <br>- [`bpy_struct.is_property_overridable_library`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_overridable_library "bpy.types.bpy_struct.is_property_overridable_library")<br>  <br>- [`bpy_struct.is_property_readonly`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_readonly "bpy.types.bpy_struct.is_property_readonly")<br>  <br>- [`bpy_struct.is_property_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_set "bpy.types.bpy_struct.is_property_set")<br>  <br>- [`bpy_struct.items`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.items "bpy.types.bpy_struct.items")<br>  <br>- [`bpy_struct.keyframe_delete`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_delete "bpy.types.bpy_struct.keyframe_delete")<br>  <br>- [`bpy_struct.keyframe_insert`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert "bpy.types.bpy_struct.keyframe_insert")<br>  <br>- [`bpy_struct.keys`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keys "bpy.types.bpy_struct.keys")<br>  <br>- [`bpy_struct.path_from_id`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_id "bpy.types.bpy_struct.path_from_id")<br>  <br>- [`bpy_struct.path_from_module`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_module "bpy.types.bpy_struct.path_from_module")<br>  <br>- [`bpy_struct.path_resolve`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_resolve "bpy.types.bpy_struct.path_resolve")<br>  <br>- [`bpy_struct.pop`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.pop "bpy.types.bpy_struct.pop")<br>  <br>- [`bpy_struct.property_overridable_library_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_overridable_library_set "bpy.types.bpy_struct.property_overridable_library_set")<br>  <br>- [`bpy_struct.property_unset`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_unset "bpy.types.bpy_struct.property_unset")<br>  <br>- [`bpy_struct.rna_ancestors`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.rna_ancestors "bpy.types.bpy_struct.rna_ancestors")<br>  <br>- [`bpy_struct.type_recast`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.type_recast "bpy.types.bpy_struct.type_recast")<br>  <br>- [`bpy_struct.values`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.values "bpy.types.bpy_struct.values") | - [`ID.bl_system_properties_get`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.bl_system_properties_get "bpy.types.ID.bl_system_properties_get")<br>  <br>- [`ID.rename`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.rename "bpy.types.ID.rename")<br>  <br>- [`ID.evaluated_get`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.evaluated_get "bpy.types.ID.evaluated_get")<br>  <br>- [`ID.copy`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.copy "bpy.types.ID.copy")<br>  <br>- [`ID.asset_mark`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_mark "bpy.types.ID.asset_mark")<br>  <br>- [`ID.asset_clear`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_clear "bpy.types.ID.asset_clear")<br>  <br>- [`ID.asset_generate_preview`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_generate_preview "bpy.types.ID.asset_generate_preview")<br>  <br>- [`ID.override_create`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.override_create "bpy.types.ID.override_create")<br>  <br>- [`ID.override_hierarchy_create`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.override_hierarchy_create "bpy.types.ID.override_hierarchy_create")<br>  <br>- [`ID.user_clear`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.user_clear "bpy.types.ID.user_clear")<br>  <br>- [`ID.user_remap`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.user_remap "bpy.types.ID.user_remap")<br>  <br>- [`ID.make_local`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.make_local "bpy.types.ID.make_local")<br>  <br>- [`ID.user_of_id`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.user_of_id "bpy.types.ID.user_of_id")<br>  <br>- [`ID.animation_data_create`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.animation_data_create "bpy.types.ID.animation_data_create")<br>  <br>- [`ID.animation_data_clear`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.animation_data_clear "bpy.types.ID.animation_data_clear")<br>  <br>- [`ID.update_tag`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.update_tag "bpy.types.ID.update_tag")<br>  <br>- [`ID.preview_ensure`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.preview_ensure "bpy.types.ID.preview_ensure")<br>  <br>- [`ID.bl_rna_get_subclass`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass "bpy.types.ID.bl_rna_get_subclass")<br>  <br>- [`ID.bl_rna_get_subclass_py`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass_py "bpy.types.ID.bl_rna_get_subclass_py")<br>  <br>- [`Light.area`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.area "bpy.types.Light.area")<br>  <br>- [`Light.inline_shader_nodes`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.inline_shader_nodes "bpy.types.Light.inline_shader_nodes")<br>  <br>- [`Light.bl_rna_get_subclass`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.bl_rna_get_subclass "bpy.types.Light.bl_rna_get_subclass")<br>  <br>- [`Light.bl_rna_get_subclass_py`](https://docs.blender.org/api/current/bpy.types.Light.html#bpy.types.Light.bl_rna_get_subclass_py "bpy.types.Light.bl_rna_get_subclass_py") |