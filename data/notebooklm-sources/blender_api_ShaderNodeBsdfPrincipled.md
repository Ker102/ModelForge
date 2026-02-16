ContentsMenuExpandLight modeDark modeAuto light/dark, in light modeAuto light/dark, in dark mode[Skip to content](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#furo-main-content)

[Back to top](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#)

Toggle Light / Dark / Auto color theme

Toggle table of contents sidebar

# ShaderNodeBsdfPrincipled(ShaderNode) [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html\#shadernodebsdfprincipled-shadernode "Link to this heading")

base classes — [`bpy_struct`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node "bpy.types.Node"), [`NodeInternal`](https://docs.blender.org/api/current/bpy.types.NodeInternal.html#bpy.types.NodeInternal "bpy.types.NodeInternal"), [`ShaderNode`](https://docs.blender.org/api/current/bpy.types.ShaderNode.html#bpy.types.ShaderNode "bpy.types.ShaderNode")

_class_ bpy.types.ShaderNodeBsdfPrincipled( _ShaderNode_) [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#bpy.types.ShaderNodeBsdfPrincipled "Link to this definition")

Physically-based, easy-to-use shader for rendering surface materials, based on the OpenPBR model

distribution [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#bpy.types.ShaderNodeBsdfPrincipled.distribution "Link to this definition")

Light scattering distribution on rough surface

- `GGX`
GGX.

- `MULTI_GGX`
Multiscatter GGX – GGX with additional correction to account for multiple scattering, preserve energy and prevent unexpected darkening at high roughness.


Type:

enum in \[`'GGX'`, `'MULTI_GGX'`\], default `'GGX'`

subsurface\_method [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#bpy.types.ShaderNodeBsdfPrincipled.subsurface_method "Link to this definition")

Method for rendering subsurface scattering

- `BURLEY`
Christensen-Burley – Approximation to physically based volume scattering.

- `RANDOM_WALK`
Random Walk – Volumetric approximation to physically based volume scattering, using the scattering radius as specified.

- `RANDOM_WALK_SKIN`
Random Walk (Skin) – Volumetric approximation to physically based volume scattering, with scattering radius automatically adjusted to match color textures. Designed for skin shading..


Type:

enum in \[`'BURLEY'`, `'RANDOM_WALK'`, `'RANDOM_WALK_SKIN'`\], default `'BURLEY'`

_classmethod_ is\_registered\_node\_type() [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#bpy.types.ShaderNodeBsdfPrincipled.is_registered_node_type "Link to this definition")

True if a registered node type

Returns:

Result

Return type:

boolean

_classmethod_ input\_template( _index_) [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#bpy.types.ShaderNodeBsdfPrincipled.input_template "Link to this definition")

Input socket template

Parameters:

**index** ( _int in_ _\[_ _0_ _,_ _inf_ _\]_) – Index

Returns:

result

Return type:

[`NodeInternalSocketTemplate`](https://docs.blender.org/api/current/bpy.types.NodeInternalSocketTemplate.html#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

_classmethod_ output\_template( _index_) [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#bpy.types.ShaderNodeBsdfPrincipled.output_template "Link to this definition")

Output socket template

Parameters:

**index** ( _int in_ _\[_ _0_ _,_ _inf_ _\]_) – Index

Returns:

result

Return type:

[`NodeInternalSocketTemplate`](https://docs.blender.org/api/current/bpy.types.NodeInternalSocketTemplate.html#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

_classmethod_ bl\_rna\_get\_subclass( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#bpy.types.ShaderNodeBsdfPrincipled.bl_rna_get_subclass "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The RNA type or default when not found.

Return type:

[`bpy.types.Struct`](https://docs.blender.org/api/current/bpy.types.Struct.html#bpy.types.Struct "bpy.types.Struct") subclass

_classmethod_ bl\_rna\_get\_subclass\_py( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html#bpy.types.ShaderNodeBsdfPrincipled.bl_rna_get_subclass_py "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The class or default when not found.

Return type:

type

## Inherited Properties [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html\#inherited-properties "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.id_data`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data "bpy.types.bpy_struct.id_data")<br>  <br>- [`Node.type`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.type "bpy.types.Node.type")<br>  <br>- [`Node.location`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.location "bpy.types.Node.location")<br>  <br>- [`Node.location_absolute`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.location_absolute "bpy.types.Node.location_absolute")<br>  <br>- [`Node.width`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.width "bpy.types.Node.width")<br>  <br>- [`Node.height`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.height "bpy.types.Node.height")<br>  <br>- [`Node.dimensions`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.dimensions "bpy.types.Node.dimensions")<br>  <br>- [`Node.name`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.name "bpy.types.Node.name")<br>  <br>- [`Node.label`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.label "bpy.types.Node.label")<br>  <br>- [`Node.inputs`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.inputs "bpy.types.Node.inputs")<br>  <br>- [`Node.outputs`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.outputs "bpy.types.Node.outputs")<br>  <br>- [`Node.internal_links`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.internal_links "bpy.types.Node.internal_links")<br>  <br>- [`Node.parent`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.parent "bpy.types.Node.parent")<br>  <br>- [`Node.warning_propagation`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.warning_propagation "bpy.types.Node.warning_propagation")<br>  <br>- [`Node.use_custom_color`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.use_custom_color "bpy.types.Node.use_custom_color")<br>  <br>- [`Node.color`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.color "bpy.types.Node.color")<br>  <br>- [`Node.color_tag`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.color_tag "bpy.types.Node.color_tag") | - [`Node.select`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.select "bpy.types.Node.select")<br>  <br>- [`Node.show_options`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.show_options "bpy.types.Node.show_options")<br>  <br>- [`Node.show_preview`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.show_preview "bpy.types.Node.show_preview")<br>  <br>- [`Node.hide`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.hide "bpy.types.Node.hide")<br>  <br>- [`Node.mute`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.mute "bpy.types.Node.mute")<br>  <br>- [`Node.show_texture`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.show_texture "bpy.types.Node.show_texture")<br>  <br>- [`Node.bl_idname`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_idname "bpy.types.Node.bl_idname")<br>  <br>- [`Node.bl_label`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_label "bpy.types.Node.bl_label")<br>  <br>- [`Node.bl_description`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_description "bpy.types.Node.bl_description")<br>  <br>- [`Node.bl_icon`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_icon "bpy.types.Node.bl_icon")<br>  <br>- [`Node.bl_static_type`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_static_type "bpy.types.Node.bl_static_type")<br>  <br>- [`Node.bl_width_default`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_width_default "bpy.types.Node.bl_width_default")<br>  <br>- [`Node.bl_width_min`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_width_min "bpy.types.Node.bl_width_min")<br>  <br>- [`Node.bl_width_max`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_width_max "bpy.types.Node.bl_width_max")<br>  <br>- [`Node.bl_height_default`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_height_default "bpy.types.Node.bl_height_default")<br>  <br>- [`Node.bl_height_min`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_height_min "bpy.types.Node.bl_height_min")<br>  <br>- [`Node.bl_height_max`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_height_max "bpy.types.Node.bl_height_max") |

## Inherited Functions [¶](https://docs.blender.org/api/current/bpy.types.ShaderNodeBsdfPrincipled.html\#inherited-functions "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.as_pointer`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.as_pointer "bpy.types.bpy_struct.as_pointer")<br>  <br>- [`bpy_struct.driver_add`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_add "bpy.types.bpy_struct.driver_add")<br>  <br>- [`bpy_struct.driver_remove`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_remove "bpy.types.bpy_struct.driver_remove")<br>  <br>- [`bpy_struct.get`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.get "bpy.types.bpy_struct.get")<br>  <br>- [`bpy_struct.id_properties_clear`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_clear "bpy.types.bpy_struct.id_properties_clear")<br>  <br>- [`bpy_struct.id_properties_ensure`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ensure "bpy.types.bpy_struct.id_properties_ensure")<br>  <br>- [`bpy_struct.id_properties_ui`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ui "bpy.types.bpy_struct.id_properties_ui")<br>  <br>- [`bpy_struct.is_property_hidden`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_hidden "bpy.types.bpy_struct.is_property_hidden")<br>  <br>- [`bpy_struct.is_property_overridable_library`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_overridable_library "bpy.types.bpy_struct.is_property_overridable_library")<br>  <br>- [`bpy_struct.is_property_readonly`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_readonly "bpy.types.bpy_struct.is_property_readonly")<br>  <br>- [`bpy_struct.is_property_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_set "bpy.types.bpy_struct.is_property_set")<br>  <br>- [`bpy_struct.items`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.items "bpy.types.bpy_struct.items")<br>  <br>- [`bpy_struct.keyframe_delete`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_delete "bpy.types.bpy_struct.keyframe_delete")<br>  <br>- [`bpy_struct.keyframe_insert`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert "bpy.types.bpy_struct.keyframe_insert")<br>  <br>- [`bpy_struct.keys`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keys "bpy.types.bpy_struct.keys")<br>  <br>- [`bpy_struct.path_from_id`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_id "bpy.types.bpy_struct.path_from_id")<br>  <br>- [`bpy_struct.path_from_module`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_module "bpy.types.bpy_struct.path_from_module")<br>  <br>- [`bpy_struct.path_resolve`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_resolve "bpy.types.bpy_struct.path_resolve")<br>  <br>- [`bpy_struct.pop`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.pop "bpy.types.bpy_struct.pop")<br>  <br>- [`bpy_struct.property_overridable_library_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_overridable_library_set "bpy.types.bpy_struct.property_overridable_library_set")<br>  <br>- [`bpy_struct.property_unset`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_unset "bpy.types.bpy_struct.property_unset")<br>  <br>- [`bpy_struct.rna_ancestors`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.rna_ancestors "bpy.types.bpy_struct.rna_ancestors")<br>  <br>- [`bpy_struct.type_recast`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.type_recast "bpy.types.bpy_struct.type_recast")<br>  <br>- [`bpy_struct.values`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.values "bpy.types.bpy_struct.values")<br>  <br>- [`Node.bl_system_properties_get`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_system_properties_get "bpy.types.Node.bl_system_properties_get")<br>  <br>- [`Node.socket_value_update`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.socket_value_update "bpy.types.Node.socket_value_update") | - [`Node.is_registered_node_type`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.is_registered_node_type "bpy.types.Node.is_registered_node_type")<br>  <br>- [`Node.poll`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.poll "bpy.types.Node.poll")<br>  <br>- [`Node.poll_instance`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.poll_instance "bpy.types.Node.poll_instance")<br>  <br>- [`Node.update`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.update "bpy.types.Node.update")<br>  <br>- [`Node.insert_link`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.insert_link "bpy.types.Node.insert_link")<br>  <br>- [`Node.init`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.init "bpy.types.Node.init")<br>  <br>- [`Node.copy`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.copy "bpy.types.Node.copy")<br>  <br>- [`Node.free`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.free "bpy.types.Node.free")<br>  <br>- [`Node.draw_buttons`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.draw_buttons "bpy.types.Node.draw_buttons")<br>  <br>- [`Node.draw_buttons_ext`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.draw_buttons_ext "bpy.types.Node.draw_buttons_ext")<br>  <br>- [`Node.draw_label`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.draw_label "bpy.types.Node.draw_label")<br>  <br>- [`Node.debug_zone_body_lazy_function_graph`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.debug_zone_body_lazy_function_graph "bpy.types.Node.debug_zone_body_lazy_function_graph")<br>  <br>- [`Node.debug_zone_lazy_function_graph`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.debug_zone_lazy_function_graph "bpy.types.Node.debug_zone_lazy_function_graph")<br>  <br>- [`Node.poll`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.poll "bpy.types.Node.poll")<br>  <br>- [`Node.bl_rna_get_subclass`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_rna_get_subclass "bpy.types.Node.bl_rna_get_subclass")<br>  <br>- [`Node.bl_rna_get_subclass_py`](https://docs.blender.org/api/current/bpy.types.Node.html#bpy.types.Node.bl_rna_get_subclass_py "bpy.types.Node.bl_rna_get_subclass_py")<br>  <br>- [`NodeInternal.poll`](https://docs.blender.org/api/current/bpy.types.NodeInternal.html#bpy.types.NodeInternal.poll "bpy.types.NodeInternal.poll")<br>  <br>- [`NodeInternal.poll_instance`](https://docs.blender.org/api/current/bpy.types.NodeInternal.html#bpy.types.NodeInternal.poll_instance "bpy.types.NodeInternal.poll_instance")<br>  <br>- [`NodeInternal.update`](https://docs.blender.org/api/current/bpy.types.NodeInternal.html#bpy.types.NodeInternal.update "bpy.types.NodeInternal.update")<br>  <br>- [`NodeInternal.draw_buttons`](https://docs.blender.org/api/current/bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons "bpy.types.NodeInternal.draw_buttons")<br>  <br>- [`NodeInternal.draw_buttons_ext`](https://docs.blender.org/api/current/bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons_ext "bpy.types.NodeInternal.draw_buttons_ext")<br>  <br>- [`NodeInternal.bl_rna_get_subclass`](https://docs.blender.org/api/current/bpy.types.NodeInternal.html#bpy.types.NodeInternal.bl_rna_get_subclass "bpy.types.NodeInternal.bl_rna_get_subclass")<br>  <br>- [`NodeInternal.bl_rna_get_subclass_py`](https://docs.blender.org/api/current/bpy.types.NodeInternal.html#bpy.types.NodeInternal.bl_rna_get_subclass_py "bpy.types.NodeInternal.bl_rna_get_subclass_py")<br>  <br>- `ShaderNode.poll`<br>  <br>- [`ShaderNode.bl_rna_get_subclass`](https://docs.blender.org/api/current/bpy.types.ShaderNode.html#bpy.types.ShaderNode.bl_rna_get_subclass "bpy.types.ShaderNode.bl_rna_get_subclass")<br>  <br>- [`ShaderNode.bl_rna_get_subclass_py`](https://docs.blender.org/api/current/bpy.types.ShaderNode.html#bpy.types.ShaderNode.bl_rna_get_subclass_py "bpy.types.ShaderNode.bl_rna_get_subclass_py") |