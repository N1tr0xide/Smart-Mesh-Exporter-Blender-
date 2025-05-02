
import bpy, re, os, json, math
from bpy.props import BoolProperty, StringProperty

def register_classes():
    add_properties()
    bpy.utils.register_class(ExportMeshes)

def unregister_classes():
    bpy.utils.unregister_class(ExportMeshes)
    remove_properties()

def add_properties():
    # choice between sphere and cube
    #bpy.types.Scene.object_choices = bpy.props.EnumProperty(
    #    name="Object Choice",
    #    description="Choose Cube or Sphere",
    #    items=[
    #        ('CUBE', "Cube", "Create a cube object"),
    #        ('SPHERE', "Sphere", "Create a sphere object")
    #    ]
    #)
    bpy.types.Scene.export_path = StringProperty(
        name="Export Path",
        subtype="DIR_PATH",
        default="//"
    )
    bpy.types.Scene.include_mats = BoolProperty(
        name= "Embed Textures",
        description = "Check if include Textures of each mesh in its respective .fbx",
        default = True,
    )
    bpy.types.Scene.include_parents = BoolProperty(
        name= "Include Parent Relationships",
        description = "Check if include the parent of each mesh, only adds it if parent is also a mesh",
        default = True,
    )
    bpy.types.Scene.export_pos = BoolProperty(
        name= "Include Position",
        description = "Check if include Position of each mesh in it the JSON Scene Data",
        default = True,
    )
    bpy.types.Scene.export_rot = BoolProperty(
        name= "Include Rotation",
        description = "Check if include Rotation of each mesh in it the JSON Scene Data",
        default = True,
    )
    bpy.types.Scene.export_scl = BoolProperty(
        name= "Include Scale",
        description = "Check if include Scale of each mesh in it the JSON Scene Data",
        default = True,
    )

def remove_properties():
    del bpy.types.Scene.export_path
    del bpy.types.Scene.include_mats
    del bpy.types.Scene.include_parents
    del bpy.types.Scene.export_pos
    del bpy.types.Scene.export_rot
    del bpy.types.Scene.export_scl

class ExportMeshes(bpy.types.Operator):
    """Export each individual mesh as an FBX, excluding specified suffixes"""
    bl_idname = "export.individual_fbx"
    bl_label = "Export Individual Meshes as FBX"

    def execute(self, context):
        export_dir = bpy.path.abspath(context.scene.export_path)
        json_path = os.path.join(export_dir, "SceneData.json")
        scene_data = []
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        for obj in bpy.context.scene.objects:
            if obj.type != 'MESH': continue
            self.write_object_data(obj, scene_data) #write obj data to Json
            if self.should_exclude(obj.name): continue # Skip exporting duplicate meshes.

            # Export mesh
            obj.select_set(True)
            bpy.ops.export_scene.fbx(
                filepath=os.path.join(export_dir, f"{obj.name}.fbx"),
                use_selection=True,
                bake_anim=False,
                path_mode='COPY',  # Ensures textures are embedded
                embed_textures= context.scene.include_mats,
                bake_space_transform = True
            )
            obj.select_set(False)

        self.export_transform_data(json_path, scene_data)
        self.report({'INFO'}, f"Exported meshes and Scene Data to {export_dir}")
        return {'FINISHED'}

    def write_object_data(self, obj, scene_data):
        """Adds data of obj into scene_data for Json file."""
        transform = self.get_transform_data(obj)  # Get object transform data
        transform["base_name"] = self.get_base_name(obj.name)  # Store base name separately

        # Append the object's transform data directly
        scene_data.append(transform)


    @staticmethod
    def export_transform_data(file_path, scene_data):
        """Writes the collected scene data to a JSON file."""
        json_data = {"objectDatas": scene_data}

        with open(file_path, "w") as json_file:
            json.dump(json_data, json_file, indent=4)

    @staticmethod
    def should_exclude(name):
        """Check if mesh name matches any user-defined regex pattern."""
        prefs = bpy.context.preferences.addons[__package__].preferences
        suffix_list = [item.name for item in prefs.my_collection]

        try:
            pattern = "|".join(suffix_list)  # Combine user regex patterns into one
            return bool(re.search(pattern, name))  # Match against patterns
        except re.error: return False

    @staticmethod
    def get_transform_data(obj):
        """Returns transform data for an object, converting rotation to degrees."""
        obj_data = {}
        obj_data["name"] = obj.name
        obj_data["parent"] = obj.parent.name if bpy.context.scene.include_parents and obj.parent and obj.parent.type == 'MESH' else None
        obj_data["location"] = list(obj.location) if bpy.context.scene.export_pos else None
        obj_data["rotation"] = [math.degrees(angle) for angle in obj.rotation_euler] if bpy.context.scene.export_rot else None # Saved as degrees
        obj_data["scale"] = list(obj.scale) if bpy.context.scene.export_scl else None
        return obj_data
    
    @staticmethod
    def get_base_name(name):
        """Removes user-defined regex patterns suffixes"""
        prefs = bpy.context.preferences.addons[__package__].preferences
        suffix_list = [item.name for item in prefs.my_collection]

        for pattern in suffix_list: # Remove matching suffixes
            name = re.sub(pattern, "", name)  
        return name.strip() 