ContentsMenuExpandLight modeDark modeAuto light/dark, in light modeAuto light/dark, in dark mode[Skip to content](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#furo-main-content)

[Back to top](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#)

Toggle Light / Dark / Auto color theme

Toggle table of contents sidebar

# TrackToConstraint(Constraint) [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html\#tracktoconstraint-constraint "Link to this heading")

base classes — [`bpy_struct`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint "bpy.types.Constraint")

_class_ bpy.types.TrackToConstraint( _Constraint_) [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint "Link to this definition")

Aim the constrained object toward the target

head\_tail [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint.head_tail "Link to this definition")

Target along length of bone: Head is 0, Tail is 1

Type:

float in \[0, 1\], default 0.0

subtarget [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint.subtarget "Link to this definition")

Armature bone, mesh or lattice vertex group, …

Type:

string, default “”, (never None)

target [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint.target "Link to this definition")

Target object

Type:

[`Object`](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object "bpy.types.Object")

track\_axis [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint.track_axis "Link to this definition")

Axis that points to the target object

Type:

enum in \[`'TRACK_X'`, `'TRACK_Y'`, `'TRACK_Z'`, `'TRACK_NEGATIVE_X'`, `'TRACK_NEGATIVE_Y'`, `'TRACK_NEGATIVE_Z'`\], default `'TRACK_X'`

up\_axis [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint.up_axis "Link to this definition")

Axis that points upward

Type:

enum in \[`'UP_X'`, `'UP_Y'`, `'UP_Z'`\], default `'UP_X'`

use\_bbone\_shape [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint.use_bbone_shape "Link to this definition")

Follow shape of B-Bone segments when calculating Head/Tail position

Type:

boolean, default False

use\_target\_z [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint.use_target_z "Link to this definition")

Target’s Z axis, not World Z axis, will constrain the Up direction

Type:

boolean, default False

_classmethod_ bl\_rna\_get\_subclass( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint.bl_rna_get_subclass "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The RNA type or default when not found.

Return type:

[`bpy.types.Struct`](https://docs.blender.org/api/current/bpy.types.Struct.html#bpy.types.Struct "bpy.types.Struct") subclass

_classmethod_ bl\_rna\_get\_subclass\_py( _id_, _default=None_, _/_) [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html#bpy.types.TrackToConstraint.bl_rna_get_subclass_py "Link to this definition")Parameters:

**id** ( _str_) – The RNA type identifier.

Returns:

The class or default when not found.

Return type:

type

## Inherited Properties [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html\#inherited-properties "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.id_data`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data "bpy.types.bpy_struct.id_data")<br>  <br>- [`Constraint.name`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.name "bpy.types.Constraint.name")<br>  <br>- [`Constraint.type`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.type "bpy.types.Constraint.type")<br>  <br>- [`Constraint.is_override_data`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.is_override_data "bpy.types.Constraint.is_override_data")<br>  <br>- [`Constraint.owner_space`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.owner_space "bpy.types.Constraint.owner_space")<br>  <br>- [`Constraint.target_space`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.target_space "bpy.types.Constraint.target_space")<br>  <br>- [`Constraint.space_object`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.space_object "bpy.types.Constraint.space_object")<br>  <br>- [`Constraint.space_subtarget`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.space_subtarget "bpy.types.Constraint.space_subtarget") | - [`Constraint.mute`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.mute "bpy.types.Constraint.mute")<br>  <br>- [`Constraint.enabled`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.enabled "bpy.types.Constraint.enabled")<br>  <br>- [`Constraint.show_expanded`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.show_expanded "bpy.types.Constraint.show_expanded")<br>  <br>- [`Constraint.is_valid`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.is_valid "bpy.types.Constraint.is_valid")<br>  <br>- [`Constraint.active`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.active "bpy.types.Constraint.active")<br>  <br>- [`Constraint.influence`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.influence "bpy.types.Constraint.influence")<br>  <br>- [`Constraint.error_location`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.error_location "bpy.types.Constraint.error_location")<br>  <br>- [`Constraint.error_rotation`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.error_rotation "bpy.types.Constraint.error_rotation") |

## Inherited Functions [¶](https://docs.blender.org/api/current/bpy.types.TrackToConstraint.html\#inherited-functions "Link to this heading")

|     |     |
| --- | --- |
| - [`bpy_struct.as_pointer`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.as_pointer "bpy.types.bpy_struct.as_pointer")<br>  <br>- [`bpy_struct.driver_add`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_add "bpy.types.bpy_struct.driver_add")<br>  <br>- [`bpy_struct.driver_remove`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_remove "bpy.types.bpy_struct.driver_remove")<br>  <br>- [`bpy_struct.get`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.get "bpy.types.bpy_struct.get")<br>  <br>- [`bpy_struct.id_properties_clear`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_clear "bpy.types.bpy_struct.id_properties_clear")<br>  <br>- [`bpy_struct.id_properties_ensure`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ensure "bpy.types.bpy_struct.id_properties_ensure")<br>  <br>- [`bpy_struct.id_properties_ui`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ui "bpy.types.bpy_struct.id_properties_ui")<br>  <br>- [`bpy_struct.is_property_hidden`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_hidden "bpy.types.bpy_struct.is_property_hidden")<br>  <br>- [`bpy_struct.is_property_overridable_library`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_overridable_library "bpy.types.bpy_struct.is_property_overridable_library")<br>  <br>- [`bpy_struct.is_property_readonly`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_readonly "bpy.types.bpy_struct.is_property_readonly")<br>  <br>- [`bpy_struct.is_property_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_set "bpy.types.bpy_struct.is_property_set")<br>  <br>- [`bpy_struct.items`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.items "bpy.types.bpy_struct.items")<br>  <br>- [`bpy_struct.keyframe_delete`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_delete "bpy.types.bpy_struct.keyframe_delete") | - [`bpy_struct.keyframe_insert`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert "bpy.types.bpy_struct.keyframe_insert")<br>  <br>- [`bpy_struct.keys`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keys "bpy.types.bpy_struct.keys")<br>  <br>- [`bpy_struct.path_from_id`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_id "bpy.types.bpy_struct.path_from_id")<br>  <br>- [`bpy_struct.path_from_module`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_module "bpy.types.bpy_struct.path_from_module")<br>  <br>- [`bpy_struct.path_resolve`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_resolve "bpy.types.bpy_struct.path_resolve")<br>  <br>- [`bpy_struct.pop`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.pop "bpy.types.bpy_struct.pop")<br>  <br>- [`bpy_struct.property_overridable_library_set`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_overridable_library_set "bpy.types.bpy_struct.property_overridable_library_set")<br>  <br>- [`bpy_struct.property_unset`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_unset "bpy.types.bpy_struct.property_unset")<br>  <br>- [`bpy_struct.rna_ancestors`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.rna_ancestors "bpy.types.bpy_struct.rna_ancestors")<br>  <br>- [`bpy_struct.type_recast`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.type_recast "bpy.types.bpy_struct.type_recast")<br>  <br>- [`bpy_struct.values`](https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.values "bpy.types.bpy_struct.values")<br>  <br>- [`Constraint.bl_rna_get_subclass`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.bl_rna_get_subclass "bpy.types.Constraint.bl_rna_get_subclass")<br>  <br>- [`Constraint.bl_rna_get_subclass_py`](https://docs.blender.org/api/current/bpy.types.Constraint.html#bpy.types.Constraint.bl_rna_get_subclass_py "bpy.types.Constraint.bl_rna_get_subclass_py") |