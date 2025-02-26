"""
全局常量和颜色定义
"""

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

# 全局字体变量
FONT_FAMILY = "Microsoft YaHei UI" if __import__('sys').platform == 'win32' else "Arial" 