"""
快捷方式管理模块，负责创建和管理Chrome快捷方式
"""

import os
import sys
import winshell
from win32com.client import Dispatch
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QFont

from .constants import FONT_FAMILY, PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR

class ShortcutManager:
    """快捷方式管理类，负责创建和管理Chrome快捷方式"""
    
    def __init__(self, main_window):
        """
        初始化快捷方式管理器
        
        Args:
            main_window: 主窗口实例，用于显示消息对话框
        """
        self.main_window = main_window
        self.desktop_path = winshell.desktop()
    
    def create_shortcut(self, name, data_dir, chrome_path):
        """
        创建Chrome快捷方式
        
        Args:
            name: 快捷方式名称
            data_dir: 数据目录路径
            chrome_path: Chrome可执行文件路径
            
        Returns:
            bool: 是否创建成功
        """
        try:
            shortcut_path = os.path.join(self.desktop_path, f"{name}.lnk")
            
            # 确保数据目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 创建快捷方式
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = chrome_path
            shortcut.Arguments = f'--user-data-dir="{data_dir}"'
            shortcut.Description = f"Chrome - {name}"
            shortcut.IconLocation = f"{chrome_path}, 0"
            shortcut.WorkingDirectory = os.path.dirname(chrome_path)
            shortcut.save()
            
            return True
        except Exception as e:
            self.show_error_message(f"创建快捷方式失败：{str(e)}")
            print(f"创建快捷方式错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def launch_browser(self, chrome_path, data_dir):
        """
        启动浏览器实例
        
        Args:
            chrome_path: Chrome可执行文件路径
            data_dir: 数据目录路径
            
        Returns:
            bool: 是否启动成功
        """
        try:
            import subprocess
            subprocess.Popen([
                chrome_path,
                f'--user-data-dir="{data_dir}"'
            ])
            return True
        except Exception as e:
            self.show_error_message(f"启动Chrome失败：{str(e)}")
            print(f"启动Chrome错误: {str(e)}")
            return False
    
    def show_error_message(self, message):
        """显示错误消息"""
        msg_box = QMessageBox(self.main_window)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("错误")
        msg_box.setText(message)
        msg_box.setFont(QFont(FONT_FAMILY, 9))
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BACKGROUND_COLOR};
            }}
            QLabel {{
                color: {TEXT_PRIMARY_COLOR};
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
                min-height: 30px;
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{
                background-color: #1C75E5;
            }}
            QPushButton:pressed {{
                background-color: #1567D3;
            }}
        """)
        msg_box.exec() 