"""
    return {'FINISHED'}  # 操作成功完成
    return {'CANCELLED'}  # 操作被取消
    return {'RUNNING_MODAL'}  # 操作正在运行(模态操作)
    return {'PASS_THROUGH'}  # 传递事件给其他操作
    return {'INTERFACE'}  # 接口需要更新
    return {'TIMER'}  # 需要定时器事件
    return {'TIMER_REMOVE'}  # 移除定时器
    return {'REGISTER'}  # 注册操作
    return {'UNREGISTER'}  # 注销操作
"""