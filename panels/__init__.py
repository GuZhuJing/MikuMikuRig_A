import os
import bpy

dir = os.path.dirname(os.path.dirname( __file__))  # 获取当前文件的父目录的父目录路径

# 函数获取JSON文件路径列表
def jsonFilesPathsList(directory):
    jsonFilePathsNames = []  # 初始化一个空列表，用于存储JSON文件路径
    for root, dirs, files in os.walk(directory):  # 遍历目录树，root为当前目录，dirs为子目录列表，files为文件列表
        for file in files:  # 遍历当前目录中的所有文件
            if file.endswith('.json'):  # 如果文件以'.json'结尾
                json_file_name = os.path.join(root, file)  # 将目录路径和文件名组合成完整的文件路径
                jsonFilePathsNames.append(json_file_name)  # 将完整路径添加到列表中
    return jsonFilePathsNames  # 返回JSON文件路径列表
# 函数获取JSON文件列表
def jsonFilesList():
    MMD_RIG_path = os.path.join(dir, 'resources', 'MMD_RIG')
    jsonFilePaths = jsonFilesPathsList(MMD_RIG_path)  # 获取指定目录下的所有JSON文件路径
    JSON_Name = []  # 初始化预设名称列表
    for path in jsonFilePaths:  # 遍历JSON文件路径列表
        name = os.path.splitext(os.path.basename(path))  # 获取文件名（去掉路径部分），分离文件名和扩展名，返回元组(文件名, 扩展名)
        jsonName = name[0]  # 获取不含扩展名的文件名
        JSON_Name.append((jsonName, jsonName, jsonName))  # 将三元组(标识符, 显示名称, 描述)添加到列表中
    return JSON_Name  # 返回预设名称列表，用于Blender枚举属性

# 类创建MMRA属性组
class MMRA_property(bpy.types.PropertyGroup):
    bonePresets: bpy.props.EnumProperty(
        name="bonePresets",
        items=jsonFilesList(),
        default='default',
        description="预设文件列表"
    )
    initialPoseFilePath: bpy.props.StringProperty(
        name="",
        subtype='FILE_PATH',
        description="初始动作路径"
    )
    number: bpy.props.IntProperty(
        name="Int Config",
        default=2,
    )
    boolean: bpy.props.BoolProperty(
        name="Boolean Config",
        default=False,
    )
    polarTarget: bpy.props.BoolProperty(
        name="Polar target",
        default=False
    )
    RIG_OPT_Extras: bpy.props.BoolProperty(
        name="Extras Enabled",
        default=False
    )
    shoulderLinkage: bpy.props.BoolProperty(
        name="Shoulder linkage",
        default=False
    )
    enableInitialPose: bpy.props.BoolProperty(
        name="Initial pose",
        default=False,
        description="是否启用初始姿态。"
    )
    json_filepath: bpy.props.StringProperty(
        name="",
        subtype='FILE_PATH',
        description="导入json字典预设"
    )
    importPresets: bpy.props.BoolProperty(
        name="Import bonePresets",
        default=False,
        description="导入JSON字典预设"
    )
    bendBones: bpy.props.BoolProperty(
        name="Bend the bones",
        default=True,
        description="非MMD骨骼不要启用,请手动弯曲骨骼"
    )
    make_presets: bpy.props.BoolProperty(
        default=True,
    )
    number: bpy.props.IntProperty(
        default=0,
    )
    json_txt: bpy.props.StringProperty(
        name="",
        subtype='FILE_NAME',
    )
    designated: bpy.props.BoolProperty(
        default=True,
    )
    designated: bpy.props.BoolProperty(
        default=True,
    )
    Copy_the_file: bpy.props.BoolProperty(
        default=True,
    )