import os
import configparser


# 读取配置文件
def getConfig(filename, section, option):
    # 获取当前目录路径
    proDir = os.path.split(os.path.realpath(__file__))[0]
    # print(proDir)

    # 拼接路径获取完整路径
    configPath = os.path.join(proDir, filename)
    # print(configPath)

    # 创建ConfigParser对象
    conf = configparser.ConfigParser()

    # 读取文件内容
    conf.read(configPath)
    config = conf.get(section, option)
    return config
