"""
Chrome多实例快捷方式管理器 - 主程序入口

此脚本启动Chrome多实例快捷方式管理器应用程序。
"""

import os
import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from chrome_manager.main_window import ChromeShortcutManager
from chrome_manager.utils import apply_font_to_app, check_os_compatibility
import chrome_manager.constants as constants

def main():
    """主程序入口函数"""
    try:
        # 检查系统兼容性
        compatible, error_msg = check_os_compatibility()
        if not compatible:
            # 创建临时应用程序对象来显示错误消息
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "系统兼容性错误", 
                                f"无法启动应用程序：\n{error_msg}\n\n请确保您的系统满足运行要求。")
            sys.exit(1)
            
        # 启用高DPI支持
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        
        app = QApplication(sys.argv)
        
        # 应用全局字体
        apply_font_to_app(app)
        
        # 添加调试信息
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