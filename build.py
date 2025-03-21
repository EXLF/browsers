import os
import sys
import shutil
import PyInstaller.__main__

def clean_build():
    """清理构建文件夹"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    spec_file = 'chrome_manager.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)

def copy_resources():
    """复制资源文件到dist目录"""
    dist_resources = os.path.join('dist', 'chrome_manager', 'chrome_manager', 'resources')
    if not os.path.exists(dist_resources):
        os.makedirs(dist_resources)
    
    # 复制resources目录下的所有文件
    src_resources = os.path.join('chrome_manager', 'resources')
    if os.path.exists(src_resources):
        for item in os.listdir(src_resources):
            s = os.path.join(src_resources, item)
            d = os.path.join(dist_resources, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

def build():
    """执行打包"""
    clean_build()
    
    PyInstaller.__main__.run([
        'main.py',
        '--name=chrome_manager',
        '--windowed',  # 不显示控制台窗口
        '--noconfirm',  # 覆盖输出目录
        '--icon=chrome_manager/resources/logo.ico',  # 应用图标
        '--add-data=chrome_manager/resources;chrome_manager/resources',  # 添加资源文件
        '--hidden-import=PyQt6.sip',  # 添加隐式导入
        '--clean',  # 清理临时文件
        '--onedir',  # 生成单文件夹
    ])
    
    # 复制资源文件
    copy_resources()
    
    print("打包完成！输出目录: dist/chrome_manager")

if __name__ == '__main__':
    build() 