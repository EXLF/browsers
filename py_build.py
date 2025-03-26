#!/usr/bin/env python
"""
构建脚本 - 用于生成可执行文件和安装包
"""

import os
import sys
import subprocess
import shutil
import time
import re

def run_command(command, check=True):
    """运行系统命令并返回结果"""
    print(f"执行命令: {command}")
    result = subprocess.run(command, shell=True, check=check, 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           encoding='utf-8', errors='replace')
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"错误输出: {result.stderr}")
    return result.returncode == 0

def clean_dirs():
    """清理旧的构建目录"""
    print("清理旧的构建文件...")
    directories = ["build", "dist"]
    for directory in directories:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"已删除 {directory} 目录")
            except Exception as e:
                print(f"无法删除 {directory}: {e}")

def check_imports():
    """检查并修复spec文件中的导入"""
    spec_file = "optimized_fix.spec"
    if not os.path.exists(spec_file):
        print(f"错误: 找不到spec文件 {spec_file}")
        return False
    
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已包含http和相关模块
        modules_to_add = [
            'http', 'http.client', 
            'urllib', 'urllib.request', 'urllib.parse', 'urllib.error',
            'email', 'email.mime', 'email.mime.text', 'email.mime.multipart',
            'json', 'ssl', 'socket', 'html', 'html.parser', 'requests'
        ]
        
        # 检查hiddenimports部分
        import_section = re.search(r'hiddenimports=\[(.*?)\]', content, re.DOTALL)
        if import_section:
            imports_text = import_section.group(1)
            modified = False
            
            for module in modules_to_add:
                if f"'{module}'" not in imports_text:
                    # 模块不存在，添加它
                    print(f"添加缺少的模块: {module}")
                    imports_text = imports_text.rstrip() + f",\n        '{module}',  # 自动添加的依赖"
                    modified = True
            
            if modified:
                # 替换导入部分
                new_content = re.sub(r'hiddenimports=\[(.*?)\]', f'hiddenimports=[\n{imports_text}\n    ]', content, flags=re.DOTALL)
                content = new_content
                print(f"已更新hiddenimports部分，添加了必要的导入模块")
            else:
                print("所有必要的导入模块已存在")
        else:
            print(f"警告: 在{spec_file}中找不到hiddenimports部分")
            
        # 检查excludes部分，确保我们需要的模块不在排除列表中
        excludes_section = re.search(r'excludes=\[(.*?)\]', content, re.DOTALL)
        if excludes_section:
            excludes_text = excludes_section.group(1)
            modified = False
            
            # 定义不应该被排除的模块
            modules_not_to_exclude = [
                'http', 'email', 'html', 'urllib', 'json', 'ssl', 'socket', 'requests'
            ]
            
            for module in modules_not_to_exclude:
                if f"'{module}'" in excludes_text:
                    # 从排除列表中移除
                    print(f"从excludes列表中移除模块: {module}")
                    excludes_text = re.sub(f",?\\s*'{module}'\\s*", '', excludes_text)
                    modified = True
            
            if modified:
                # 清理多余的逗号
                excludes_text = re.sub(r',\s*,', ',', excludes_text)
                excludes_text = re.sub(r',\s*\]', ']', excludes_text)
                
                # 替换排除部分
                new_content = re.sub(r'excludes=\[(.*?)\]', f'excludes=[{excludes_text}]', content, flags=re.DOTALL)
                
                # 写回文件
                with open(spec_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"已更新excludes部分，移除了必要的模块")
            else:
                with open(spec_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("excludes列表中没有发现需要排除的必要模块")
        else:
            # 如果没有找到excludes部分，但需要保存hiddenimports的变更
            with open(spec_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"警告: 在{spec_file}中找不到excludes部分")
    
    except Exception as e:
        print(f"检查导入时出错: {e}")
        return False
    
    return True

def build_exe():
    """使用PyInstaller构建EXE"""
    print("\n===== 开始构建可执行文件 =====")
    
    # 首先检查并修复imports
    if not check_imports():
        print("未能检查或修复导入依赖")
    
    # 尝试查找PyInstaller
    pyinstaller_paths = [
        # 尝试直接使用模块
        f"{sys.executable} -m PyInstaller",
        # 尝试使用用户安装的脚本
        r"C:\Users\Administrator\AppData\Roaming\Python\Python312\Scripts\pyinstaller.exe",
        # 尝试使用全局安装
        "pyinstaller"
    ]
    
    for path in pyinstaller_paths:
        command = f"{path} optimized_fix.spec"
        if run_command(command, check=False):
            return True
    
    print("无法找到或运行PyInstaller")
    return False

def build_installer():
    """使用Inno Setup构建安装程序"""
    print("\n===== 开始构建安装程序 =====")
    
    # 检查exe文件是否存在
    exe_path = os.path.join("dist", "FourAir浏览器多开管理器.exe")
    if not os.path.exists(exe_path):
        print(f"错误: 可执行文件不存在: {exe_path}")
        return False
    
    # 调用Inno Setup编译器
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    
    for path in iscc_paths:
        if os.path.exists(path):
            return run_command(f'"{path}" FourAir.iss')
    
    print("未找到Inno Setup编译器")
    return False

def test_exe():
    """测试生成的可执行文件"""
    print("\n===== 测试生成的可执行文件 =====")
    exe_path = os.path.join("dist", "FourAir浏览器多开管理器.exe")
    
    if not os.path.exists(exe_path):
        print(f"错误: 可执行文件不存在: {exe_path}")
        return False
    
    print(f"尝试运行 {exe_path} 以检查是否有启动错误...")
    # 仅运行几秒钟进行快速测试，然后终止进程
    try:
        process = subprocess.Popen(exe_path)
        print("等待3秒检查启动问题...")
        time.sleep(3)
        process.terminate()
        print("测试通过: 应用程序成功启动")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def main():
    """主函数"""
    print("===== 应用程序构建脚本 =====")
    clean_dirs()
    
    if build_exe():
        print("可执行文件创建成功!")
        
        # 可选的测试步骤
        test_result = input("是否测试生成的可执行文件？ (y/n): ").strip().lower()
        if test_result == 'y':
            test_exe()
        
        if build_installer():
            print("\n✓ 安装程序创建成功!")
        else:
            print("\n✗ 安装程序创建失败!")
    else:
        print("\n✗ 可执行文件创建失败!")
    
    print("\n==========================")
    input("按Enter键退出...")

if __name__ == "__main__":
    main() 