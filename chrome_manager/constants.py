"""
全局常量和颜色定义
"""

import sys
from PyQt6.QtWidgets import QApplication

# 颜色常量
PRIMARY_COLOR = "#2382FE"
SUCCESS_COLOR = "#4CAF50"
DANGER_COLOR = "#F44336"
WARNING_COLOR = "#FF9800"
BACKGROUND_COLOR = "#FFFFFF"
SURFACE_COLOR = "#F8F9FA"
BORDER_COLOR = "#E0E0E0"
TEXT_PRIMARY_COLOR = "#333333"
TEXT_SECONDARY_COLOR = "#666666"
TEXT_HINT_COLOR = "#999999"
ACCENT_COLOR = "#2382FE"  # 突出显示颜色
SIDEBAR_BACKGROUND = "#F8F9FA"  # 侧边栏背景颜色

# 全局字体变量
FONT_FAMILY = "Microsoft YaHei UI" if sys.platform == 'win32' else "Arial"

# 获取屏幕尺寸
def get_screen_size():
    """获取主屏幕的尺寸"""
    app = QApplication.instance()
    if not app:
        # 如果没有QApplication实例，创建一个临时的
        app = QApplication([])
    screen = app.primaryScreen()
    size = screen.size()
    return size.width(), size.height()

# 动态调整窗口尺寸
def get_window_size():
    """根据屏幕分辨率返回适合的窗口尺寸"""
    screen_width, screen_height = get_screen_size()
    
    # 根据屏幕分辨率调整窗口大小
    if screen_width <= 1366:  # 低分辨率屏幕(如1366x768)
        return 1000, 700
    elif screen_width <= 1600:  # 中等分辨率(如1600x900)
        return 1100, 750
    else:  # 高分辨率屏幕
        return 1200, 800

# 获取合适的窗口尺寸
WINDOW_WIDTH, WINDOW_HEIGHT = get_window_size()

# 其他尺寸常量
SIDEBAR_WIDTH = 200
MENU_ITEM_HEIGHT = 40 