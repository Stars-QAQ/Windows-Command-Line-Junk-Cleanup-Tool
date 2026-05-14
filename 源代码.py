import os
import tkinter as tk
from tkinter import filedialog # 导入tkinter库和filedialog模块，用于创建图形界面和文件夹选择对话框
import json                   # 导入json模块，用于处理JSON数据
import shutil                # 导入shutil模块，用于执行高级文件操作，如复制和删除文件
import sys                 # 导入sys模块，用于访问系统相关的功能，如退出程序
import ctypes             # 导入ctypes模块，用于调用Windows API函数
#潮汐の梦
#检查管理员权限的,建议别动
def is_admin():
    """判断当前是否以管理员身份运行"""
    try:
        # 只有管理员才能调用这个Windows API，返回非0代表是管理员
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def run_as_admin():
    """以管理员权限重新启动当前脚本"""
    if sys.argv[0].endswith('.py'):
        # 直接运行 .py 文件：用 python 解释器启动
        args = [sys.executable] + sys.argv
    else:
        # 打包成 exe 后的情况
        args = sys.argv
    # ShellExecuteW 的 runas 参数会弹出UAC确认窗口
    ctypes.windll.shell32.ShellExecuteW(
        None,               # 父窗口句柄
        "runas",            # 以管理员运行
        args[0],            # 程序路径
        " ".join(args[1:]), # 参数
        None,               # 工作目录
        1                   # 窗口显示方式（正常显示）
    )
    sys.exit()  # 退出当前非提权进程
