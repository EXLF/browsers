"""
快捷方式管理模块，负责创建和管理Chrome快捷方式
"""

import os
import sys
import winshell
from win32com.client import Dispatch
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QFont
import subprocess

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
            # 使用状态栏显示错误消息
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"创建快捷方式失败：{str(e)}", 5000)
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
            print(f"尝试删除快捷方式文件: {shortcut_path}")
            
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print(f"快捷方式文件删除成功: {shortcut_path}")
            else:
                print(f"快捷方式文件不存在: {shortcut_path}")
            
            # 检查是否有相关的Chrome进程在运行
            if self.is_chrome_running(data_dir):
                error_msg = f"无法删除数据目录 '{data_dir}'，因为相关的Chrome浏览器正在运行。请先关闭浏览器后再尝试删除。"
                print(error_msg)
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(error_msg, 5000)
                return False
            
            # 删除数据目录
            print(f"尝试删除数据目录: {data_dir}")
            if os.path.exists(data_dir) and os.path.isdir(data_dir):
                import shutil
                shutil.rmtree(data_dir)
                print(f"数据目录删除成功: {data_dir}")
            else:
                print(f"数据目录不存在或不是目录: {data_dir}")
                
            return True
        except PermissionError as e:
            error_msg = f"删除失败，文件被占用：{str(e)}。请确保所有相关的Chrome浏览器已关闭。"
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(error_msg, 5000)
            print(f"删除快捷方式权限错误: {str(e)}")
            return False
        except Exception as e:
            # 使用状态栏显示错误消息
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"删除快捷方式失败：{str(e)}", 5000)
            print(f"删除快捷方式错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def is_chrome_running(self, data_dir):
        """
        检查与特定数据目录相关的Chrome进程是否在运行
        
        Args:
            data_dir: 数据目录路径
            
        Returns:
            bool: 是否有相关Chrome进程在运行
        """
        try:
            import psutil
            for proc in psutil.process_iter(['name', 'cmdline']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        # 检查命令行中是否包含数据目录路径
                        if data_dir.lower() in cmdline.lower():
                            print(f"找到运行中的Chrome进程，使用数据目录: {data_dir}")
                            return True
            return False
        except Exception as e:
            print(f"检查Chrome进程时出错: {str(e)}")
            return False  # 出错时保守地返回False
    
    def launch_browser(self, shortcut):
        """启动浏览器实例"""
        try:
            # 验证Chrome路径
            if not os.path.exists(self.chrome_path):
                # 使用状态栏显示错误消息
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(f"未找到Chrome浏览器，请在设置中指定正确的Chrome路径", 5000)
                return False
                
            # 确保数据目录存在
            data_dir = os.path.join(self.data_root, shortcut.data_dir)
            os.makedirs(data_dir, exist_ok=True)
            
            # 构建启动命令
            cmd = [
                f'"{self.chrome_path}"',  # 使用引号包裹路径，处理路径中的空格
                f'--user-data-dir="{data_dir}"',  # 指定用户数据目录
                '--no-first-run',  # 跳过首次运行设置
                '--no-default-browser-check',  # 跳过默认浏览器检查
            ]
            
            # 如果有其他启动参数，添加到命令中
            if shortcut.extra_args:
                cmd.extend(shortcut.extra_args.split())
                
            # 启动进程
            subprocess.Popen(' '.join(cmd), shell=True)
            return True
            
        except Exception as e:
            # 使用状态栏显示错误消息
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"启动Chrome时发生错误：{str(e)}", 5000)
            return False
    
    def show_error_message(self, message):
        """显示错误消息"""
        # 此方法已不再使用，改为使用状态栏显示消息
        # 保留方法签名以防有代码调用，但内部实现改为使用状态栏
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(message, 5000) 