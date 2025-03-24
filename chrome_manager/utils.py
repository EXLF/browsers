"""
工具函数模块
"""

import os
import sys
import time
import psutil
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont

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