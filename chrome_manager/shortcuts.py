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
        self.shortcuts_dir = self.desktop_path  # 默认使用桌面路径
    
    def set_shortcuts_dir(self, path):
        """
        设置快捷方式保存目录
        
        Args:
            path: 快捷方式保存目录路径
        """
        if path and os.path.exists(path):
            self.shortcuts_dir = path
        else:
            self.shortcuts_dir = self.desktop_path  # 如果路径无效，使用桌面路径
    
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
            # 提取数据目录名称作为Profile名称
            profile_name = os.path.basename(data_dir)
            
            # 创建更简洁的显示名称
            display_name = name
            
            # 创建快捷方式路径
            shortcut_path = os.path.join(self.shortcuts_dir, f"{display_name}.lnk")
            
            # 确保数据目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 确保快捷方式目录存在
            os.makedirs(os.path.dirname(shortcut_path), exist_ok=True)
            
            # 创建快捷方式
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = chrome_path
            shortcut.Arguments = f'--user-data-dir="{data_dir}"'
            shortcut.Description = f"Chrome - {display_name}"
            shortcut.IconLocation = f"{chrome_path}, 0"
            shortcut.WorkingDirectory = os.path.dirname(chrome_path)
            shortcut.save()
            
            print(f"快捷方式已创建: {shortcut_path}")
            return True
        except Exception as e:
            self.show_error_message(f"创建快捷方式失败：{str(e)}")
            print(f"创建快捷方式错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_shortcut(self, name, data_dir):
        """
        删除Chrome快捷方式和数据目录
        
        Args:
            name: 快捷方式名称
            data_dir: 数据目录路径
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 删除快捷方式文件
            shortcut_path = os.path.join(self.shortcuts_dir, f"{name}.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print(f"快捷方式已删除: {shortcut_path}")
            
            # 删除数据目录
            if os.path.exists(data_dir) and os.path.isdir(data_dir):
                import shutil
                shutil.rmtree(data_dir)
                print(f"数据目录已删除: {data_dir}")
                
            return True
        except Exception as e:
            self.show_error_message(f"删除快捷方式失败：{str(e)}")
            print(f"删除快捷方式错误: {str(e)}")
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