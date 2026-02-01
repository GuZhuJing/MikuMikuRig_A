# MikuMikuRig_A
【Blender 插件】傻瓜式MMD K帧插件
## 公告
    1.现代码移除了大量非核心功能并重构全部核心代码。
    2.现代码已更新到Blender 5.0.0版本。
    3.其实代码早在2026年1月月初就，完成的公告的1、2，但不巧的是测试过程中发现三处异常，鄙人不才，调试至天有余未能确定根源并修复，所有在此向各位神通广大的网友求助。
    4.异常均在RIG.py中且已用注释表明（示例：# 异常……）。
    5.异常描述：RIG异常_#1：意外导致编辑对象为metarig（即RIG_Armature_data,应为MMD_Armature_data_bone）
    6.异常描述：RIG异常_#2：数据随机异常（如根目录图 RIG异常_#2.png），已发送Issues，捕获异常数据如下
    （bpy.data.armatures['花火.001'].edit_bones["��.L"]）
    （bpy.data.armatures['花火.001'].edit_bones["�5��"]）
    7.异常描述：RIG异常_#3：意外bpy.context.edit_object.data为空
    8.以上异常均随机发送，没有固定
### 测试平台
|软件/硬件|版本|
|-|-|
|Blender|5.0.0|
|Python包|文件 requirements.txt|
|CPU|Intel(R) Core(TM) i5-14400F|

## 相关信息
原作者_1：https://space.bilibili.com/2708891
原作者_2:https://space.bilibili.com/2109816568