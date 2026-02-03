import bpy
import os
import sys

currentFilePath = __file__  # 当前运行的Py文件的路径
FILE_NAME = os.path.basename(currentFilePath)

def modeInit(modeName, isDeselect=True, deselectMode="object"):  # 函数模式初始
    DEF_NAME = sys._getframe().f_code.co_name
    if modeName == 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    elif modeName == 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    elif modeName == 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    elif modeName == 'SCULPT':
        bpy.ops.object.mode_set(mode='SCULPT')
    elif modeName == 'PARTICLE':
        bpy.ops.object.mode_set(mode='PARTICLE')
    else:
        print(f'[{FILE_NAME}/{DEF_NAME}]模式不存在！')
    if isDeselect:
        if deselectMode == "object":
            bpy.ops.object.select_all(action='DESELECT')
        elif deselectMode == "pose":
            bpy.ops.pose.select_all(action='DESELECT')
        elif deselectMode == "armature":
            bpy.ops.armature.select_all(action='DESELECT')
        else:
            print(f'[{FILE_NAME}/{DEF_NAME}] deselectedMode={deselectMode}不存在！')