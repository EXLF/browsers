"""
主窗口模块
"""

import os
import sys
import time
import threading
import subprocess
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QStackedWidget, QStyleFactory, QDialog, QFrame, QPushButton,
    QApplication, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QDesktopServices, QIcon

from .constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR, 
    TEXT_SECONDARY_COLOR, TEXT_HINT_COLOR, FONT_FAMILY,
    SIDEBAR_WIDTH, SIDEBAR_BACKGROUND, MENU_ITEM_HEIGHT,
    WINDOW_WIDTH, WINDOW_HEIGHT, ACCENT_COLOR
)
from .config import ConfigManager
from .shortcuts import ShortcutManager
from .ui.components import ModernButton
from .ui.message import MessageDialogs
from .ui.pages import HomePage, SettingsPage, AccountPage, ScriptPage
from .utils import get_system_info
from .database_manager import DatabaseManager
from .app_updater import AppUpdater

class ChromeShortcutManager(QMainWindow):
    """Chrome多实例快捷方式管理器主窗口类"""
    
    def __init__(self):
        """初始化应用程序主窗口"""
        super().__init__()
        
        # 设置窗口标题
        self.setWindowTitle("FourAir社区专用Chrome多开管理器")
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 设置窗口固定大小
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)  # 设置固定大小
        
        # 允许最大化按钮
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        # 初始化消息对话框工具类
        self.message_dialogs = MessageDialogs(self)
        
        # 初始化变量
        self.chrome_path = self.find_chrome_path()  # 使用函数查找Chrome路径
        self.data_root = os.getcwd()  # 默认使用当前目录
        self.user_modified_data_root = False
        self.shortcuts = []
        self.account_info = {}  # 确保账号信息有默认值
        self.current_page_index = 0
        
        try:
            # 初始化配置管理器
            self.config_manager = ConfigManager(self)
            
            # 初始化快捷方式管理器
            self.shortcut_manager = ShortcutManager(self)
            self.shortcuts_dir = self.shortcut_manager.desktop_path  # 默认使用桌面路径
            
            # 打印系统信息
            self._print_system_info()
            
            # 创建UI
            self.init_ui()
            
            # 加载配置
            self.load_config()
            
            # 更新页面
            self.update_ui()
            
            # 设置定时保存
            self.auto_save_timer = QTimer(self)
            self.auto_save_timer.timeout.connect(self.auto_save_config)
            self.auto_save_timer.start(30000)  # 每30秒自动保存一次

            # 初始化应用更新器
            self.app_updater = AppUpdater(self)
            self.app_updater.update_available.connect(self._on_app_update_available)
            self.app_updater.update_complete.connect(self._on_app_update_complete)
            
            # 启动时检查更新
            QTimer.singleShot(3000, self.check_app_updates)
        except Exception as e:
            print(f"初始化主窗口时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            # 确保基本UI已创建
            if not hasattr(self, 'shortcut_manager'):
                self.shortcut_manager = ShortcutManager(self)
                self.shortcuts_dir = self.shortcut_manager.desktop_path
            if not hasattr(self, 'init_ui'):
                self.init_ui()

    def find_chrome_path(self):
        """查找Chrome安装路径"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe")
        ]
        
        # 检查注册表
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as key:
                chrome_path = winreg.QueryValue(key, None)
                if os.path.exists(chrome_path):
                    return chrome_path
        except:
            pass
            
        # 检查可能的安装路径
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # 如果都找不到，返回默认路径
        return r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    def init_ui(self):
        """初始化UI"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧菜单栏
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar_widget)
        
        # 右侧内容区
        self.setup_content_area()
        main_layout.addWidget(self.content_stack)
        
        # 设置布局比例
        main_layout.setStretch(0, 0)  # 左侧菜单栏不伸缩
        main_layout.setStretch(1, 1)  # 右侧内容区自适应

    def setup_sidebar(self):
        """设置左侧菜单栏"""
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(SIDEBAR_WIDTH)
        self.sidebar_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {SIDEBAR_BACKGROUND};
                border-right: 1px solid #EEEEEE;
            }}
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(16, 16, 16, 24)  # 减小顶部边距
        sidebar_layout.setSpacing(4)  # 减小间距
        
        # Logo和标题容器
        title_container = QVBoxLayout()
        title_container.setSpacing(2)  # logo和标题之间的间距很小
        
        # Logo图片
        logo_label = QLabel()
        logo_label.setFixedSize(166, 136)  # 增大logo大小
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(__file__), "resources", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(166, 136, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        title_container.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 标题文字
        title_label = QLabel("FourAir社区专用\nChrome多开管理器")  # 将标题分成两行
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))  # 减小字体大小
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_container.addWidget(title_label)
        
        sidebar_layout.addLayout(title_container)
        sidebar_layout.addSpacing(16)  # 减小标题与菜单按钮之间的间距
        
        # 菜单按钮
        self.home_btn = self.create_menu_button("主页", True)
        self.account_btn = self.create_menu_button("账号管理")
        self.script_btn = self.create_menu_button("脚本插件")  
        self.settings_btn = self.create_menu_button("设置")
        
        sidebar_layout.addWidget(self.home_btn)
        sidebar_layout.addWidget(self.account_btn)
        sidebar_layout.addWidget(self.script_btn)  
        sidebar_layout.addWidget(self.settings_btn)
        
        # 添加弹性空间
        sidebar_layout.addStretch()
        
        # 添加社区信息区域
        community_container = QWidget()
        community_layout = QVBoxLayout(community_container)
        community_layout.setContentsMargins(10, 0, 10, 20)
        community_layout.setSpacing(8)
        
        # 添加社区标题
        community_title = QLabel("作者及社区链接")
        community_title.setStyleSheet(f"""
            color: {TEXT_SECONDARY_COLOR};
            font-size: 16px;
            font-weight: bold;
            padding-bottom: 4px;
        """)
        community_layout.addWidget(community_title)
        
        # 社区链接样式
        link_style = """
            QPushButton {
                text-align: left;
                padding: 5px;
                border: none;
                color: #666;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #1a73e8;
            }
        """
        
        # Discord链接
        discord_btn = QPushButton("Discord社区")
        discord_btn.setStyleSheet(link_style)
        discord_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        discord_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://discord.gg/cTZCaYefPY")))
        community_layout.addWidget(discord_btn)
        
        # GitHub链接
        github_btn = QPushButton("GitHub仓库")
        github_btn.setStyleSheet(link_style)
        github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/EXLF/browsers")))
        community_layout.addWidget(github_btn)
        
        # Twitter链接
        twitter_btn = QPushButton("Twitter")
        twitter_btn.setStyleSheet(link_style)
        twitter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        twitter_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://x.com/xiao_yi24405")))
        community_layout.addWidget(twitter_btn)
        
        sidebar_layout.addWidget(community_container)
        
        # 版本信息
        version_label = QLabel("Version 1.1")
        version_label.setStyleSheet(f"color: {TEXT_HINT_COLOR};")
        version_label.setFont(QFont(FONT_FAMILY, 8))
        sidebar_layout.addWidget(version_label)
        
        # 连接信号
        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        self.account_btn.clicked.connect(lambda: self.switch_page(1))
        self.script_btn.clicked.connect(lambda: self.switch_page(3))
        self.settings_btn.clicked.connect(lambda: self.switch_page(2))

    def create_menu_button(self, text, is_active=False):
        """创建菜单按钮"""
        btn = ModernButton(text)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        btn.setFixedHeight(MENU_ITEM_HEIGHT)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                text-align: left;
                color: {TEXT_PRIMARY_COLOR};
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_COLOR}15;
            }}
            QPushButton:checked {{
                background-color: {PRIMARY_COLOR}25;
                color: {PRIMARY_COLOR};
                font-weight: bold;
            }}
        """)
        
        return btn

    def setup_content_area(self):
        """设置右侧内容区"""
        self.content_stack = QStackedWidget()
        self.content_stack.setContentsMargins(0, 0, 0, 0)
        self.content_stack.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        
        # 主页（浏览器实例管理）
        self.home_page = HomePage(self)
        self.content_stack.addWidget(self.home_page)
        
        # 账号管理页面
        self.account_page = AccountPage(self)
        self.content_stack.addWidget(self.account_page)
        
        # 设置页面
        self.settings_page = SettingsPage(self)
        self.content_stack.addWidget(self.settings_page)

        # 脚本插件页面
        self.script_page = ScriptPage(self)
        self.content_stack.addWidget(self.script_page)

    def switch_page(self, index):
        """切换页面"""
        self.content_stack.setCurrentIndex(index)
        
        # 更新菜单按钮状态
        self.home_btn.setChecked(index == 0)
        self.account_btn.setChecked(index == 1)
        self.script_btn.setChecked(index == 3)
        self.settings_btn.setChecked(index == 2)
        
        # 如果切换到账号管理页面，更新账号卡片
        if index == 1:
            self.account_page.update_cards()
        
        # 如果切换到设置页面，更新输入框的值
        if index == 2:
            self.settings_page.update_ui()
            
        # 如果切换到首页，更新浏览器网格
        if index == 0:
            self.home_page.update_browser_grid()

    def update_ui(self):
        """更新所有UI页面"""
        # 更新首页
        self.home_page.update_browser_grid()
        
        # 更新账号页
        self.account_page.update_cards()
        
        # 更新设置页
        self.settings_page.update_ui()

    def load_config(self):
        """加载配置"""
        try:
            print(f"\n============ 开始加载配置 ============")
            config = self.config_manager.load_config()
            
            # 设置Chrome路径
            self.chrome_path = config.get('chrome_path', self.chrome_path)
            print(f"加载配置 - Chrome路径: {self.chrome_path}")
            
            # 设置数据根目录
            self.data_root = config.get('data_root', self.data_root)
            self.user_modified_data_root = config.get('user_modified_data_root', False)
            print(f"加载配置 - 数据根目录: {self.data_root}")
                
            # 设置快捷方式保存路径
            shortcuts_dir = config.get('shortcuts_dir')
            if shortcuts_dir and os.path.exists(shortcuts_dir):
                self.shortcuts_dir = shortcuts_dir
                self.shortcut_manager.set_shortcuts_dir(shortcuts_dir)
            print(f"加载配置 - 快捷方式目录: {self.shortcuts_dir}")
            
            # 加载快捷方式
            self.shortcuts = config.get('shortcuts', [])
            print(f"加载配置 - 快捷方式数量: {len(self.shortcuts)}")
            print(f"加载配置 - 快捷方式详情: {[s.get('name') for s in self.shortcuts]}")
                
            # 加载账号信息
            self.account_info = config.get('account_info', {})
            print(f"加载配置 - 账号信息数量: {len(self.account_info)}")
            print(f"============ 配置加载结束 ============\n")
        except Exception as e:
            print(f"加载配置时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            # 在出错时使用默认配置
            self.shortcuts = []
            self.account_info = {}
    
    # 修改ConfigSaveThread类
    class ConfigSaveThread(QThread):
        """配置保存线程"""
        
        save_finished = pyqtSignal(bool, str)  # 保存完成信号
        
        def __init__(self, config_data, config_dir):
            super().__init__()
            self.config_data = config_data
            self.config_dir = config_dir  # 保存配置目录路径而非配置管理器实例
            
        def run(self):
            """运行线程，保存配置"""
            try:
                # 创建一个新的数据库管理器实例
                db_manager = DatabaseManager(self.config_dir)
                
                print(f"\n============ 开始保存配置 ============")
                print(f"保存配置 - Chrome路径: {self.config_data.get('chrome_path')}")
                print(f"保存配置 - 数据根目录: {self.config_data.get('data_root')}")
                print(f"保存配置 - 快捷方式列表数量: {len(self.config_data.get('shortcuts', []))}")
                print(f"保存配置 - 快捷方式详情: {[s.get('name') for s in self.config_data.get('shortcuts', [])]}")
                
                # 确保数据根目录不为空
                if not self.config_data.get('data_root'):
                    self.config_data['data_root'] = os.getcwd()
                    print(f"数据根目录为空，使用当前目录: {self.config_data['data_root']}")
                
                # 确保目录存在
                if not os.path.exists(self.config_data.get('data_root')):
                    try:
                        os.makedirs(self.config_data.get('data_root'), exist_ok=True)
                        print(f"创建数据根目录: {self.config_data.get('data_root')}")
                    except Exception as e:
                        print(f"创建数据根目录失败: {str(e)}")
                
                # 保存Chrome实例信息
                # 先清空现有实例
                print(f"正在清空数据库中的Chrome实例数据")
                db_manager.clear_chrome_instances()
                
                # 重新添加所有实例
                print(f"开始保存{len(self.config_data.get('shortcuts', []))}个Chrome实例到数据库")
                for shortcut in self.config_data.get('shortcuts', []):
                    print(f"  保存实例: {shortcut.get('name')}")
                    db_manager.save_chrome_instance(shortcut)
                
                # 保存账号信息
                for name, account_data in self.config_data.get('account_info', {}).items():
                    if any(s["name"] == name for s in self.config_data.get('shortcuts', [])):
                        db_manager.save_account_info(name, account_data)
                
                # 保存其他配置
                db_manager.save_config(self.config_data)
                
                print("配置已成功保存")
                print(f"============ 配置保存结束 ============\n")
                
                # 关闭数据库连接
                db_manager.close()
                
                self.save_finished.emit(True, "")
            except Exception as e:
                error_msg = f"保存配置失败：{str(e)}"
                print(f"保存配置错误: {error_msg}")
                import traceback
                traceback.print_exc()
                self.save_finished.emit(False, str(e))

    def auto_save_config(self):
        """自动保存配置"""
        print(f"准备保存配置...")
        print(f"当前快捷方式列表: {[s['name'] for s in self.shortcuts]}")
        
        # 处理一些UI事件，确保界面响应
        QApplication.processEvents()
        
        config = {
            'chrome_path': self.chrome_path,
            'data_root': self.data_root,
            'user_modified_data_root': self.user_modified_data_root,
            'shortcuts_dir': self.shortcuts_dir,
            'shortcuts': self.shortcuts,
            'account_info': self.account_info
        }
        
        # 创建后台线程保存配置，传递配置目录路径而非配置管理器实例
        self.save_thread = self.ConfigSaveThread(config, self.config_manager.config_dir)
        self.save_thread.save_finished.connect(self._on_save_finished, type=Qt.ConnectionType.QueuedConnection)
        self.save_thread.start()
        
        # 立即返回，不阻塞UI
        QApplication.processEvents()

    def _on_save_finished(self, success, error):
        """配置保存完成回调"""
        if success:
            print(f"配置已保存到数据库")
            print(f"已保存配置 - Chrome路径: {self.chrome_path}")
            print(f"已保存配置 - 数据根目录: {self.data_root}")
            print(f"已保存配置 - 快捷方式目录: {self.shortcuts_dir}")
            print(f"已保存配置 - 快捷方式列表: {[s['name'] for s in self.shortcuts]}")
        else:
            print(f"保存配置失败: {error}")
        
        # 确保UI处理所有事件
        QApplication.processEvents()

    def changeEvent(self, event):
        """窗口状态改变事件（最大化/还原）"""
        if event.type() == event.Type.WindowStateChange:
            # 窗口状态改变时更新网格布局
            self.home_page.update_browser_grid()
        super().changeEvent(event)

    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 保存配置
            self.auto_save_config()
            
            # 显示最终性能报告
            print("\n=== 性能报告 ===")
            print("==============\n")
            
            # 确保相关资源被释放
            if hasattr(self, 'auto_save_timer'):
                self.auto_save_timer.stop()
                
            # 接受关闭事件
            event.accept()
        except Exception as e:
            print(f"关闭窗口时出错: {str(e)}")
            event.accept()  # 无论如何关闭窗口

    def _print_system_info(self):
        """打印系统信息"""
        print("\n=== 系统信息 ===")
        info = get_system_info()
        print(f"CPU核心数: {info['cpu_count']} (物理核心: {info['cpu_physical']})")
        print(f"CPU使用率: {info['cpu_percent']}%")
        print(f"内存总量: {info['memory_total']:.1f}GB")
        print(f"可用内存: {info['memory_available']:.1f}GB")
        print(f"内存使用率: {info['memory_percent']}%")
        print(f"进程CPU使用率: {info['process_cpu']}%")
        print(f"进程内存使用: {info['process_memory']:.1f}MB")
        print("==============\n") 

    # 添加应用更新相关方法
    def check_app_updates(self):
        """检查应用更新"""
        self.statusBar().showMessage("正在检查应用更新...")
        self.app_updater.start()

    def _on_app_update_available(self, latest_version):
        """处理可用应用更新"""
        reply = QMessageBox.question(
            self,
            "发现新版本",
            f"发现新版本 v{latest_version}\n\n是否前往下载更新？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 打开固定的下载链接
            success, msg = self.app_updater.download_update()
            if success:
                self.statusBar().showMessage(msg, 5000)

    def _on_app_update_complete(self, success, message):
        """更新检查完成"""
        if success:
            self.statusBar().showMessage(message, 5000)
        else:
            print(f"更新检查失败: {message}")  # 只在控制台打印，不打扰用户 