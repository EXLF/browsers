"""
工具函数模块
"""

import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase

def load_system_font():
    """
    加载系统默认字体，为UI提供更好的字体支持
    
    Returns:
        str: 字体家族名称
    """
    # 尝试加载微软雅黑字体，如果失败则使用系统默认字体
    try:
        if os.path.exists("C:/Windows/Fonts/msyh.ttc"):
            font_id = QFontDatabase.addApplicationFont("C:/Windows/Fonts/msyh.ttc")
            if font_id >= 0:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    return font_families[0]
    except Exception:
        pass
    
    # 如果无法加载微软雅黑，返回系统默认字体
    return QApplication.font().family() 