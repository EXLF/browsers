import os
import json
import webbrowser
import requests
import hashlib
import base64
import re
from urllib.parse import urlparse
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key
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
        
        # 安全设置
        # 白名单域名列表，只允许从这些域名下载脚本
        self.allowed_domains = [
            'github.com',
            'raw.githubusercontent.com',
            'lanzou.com',
            'lanzoux.com',
            'lanzout.com',
            'aliyundrive.com',
            'pan.baidu.com'
        ]
        
        # 验证签名的公钥 (使用RSA非对称加密)
        # 注意：这里只存储公钥，私钥应该只在签名工具中使用
        self.public_key_pem = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAn+6JB1AdG597fgDQ2pzK
WbP40wBwG+gD9Ij3ocVpH1I/clDqzf/0vbV7upxOowwranW5dRECYGyCtWH7KGwn
Z67j1uzZuCFlyZ5tk+R2vjEvblanaCUyxYGOzGOi6AZY6cel45NJB2ooz27liBxA
lJ0TcYMOANOlBPIEnKjn911DsZDnjBIlcnk5F9zdnvsyI1LAP4S4ElE2UwpN5NWW
gfbtxIiW2I98dATDVzJSRXeRWh+iSYndaAYpB6svv3DzpgSb55dM99fhyACNHIwA
FYWYM649SXqpBGoIFakUsc0d9UnTS+pAlqezypGeOoAY3NVV6OiZF0i3EWJ1bQsW
CwIDAQAB
-----END PUBLIC KEY-----"""
    
    def run(self):
        """检查脚本更新"""
        try:
            # 获取最新元数据，确保使用HTTPS
            if not self.metadata_url.startswith('https://'):
                self.update_complete.emit(False, "元数据URL必须使用HTTPS")
                return
                
            response = requests.get(self.metadata_url, timeout=10)
            response.raise_for_status()
            
            server_data = response.json()
            
            # 验证JSON数据的完整性和真实性
            if not self._verify_metadata(server_data):
                self.update_complete.emit(False, "元数据验证失败，可能被篡改")
                return
            
            server_scripts = server_data.get("scripts", [])
            
            # 验证所有下载链接的安全性
            for script in server_scripts:
                download_url = script.get("download_url", "")
                if download_url and not self._is_url_safe(download_url):
                    self.update_complete.emit(False, f"发现不安全的下载链接: {download_url}")
                    return
            
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
            
        except requests.exceptions.RequestException as e:
            self.update_available.emit([])
            self.update_complete.emit(False, f"无法连接到脚本服务器，请检查网络连接")
        except Exception as e:
            self.update_available.emit([])
            self.update_complete.emit(False, f"更新检查失败: {str(e)}")
    
    def download_script(self, script_info):
        """打开云盘链接下载脚本"""
        download_url = script_info["download_url"]
        
        # 再次进行安全检查
        if not self._is_url_safe(download_url):
            return False, "下载链接不安全，已阻止访问"
        
        # 打开浏览器跳转到下载链接
        webbrowser.open(download_url)
        
        return True, "浏览器已打开下载链接，请前往云盘下载脚本文件"
    
    def _verify_metadata(self, data):
        """使用RSA验证元数据的真实性和完整性"""
        try:
            # 检查是否包含签名
            if "signature" not in data:
                return False
                
            signature = data.pop("signature", "")
            signature_bytes = base64.b64decode(signature)
            
            # 计算数据的哈希
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
            
            # 将签名放回去，不影响后续处理
            data["signature"] = signature
            
            # 加载公钥
            public_key = load_pem_public_key(self.public_key_pem.encode('utf-8'))
            
            # 验证签名
            try:
                public_key.verify(
                    signature_bytes,
                    data_str,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
            except Exception:
                return False
                
        except Exception as e:
            print(f"验证签名出错: {str(e)}")
            return False
    
    def _is_url_safe(self, url):
        """检查URL是否安全"""
        # 必须是HTTPS
        if not url.startswith('https://'):
            return False
            
        # 检查域名是否在白名单中
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # 检查是否包含危险模式，如javascript:
        if re.search(r'^javascript:|data:|vbscript:|file:', url, re.IGNORECASE):
            return False
            
        # 域名白名单检查
        for allowed_domain in self.allowed_domains:
            if domain == allowed_domain or domain.endswith('.' + allowed_domain):
                return True
                
        return False
    
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