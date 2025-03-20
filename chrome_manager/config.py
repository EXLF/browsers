"""
配置管理模块
"""

import os
import json
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QFont
import winshell

from .constants import FONT_FAMILY, PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR

class ConfigManager:
    """配置管理类，负责配置文件的加载和保存"""
    
    def __init__(self, main_window):
        """
        初始化配置管理器
        
        Args:
            main_window: 主窗口实例，用于显示消息对话框
        """
        self.main_window = main_window
        
        # 配置文件路径
        appdata_dir = os.getenv('APPDATA')
        self.config_file = os.path.join(appdata_dir, 'ChromeShortcuts', 'config.json')
        
        # 确保配置目录存在
        self.ensure_config_dir()
    
    def ensure_config_dir(self):
        """确保配置目录存在"""
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir, exist_ok=True)
                print(f"创建配置目录: {config_dir}")
            except Exception as e:
                print(f"创建配置目录失败: {str(e)}")
                self.show_error_message(f"创建配置目录失败: {str(e)}")
        else:
            print(f"配置目录已存在: {config_dir}")
    
    def load_config(self):
        """
        加载配置
        
        Returns:
            dict: 配置字典，包含chrome_path, data_root和shortcuts
        """
        print(f"尝试加载配置文件: {self.config_file}")
        
        default_config = {
            'chrome_path': r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            'data_root': os.getcwd(),
            'user_modified_data_root': False,
            'shortcuts_path': winshell.desktop(),  # 默认保存在桌面
            'shortcuts': []
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"成功读取配置文件内容: {config}")
                    
                    # 确保配置包含所有必要的键
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    
                    # 验证数据根目录
                    if not config.get('data_root') or not os.path.exists(config.get('data_root')):
                        if not config.get('data_root'):
                            print("配置文件中数据根目录为空，使用默认值")
                        else:
                            print(f"配置文件中的数据根目录不存在: {config.get('data_root')}，使用默认值")
                        config['data_root'] = os.getcwd()
                    
                    # 验证快捷方式保存路径
                    if not config.get('shortcuts_path') or not os.path.exists(config.get('shortcuts_path')):
                        if not config.get('shortcuts_path'):
                            print("配置文件中快捷方式保存路径为空，使用默认值")
                        else:
                            print(f"配置文件中的快捷方式保存路径不存在: {config.get('shortcuts_path')}，使用默认值")
                        config['shortcuts_path'] = winshell.desktop()
                    
                    return config
                    
            except Exception as e:
                self.show_error_message(f"加载配置文件失败：{str(e)}")
                print(f"加载配置文件错误: {str(e)}")
                import traceback
                traceback.print_exc()
                return default_config
        else:
            print("配置文件不存在，将使用默认设置")
            return default_config
    
    def save_config(self, config):
        """
        保存配置
        
        Args:
            config: 配置字典，包含chrome_path, data_root和shortcuts
        """
        try:
            print(f"保存配置 - Chrome路径: {config.get('chrome_path')}")
            print(f"保存配置 - 数据根目录: {config.get('data_root')}")
            print(f"保存配置 - 快捷方式保存路径: {config.get('shortcuts_path')}")
            
            # 确保数据根目录不为空
            if not config.get('data_root'):
                config['data_root'] = os.getcwd()
                print(f"数据根目录为空，使用当前目录: {config['data_root']}")
            
            # 确保快捷方式保存路径不为空
            if not config.get('shortcuts_path'):
                config['shortcuts_path'] = winshell.desktop()
                print(f"快捷方式保存路径为空，使用桌面: {config['shortcuts_path']}")
            
            # 确保目录存在
            if not os.path.exists(config.get('data_root')):
                try:
                    os.makedirs(config.get('data_root'), exist_ok=True)
                    print(f"创建数据根目录: {config.get('data_root')}")
                except Exception as e:
                    print(f"创建数据根目录失败: {str(e)}")
            
            # 确保快捷方式保存目录存在
            if not os.path.exists(config.get('shortcuts_path')):
                try:
                    os.makedirs(config.get('shortcuts_path'), exist_ok=True)
                    print(f"创建快捷方式保存目录: {config.get('shortcuts_path')}")
                except Exception as e:
                    print(f"创建快捷方式保存目录失败: {str(e)}")
            
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            print(f"确保配置目录存在: {config_dir}")
            os.makedirs(config_dir, exist_ok=True)
            
            # 保存配置文件
            print(f"正在保存配置到: {self.config_file}")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"配置已成功保存，数据根目录: {config.get('data_root')}")
            
            # 验证配置文件是否已创建
            if os.path.exists(self.config_file):
                print(f"配置文件已成功创建: {self.config_file}")
                print(f"配置文件大小: {os.path.getsize(self.config_file)} 字节")
            else:
                print(f"警告: 配置文件未能创建: {self.config_file}")
                
        except Exception as e:
            error_msg = f"保存配置文件失败：{str(e)}"
            self.show_error_message(error_msg)
            print(f"保存配置错误: {error_msg}")
            import traceback
            traceback.print_exc()
    
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