"""
配置管理模块
"""

import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QFont

from .constants import FONT_FAMILY, PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR
from .database_manager import DatabaseManager

class ConfigManager:
    """配置管理类，负责配置的加载和保存"""
    
    def __init__(self, main_window):
        """
        初始化配置管理器
        
        Args:
            main_window: 主窗口实例，用于显示消息对话框
        """
        self.main_window = main_window
        
        # 配置目录路径
        appdata_dir = os.getenv('APPDATA')
        self.config_dir = os.path.join(appdata_dir, 'ChromeShortcuts')
        
        # 确保配置目录存在
        self.ensure_config_dir()
        
        # 初始化数据库管理器
        self.db_manager = DatabaseManager(self.config_dir)
    
    def ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(self.config_dir):
            try:
                os.makedirs(self.config_dir, exist_ok=True)
                print(f"创建配置目录: {self.config_dir}")
            except Exception as e:
                print(f"创建配置目录失败: {str(e)}")
                # 使用状态栏显示错误消息
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(f"创建配置目录失败: {str(e)}", 5000)
        else:
            print(f"配置目录已存在: {self.config_dir}")
    
    def load_config(self):
        """
        加载配置
        
        Returns:
            dict: 配置字典，包含chrome_path, data_root和shortcuts
        """
        print(f"尝试加载配置")
        
        default_config = {
            'chrome_path': r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            'data_root': os.getcwd(),
            'user_modified_data_root': False,
            'shortcuts': [],
            'account_info': {}  # 确保账号信息默认为空字典
        }
        
        try:
            # 从数据库加载配置
            try:
                config = self.db_manager.load_config()
            except Exception as db_err:
                print(f"从数据库加载配置失败，使用默认配置: {str(db_err)}")
                return default_config
            
            # 确保配置包含所有必要的键
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            
            # 验证数据根目录
            if not config.get('data_root') or not os.path.exists(config.get('data_root')):
                if not config.get('data_root'):
                    print("配置中数据根目录为空，使用默认值")
                else:
                    print(f"配置中的数据根目录不存在: {config.get('data_root')}，使用默认值")
                config['data_root'] = os.getcwd()
            
            # 确保账号信息是字典
            if not isinstance(config.get('account_info'), dict):
                config['account_info'] = {}
            
            # 确保shortcuts是列表
            if not isinstance(config.get('shortcuts'), list):
                config['shortcuts'] = []
                
            return config
            
        except Exception as e:
            # 不显示错误对话框，避免弹出额外窗口
            print(f"加载配置错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return default_config
    
    def save_config(self, config):
        """
        保存配置
        
        Args:
            config: 配置字典，包含chrome_path, data_root和shortcuts
        """
        try:
            print(f"\n============ 开始保存配置 ============")
            print(f"保存配置 - Chrome路径: {config.get('chrome_path')}")
            print(f"保存配置 - 数据根目录: {config.get('data_root')}")
            print(f"保存配置 - 快捷方式列表数量: {len(config.get('shortcuts', []))}")
            print(f"保存配置 - 快捷方式详情: {[s.get('name') for s in config.get('shortcuts', [])]}")
            
            # 确保数据根目录不为空
            if not config.get('data_root'):
                config['data_root'] = os.getcwd()
                print(f"数据根目录为空，使用当前目录: {config['data_root']}")
            
            # 确保目录存在
            if not os.path.exists(config.get('data_root')):
                try:
                    os.makedirs(config.get('data_root'), exist_ok=True)
                    print(f"创建数据根目录: {config.get('data_root')}")
                except Exception as e:
                    print(f"创建数据根目录失败: {str(e)}")
            
            # 保存Chrome实例信息
            # 先清空现有实例
            print(f"正在清空数据库中的Chrome实例数据")
            self.db_manager.clear_chrome_instances()
            
            # 重新添加所有实例
            print(f"开始保存{len(config.get('shortcuts', []))}个Chrome实例到数据库")
            for shortcut in config.get('shortcuts', []):
                print(f"  保存实例: {shortcut.get('name')}")
                self.db_manager.save_chrome_instance(shortcut)
            
            # 保存账号信息
            for name, account_data in config.get('account_info', {}).items():
                if any(s["name"] == name for s in config.get('shortcuts', [])):
                    self.db_manager.save_account_info(name, account_data)
            
            # 保存其他配置
            self.db_manager.save_config(config)
            
            print("配置已成功保存")
            print(f"============ 配置保存结束 ============\n")
                
        except Exception as e:
            error_msg = f"保存配置失败：{str(e)}"
            print(f"保存配置错误: {error_msg}")
            # 使用状态栏显示错误消息
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(error_msg, 5000)
            import traceback
            traceback.print_exc()
    
    def show_error_message(self, message):
        """显示错误消息"""
        # 此方法已不再使用，改为使用状态栏显示消息
        # 保留方法签名以防有代码调用，但内部实现改为使用状态栏
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(message, 5000) 