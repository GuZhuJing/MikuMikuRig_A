import os
import sys
import json
import bpy
import mathutils
from . import modeInit
from ..resources import getMMD_RIGFolderPath
from .. import getToml

ADDON_NAME = getToml()['name']

class buildRigifyController(bpy.types.Operator):  # 构建MMD-Rigify控制器
    bl_idname = "object.build_rigify_controller"
    bl_label = "构建MMD-Rigify控制器"
    bl_description = "基于MMD模型构建Rigify控制器系统"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        OBJ = context.view_layer.objects.active
        if OBJ is not None and OBJ.type == 'ARMATURE':
                return True
        return False
    def spineContinuityVerify(self, armatureName):  # 脊柱连续性验证与修复
        CLASS_NAME = self.__class__.__name__
        DEF_NAME = sys._getframe().f_code.co_name
        printer = f'{ADDON_NAME}/{CLASS_NAME}/{DEF_NAME}'
        wetherReported =  False
        modeInit('OBJECT')
        bpy.ops.object.select_pattern(pattern=armatureName)  # 选择名称匹配 armature_name 模式的对象
        bpy.context.view_layer.objects.active = bpy.data.objects[armatureName]  # 将活动对象设置为名为 armature_name 的对象
        bpy.ops.object.mode_set(mode='EDIT')  # 进入编辑模式
        spineBones = ['spine', 'spine.001', 'spine.002', 'spine.003', 'spine.004',"shoulder.L", "shoulder.R"]
        # 确保每个骨骼的尾部连接到下一个骨骼的头部
        for i in range(len(spineBones) - 1):  # 遍历 spineBones 数组，从第一个到倒数第二个元素
            currentBone = bpy.context.object.data.edit_bones.get(spineBones[i])  # 获取当前骨骼（第i个）
            nextBone = bpy.context.object.data.edit_bones.get(spineBones[i + 1])  # 获取下一个骨骼（第i+1个）
            if currentBone and nextBone:  # 如果两个骨骼都存在
                if (currentBone.tail - nextBone.head).length > 0.001 and nextBone.name not in ["shoulder.L", "shoulder.R"]:  # 检查骨骼连接是否断开（距离大于0.001）
                    if not wetherReported:
                        self.report({'WARNING'}, '检测到未连接的骨骼，正在修复……（详情见系统命令行）')
                        wetherReported = True
                    nextBone.head = currentBone.tail  # 将下一个骨骼的头部移到当前骨骼的尾部位置，使它们连接起来
                    print(f"[{printer}]修复骨骼连续性: {currentBone.name} -> {nextBone.name}")  # 打印调试信息，显示正在修复哪两个骨骼的连接
                if not currentBone.use_connect:
                    currentBone.use_connect = True  # 启用当前骨骼的连接
                    print(f"[{printer}]修复骨骼启用相连项: {currentBone.name}")  # 打印调试信息，显示正在修复哪两个骨骼的连接
                if not nextBone.use_connect:
                    nextBone.use_connect = True  # 启用下一个骨骼的连接
                    print(f"[{printer}]修复骨骼启用相连项: {nextBone.name}")  # 打印调试信息，显示正在修复哪两个骨骼的连接
        modeInit('OBJECT')  # 返回物体模式
    def execute(self, context: bpy.types.Context):
        CLASS_NAME = self.__class__.__name__
        printer = f'{ADDON_NAME}/{CLASS_NAME}'
        # 作用外部数据准备
        MMRA = context.object.MMRA
        JSON_FileName = MMRA.bonePresets + '.json'
        JSON_FilePath = os.path.join(getMMD_RIGFolderPath(), JSON_FileName)
        if MMRA.importPresets:
            newPath = MMRA.json_filepath
        with open(JSON_FilePath) as f:  # 读取json文件
            JSON_text = json.load(f)
        if 'rigify' not in bpy.context.preferences.addons.keys():  # 检测rigify
            self.report({'WARNING'}, '未加载Rigify！尝试启动……')
            try:
                bpy.ops.preferences.addon_enable(module="rigify")
            finally:
                self.report({'ERROR'}, 'Rigify未安装！请安装Rigify并重新启动！')
                return {'CANCELLED'}
        print(f"[{printer}]外部数据准备就绪！")

        # 作用内部数据准备（MMD）
        bpy.ops.object.mode_set(mode='OBJECT')  # 切换物体模式
        armName = bpy.context.active_object.name  # 当前活动物体名称
        armName_Object = bpy.data.objects[armName]  # 通过名称获取对应的对象引用
        if armName_Object not in bpy.context.selected_objects:  # 检查该对象是否在当前选中的对象列表中
            self.report({'ERROR'}, '未选中骨骼!')  # 如果对象未被选中，则报告错误信息
            return {'CANCELLED'}  # 返回取消状态，终止操作执行
        armName_Object_worldMatrix = armName_Object.matrix_world  # 获取世界矩阵
        armName_Object_worldMatrix_location = armName_Object_worldMatrix.translation  # 获取世界空间坐标
        # 复制物体
        bpy.ops.object.duplicate_move(
            OBJECT_OT_duplicate={
                "linked": False,
                "mode": 'TRANSLATION'},
            TRANSFORM_OT_translate={
                "value": (0, 0, 0),
                "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1))})
        arm2Name = bpy.context.active_object.name
        bpy.ops.object.duplicate_move(
            OBJECT_OT_duplicate={
                "linked": False,
                "mode": 'TRANSLATION'},
            TRANSFORM_OT_translate={
                "value": (0, 0, 0),
                "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1))})
        arm3Name = bpy.context.active_object.name
        print(f"[{printer}]内部数据（MMD）准备就绪！")

        # 作用内部数据准备（Rigify）
        bpy.ops.object.armature_human_metarig_add()
        RigName = bpy.context.active_object.name
        RigName_Object = bpy.data.objects[RigName]
        RigName_Object.location = armName_Object_worldMatrix_location  # 设置Rig骨架的世界空间坐标为得到的mmd骨架坐标
        bpy.ops.object.select_all(action='DESELECT')  # 清空选择
        print(f"[{printer}]内部数据（Rigify）准备就绪！")

        # 作用读取Arm2数据
        bpy.ops.object.select_pattern(pattern=arm2Name)  # 选择物体
        arm2Name_Object = bpy.data.objects[arm2Name]
        bpy.context.view_layer.objects.active = arm2Name_Object  # 将该物体设置为活动对象
        modeInit('POSE', deselectMode="pose")
        bpy.context.active_object.pose.bones['頭'].select = True  # 将頭骨骼设置为活动对象，让骨骼在视图中高亮显示
        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones['頭'].bone  # 将骨骼设为活动状态（功.能上的选中，用于后续操作的目标）
        arm2Name_Object = bpy.context.active_object
        arm2Name_Object_headBone = arm2Name_Object.pose.bones['頭']  # 获取头部骨骼的姿势引用
        arm2Name_Object_Head_matrixWorldTailLocation = arm2Name_Object.matrix_world @ arm2Name_Object_headBone.tail  # 计算骨骼尾部在世界空间中的坐标

        # 作用读取Rig数据
        bpy.ops.object.select_pattern(pattern=RigName)  # 选择物体
        RigName_Object = bpy.data.objects[RigName]
        bpy.context.view_layer.objects.active = RigName_Object  # 将该物体设置为活动对象
        modeInit('POSE', deselectMode="pose")
        bpy.context.active_object.pose.bones['face'].select = True  # 将face骨骼设置为活动对象，让骨骼在视图中高亮显
        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones['face'].bone  # 将face骨骼设为活动状态（功.能上的选中，用于后续操作的目标）
        RigName_Object_face = RigName_Object.pose.bones["face"]  # 获取特定骨骼的姿势对象
        RigName_Object_face_tailLocation = RigName_Object_face.tail  # 获取当前骨骼（'face'骨骼）在局部空间中的尾部坐标

        # 作用变换Rig
        arm2Name_Object_Head_RIGmatrixWorldTailLocation = RigName_Object.matrix_world.inverted() @ arm2Name_Object_Head_matrixWorldTailLocation  # 将目标骨骼(arm2Name_Object_Head)尾部的世界坐标转换为当前物体(RigName_Object)的局部坐标
        offset = arm2Name_Object_Head_RIGmatrixWorldTailLocation - RigName_Object_face_tailLocation  # 计算目标骨骼（arm2Name_Object_Head）的尾部在当前物体（RigName_Object）中的位置
        offset_matrix = mathutils.Matrix.Translation(offset)  # 根据偏移量创建平移变换矩阵
        RigName_Object_face_matrix = RigName_Object_face.matrix  # 获取当前face骨骼的变换矩阵
        offsetRIG_matrix = offset_matrix @ RigName_Object_face_matrix  # 将平移变换应用到face骨骼的原始矩阵上，得到新地变换矩阵
        RigName_Object_face.matrix = offsetRIG_matrix  # 应用新地变换矩阵到face骨骼，完成骨骼位置的调整
        bpy.ops.pose.armature_apply(selected=False)  # 应用姿态
        modeInit('OBJECT')

        def applyCustomInitialActions():  # 应用初始动作
            DEF_NAME = sys._getframe().f_code.co_name
            if not MMRA.enableInitialPose:
                return
            bpy.ops.object.mode_set(mode='OBJECT')  # 切换物体模式
            bpy.ops.object.select_all(action='DESELECT')  # 清空选择
            bpy.ops.object.select_pattern(pattern=arm2Name)  # 选择物体
            bpy.context.view_layer.objects.active = arm2Name_Object  # 将该物体设置为活动对象
            frameEnd = bpy.context.scene.frame_end  # 获取结束帧数值
            defaultInitialPoseFilePath = MMRA.initialPoseFilePath
            defaultInitialPoseFilePath_fileName = os.path.basename(defaultInitialPoseFilePath)  # 获取文件名称
            defaultInitialPoseFilePath_dir = os.path.dirname(defaultInitialPoseFilePath)  # 提取文件所在文件夹路径
            # 是否启用了弯曲骨骼选项
            if MMRA.bendBones:
                # 导入初始姿势VMD文件
                bpy.ops.mmd_tools.import_vmd(filepath=defaultInitialPoseFilePath,
                                             files=[{"name": defaultInitialPoseFilePath_fileName}],
                                             directory=defaultInitialPoseFilePath_dir)
            currentFrame = bpy.context.scene.frame_current  # 获取当前帧数值
            bpy.context.scene.frame_current = 7  # 当前帧设置为第7帧
            bpy.context.scene.frame_end = frameEnd # 恢复原来地结束帧数值
            bpy.ops.object.mode_set(mode='POSE')  # 进入姿态模式
            bpy.ops.pose.armature_apply(selected=False)  # 应用姿态
            bpy.ops.object.mode_set(mode='OBJECT')  # 切换物体模式
            bpy.ops.object.select_all(action='DESELECT')  # 清空选择
            bpy.context.scene.frame_current = currentFrame  # 恢复当前帧
            self.report({'INFO'}, '应用初始姿势完成！')
            print(f'[{printer}/{DEF_NAME}]应用初始姿势完成！')
        def mergeBones(bone, bonesName):   # 融并骨骼
            bpy.ops.object.mode_set(mode='OBJECT')  # 切换物体模式
            bpy.ops.object.select_all(action='DESELECT')  # 清空选择
            bpy.ops.object.select_pattern(pattern=bone)  # 选择骨架
            Arm_object = bpy.data.objects[bone]
            bpy.context.view_layer.objects.active = Arm_object  # 将该物体设置为活动对象
            bpy.ops.object.mode_set(mode='EDIT')  # 切换到编辑模式
            bpy.ops.armature.select_all(action='DESELECT')  # 取消所有选择
            bpy.ops.object.select_pattern(pattern=bonesName)  # 选择活动骨骼
            armatureData = bpy.context.edit_object.data  # 获取当前编辑对象（骨架）的数据
            bone = armatureData.edit_bones.get(bonesName)  # 从骨架中获取名为 bones 的骨骼
            bpy.context.edit_object.data.edit_bones.active = bone  # 将获取到的骨骼设置为当前骨架中活动的骨骼
            bpy.ops.armature.dissolve('INVOKE_DEFAULT')  # 融并骨骼
            bpy.ops.armature.select_all(action='DESELECT')  # 取消所有选择
            bpy.ops.object.mode_set(mode='OBJECT')  # 切换物体模式
            bpy.ops.object.select_all(action='DESELECT')  # 清空选择
            """
                在Blender单选骨骼融并时会默认与下一根骨骼融并
            """
        def correctRoll(bone):  # 修正约束骨骼扭转值
            """
               差值 = 公式：原骨骼 - 处理完的骨骼
               扭转值（修正） = 差值 + 约束骨骼
            """
            modeInit('OBJECT')
            bpy.ops.object.select_pattern(pattern=arm3Name)   # 选择物体
            arm3Name_Object = bpy.data.objects[arm3Name]
            bpy.context.view_layer.objects.active = arm3Name_Object
            modeInit('EDIT', deselectMode='armature')
            bpy.ops.object.select_pattern(pattern=bone, extend=False)
            armature = bpy.context.edit_object.data  # 获取当前编辑模式下的骨架对象数据并赋值给变量armature，异常未证实原因导致bpy.context.edit_object.data为空
            arm3_bone = armature.edit_bones.get(bone)  # 从骨架的编辑骨骼集合中获取名为MMD_bone的骨骼并赋值给变量bone
            bpy.context.edit_object.data.edit_bones.active = arm3_bone  # 将获取到的骨骼设置为当前编辑模式下的活动骨骼
            Arm3_roll = bpy.context.active_bone.roll  # 获取当前活动骨骼的扭转值（roll）并赋值给变量Rig_roll
            bpy.ops.armature.select_all(action='DESELECT')   # 取消所有选择
            modeInit('OBJECT')
            bpy.ops.object.select_pattern(pattern=arm2Name)  # 选择物体
            bpy.context.view_layer.objects.active = arm2Name_Object  # 将该物体设置为活动对象
            modeInit('EDIT', deselectMode='armature')
            bpy.ops.object.select_pattern(pattern=bone, extend=False)
            armature = bpy.context.edit_object.data
            arm2_bone = armature.edit_bones.get(bone)  # 从骨架的编辑骨骼集合中获取名为MMD_bone的骨骼并赋值给变量bone
            bpy.context.edit_object.data.edit_bones.active = arm2_bone  # 将获取到的骨骼设置为当前编辑模式下的活动骨骼
            Arm2_roll = bpy.context.active_bone.roll
            bpy.ops.armature.select_all(action='DESELECT')
            modeInit('OBJECT')
            bpy.ops.object.select_pattern(pattern=armName)  # 选择物体
            bpy.context.view_layer.objects.active = armName_Object
            modeInit('EDIT', deselectMode='armature')
            bpy.ops.object.select_pattern(pattern=bone, extend=False)  # 选择活动骨骼
            armature = bpy.context.edit_object.data
            arm_bone = armature.edit_bones.get(bone)
            bpy.context.edit_object.data.edit_bones.active = arm_bone
            Arm_roll = bpy.context.active_bone.roll
            deviation = Arm3_roll - Arm2_roll
            torsionValue = deviation + Arm_roll
            bpy.context.active_bone.roll = torsionValue
            bpy.ops.armature.select_all(action='DESELECT')  # 取消所有选择
            modeInit('OBJECT')
        def MMD_RIGAlignment(MMD_boneName, RIG_boneName):  # MMD骨骼-Rig骨骼对齐
            DEF_NAME = sys._getframe().f_code.co_name
            modeInit('OBJECT')
            bpy.ops.object.select_pattern(pattern=arm2Name)  # 选择物体
            bpy.context.view_layer.objects.active = arm2Name_Object
            # 判断骨骼是否存在
            if MMD_boneName in arm2Name_Object.data.bones:
                modeInit('EDIT', deselectMode="armature")
                bpy.context.view_layer.objects.active = arm2Name_Object
                bpy.ops.object.select_pattern(pattern=MMD_boneName, extend=False)  # 选择活动骨骼
                MMD_Armature_data = bpy.context.edit_object.data
                MMD_Armature_data_bone = MMD_Armature_data.edit_bones.get(MMD_boneName)
                bpy.context.edit_object.data.edit_bones.active = MMD_Armature_data_bone
                MMD_Armature_data_bone_head = bpy.context.active_bone.head
                MMD_Armature_data_bone_tail = bpy.context.active_bone.tail
                MMD_Armature_data_bone_head_x = MMD_Armature_data_bone_head[0]  # X坐标
                MMD_Armature_data_bone_head_y = MMD_Armature_data_bone_head[1]  # Y坐标
                MMD_Armature_data_bone_head_z = MMD_Armature_data_bone_head[2]  # Z坐标
                MMD_Armature_data_bone_tail_x = MMD_Armature_data_bone_tail[0]
                MMD_Armature_data_bone_tail_y = MMD_Armature_data_bone_tail[1]
                MMD_Armature_data_bone_tail_z = MMD_Armature_data_bone_tail[2]
                modeInit('OBJECT')
                bpy.ops.object.select_pattern(pattern=RigName)  # 选择物体
                bpy.context.view_layer.objects.active = RigName_Object  # 将该物体设置为活动对象
                modeInit('EDIT', deselectMode="armature")
                bpy.ops.object.select_pattern(pattern=RIG_boneName, extend=False)  # 选择活动骨骼
                RIG_Armature_data = bpy.context.edit_object.data  # 获取当前编辑的RIG骨架数据
                RIG_Armature_data_bone = RIG_Armature_data.edit_bones.get(RIG_boneName)  # 获取RIG骨骼
                bpy.context.edit_object.data.edit_bones.active = RIG_Armature_data_bone  # 设置为活动骨骼
                bpy.context.active_bone.head[0] = MMD_Armature_data_bone_head_x  # 修改头部的x坐标
                bpy.context.active_bone.head[1] = MMD_Armature_data_bone_head_y  # 修改头部的y坐标
                bpy.context.active_bone.head[2] = MMD_Armature_data_bone_head_z  # 修改头部的z坐标
                bpy.context.active_bone.tail[0] = MMD_Armature_data_bone_tail_x  # 修改尾部的x坐标
                bpy.context.active_bone.tail[1] = MMD_Armature_data_bone_tail_y  # 修改尾部的y坐标
                bpy.context.active_bone.tail[2] = MMD_Armature_data_bone_tail_z  # 修改尾部的z坐标
                bpy.ops.object.select_pattern(pattern="spine", extend=False)  # 选择活动骨骼
                bpy.context.edit_object.data.edit_bones.active = bpy.context.edit_object.data.edit_bones.get("spine")  # 设置活动骨骼
                bpy.ops.armature.parent_clear(type='DISCONNECT')  # 清除父子关系
                bpy.ops.armature.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                print(f"[{printer}/{DEF_NAME}]骨骼 {MMD_boneName} 不存在。")
                self.report({'WARNING'}, "骨骼不存在。")
        def addBoneParent(childBoneName, parentBoneName):  # 加骨父级
            bpy.ops.object.mode_set(mode='EDIT')  # 切换到编辑模式
            armature = bpy.context.object  # 获取骨架对象
            # 获取父骨骼和子骨骼
            childBone = armature.data.edit_bones.get(childBoneName)
            parentBone = armature.data.edit_bones.get(parentBoneName)
            if parentBone.parent == childBone:
                parentBone.parent = None
            childBone.parent = parentBone  # 设置父子关系
        def selectBones(bone):  # 选择骨骼
            bpy.ops.object.select_pattern(pattern=bone, extend=False)  # 选择活动骨骼，不扩展选择（extend=False）
            data = bpy.context.edit_object.data  # 获取当前编辑对象（骨架）的数据
            bone = data.edit_bones.get(bone)  # 从骨架的编辑骨骼集合中获取指定名称的骨骼
            bpy.context.edit_object.data.edit_bones.active = bone
        def copyParentsBone(bone):  # 复制父级骨骼
            modeInit('OBJECT')
            bpy.ops.object.select_pattern(pattern=rigifyName)  # 选择物体
            bpy.context.view_layer.objects.active = bpy.data.objects[rigifyName]  # 将该物体设置为活动对象
            modeInit('EDIT', deselectMode="armature")
            selectBones(bone)
            # 复制
            bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={
                                                "do_flip_names": False},
                                            TRANSFORM_OT_translate={
                                                "value": (0, 0, 0),
                                                "orient_type": 'GLOBAL',
                                                "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1))})
            bpy.context.active_bone.name = bone + 'Parent'  # 改名称
            bpy.ops.armature.parent_clear(type='CLEAR')  # 清空父级
            bpy.ops.object.mode_set(mode='POSE')  # 进入姿态模式
            poseBones = bpy.context.selected_pose_bones  # 删除当前选中骨骼所有约束
            for bone in poseBones:
                for constraint in bone.constraints:
                    bone.constraints.remove(constraint)
        def copyRotation(armature, bone, bone_1):  # 复制旋转
            modeInit('OBJECT')
            bpy.ops.object.select_pattern(pattern=armature)  # 选择物体
            armature_Object = bpy.data.objects[armature]
            bpy.context.view_layer.objects.active = armature_Object  # 将该物体设置为活动对象
            # 判断骨骼是否存在
            if bone in armature_Object.data.bones:
                modeInit('OBJECT')
                bpy.context.view_layer.objects.active = armature_Object  # 将该物体设置为活动对象
                modeInit('POSE', deselectMode="pose")
                bpy.context.active_object.pose.bones[bone].bone.select = True  # 将该骨骼设置为选中状态
                bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[bone].bone  # 将骨骼设置为活动骨骼
                bpy.ops.pose.constraint_add(type='COPY_ROTATION')  # 添加约束
                constraintName = bpy.context.active_object.pose.bones[bone].constraints[-1].name  # 获取新的约束名称
                constraints_name = 'MMR_复制旋转'
                bpy.context.object.pose.bones[bone].constraints[constraintName].name = constraints_name
                # 设置参数
                bpy.context.object.pose.bones[bone].constraints[constraints_name].target = bpy.data.objects[armature]
                bpy.context.object.pose.bones[bone].constraints[constraints_name].subtarget = bone_1
                bpy.context.object.pose.bones[bone].constraints[constraints_name].influence = 0.5
        def bonesAlignmnet(armature, armature_bone, armature_1, armature_1_bone):  # 骨骼对齐
            '''
                骨骼 armature_bone 对齐到骨骼 armature_1_bone
            '''
            DEF_NAME = sys._getframe().f_code.co_name
            modeInit('OBJECT')
            bpy.ops.object.select_pattern(pattern=armature_1)  # 选择物体
            armature_1_Object = bpy.data.objects[armature_1]
            bpy.context.view_layer.objects.active = armature_1_Object  # 将该物体设置为活动对象
            # 判断骨骼是否存在
            if armature_1_bone in armature_1_Object.data.bones:
                modeInit('EDIT', deselectMode="armature")
                bpy.context.view_layer.objects.active = armature_1_Object  # 将该物体设置为活动对象
                bpy.ops.object.select_pattern(pattern=armature_1_bone, extend=False)  # 选择活动骨骼
                armature_1_bone_data = bpy.context.edit_object.data
                armature_1_bone_data_bone = armature_1_bone_data.edit_bones.get(armature_1_bone)
                bpy.context.edit_object.data.edit_bones.active = armature_1_bone_data_bone
                armature_1_bone_data_bone_head = bpy.context.active_bone.head
                armature_1_bone_data_bone_tail = bpy.context.active_bone.tail
                armature_1_bone_data_bone_head_x = armature_1_bone_data_bone_head[0]  # X坐标
                armature_1_bone_data_bone_head_y = armature_1_bone_data_bone_head[1]  # Y坐标
                armature_1_bone_data_bone_head_z = armature_1_bone_data_bone_head[2]  # Z坐标
                armature_1_bone_data_bone_tail_x = armature_1_bone_data_bone_tail[0]
                armature_1_bone_data_bone_tail_y = armature_1_bone_data_bone_tail[1]  # Z坐标
                armature_1_bone_data_bone_tail_z = armature_1_bone_data_bone_tail[2]
                modeInit('OBJECT')
                bpy.ops.object.select_pattern(pattern=armature)  # 选择物体
                armature_Object = bpy.data.objects[armature]
                bpy.context.view_layer.objects.active = armature_Object  # 将该物体设置为活动对象
                modeInit('EDIT', deselectMode="armature")
                bpy.ops.object.select_pattern(pattern=armature_bone, extend=False)  # 选择活动骨骼
                armature_bone_data = bpy.context.edit_object.data  # 获取当前编辑的RIG骨架数据
                armature_bone_data = armature_bone_data.edit_bones.get(armature_bone)  # 获取RIG骨骼
                bpy.context.edit_object.data.edit_bones.active = armature_bone_data  # 设置为活动骨骼
                bpy.context.active_bone.head[0] = armature_1_bone_data_bone_head_x  # 修改头部的x坐标
                bpy.context.active_bone.head[1] = armature_1_bone_data_bone_head_y  # 修改头部的y坐标
                bpy.context.active_bone.head[2] = armature_1_bone_data_bone_head_z  # 修改头部的z坐标
                bpy.context.active_bone.tail[0] = armature_1_bone_data_bone_tail_x  # 修改尾部的x坐标
                bpy.context.active_bone.tail[1] = armature_1_bone_data_bone_tail_y  # 修改尾部的y坐标
                bpy.context.active_bone.tail[2] = armature_1_bone_data_bone_tail_z  # 修改尾部的z坐标
                bpy.ops.armature.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                print(f"[{printer}/{DEF_NAME}]骨骼 {armature_1_bone} 不存在。")
                self.report({'WARNING'}, f"骨骼 {armature_1_bone} 不存在。")       
        def addConstraints(constraintType, armatureName, armature_boneName, targetArmatureName, targetArmature_boneName, **constraintParams):  # 添加约束
            '''
                armatureName 的 armature_boneName 是被约束对象
                @param constraintType 约束类型，支持 "复制位置"（COPY_LOCATION）, "复制旋转"（COPY_ROTATION）, "复制缩放"（COPY_SCALE）, "复制变换"（COPY_TRANSFORM）
                @param armatureName 被约束物体名称
                @param armature_boneName 被约束骨骼名称
                @param targetArmatureName 目标物体名称
                @param targetArmature_boneName 目标骨骼名称
                @param constraintParams 约束参数
            '''
            DEF_NAME = sys._getframe().f_code.co_name
            # 参数检查
            if constraintType not in ["复制位置", "复制旋转", "复制缩放", "复制变换"]:
                print(f"[{printer}/{DEF_NAME}]约束类型 {constraintType} 不在支持的约束类型中。")
                self.report({'WARNING'}, f"约束类型 {constraintType} 不在支持的约束类型中。")
                return False
            try:
                armature_object = bpy.data.objects[armatureName]
                targetArmature_object = bpy.data.objects[targetArmatureName]
            except KeyError:
                print(f"[{printer}/{DEF_NAME}]物体 {armatureName} 或 {targetArmatureName} 不存在。")
                self.report({'WARNING'}, f"物体 {armatureName} 或 {targetArmatureName} 不存在。")
                return False
            if armature_boneName not in armature_object.pose.bones:
                print(f"[{printer}/{DEF_NAME}]骨骼 {armature_boneName} 不存在。")
                self.report({'WARNING'}, f"骨骼 {armature_boneName} 不存在。")
                return False
            if targetArmature_boneName not in targetArmature_object.pose.bones:
                print(f"[{printer}/{DEF_NAME}]骨骼 {targetArmature_boneName} 不存在。")
                self.report({'WARNING'}, f"骨骼 {targetArmature_boneName} 不存在。")
                return False
            # 加载约束参数
            armature_bone = armature_object.pose.bones[armature_boneName]
            constraint_nameMap = {
                "复制位置": "COPY_LOCATION",
                "复制旋转": "COPY_ROTATION",
                "复制缩放": "COPY_SCALE",
                "复制变换": "COPY_TRANSFORMS"}
            enableBoneRollSynchronized = constraintParams.get('扭转同步', False)  # 设置是否启用扭转同步
            enableCorrectRoll = constraintParams.get('修正旋转', False)  # 设置是否启用修正旋转
            enableX = constraintParams.get('启用X轴', True)  # 设置是否启用X轴
            enableY = constraintParams.get('启用Y轴', True)  # 设置是否启用Y轴
            enableZ = constraintParams.get('启用Z轴', True)  # 设置是否启用Z轴
            invertX = constraintParams.get('反转X轴', False)  # 设置X轴上是否反转
            invertY = constraintParams.get('反转Y轴', False)
            invertZ = constraintParams.get('反转Z轴', False)
            mixMode = constraintParams.get('混合模式', 'REPLACE')  # 设置混合模式为替换
            targetSpace = constraintParams.get('目标空间', 'WORLD')  # 设置目标空间为世界空间
            ownerSpace = constraintParams.get('所有者空间', 'WORLD')  # 设置所有者空间为世界空间
            # 设置约束
            constraint = armature_bone.constraints.new(type=constraint_nameMap[constraintType])  
            constraint.name = f'[MMRA]{constraintType}'  # 重命名复制变换约束
            constraint.target = bpy.data.objects[targetArmatureName]  # 设置约束目标对象，将约束的目标对象设置为 targetArmatureName
            constraint.subtarget = targetArmature_boneName  # 设置约束目标子骨骼，将约束的目标子骨骼设置为 targetArmature_boneName
            if enableBoneRollSynchronized:
                boneRollSynchronized(targetArmatureName, targetArmature_boneName, armatureName, armature_boneName)  # 复制 armature_bone 的扭转值到 targetArmature_boneName
            if enableCorrectRoll:
                correctRoll(armature_boneName)  # 修正 armature_bone 的旋转值
            if constraintType not in ["复制位置", "复制缩放"]:
                constraint.mix_mode = mixMode  # 设置混合模式
            if constraintType != "复制变换":
                constraint.use_x = enableX  # 设置是否启用X轴
                constraint.use_y = enableY  # 设置是否启用Y轴
                constraint.use_z = enableZ  # 设置是否启用Z轴
                if constraintType not in ["复制缩放"]:
                    constraint.invert_x = invertX  # 设置X轴上是否反转
                    constraint.invert_y = invertY  # 设置Y轴上是否反转
                    constraint.invert_z = invertZ  # 设置Z轴上是否反转
                constraint.target_space = targetSpace  # 设置目标空间
                constraint.owner_space = ownerSpace  # 设置所有者空间
            return True
        def boneRollSynchronized(armatureName: str, armature_boneName: str, armature01Name: str, armature01Name_boneName: str):  # 骨骼扭转同步
            '''
                将 armature_bone 的扭转值同步到 armature01Name_boneName
                @param armatureName: 骨架名称
                @param armature_boneName: 要同步扭转值的骨骼名称
                @param armature01Name: 要同步扭转值的目标骨架名称
                @param armature01Name_boneName: 要同步扭转值的目标骨骼名称
            '''
            DEF_NAME = sys._getframe().f_code.co_name
            originalMode = bpy.context.object.mode if bpy.context.object != None else 'OBJECT'  # 记录当前模式  # 获取当前活动对象的模式
            armatureName_Object = bpy.data.objects.get(armatureName)
            armature01Name_Object = bpy.data.objects.get(armature01Name)
            # armatureName
            if not armatureName_Object or not armature01Name_Object:
                print(f'[{printer}/{DEF_NAME}]未找到指定的骨架物体！')
                self.report({'ERROR'}, '未找到指定的骨架物体！')
                return False             
            bpy.context.view_layer.objects.active = armatureName_Object  # 将该物体设置为活动对象
            modeInit('EDIT', deselectMode='armature')
            armature_bone = armatureName_Object.data.edit_bones.get(armature_boneName)  # 从骨架的编辑骨骼集合中获取名为armature_boneName的骨骼并赋值给变量armature_bone
            if not armature_bone:
                print(f'[{printer}/{DEF_NAME}]骨骼 {armature_boneName} 未找到！')
                self.report({'ERROR'}, f'骨骼 {armature_boneName} 未找到！')
                return False
            armature_bone_roll = armature_bone.roll  # 获取当前活动骨骼的扭转值（roll）
            # armature01Name
            bpy.context.view_layer.objects.active = armature01Name_Object
            modeInit('EDIT', deselectMode='armature')
            armature01Name_bone = armature01Name_Object.data.edit_bones.get(armature01Name_boneName)  # 从骨架的编辑骨骼集合中获取名为armature01Name_boneName的骨骼并赋值给变量armature01Name_bone
            if not armature01Name_bone:
                print(f'[{printer}/{DEF_NAME}]骨骼 {armature01Name_boneName} 未找到！')
                self.report({'ERROR'}, f'骨骼 {armature01Name_boneName} 未找到！')
                return False
            armature01Name_bone.roll = armature_bone_roll  # 设置扭转值
            modeInit(originalMode)
        def delete(type:str, targetName:str, subObjectsNames:list=None):  # 删除
            '''
                @param type: 删除类型，"OBJECT" 或 "BONE"
                @param targetName: 物体名称或骨骼名称
                @param subObjects: 若 type 为 "BONE"，subObjects 为骨骼名称列表
            '''
            DEF_NAME = sys._getframe().f_code.co_name
            targetName_object = bpy.data.objects.get(targetName)
            # 参数检查
            if type not in ["OBJECT", "BONE"]:
                print(f"[{printer}/{DEF_NAME}]删除类型 {type} 不在支持的删除类型中。")
                self.report({'WARNING'}, f"删除类型 {type} 不在支持的删除类型中。")
                return False
            if not targetName_object:
                print(f"[{printer}/{DEF_NAME}]物体 {targetName} 不存在。")
                self.report({'WARNING'}, f"物体 {targetName} 不存在。")
                return False
            # 删除物体
            if type == "OBJECT":
                bpy.data.objects.remove(targetName_object, do_unlink=True)
                return True
            elif type == "BONE":
                # 参数检查
                if not subObjectsNames or not isinstance(subObjectsNames, list):
                    print(f"[{printer}/{DEF_NAME}]删除骨骼 {targetName} 时 subObjectsNames 必须为非空列表。")
                    self.report({'WARNING'}, f"删除骨骼 {targetName} 时 subObjectsNames 必须为非空列表。")
                    return False
                if targetName_object.type != 'ARMATURE':
                    print(f"[{printer}/{DEF_NAME}]物体 {targetName} 不是骨架。")
                    self.report({'WARNING'}, f"物体 {targetName} 不是骨架。")
                    return False
                # 删除骨骼
                originalActive = bpy.context.active_object  # 记录当前活动物体
                originalSelecteds = [obj for obj in bpy.context.selected_objects]  # 记录当前选择物体
                originalMode = bpy.context.object.mode if bpy.context.object != None else 'OBJECT'  # 记录当前模式
                try:
                    bpy.context.view_layer.objects.active = targetName_object  # 将目标物体设置为活动物体
                    bpy.ops.object.mode_set(mode='EDIT')
                    for subObjectName in subObjectsNames:
                        editBone = targetName_object.data.edit_bones.get(subObjectName)
                        if not editBone:
                            print(f"[{printer}/{DEF_NAME}]骨骼 {subObjectName} 不存在。")
                            self.report({'WARNING'}, f"骨骼 {subObjectName} 不存在。")
                            continue
                        targetName_object.data.edit_bones.remove(editBone)
                    return True
                finally:
                    bpy.ops.object.mode_set(mode=originalMode)  # 恢复到原始模式
                    bpy.context.view_layer.objects.active = originalActive  # 恢复到原始活动物体
                    bpy.ops.object.select_all(action='DESELECT')  # 清空选择
                    for object in originalSelecteds:
                        object.select_set(True)  # 恢复到原始选择物体
        print(f"[{printer}]函数组加载完成！")

        # 作用应用初始动作并对齐骨骼
        applyCustomInitialActions()  # 应用初始动作
        for key, value in JSON_text["对齐"].items():  # 对齐MMD-RIG骨骼
            if value == '#':
                continue # 跳过注释行
            elif value == 'spine.004':
                mergeBones(RigName, value)
                print(f"[{printer}]骨骼{value}融并完成！")
            elif isinstance(value, list):
                for RIG_boneName in value:
                    MMD_RIGAlignment(key, RIG_boneName)
            else:
                MMD_RIGAlignment(key, value)
        delete("BONE", RigName, ['breast.R', 'breast.L', 'pelvis.R', 'pelvis.L'])  # 删除多余骨骼
        print(f"[{printer}]应用初始动作完成（若有），骨骼对齐完成，冗余骨骼移除完成！")

        # 作用生成Rigify控制器并设置联动
        bpy.ops.object.select_all(action='DESELECT')  # 清空选择
        bpy.ops.object.select_pattern(pattern=RigName)  # 选择物体
        bpy.context.view_layer.objects.active = RigName_Object  # 将该物体设置为活动对象
        self.spineContinuityVerify(RigName)  # 确保脊柱骨骼连续性
        if "spine.007" in RigName_Object.data.bones:
            modeInit('EDIT', deselectMode="armature")
            delete("BONE", RigName, ['spine.007'])
            print(f"[{printer}]骨骼spine.007移除完成！")
            modeInit('OBJECT')
        bpy.ops.pose.rigify_generate('INVOKE_DEFAULT')  # 生成Rigify控制器
        rigifyName = bpy.context.active_object.name  # 当前活动物体（rigify控制器）名称
        bpy.context.object.data.collections_all["ORG"].is_visible = True  # 显示ORG
        # 眼睛
        copyParentsBone('ORG-eye.L')
        copyParentsBone('ORG-eye.R')
        if MMRA.shoulderLinkage:
            # 肩膀
            copyParentsBone('ORG-shoulder.R')
            copyParentsBone('ORG-shoulder.L')
        bpy.ops.object.mode_set(mode='POSE')  # 进入姿态模式
        bpy.ops.pose.armature_apply(selected=False)  # 应用姿态
        # 添加父级骨骼，眼睛
        addBoneParent('ORG-eye.LParent', 'ORG-eye.L')
        addBoneParent('ORG-eye.RParent', 'ORG-eye.R')
        modeInit('OBJECT')
        bpy.context.view_layer.objects.active = armName_Object
        addBoneParent('肩C.L', '腕.L')  # 肩膀控制器父级设置为腕.L，以保证手臂装饰联动
        addBoneParent('肩C.R', '腕.R')
        bonesAlignmnet(rigifyName, 'ORG-eye.L', armName, '目.L')
        bonesAlignmnet(rigifyName, 'ORG-eye.R', armName, '目.R')
        bpy.context.view_layer.objects.active = RigName_Object
        if MMRA.shoulderLinkage:  # 肩膀
            addBoneParent('ORG-shoulder.RParent', 'ORG-RIG_armatue.R')
            addBoneParent('ORG-shoulder.LParent', 'ORG-RIG_armatue.L')
        for key, value in JSON_text['添加约束'].items():  # 添加约束
            if value == '#':
                continue  # 跳过注释行
            elif key == '下半身':  # 针对骨骼“下半身“做特殊处理
                for type , param in [("复制位置", {"目标空间": "POSE", "所有者空间": "POSE"}),
                                     ("复制旋转", {"目标空间": "POSE", "所有者空间": "POSE", "反转X轴": True}),
                                     ("复制缩放", {"目标空间": "POSE", "所有者空间": "POSE"})]:
                    addConstraints(type, armName, key, rigifyName, value, **param)
            elif key == '足首D.R' or key == '足首D.L':
                addConstraints("复制旋转", armName, key, rigifyName, value, **{"启用X轴": False})
            elif key == '足先EX.R' or key == '足先EX.L':
                addConstraints("复制旋转", armName, key, rigifyName, value, **{"目标空间": "POSE", "所有者空间": "POSE", "扭转同步": True})
            elif isinstance(value, list):
                for RIG_boneName in value:
                    addConstraints("复制变换", armName, key, rigifyName, value, **{"扭转同步": True, "修正旋转": True})
            else:
                addConstraints("复制变换", armName, key, rigifyName, value, **{"扭转同步": True, "修正旋转": True})
        modeInit('OBJECT')
        print(f"[{printer}]约束添加完成！")
    
        bpy.ops.object.select_pattern(pattern=rigifyName)
        rigifyName_Object = bpy.data.objects[rigifyName]
        bpy.context.view_layer.objects.active = rigifyName_Object  # 将该物体设置为活动对象
        # 设置可见性
        bonesCollection = ["ORG",
                           "Face (Primary)", "Face (Secondary)",
                           "Torso (Tweak)", "Fingers (Detail)",
                           "Arm.L (FK)", "Arm.R (FK)", "Arm.L (Tweak)", "Arm.R (Tweak)",
                           "Leg.L (FK)", "Leg.R (FK)", "Leg.L (Tweak)", "Leg.R (Tweak)"]
        for collectionName in bonesCollection:
            if collectionName in bpy.context.object.data.collections:
                bpy.context.object.data.collections[collectionName].is_visible = False
            else:
                print(f"[{printer}]骨骼集合 {collectionName} 不存在，设置可见性失败！")
                self.report({'WARNING'}, f"骨骼集合 {collectionName} 不存在，设置可见性失败！")
        bpy.context.object.show_in_front = True  # Rigify控制器骨架设置为始终显示在最前面
        modeInit('EDIT', deselectMode="armature")
        selectBones('thigh_ik.L')  # 选择活动骨骼
        thigh_z = bpy.context.active_bone.tail[2]  # 获取活动骨骼的Z坐标
        bpy.ops.armature.select_all(action='DESELECT')  # 取消所有选择
        selectBones('torso')  # 选择活动骨骼
        # 复制
        bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={
                                            "do_flip_names": False},
                                        TRANSFORM_OT_translate={
                                            "value": (0, 0, 0),
                                            "orient_type": 'GLOBAL',
                                            "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1))})
        bpy.context.active_bone.name = "torso_root"  # 改名称
        bpy.context.active_bone.tail[2] = thigh_z
        bpy.context.active_bone.head[2] = thigh_z
        bpy.ops.armature.parent_clear(type='CLEAR')  # 清除父级
        addBoneParent('torso', 'torso_root')
        addBoneParent('hand_ik.R', 'torso_root')
        addBoneParent('hand_ik.L', 'torso_root')
        addBoneParent('torso_root', 'root')
        bpy.ops.object.mode_set(mode='POSE')  # 进入姿态模式
        bpy.context.active_pose_bone.custom_shape = bpy.data.objects["WGT-rig_root"]  # 为当前选中的姿态骨骼设置自定义控制器形状
        bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'  #将变换中心点设为独立原点，便于单独操作骨骼
        bpy.context.object.pose.use_auto_ik = True  #  开启自动IK功能，让骨骼链能够自然跟随末端控制器
        # 隐藏骨骼
        boneNames = ["jaw_master", "teeth.T", "teeth.B", "nose_master", "tongue_master"]
        for boneName in boneNames:
            if boneName in bpy.data.objects[rigifyName].data.bones:
                arm2Name_Object_head = bpy.data.objects[rigifyName].data.bones[boneName]
                arm2Name_Object_head.hide = True
        # 关闭ik拉伸
        bpy.context.object.pose.bones["thigh_parent.R"]["IK_Stretch"] = 0
        bpy.context.object.pose.bones["thigh_parent.L"]["IK_Stretch"] = 0
        bpy.context.object.pose.bones["upper_arm_parent.L"]["IK_Stretch"] = 0
        bpy.context.object.pose.bones["upper_arm_parent.R"]["IK_Stretch"] = 0
        bpy.ops.pose.select_all(action='DESELECT')  # 取消所有选择
        if MMRA.polarTarget:  # 是否启用级向
            bones = [('upper_arm_ik.L', 'upper_arm_parent.L'), ('upper_arm_ik.R', 'upper_arm_parent.R')]
            for ik_bone_name, parent_bone_name in bones:
                # 设置IK骨骼为活动骨骼并选择
                ik_bone = bpy.context.active_object.pose.bones[ik_bone_name].bone
                ik_bone.select = True
                bpy.context.active_object.data.bones.active = ik_bone
                bpy.context.object.pose.bones[parent_bone_name]["pole_vector"] = True  # 启用级向
                ik_bone.select = False  # 取消选择当前骨骼以便下次循环
        if MMRA.shoulderLinkage:  # 肩膀联动
            copyRotation(rigifyName, 'shoulder.R', 'ORG-shoulder.R_parent')
            copyRotation(rigifyName, 'shoulder.L', 'ORG-shoulder.L_parent')
        bpy.context.active_object.pose.bones['root'].select = True
        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones['root'].bone
        
        # 作用处理外源问题（启用MCH-heel.02_roll2轴向）
        modeInit('POSE', deselectMode="pose")
        for roll2BoneName in ['MCH-heel.02_roll2.L', 'MCH-heel.02_roll2.R']:
            roll2Bone = rigifyName_Object.pose.bones[roll2BoneName]  # 从骨架的编辑骨骼集合中获取名为roll2BoneName的骨骼并赋值给变量roll2_bone
            if not roll2Bone:  # 如果未找到该骨骼
                print(f'[{printer}]骨骼 {roll2BoneName} 未找到！') 
                self.report({'ERROR'}, f'骨骼 {roll2BoneName} 未找到！')
                continue
            LRsuffix = roll2BoneName[-1:]  # 获取骨骼名称的后缀（如.L或.R）
            targetBoneName = f'foot_heel_ik.{LRsuffix}'  # 构建目标骨骼名称（如MCH-heel.L）
            for constraint in roll2Bone.constraints:  # 遍历roll2Bone的所有约束
                if (constraint.type == 'COPY_ROTATION' and
                    constraint.target.name == rigifyName and
                    constraint.subtarget == targetBoneName):
                    constraint.use_x = True  # 启用X轴旋转
                    constraint.use_y = True
                    constraint.use_z = True
            
        # 作用处理表层细节
        bpy.ops.object.mode_set(mode='OBJECT')  # 切换物体模式
        bpy.context.view_layer.objects.active = bpy.data.objects[rigifyName]  # 确保活动对象正确
        bpy.context.object.name = f'{armName}_{rigifyName}'  # 改名称
        for objectName in [RigName, arm2Name, arm3Name]:  # 遍历物体名称列表，调用delete_object函数删除物体
            delete("OBJECT", objectName)
        bpy.data.objects[armName].hide_set(True)  # 隐藏物体

        print(f"[{printer}]Rigify控制器构造完成！")
        self.report({'INFO'}, 'Rigify控制器构造完成！')
        return {'FINISHED'}