#直到这里都是管理员的东西，别乱动
CONFIG_JSON = "clean_targets.json"   # 配置文件名，可以自己改
def clean_from_json_config():        
    """根据 JSON 配置文件清理文件/文件夹，如不存在则自动创建模板"""    # 定义一个clean_from_json_config函数，用于根据JSON配置文件清理文件或文件夹，如果配置文件不存在则自动创建一个模板
    #  检查文件是否存在，不存在就建模板喵
    if not os.path.exists(CONFIG_JSON):        # 如果配置文件不存在
        print(f"配置文件 '{CONFIG_JSON}' 不存在，正在创建空白模板...")     # 打印配置文件不存在的消息，并提示正在创建空白模板
        temp_path = os.environ.get('TEMP', 'C:\\Windows\\Temp')  # 获取系统临时文件夹路径，作为默认路径之一
        default_config = {
    "targets": [
        {"path": temp_path, "description": "系统临时文件夹"},
        {"path": "D:\\某个软件\\cache", "description": "示例：软件缓存目录"}
    ]
}                                                                            # 定义一个默认配置字典，包含一个"targets"键，对应一个列表，列表中包含两个示例目标路径和描述，可以根据需要修改或添加更多目标
        with open(CONFIG_JSON, 'w', encoding='utf-8') as f:                 # 打开配置文件进行写入，使用UTF-8编码
            json.dump(default_config, f, indent=4, ensure_ascii=False)   # 将默认配置写入JSON文件，使用indent参数格式化输出，ensure_ascii=False确保中文字符正常显示
        print(f"空白模板已创建：{CONFIG_JSON}")
        print("请用记事本打开它，把里面的路径改成你需要清理的目录。")
        return
    # 读取 JSON喵
    try:
        with open(CONFIG_JSON, 'r', encoding='utf-8') as f:             # 打开配置文件并读取内容，使用UTF-8编码
            config = json.load(f)                                       # 将读取到的JSON数据解析为Python对象，存储在config变量中
    except Exception as e:                                              # 如果在读取或解析JSON文件时发生任何异常，捕获异常并打印错误消息
        print(f"读取配置文件出错: {e}")                                 # 打印读取配置文件出错的消息和具体的错误信息
        return
    targets = config.get("targets", [])                                 # 从解析后的配置对象中获取"targets"键对应的值，如果不存在则返回一个空列表，存储在targets变量中
    if not targets:
        print("配置文件中没有写入任何路径。")                             # 如果targets列表为空，打印配置文件中没有写入任何路径的消息，并直接返回，不进行任何清理操作
        return
    # 显示清单，确认
    print(f"\n从 '{CONFIG_JSON}' 中读取到 {len(targets)} 个目标：")     # 打印从配置文件中读取到的目标数量，并提示用户确认要删除这些目标
    for i, item in enumerate(targets, 1):
        path = item.get("path", "")
        desc = item.get("description", "")
        print(f"  {i}. [{desc}]  {path}")
    confirm = input("\n确认删除以上所有文件/文件夹吗？(y/n): ").strip().lower()     # 获取用户输入的确认选项，并去除两端的空白字符，转换为小写字母
    if confirm != 'y':
        print("操作已取消。")
        return
    # 执行删除w
    deleted = 0
    failed = 0
    for item in targets:
        path = item.get("path", "")
        if not os.path.exists(path):
            print(f"⚠ 路径不存在，跳过: {path}")
            continue
        try:
            if os.path.isfile(path):
                os.remove(path)
                print(f"✓ 已删除文件: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path)          # 删除整个文件夹（哪怕里面不空）
                print(f"✓ 已删除文件夹: {path}")
            deleted += 1
        except Exception as e:
            print(f"✗ 删除失败: {path} - {e}")
            failed += 1
    print(f"\n清理完成：成功 {deleted} 个，失败 {failed} 个。")
def select_folder():           # 定义一个select_folder函数，用于弹出文件夹选择对话框，并返回用户选择的文件夹路径
    """弹出对话框选文件夹，返回路径，取消返回空"""
    root = tk.Tk()                          # 创建一个Tkinter主窗口
    root.withdraw()                         # 隐藏主窗口
    folder = filedialog.askdirectory(title="请选择要扫描的文件夹") # 弹出文件夹选择对话框，标题为“请选择要扫描的文件夹”，并将用户选择的路径存储在folder变量中
    root.destroy()                          # 销毁主窗口
    return folder if folder else ""         # 选了就返回路径，没选返回空字符串
def clean_empty_folders(path):         # 定义一个clean_empty_folders函数，用于删除指定路径的空文件夹
    if not os.path.exists(path):       # 如果路径不存在
        print("路径不存在！")           # 打印路径不存在
        return                         # 直接返回，不做任何事
    #下面要开始删除空文件夹了
    #先搜集信息w，好难啊
    else:                              # 否则
        empty_list = []              # 定义一个空列表empty_list，用于存储空文件夹的路径
        for root, dirs, files in os.walk(path):  # 使用os.walk函数遍历指定路径下的所有文件夹和文件
            if not dirs and not files:             # 如果当前目录没有子目录和文件
                empty_list.append(root)   # 如果当前目录没有子目录和文件，则将其添加到empty_list列表中
         #如果没有文件夹为空，就直接返回
        if len(empty_list) == 0:
                print("没有空文件夹欸，换个目录试试吧！")  # 如果empty_list列表为空，则打印没有空文件夹
                return                         # 直接返回，不做任何事
        #如果有空文件夹，就删除它们
        else:                              # 否则
            # 1. 展示列表（带编号）
            print(f"\n找到 {len(empty_list)} 个空文件夹：")# 打印找到的空文件夹数量
            for i, folder in enumerate(empty_list, 1):# 使用enumerate函数遍历empty_list列表中的每个空文件夹路径，并打印带编号的空文件夹路径
                print(f"  {i}. {folder}")# 打印带编号的空文件夹路径
            # 依旧选择，依旧if,还在嵌套
            scxx=input("\n是否删除这些空文件夹？(y/n): ")# 获取用户输入的是否删除空文件夹的选项，并去除两端的空白字符
            if scxx.lower() == 'y':          # 如果用户输入的是'y'（不区分大小写）
                for empty in empty_list:         # 遍历empty_list列表中的每个空文件夹路径
                    try:                        # 尝试删除空文件夹
                        os.rmdir(empty)          # 使用os.rmdir函数删除空文件夹
                        print(f"已删除空文件夹: {empty}")  # 打印已删除的空文件夹路径
                    except OSError as e:          # 如果删除过程中发生错误
                        print(f"无法删除 {empty}: {e}")  # 打印无法删除的空文件夹路径和错误信息
            elif scxx.lower() == 'n':                          # 否则
                print("好嘛，不删了QAQ")  # 打印我不删了，白选了
                return                         # 直接返回，不做任何事
            else:                              # 否则
                print("输入无效，默认不删除空文件夹。")  # 打印输入无效的消息，并默认不删除空文件夹
                return                         # 直接返回，不做任何事
#检查管理员权限，如果没有就提权
if __name__ == "__main__":
    # 如果当前不是管理员，就重新以管理员身份启动
    if not is_admin():
        print("需要管理员权限才能执行清理操作，正在请求提权...")
        run_as_admin()
#该打印界面了
while True:
    print("\n欢迎使用空文件夹清理工具！")
    print("1. 清理空文件夹工具")
    print("2. 复制文件目录下文件路径，方便给ai分析")
    print("3. 一键清理c盘垃圾文件，根据配置文件清理（首次运行会创建一个配置文件模板）")
    print("4. 退出程序")
    xuanxiang = input("请输入选项（1-4）: ").strip()
    if xuanxiang == "1":
        path = select_folder()
        if path:
            clean_empty_folders(path)
    elif xuanxiang == "2":
        print("该功能尚未实现，敬请期待！（其实是我懒得写了）")
    elif xuanxiang == "3":
            clean_from_json_config()
    elif xuanxiang == "4":
        print("再见咯！呜呜呜")
        break
    else:
        print("无效选项，请重新输入。")
