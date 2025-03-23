"""
重置应用程序配置

此脚本用于重置Chrome多开管理器的配置，清除所有ChromeShortcuts目录下的内容。
仅用于测试和开发目的。
"""

import os
import shutil
import sys

def main():
    # 获取配置目录路径
    appdata_dir = os.getenv('APPDATA')
    config_dir = os.path.join(appdata_dir, 'ChromeShortcuts')
    
    if not os.path.exists(config_dir):
        print(f"配置目录不存在: {config_dir}")
        return
    
    try:
        # 删除数据库文件和配置文件
        db_file = os.path.join(config_dir, "chrome_manager.db")
        config_file = os.path.join(config_dir, "config.json")
        encryption_key = os.path.join(config_dir, "encryption.key")
        
        for file_path in [db_file, config_file, encryption_key]:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已删除: {file_path}")
            else:
                print(f"文件不存在: {file_path}")
        
        print("\n配置已重置。下次启动应用程序时将使用默认配置。")
    except Exception as e:
        print(f"重置配置时出错: {str(e)}")
    
    input("按Enter键退出...")

if __name__ == "__main__":
    main() 