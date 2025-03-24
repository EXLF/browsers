import os
import json
import webbrowser
import requests
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication

class ScriptUpdater(QThread):
    """脚本更新检查器"""
    
    update_available = pyqtSignal(list)  # 发送可用更新列表
    update_complete = pyqtSignal(bool, str)  # 更新完成信号
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # 使用你GitHub仓库的原始链接
        self.metadata_url = "https://raw.githubusercontent.com/EXLF/chrome-scripts/refs/heads/main/scripts_metadata.json"
        
        # 本地存储的脚本信息文件
        app_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "ChromeShortcuts")
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)
        
        self.local_metadata_file = os.path.join(app_data_dir, "scripts_metadata.json")
    
    def run(self):
        """检查脚本更新"""
        try:
            # 获取最新元数据
            response = requests.get(self.metadata_url, timeout=10)
            response.raise_for_status()
            
            server_data = response.json()
            server_scripts = server_data.get("scripts", [])
            
            # 读取本地元数据
            local_scripts = []
            if os.path.exists(self.local_metadata_file):
                with open(self.local_metadata_file, 'r', encoding='utf-8') as f:
                    try:
                        local_data = json.load(f)
                        local_scripts = local_data.get("scripts", [])
                    except json.JSONDecodeError:
                        local_scripts = []
            
            # 比较版本，找出需要更新的脚本
            updates_available = []
            for server_script in server_scripts:
                is_new = True
                for local_script in local_scripts:
                    if server_script["id"] == local_script["id"]:
                        is_new = False
                        if self._compare_versions(server_script["version"], local_script["version"]) > 0:
                            updates_available.append(server_script)
                        break
                
                if is_new:
                    updates_available.append(server_script)
            
            # 保存新的元数据
            with open(self.local_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(server_data, f, ensure_ascii=False, indent=2)
            
            # 发送更新信号
            self.update_available.emit(server_scripts)  # 发送所有脚本，不只是更新的
            self.update_complete.emit(True, f"发现{len(updates_available)}个新脚本或更新")
            
        except Exception as e:
            self.update_complete.emit(False, f"更新检查失败: {str(e)}")
    
    def download_script(self, script_info):
        """打开云盘链接下载脚本"""
        download_url = script_info["download_url"]
        
        # 打开浏览器跳转到下载链接
        webbrowser.open(download_url)
        
        return True, "浏览器已打开下载链接，请前往云盘下载脚本文件"
    
    def _compare_versions(self, version1, version2):
        """比较两个版本号"""
        v1_parts = [int(x) for x in version1.replace('v', '').split('.')]
        v2_parts = [int(x) for x in version2.replace('v', '').split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
                
        return 0 