
import bpy
from . import smartExporter

def register_classes():
    bpy.utils.register_class(ExportPanel)

def unregister_classes():
    bpy.utils.unregister_class(ExportPanel)

class ExportPanel(bpy.types.Panel):
    """Creates a Panel in the object context of the properties editor"""
    bl_label = "Smart Mesh Export"
    bl_idname = "ExportTab"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Smart Mesh Export"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "export_path")
        layout.prop(context.scene, "include_mats")
        layout.label(text="Scene Data for JSON:")
        layout.prop(context.scene, "include_parents")
        layout.prop(context.scene, "export_pos")
        layout.prop(context.scene, "export_rot")
        layout.prop(context.scene, "export_scl")
        col = layout.column()
        col.operator(smartExporter.ExportMeshes.bl_idname)