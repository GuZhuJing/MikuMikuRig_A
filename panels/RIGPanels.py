import bpy
from ..operators.RIG import buildRigifyController
from ..common.i18n.i18n import i18n

class Rig_Opt(bpy.types.Panel):
    bl_label = "Rigify"             # 面板标题，显示在侧边栏中的面板名称
    bl_idname = "SCENE_PT_MMRA_RIG_OPT"  # 面板的唯一标识符
    bl_space_type = "VIEW_3D"          # 指定面板显示在3D视图空间中
    bl_region_type = 'UI'              # 指定面板显示在UI区域（右侧边栏）
    bl_category = "MMRA"               # 指定面板所属的标签页类别，会在3D视图右侧面板显示为"MMRA"标签

    def draw(self, context: bpy.types.Context):
        layout = self.layout  # 从上往下排列
        MMRA = context.object.MMRA
        layout.scale_y = 1.2  # 这将使按钮的垂直尺寸加倍
        layout.operator(buildRigifyController.bl_idname, text="构建控制器", icon="OUTLINER_DATA_ARMATURE")
        layout.prop(MMRA, "RIG_OPT_Extras", text=i18n("额外选项"), toggle=True, icon="PREFERENCES")
        if MMRA.RIG_OPT_Extras:
            layout.prop(MMRA, "bendBones", text=i18n("弯曲骨骼"))
            layout.prop(MMRA, "polarTarget", text=i18n("极向目标"))
            layout.prop(MMRA, "shoulderLinkage", text=i18n("肩部联动"))
            if MMRA.bendBones:
                layout.prop(MMRA, "enableInitialPose", text=i18n("自定义初始姿势"))
                if MMRA.enableInitialPose:
                    layout.prop(MMRA, "initialPoseFilePath")
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None
