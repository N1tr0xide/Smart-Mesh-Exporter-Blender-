
import bpy

from . import smartExporter
from . import panel
from . import preferences
from . import _refresh_
_refresh_.reload_modules()

bl_info = {
 "name": "Smart Mesh Exporter",
 "author": "Angel Quintero",
 "version": (1, 0),
 "blender": (4, 2, 1),
 "description": "Streamlined Blender-to-Unity asset export tool.",
 "category": "Export",
}

def register():
    preferences.register_classes()
    smartExporter.register_classes()
    panel.register_classes()

def unregister():
    panel.unregister_classes()
    smartExporter.unregister_classes()
    preferences.unregister_classes()

