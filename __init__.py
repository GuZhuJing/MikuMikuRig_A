import bpy
import tomllib
import os
from .panels import MMRA_property
from .common.class_loader import auto_load
from .common.class_loader.auto_load import add_properties, remove_properties
from .common.i18n.dictionary import dictionary
from .common.i18n.i18n import load_dictionary

_addon_properties = {}

def getToml():
    manifest_path = os.path.join(os.path.dirname(__file__), 'blender_manifest.toml')
    with open(manifest_path,'rb') as tomlFile:
        result = tomllib.load(tomlFile)
    return result

def register():
    auto_load.init()
    auto_load.register()
    add_properties(_addon_properties)
    bpy.utils.register_class(MMRA_property)
    bpy.types.Object.MMRA = bpy.props.PointerProperty(type=MMRA_property)
    load_dictionary(dictionary)  # 国际化（多语言支持相关操作）
    bpy.app.translations.register(__package__, dictionary)

def unregister():
    bpy.app.translations.unregister(__package__)
    auto_load.unregister()
    remove_properties(_addon_properties)
    bpy.utils.unregister_class(MMRA_property)
    del bpy.types.Object.MMRA