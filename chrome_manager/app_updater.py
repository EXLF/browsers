import requests
import webbrowser
from PyQt6.QtCore import QThread, pyqtSignal
from . import __version__ as current_version

class AppUpdater(QThread):
    """简化版应用更新检查器"""
    
    update_available = pyqtSignal(str)  # 发送最新版本号
    update_complete = pyqtSignal(bool, str)  # 更新检查完成信号
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # 使用GitHub仓库的版本文件链接
        self.version_url = "https://raw.githubusercontent.com/EXLF/chrome-scripts/refs/heads/main/version.txt"
        
        # 固定的蓝奏云更新下载链接
        self.download_url = "https://wwmf.lanzout.com/b009h0yqwf"
    
    def run(self):
        """检查应用更新"""
        try:
            # 获取最新版本信息
            response = requests.get(self.version_url, timeout=10)
            response.raise_for_status()
            
            # 获取版本号(去除可能的空白字符)
            latest_version = response.text.strip()
            
            # 比较版本
            if self._compare_versions(latest_version, current_version) > 0:
                # 发送更新信号
                self.update_available.emit(latest_version)
                self.update_complete.emit(True, f"发现新版本 v{latest_version}")
            else:
                self.update_complete.emit(True, "当前已是最新版本")
            
        except requests.exceptions.RequestException as e:
            self.update_complete.emit(False, f"无法连接到更新服务器，请检查网络连接")
        except Exception as e:
            self.update_complete.emit(False, f"更新检查失败: {str(e)}")
    
    def download_update(self):
        """打开下载链接"""
        # 打开浏览器跳转到蓝奏云下载链接
        webbrowser.open(self.download_url)
        return True, "浏览器已打开下载链接，请下载并安装新版本"
    
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