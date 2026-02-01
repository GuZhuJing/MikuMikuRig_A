import os

# 功能获取MMD-RigJSON文件夹路径
def getMMD_RIGFolderPath():
    currentFilePath = os.path.abspath(__file__)
    currentFolderPath = os.path.dirname(os.path.dirname(currentFilePath))
    MMDRIGBoonFolderPath = os.path.join(currentFolderPath,'resources', 'MMD_RIG')
    return os.path.join(MMDRIGBoonFolderPath)

# 功能获取初始姿态文件夹路径
def getInitialPoseFolderPath():
    currentFilePath = os.path.abspath(__file__)
    currentFolderPath = os.path.dirname(os.path.dirname(currentFilePath))
    initialPoseFolderPath = os.path.join(currentFolderPath, 'initialPose')
    return os.path.join(initialPoseFolderPath)

if __name__ == "__main__":
    print("MMD-Rig骨骼绑定文件夹路径：", getMMD_RIGFolderPath())
    print("初始姿态文件夹路径：" , getInitialPoseFolderPath())