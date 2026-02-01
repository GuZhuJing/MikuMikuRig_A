import bpy
import os
import json


# 假设这个函数是从 __init__.py 中获取路径的简化版本
# 实际项目中，你应该确保这个路径获取函数是可用的。



class MMDBonesTools:
    def checkMMDBonesPresetsExistence(self, context: bpy.types.Context, presetsList: str):
        """
        读取指定的 JSON 预设文件，检测当前活动骨架中是否存在这些骨骼。
        将存在的骨骼在姿态模式下选中，并输出不存在的骨骼列表。

        :param context: Blender 上下文对象。
        :param presetsList: 要读取的预设文件名（例如 'MMD_Default'）。
        """

        # 1. 确保选中了骨架物体
        activeObject = context.view_layer.objects.active
        if not activeObject or activeObject.type != 'ARMATURE':
            self.report({'ERROR'}, "活动物体不是骨架，请选择一个骨架。")
            return {'CANCEL'}

        armature = activeObject.data

        # 2. 获取 JSON 文件路径
        presetFilePath = GetMMD_BoonPresetsPath()  # 假设该函数返回了 MMD_Default.json 的完整路径

        if not os.path.exists(presetFilePath):
            self.report({'ERROR'}, f"未找到预设文件: {presetFilePath}")
            return {'CANCEL'}

        # 3. 读取 JSON 文件内容
        bonePresets = {}
        try:
            with open(presetFilePath, 'r', encoding='utf-8') as f:
                # 注意：JSON 文件中的键和值可能是相同的骨骼名，我们只需要键（MMD 骨骼名）
                bonePresets = json.load(f)
        except Exception as e:
            self.report({'ERROR'}, f"读取 JSON 预设文件时发生错误: {e}")
            return {'CANCEL'}

        # 4. 模式切换：进入姿态模式
        bpy.ops.object.mode_set(mode='POSE')

        # 5. 清除当前选中骨骼
        bpy.ops.pose.select_all(action='DESELECT')

        existingBonesCount = 0
        nonExistingBones = []

        # 6. 遍历预设骨骼，检查并选中
        for mmdBoneName in bonePresets.keys():
            # 姿态模式下的骨骼对象通过 pose.bones 访问
            poseBone = activeObject.pose.bones.get(mmdBoneName)

            if poseBone:
                # 骨骼存在，选中它
                poseBone.bone.select = True
                existingBonesCount += 1
            else:
                # 骨骼不存在
                nonExistingBones.append(mmdBoneName)

        # 7. 结果输出
        if nonExistingBones:
            print(f"当前骨架中未找到以下 {len(nonExistingBones)} 个预设骨骼:", "WARNING")
            for boneName in nonExistingBones:
                print(f"- {boneName}")
        else:
            print("所有预设骨骼均在当前骨架中找到。", "INFO")

        print(f"共选中 {existingBonesCount} 个存在的预设骨骼。", "INFO")

        # 8. 返回操作成功
        return {'FINISHED'}

# 注意：在实际插件中，你需要在 __init__.py 中注册这个类，并且这个函数通常
# 作为某个 Operator 的 execute 方法的一部分被调用。
# 比如：class MMRCheckBonesOperator(bpy.types.Operator, MMDBonesTools): ...
# 并在其 execute 方法中调用 self.checkMMDBonesPresetsExistence(context, 'MMD_Default')