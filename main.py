"""
Chrome多实例快捷方式管理器 - 主程序入口

此脚本启动Chrome多实例快捷方式管理器应用程序。
"""

import os
import sys
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from chrome_manager.main_window import ChromeShortcutManager
from chrome_manager.utils import load_system_font
import chrome_manager.constants as constants

def main():
    """主程序入口函数"""
    try:
        # 启用高DPI支持
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        
        app = QApplication(sys.argv)
        
        # 加载字体
        constants.FONT_FAMILY = load_system_font()
        
        # 添加调试信息
        print(f"加载字体: {constants.FONT_FAMILY}")
        print(f"Python版本: {sys.version}")
        try:
            from PyQt6.QtCore import QLibraryInfo
            print(f"PyQt6版本: {QLibraryInfo.version().toString()}")
        except Exception as e:
            print(f"无法获取PyQt6版本: {str(e)}")
        
        window = ChromeShortcutManager()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"程序启动错误: {str(e)}")
        print("详细错误信息:")
        traceback.print_exc()
        print("\n系统信息:")
        print(f"Python版本: {sys.version}")
        print(f"操作系统: {sys.platform}")
        print(f"当前工作目录: {os.getcwd()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 