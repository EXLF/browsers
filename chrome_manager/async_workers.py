"""
异步工作线程模块

提供各种异步工作线程，用于执行耗时操作，避免阻塞UI线程
"""

import os
import json
import shutil
import time
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

class ExtensionSearchWorker(QThread):
    """扩展搜索工作线程"""
    
    # 定义信号
    finished = pyqtSignal(list)  # 搜索完成信号，传递搜索结果
    progress = pyqtSignal(str)   # 进度信息信号
    error = pyqtSignal(str)      # 错误信号
    
    def __init__(self, extension_manager, keyword):
        """
        初始化搜索工作线程
        
        Args:
            extension_manager: 扩展管理器实例
            keyword: 搜索关键词
        """
        super().__init__()
        self.extension_manager = extension_manager
        self.keyword = keyword
        
    def run(self):
        """线程执行函数"""
        try:
            self.progress.emit("正在搜索扩展...")
            
            # 调用扩展管理器的搜索方法
            results = self.extension_manager.search_extensions_impl(self.keyword, self.progress)
            
            # 发送完成信号
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"搜索扩展时出错: {str(e)}")
            self.finished.emit([])


class BatchInstallWorker(QThread):
    """批量安装扩展工作线程"""
    
    # 定义信号
    finished = pyqtSignal(dict)  # 安装完成信号，传递安装结果
    progress = pyqtSignal(str)   # 进度信息信号
    error = pyqtSignal(str)      # 错误信号
    
    def __init__(self, extension_manager, extension_ids, instance_names):
        """
        初始化批量安装工作线程
        
        Args:
            extension_manager: 扩展管理器实例
            extension_ids: 扩展ID列表
            instance_names: 实例名称列表
        """
        super().__init__()
        self.extension_manager = extension_manager
        self.extension_ids = extension_ids
        self.instance_names = instance_names
        
    def run(self):
        """线程执行函数"""
        try:
            all_results = {}
            total = len(self.extension_ids)
            
            for i, ext_id in enumerate(self.extension_ids):
                self.progress.emit(f"正在安装扩展 {i+1}/{total}...")
                
                # 调用扩展管理器的安装方法
                results = self.extension_manager.install_extension_to_instances(
                    ext_id, self.instance_names
                )
                all_results[ext_id] = results
                
                # 每个扩展安装后稍微延迟，避免Chrome实例同时启动过多
                if i < total - 1:
                    time.sleep(1)
            
            # 发送完成信号
            self.finished.emit(all_results)
            
        except Exception as e:
            self.error.emit(f"批量安装扩展时出错: {str(e)}")
            self.finished.emit({})


class ConfigSaveWorker(QThread):
    """配置保存工作线程"""
    
    # 定义信号
    finished = pyqtSignal(bool)  # 保存完成信号，传递是否成功
    error = pyqtSignal(str)      # 错误信号
    
    def __init__(self, config_file, config):
        """
        初始化配置保存工作线程
        
        Args:
            config_file: 配置文件路径
            config: 配置字典
        """
        super().__init__()
        self.config_file = config_file
        self.config = config
        
    def run(self):
        """线程执行函数"""
        try:
            # 确保目录存在
            config_dir = os.path.dirname(self.config_file)
            os.makedirs(config_dir, exist_ok=True)
            
            # 保存配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            # 发送完成信号
            self.finished.emit(True)
            
        except Exception as e:
            self.error.emit(f"保存配置文件失败: {str(e)}")
            self.finished.emit(False)


class DeleteShortcutWorker(QThread):
    """删除快捷方式工作线程"""
    
    # 定义信号
    finished = pyqtSignal(bool)  # 删除完成信号，传递是否成功
    error = pyqtSignal(str)      # 错误信号
    
    def __init__(self, shortcut_path, data_dir):
        """
        初始化删除快捷方式工作线程
        
        Args:
            shortcut_path: 快捷方式文件路径
            data_dir: 数据目录路径
        """
        super().__init__()
        self.shortcut_path = shortcut_path
        self.data_dir = data_dir
        
    def run(self):
        """线程执行函数"""
        try:
            # 删除快捷方式文件
            if os.path.exists(self.shortcut_path):
                os.remove(self.shortcut_path)
            
            # 删除数据目录
            if os.path.exists(self.data_dir):
                shutil.rmtree(self.data_dir)
            
            # 发送完成信号
            self.finished.emit(True)
            
        except Exception as e:
            self.error.emit(f"删除快捷方式失败: {str(e)}")
            self.finished.emit(False) 