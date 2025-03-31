"""
工具函数模块
"""

import os
import sys
import time
import psutil
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont

def check_os_compatibility():
    """
    检查系统兼容性，确保应用程序可以在当前操作系统上运行
    
    Returns:
        bool: 系统是否兼容
        str: 不兼容时的错误消息，兼容时为空字符串
    """
    # 检查操作系统类型
    if sys.platform != 'win32':
        return False, f"当前应用仅支持Windows系统，不支持当前系统({sys.platform})"
    
    # 检查Windows版本
    try:
        import platform
        win_ver = platform.win32_ver()[0]
        # 转换为数字进行比较，例如'10'或'11'
        win_ver_num = float(win_ver) if win_ver.replace('.', '').isdigit() else 0
        
        if win_ver_num < 7:
            return False, f"当前应用要求Windows 7及以上版本，检测到Windows {win_ver}"
    except Exception as e:
        # 如果无法获取Windows版本，则不阻止运行
        print(f"检查Windows版本出错: {str(e)}")
    
    # 检查Python版本
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
        return False, f"当前应用要求Python 3.6及以上版本，检测到Python {sys.version.split()[0]}"
    
    # 确认所有必要的依赖项可用
    required_modules = ['PyQt6', 'psutil', 'requests']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        return False, f"缺少必要的依赖库: {', '.join(missing_modules)}"
    
    # 所有检查都通过
    return True, ""

def load_system_font():
    """
    加载系统默认字体，为UI提供更好的字体支持
    
    Returns:
        str: 字体家族名称
    """
    # 直接返回微软雅黑字体名称，不再尝试加载字体文件
    # 因为Windows系统已经内置了这个字体
    if sys.platform == 'win32':
        return "Microsoft YaHei UI"
    
    # 对于非Windows系统，尝试加载系统默认字体
    return QApplication.font().family()

def apply_font_to_app(app):
    """
    将字体应用到整个应用程序
    
    Args:
        app: QApplication实例
    """
    font_name = load_system_font()
    font = QFont(font_name, 9)
    app.setFont(font)
    
    print(f"应用全局字体: {font_name}")
    
    # 确保所有控件都使用这个字体
    QApplication.setFont(font)

def get_system_info():
    """获取系统信息"""
    info = {}
    
    # 获取CPU信息
    info['cpu_count'] = psutil.cpu_count(logical=True)
    info['cpu_physical'] = psutil.cpu_count(logical=False)
    info['cpu_percent'] = psutil.cpu_percent(interval=0.1)
    
    # 获取内存信息
    mem = psutil.virtual_memory()
    info['memory_total'] = mem.total / (1024 * 1024 * 1024)  # GB
    info['memory_available'] = mem.available / (1024 * 1024 * 1024)  # GB
    info['memory_percent'] = mem.percent
    
    # 获取进程信息
    process = psutil.Process()
    info['process_cpu'] = process.cpu_percent(interval=0.1)
    info['process_memory'] = process.memory_info().rss / (1024 * 1024)  # MB
    
    return info