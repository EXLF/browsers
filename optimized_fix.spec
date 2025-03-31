# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('chrome_manager/resources', 'chrome_manager/resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'sqlite3',
        'win32com',    # 添加win32com作为隐式导入
        'win32api',    # 添加win32api作为隐式导入
        'win32com.client',  # 添加子模块
        'pythoncom',   # 添加pythoncom，它是win32com的依赖
        'http',        # 添加http模块
        'http.client', # 添加http.client子模块
        'urllib',      # 添加urllib模块
        'urllib.request', # 添加urllib.request子模块
        'urllib.parse',  # 添加urllib.parse子模块
        'urllib.error',  # 添加urllib.error子模块
        'email',  # 自动添加的依赖
        'email.mime',  # 自动添加的依赖
        'email.mime.text',  # 自动添加的依赖
        'email.mime.multipart',  # 自动添加的依赖
        'json',  # 自动添加的依赖
        'ssl',  # 自动添加的依赖
        'socket',  # 自动添加的依赖
        'html',  # 添加html模块
        'html.parser',  # 添加html解析器
        'requests',  # 添加requests库
        'platform',  # 添加platform模块，用于操作系统检测
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # 排除不必要的大型库
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy',
        'tkinter', 'tk', 'tcl', 
        'PySide', 'PySide2', 'PyQt5',
        'IPython', 'docutils', 'pygments',
        'sphinx',
        'multiprocessing',
        'pydoc', 'xmlrpc', 'setuptools', 
        'distutils', 'unittest', 'test'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤不必要的动态库
def remove_unnecessary_binaries(binaries):
    result = []
    for b in binaries:
        # 移除调试DLL和不需要的DLL
        if 'vcruntime140_1.dll' in b[0].lower() or \
           'qwebengine' in b[0].lower() or \
           'qml' in b[0].lower() or \
           '_d.dll' in b[0].lower() or \
           'opengl32sw.dll' in b[0].lower():
            continue
        result.append(b)
    return result

a.binaries = remove_unnecessary_binaries(a.binaries)

# 过滤掉一些大型数据文件
def strip_unneeded_data(datas):
    result = []
    for d in datas:
        # 过滤掉不需要的资源文件
        if 'translations' in d[0].lower():
            # 只保留中文和英文翻译
            if 'zh_CN' in d[0].lower() or 'en' in d[0].lower():
                result.append(d)
        else:
            result.append(d)
    return result

a.datas = strip_unneeded_data(a.datas)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FourAir浏览器多开管理器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 启用strip以减少二进制大小
    upx=True,    # 已启用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='chrome_manager/resources/logo.ico',
) 