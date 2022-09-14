bl_info = {
	"name": "Import Ace Combat Models format",
	"description": "Import Ace Combat Model",
	"author": "GreenTrafficLight",
	"version": (1, 0),
	"blender": (2, 92, 0),
	"location": "File > Import > Ace Combat Importer",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"support": "COMMUNITY",
	"category": "Import-Export"}

import bpy

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ImportAceCombat(Operator, ImportHelper):
    """Load a Ace Combat model file"""
    bl_idname = "import_scene.acecombat_data"
    bl_label = "Import Ace Combat Data"

    filename_ext = ""
    filter_glob: StringProperty(default="*", options={'HIDDEN'}, maxlen=255,)

    clear_scene: BoolProperty(
        name="Clear scene",
        description="Clear everything from the scene",
        default=False,
    )

    fhm_ac6: BoolProperty(
        name="FHM Ace Combat 6",
        description="Activate this to read FHM from Ace Combat 6",
        default=False,
    )

    mnt_debug: BoolProperty(
        name="MNT Debug ( for memory dumps )",
        description="Fix the ordering armature of memory dumps ( doesn't work on all models )",
        default=False,
    )


    def execute(self, context):
        from . import  import_fhm
        import_fhm.main(self.filepath, self.clear_scene, self.fhm_ac6, self.mnt_debug)
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportAceCombat.bl_idname, text="Ace Combat")


def register():
    bpy.utils.register_class(ImportAceCombat)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportAceCombat)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()