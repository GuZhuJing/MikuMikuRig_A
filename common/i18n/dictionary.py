from ..class_loader.auto_load import preprocess_dictionary

dictionary = {
    "zh_CN": {
        ("*", "MMD tool"): "MMD工具",
        ("Operator", "Optimization MMD Armature"): "优化MMD骨骼",
        ("Operator", "Build a controller"): "生成控制器",
        ("", "Extras"): "额外选项",
        ("*", "Controller options"): "控制器选项",
        ("", "Polar target"): "极向目标",
        ("", "Shoulder linkage"): "肩膀联动",
        ("", "Customize the initial pose"): "自定初始姿势",
        ("", "This option has a serious bug and should not be enabled"): "此选项存在严重的Bug，不要启用",
        ("", "bonePresets"): "预设",
        ("", "Import bonePresets"): "导入预设",
        ("", "Bend the bones"): "弯曲骨骼",
        ("Operator", "make bonePresets"): "制作预设",
        ("Operator", "Exit the designation"): "退出指定",
        ("Operator", "designated"): "指定",
        ("Operator", "Export VMD actions"): "导出VMD动作",
    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
