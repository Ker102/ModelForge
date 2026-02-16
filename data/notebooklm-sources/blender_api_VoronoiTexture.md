ContentsMenuExpandLight modeDark modeAuto light/dark, in light modeAuto light/dark, in dark mode[Skip to content](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#furo-main-content)

[Back to top](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#)

Toggle Light / Dark / Auto color theme

Toggle table of contents sidebar

# VoronoiTexture(Texture) [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html\#voronoitexture-texture "Link to this heading")

base classes — [`bpy_struct`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID "bpy.types.ID"), [`Texture`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture "bpy.types.Texture")

_class_ bpy.types.VoronoiTexture( _Texture_) [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture "Link to this definition")

Procedural voronoi texture

color\_mode [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.color_mode "Link to this definition")

- `INTENSITY`
Intensity – Only calculate intensity.

- `POSITION`
Position – Color cells by position.

- `POSITION_OUTLINE`
Position and Outline – Use position plus an outline based on F2-F1.

- `POSITION_OUTLINE_INTENSITY`
Position, Outline, and Intensity – Multiply position and outline by intensity.


Type:

enum in \[`'INTENSITY'`, `'POSITION'`, `'POSITION_OUTLINE'`, `'POSITION_OUTLINE_INTENSITY'`\], default `'INTENSITY'`

distance\_metric [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.distance_metric "Link to this definition")

Algorithm used to calculate distance of sample points to feature points

- `DISTANCE`
Actual Distance – sqrt(x\*x+y\*y+z\*z).

- `DISTANCE_SQUARED`
Distance Squared – (x\*x+y\*y+z\*z).

- `MANHATTAN`
Manhattan – The length of the distance in axial directions.

- `CHEBYCHEV`
Chebychev – The length of the longest Axial journey.

- `MINKOVSKY_HALF`
Minkowski 1/2 – Set Minkowski variable to 0.5.

- `MINKOVSKY_FOUR`
Minkowski 4 – Set Minkowski variable to 4.

- `MINKOVSKY`
Minkowski – Use the Minkowski function to calculate distance (exponent value determines the shape of the boundaries).


Type:

enum in \[`'DISTANCE'`, `'DISTANCE_SQUARED'`, `'MANHATTAN'`, `'CHEBYCHEV'`, `'MINKOVSKY_HALF'`, `'MINKOVSKY_FOUR'`, `'MINKOVSKY'`\], default `'DISTANCE'`

minkovsky\_exponent [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.minkovsky_exponent "Link to this definition")

Minkowski exponent

Type:

float in \[0.01, 10\], default 2.5

nabla [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.nabla "Link to this definition")

Size of derivative offset used for calculating normal

Type:

float in \[0.001, 0.1\], default 0.025

noise\_intensity [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.noise_intensity "Link to this definition")

Scales the intensity of the noise

Type:

float in \[0.01, 10\], default 1.0

noise\_scale [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.noise_scale "Link to this definition")

Scaling for noise input

Type:

float in \[0.0001, inf\], default 0.25

weight\_1 [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.weight_1 "Link to this definition")

Voronoi feature weight 1

Type:

float in \[-2, 2\], default 1.0

weight\_2 [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.weight_2 "Link to this definition")

Voronoi feature weight 2

Type:

float in \[-2, 2\], default 0.0

weight\_3 [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.weight_3 "Link to this definition")

Voronoi feature weight 3

Type:

float in \[-2, 2\], default 0.0

weight\_4 [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.weight_4 "Link to this definition")

Voronoi feature weight 4

Type:

float in \[-2, 2\], default 0.0

users\_material [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.users_material "Link to this definition")

Materials that use this texture

Type:

tuple of [`Material`](https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material "bpy.types.Material")

Note

Takes `O(len(bpy.data.materials) * len(material.texture_slots))` time.

(readonly)

users\_object\_modifier [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.users_object_modifier "Link to this definition")

Object modifiers that use this texture

Type:

tuple of [`Object`](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object "bpy.types.Object")

Note

Takes `O(len(bpy.data.objects) * len(obj.modifiers))` time.

(readonly)

_classmethod_ bl\_rna\_get\_subclass( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.bl_rna_get_subclass "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The RNA type or default when not found.

Return type:

[`bpy.types.Struct`](https://docs.blender.org/api/current/bpy.types.Struct.html#bpy.types.Struct "bpy.types.Struct") subclass

_classmethod_ bl\_rna\_get\_subclass\_py( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html#bpy.types.VoronoiTexture.bl_rna_get_subclass_py "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The class or default when not found.

Return type:

type

## Inherited Properties [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html\#inherited-properties "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.id_data`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data "bpy.types.bpy_struct.id_data")<br>  <br>- [`ID.name`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.name "bpy.types.ID.name")<br>  <br>- [`ID.name_full`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.name_full "bpy.types.ID.name_full")<br>  <br>- [`ID.id_type`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.id_type "bpy.types.ID.id_type")<br>  <br>- [`ID.session_uid`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.session_uid "bpy.types.ID.session_uid")<br>  <br>- [`ID.is_evaluated`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_evaluated "bpy.types.ID.is_evaluated")<br>  <br>- [`ID.original`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.original "bpy.types.ID.original")<br>  <br>- [`ID.users`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.users "bpy.types.ID.users")<br>  <br>- [`ID.use_fake_user`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.use_fake_user "bpy.types.ID.use_fake_user")<br>  <br>- [`ID.use_extra_user`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.use_extra_user "bpy.types.ID.use_extra_user")<br>  <br>- [`ID.is_embedded_data`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_embedded_data "bpy.types.ID.is_embedded_data")<br>  <br>- [`ID.is_linked_packed`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_linked_packed "bpy.types.ID.is_linked_packed")<br>  <br>- [`ID.is_missing`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_missing "bpy.types.ID.is_missing")<br>  <br>- [`ID.is_runtime_data`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_runtime_data "bpy.types.ID.is_runtime_data")<br>  <br>- [`ID.is_editable`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_editable "bpy.types.ID.is_editable")<br>  <br>- [`ID.tag`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.tag "bpy.types.ID.tag")<br>  <br>- [`ID.is_library_indirect`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.is_library_indirect "bpy.types.ID.is_library_indirect")<br>  <br>- [`ID.library`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.library "bpy.types.ID.library")<br>  <br>- [`ID.library_weak_reference`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.library_weak_reference "bpy.types.ID.library_weak_reference") | - [`ID.asset_data`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_data "bpy.types.ID.asset_data")<br>  <br>- [`ID.override_library`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.override_library "bpy.types.ID.override_library")<br>  <br>- [`ID.preview`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.preview "bpy.types.ID.preview")<br>  <br>- [`Texture.type`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.type "bpy.types.Texture.type")<br>  <br>- [`Texture.use_clamp`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.use_clamp "bpy.types.Texture.use_clamp")<br>  <br>- [`Texture.use_color_ramp`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.use_color_ramp "bpy.types.Texture.use_color_ramp")<br>  <br>- [`Texture.color_ramp`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.color_ramp "bpy.types.Texture.color_ramp")<br>  <br>- [`Texture.intensity`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.intensity "bpy.types.Texture.intensity")<br>  <br>- [`Texture.contrast`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.contrast "bpy.types.Texture.contrast")<br>  <br>- [`Texture.saturation`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.saturation "bpy.types.Texture.saturation")<br>  <br>- [`Texture.factor_red`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.factor_red "bpy.types.Texture.factor_red")<br>  <br>- [`Texture.factor_green`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.factor_green "bpy.types.Texture.factor_green")<br>  <br>- [`Texture.factor_blue`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.factor_blue "bpy.types.Texture.factor_blue")<br>  <br>- [`Texture.use_preview_alpha`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.use_preview_alpha "bpy.types.Texture.use_preview_alpha")<br>  <br>- [`Texture.use_nodes`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.use_nodes "bpy.types.Texture.use_nodes")<br>  <br>- [`Texture.node_tree`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.node_tree "bpy.types.Texture.node_tree")<br>  <br>- [`Texture.animation_data`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.animation_data "bpy.types.Texture.animation_data")<br>  <br>- [`Texture.users_material`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.users_material "bpy.types.Texture.users_material")<br>  <br>- [`Texture.users_object_modifier`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.users_object_modifier "bpy.types.Texture.users_object_modifier") |

## Inherited Functions [¶](https://docs.blender.org/api/current/bpy.types.VoronoiTexture.html\#inherited-functions "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.as_pointer`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.as_pointer "bpy.types.bpy_struct.as_pointer")<br>  <br>- [`bpy_struct.driver_add`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_add "bpy.types.bpy_struct.driver_add")<br>  <br>- [`bpy_struct.driver_remove`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_remove "bpy.types.bpy_struct.driver_remove")<br>  <br>- [`bpy_struct.get`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.get "bpy.types.bpy_struct.get")<br>  <br>- [`bpy_struct.id_properties_clear`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_clear "bpy.types.bpy_struct.id_properties_clear")<br>  <br>- [`bpy_struct.id_properties_ensure`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ensure "bpy.types.bpy_struct.id_properties_ensure")<br>  <br>- [`bpy_struct.id_properties_ui`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ui "bpy.types.bpy_struct.id_properties_ui")<br>  <br>- [`bpy_struct.is_property_hidden`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_hidden "bpy.types.bpy_struct.is_property_hidden")<br>  <br>- [`bpy_struct.is_property_overridable_library`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_overridable_library "bpy.types.bpy_struct.is_property_overridable_library")<br>  <br>- [`bpy_struct.is_property_readonly`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_readonly "bpy.types.bpy_struct.is_property_readonly")<br>  <br>- [`bpy_struct.is_property_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_set "bpy.types.bpy_struct.is_property_set")<br>  <br>- [`bpy_struct.items`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.items "bpy.types.bpy_struct.items")<br>  <br>- [`bpy_struct.keyframe_delete`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_delete "bpy.types.bpy_struct.keyframe_delete")<br>  <br>- [`bpy_struct.keyframe_insert`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert "bpy.types.bpy_struct.keyframe_insert")<br>  <br>- [`bpy_struct.keys`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keys "bpy.types.bpy_struct.keys")<br>  <br>- [`bpy_struct.path_from_id`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_id "bpy.types.bpy_struct.path_from_id")<br>  <br>- [`bpy_struct.path_from_module`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_module "bpy.types.bpy_struct.path_from_module")<br>  <br>- [`bpy_struct.path_resolve`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_resolve "bpy.types.bpy_struct.path_resolve")<br>  <br>- [`bpy_struct.pop`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.pop "bpy.types.bpy_struct.pop")<br>  <br>- [`bpy_struct.property_overridable_library_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_overridable_library_set "bpy.types.bpy_struct.property_overridable_library_set")<br>  <br>- [`bpy_struct.property_unset`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_unset "bpy.types.bpy_struct.property_unset")<br>  <br>- [`bpy_struct.rna_ancestors`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.rna_ancestors "bpy.types.bpy_struct.rna_ancestors")<br>  <br>- [`bpy_struct.type_recast`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.type_recast "bpy.types.bpy_struct.type_recast") | - [`bpy_struct.values`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.values "bpy.types.bpy_struct.values")<br>  <br>- [`ID.bl_system_properties_get`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.bl_system_properties_get "bpy.types.ID.bl_system_properties_get")<br>  <br>- [`ID.rename`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.rename "bpy.types.ID.rename")<br>  <br>- [`ID.evaluated_get`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.evaluated_get "bpy.types.ID.evaluated_get")<br>  <br>- [`ID.copy`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.copy "bpy.types.ID.copy")<br>  <br>- [`ID.asset_mark`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_mark "bpy.types.ID.asset_mark")<br>  <br>- [`ID.asset_clear`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_clear "bpy.types.ID.asset_clear")<br>  <br>- [`ID.asset_generate_preview`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.asset_generate_preview "bpy.types.ID.asset_generate_preview")<br>  <br>- [`ID.override_create`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.override_create "bpy.types.ID.override_create")<br>  <br>- [`ID.override_hierarchy_create`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.override_hierarchy_create "bpy.types.ID.override_hierarchy_create")<br>  <br>- [`ID.user_clear`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.user_clear "bpy.types.ID.user_clear")<br>  <br>- [`ID.user_remap`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.user_remap "bpy.types.ID.user_remap")<br>  <br>- [`ID.make_local`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.make_local "bpy.types.ID.make_local")<br>  <br>- [`ID.user_of_id`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.user_of_id "bpy.types.ID.user_of_id")<br>  <br>- [`ID.animation_data_create`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.animation_data_create "bpy.types.ID.animation_data_create")<br>  <br>- [`ID.animation_data_clear`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.animation_data_clear "bpy.types.ID.animation_data_clear")<br>  <br>- [`ID.update_tag`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.update_tag "bpy.types.ID.update_tag")<br>  <br>- [`ID.preview_ensure`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.preview_ensure "bpy.types.ID.preview_ensure")<br>  <br>- [`ID.bl_rna_get_subclass`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass "bpy.types.ID.bl_rna_get_subclass")<br>  <br>- [`ID.bl_rna_get_subclass_py`](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass_py "bpy.types.ID.bl_rna_get_subclass_py")<br>  <br>- [`Texture.evaluate`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.evaluate "bpy.types.Texture.evaluate")<br>  <br>- [`Texture.bl_rna_get_subclass`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.bl_rna_get_subclass "bpy.types.Texture.bl_rna_get_subclass")<br>  <br>- [`Texture.bl_rna_get_subclass_py`](https://docs.blender.org/api/current/bpy.types.Texture.html#bpy.types.Texture.bl_rna_get_subclass_py "bpy.types.Texture.bl_rna_get_subclass_py") |