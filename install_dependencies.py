"""
依赖项安装脚本

此脚本用于安装Chrome多开管理器所需的所有依赖项
"""

import subprocess
import sys
import os

def install_package(package):
    """安装指定的Python包"""
    try:
        print(f"正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
        print(f"{package} 安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"安装 {package} 失败：{str(e)}")
        return False

def main():
    """安装所有必要的依赖项"""
    print("Chrome多开管理器依赖项安装程序")
    print("=" * 40)
    
    # 必要的依赖项列表
    packages = [
        "PyQt6",
        "winshell",
        "pywin32",
        "cryptography"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n安装摘要:")
    print(f"成功安装: {success_count}/{len(packages)}")
    
    if success_count == len(packages):
        print("\n所有依赖项已成功安装！您现在可以运行Chrome多开管理器了。")
    else:
        print("\n一些依赖项安装失败。请检查错误信息并手动安装缺失的依赖项。")
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    # 尝试以管理员权限运行
    if sys.platform.startswith('win'):
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("正在尝试以管理员权限运行...")
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit(0)
        except Exception as e:
            print(f"无法以管理员权限运行: {str(e)}")
    
    main() 