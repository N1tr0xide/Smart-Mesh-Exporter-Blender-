import bpy
import re
from bpy.props import StringProperty, CollectionProperty, IntProperty

def register_classes():
    bpy.utils.register_class(SuffixPattern)
    bpy.utils.register_class(MY_UL_StringList)
    bpy.utils.register_class(AddItem)
    bpy.utils.register_class(RemoveItem)
    bpy.utils.register_class(AddonPreferences)

    prefs = bpy.context.preferences.addons[__package__].preferences
    new_item = prefs.my_collection.add()
    new_item.name = "\.\d{3}$"
    prefs.active_index = len(prefs.my_collection) - 1

def unregister_classes():
    bpy.utils.unregister_class(AddonPreferences)
    bpy.utils.unregister_class(SuffixPattern)
    bpy.utils.unregister_class(MY_UL_StringList)
    bpy.utils.unregister_class(AddItem)
    bpy.utils.unregister_class(RemoveItem)

def update_active_index(self, context):
    """Updates active_index when user interacts with a name field."""
    prefs = bpy.context.preferences.addons[__package__].preferences
    for i, item in enumerate(prefs.my_collection):
        if item == self:  # Compare object references, not names
            prefs.active_index = i  # Set active index to the clicked item
            break

class SuffixPattern(bpy.types.PropertyGroup):
    value: StringProperty(name="Item", update=update_active_index) # type: ignore

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    my_collection: CollectionProperty(type=SuffixPattern)  # type: ignore
    active_index: IntProperty(name="Active Index", default=0) # type: ignore

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.template_list("MY_UL_StringList", "", self, "my_collection", self, "active_index", rows=5)
        row = col.row()
        row.operator("myaddon.add_item", icon="ADD")
        row.operator("myaddon.remove_item", icon="REMOVE")

        if self.my_collection and 0 <= self.active_index < len(self.my_collection):
            item = self.my_collection[self.active_index]
            col.prop(item, "name", text="Entry Name")

class MY_UL_StringList(bpy.types.UIList):
    """Draw list"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "name", text="", emboss=False)

class AddItem(bpy.types.Operator):
    """Add item to list"""
    bl_idname = "myaddon.add_item"
    bl_label = "Add Item"

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        new_item = prefs.my_collection.add()
        new_item.name = f"New Entry {len(prefs.my_collection)}"
        prefs.active_index = len(prefs.my_collection) - 1
        return {'FINISHED'}

class RemoveItem(bpy.types.Operator):
    """Remove item from list"""
    bl_idname = "myaddon.remove_item"
    bl_label = "Remove Item"

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        if prefs.my_collection:
            prefs.my_collection.remove(prefs.active_index)
            prefs.active_index = max(0, min(prefs.active_index, len(prefs.my_collection) - 1))
        return {'FINISHED'}