"""
主窗口模块
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QGridLayout, QStackedWidget, QStyleFactory, QDialog, QFileDialog, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QPixmap, QDesktopServices, QIcon

from .constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR, 
    TEXT_SECONDARY_COLOR, TEXT_HINT_COLOR, FONT_FAMILY
)
from .config import ConfigManager
from .shortcuts import ShortcutManager
from .ui.components import ModernButton, ModernLineEdit
from .ui.dialogs import AddShortcutDialog
from .ui.cards import BrowserCard
from .ui.message import MessageDialogs

class ChromeShortcutManager(QMainWindow):
    """Chrome多实例快捷方式管理器主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题
        self.setWindowTitle("FourAir社区专用Chrome多开管理器")
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 设置窗口固定大小
        self.setMinimumSize(1200, 800)
        self.setFixedSize(1200, 800)  # 设置固定大小
        
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
        
        try:
            # 初始化配置管理器
            self.config_manager = ConfigManager(self)
            
            # 初始化快捷方式管理器
            self.shortcut_manager = ShortcutManager(self)
            self.shortcuts_dir = self.shortcut_manager.desktop_path  # 默认使用桌面路径
            
            # 创建UI
            self.init_ui()
            
            # 加载配置
            self.load_config()
            
            # 更新快捷方式列表
            self.update_browser_grid()
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
        self.sidebar_widget.setFixedWidth(200)
        self.sidebar_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {BACKGROUND_COLOR};
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
        self.script_btn = self.create_menu_button("脚本插件")  # 添加脚本插件菜单项
        self.settings_btn = self.create_menu_button("设置")
        
        sidebar_layout.addWidget(self.home_btn)
        sidebar_layout.addWidget(self.account_btn)
        sidebar_layout.addWidget(self.script_btn)  # 添加脚本插件按钮
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
        btn.setFixedHeight(40)
        
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
        home_page = self.setup_home_page()
        self.content_stack.addWidget(home_page)
        
        # 账号管理页面
        account_page = self.setup_account_page()
        self.content_stack.addWidget(account_page)
        
        # 设置页面
        settings_page = self.setup_settings_page()
        self.content_stack.addWidget(settings_page)
        
        # 脚本插件页面
        script_page = self.setup_script_page()
        self.content_stack.addWidget(script_page)

    def setup_home_page(self):
        """主页（浏览器实例管理）"""
        home_page = QWidget()
        
        home_layout = QVBoxLayout(home_page)
        home_layout.setContentsMargins(32, 24, 32, 24)  # 减小上下边距
        
        # 顶部操作栏
        top_bar = QHBoxLayout()
        
        page_title = QLabel("浏览器实例管理")
        page_title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        
        # 添加新实例按钮
        add_btn = ModernButton("添加新实例", accent=True)
        add_btn.clicked.connect(self.add_shortcut)
        
        # 批量操作按钮
        self.batch_btn = ModernButton("批量删除")
        self.batch_btn.clicked.connect(self.toggle_batch_mode)
        
        # 全选按钮（初始隐藏）
        self.select_all_btn = ModernButton("全选")
        self.select_all_btn.setVisible(False)
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        
        # 批量删除确认按钮（初始隐藏）
        self.confirm_delete_btn = ModernButton("删除选中", accent=True)
        self.confirm_delete_btn.setVisible(False)
        self.confirm_delete_btn.clicked.connect(self.delete_selected_shortcuts)
        
        # 取消批量操作按钮（初始隐藏）
        self.cancel_batch_btn = ModernButton("取消")
        self.cancel_batch_btn.setVisible(False)
        self.cancel_batch_btn.clicked.connect(self.toggle_batch_mode)
        
        top_bar.addWidget(page_title)
        top_bar.addStretch()
        top_bar.addWidget(self.batch_btn)
        top_bar.addWidget(self.select_all_btn)
        top_bar.addWidget(self.confirm_delete_btn)
        top_bar.addWidget(self.cancel_batch_btn)
        top_bar.addWidget(add_btn)
        
        home_layout.addLayout(top_bar)
        
        # 浏览器网格区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #CCCCCC;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(16)
        
        scroll_area.setWidget(self.grid_widget)
        home_layout.addWidget(scroll_area)
        
        # 批量操作状态
        self.is_batch_mode = False
        self.is_all_selected = False  # 添加全选状态标记
        self.card_widgets = []  # 保存所有卡片组件
        
        return home_page
        
    def setup_account_page(self):
        """账号管理页面"""
        account_page = QWidget()
        
        account_layout = QVBoxLayout(account_page)
        account_layout.setContentsMargins(32, 24, 32, 24)  # 减小上下边距
        account_layout.setSpacing(16)  # 减小整体间距
        
        # 顶部标题
        page_title = QLabel("账号管理")
        page_title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        account_layout.addWidget(page_title)
        
        # 说明文字
        description = QLabel("管理每个浏览器实例对应的账号信息，包括钱包和社交媒体账号")
        description.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 14px; margin-bottom: 8px;")
        description.setWordWrap(True)
        account_layout.addWidget(description)
        
        # 账号信息区域（滚动区域）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CCCCCC;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #AAAAAA;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        
        # 背景容器
        background_widget = QWidget()
        background_widget.setStyleSheet("background-color: white; border-radius: 8px;")
        background_layout = QVBoxLayout(background_widget)
        background_layout.setContentsMargins(0, 0, 0, 0)
        
        # 内容容器
        self.account_content_widget = QWidget()
        self.account_content_widget.setStyleSheet("background-color: transparent;")
        self.account_content_layout = QVBoxLayout(self.account_content_widget)
        self.account_content_layout.setContentsMargins(16, 16, 16, 16)  # 内边距
        self.account_content_layout.setSpacing(12)  # 减小卡片之间的间距
        
        # 先添加一个占位符，后续会根据实际情况更新
        self.account_placeholder = QLabel("暂无浏览器实例数据。请先在主页创建浏览器实例，然后在此处管理对应的账号信息。")
        self.account_placeholder.setStyleSheet(f"""
            color: #505050; 
            font-size: 15px;
            margin: 40px 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px dashed #cccccc;
        """)
        self.account_placeholder.setWordWrap(True)
        self.account_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.account_content_layout.addWidget(self.account_placeholder)
        
        # 添加弹性空间
        self.account_content_layout.addStretch()
        
        # 将内容添加到背景容器
        background_layout.addWidget(self.account_content_widget)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(background_widget)
        account_layout.addWidget(scroll_area)
        
        # 保存按钮
        save_btn_layout = QHBoxLayout()
        save_account_btn = ModernButton("保存账号信息", accent=True)
        save_account_btn.clicked.connect(self.save_account_info)
        save_account_btn.setMinimumWidth(120)
        save_btn_layout.addStretch()
        save_btn_layout.addWidget(save_account_btn)
        account_layout.addLayout(save_btn_layout)
        
        # 预先检查是否有实例，初始设置占位符状态
        self.account_placeholder.setVisible(True)
        
        return account_page
        
    def update_account_cards(self):
        """更新账号管理卡片"""
        try:
            # 清除现有的所有卡片
            for i in reversed(range(self.account_content_layout.count()-1)):  # 保留最后的stretch
                item = self.account_content_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    # 不要删除占位符标签
                    if widget != self.account_placeholder:
                        widget.setParent(None)
            
            # 如果没有浏览器实例，显示占位符并返回
            if not self.shortcuts:
                self.account_placeholder.setVisible(True)
                # 确保占位符在布局中的位置正确
                self.account_content_layout.insertWidget(0, self.account_placeholder)
                return
            
            # 有实例时隐藏占位符
            self.account_placeholder.setVisible(False)
            
            # 为每个浏览器实例创建一个账号信息卡片
            for shortcut in self.shortcuts:
                name = shortcut["name"]
                data_dir = shortcut["data_dir"]
                
                # 创建卡片容器
                card = QWidget()
                card.setObjectName(f"account_card_{name}")
                card.setStyleSheet("""
                    QWidget {
                        background-color: #f8f9fa;
                        border-radius: 6px;
                    }
                """)
                
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(16, 12, 16, 12)  # 减小内边距
                card_layout.setSpacing(8)  # 减小间距
                
                # 标题和数据目录在一行
                header_layout = QHBoxLayout()
                header_layout.setSpacing(10)
                
                # 标题
                title = QLabel(name)
                title.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
                title.setStyleSheet("color: #1a73e8;")
                header_layout.addWidget(title)
                header_layout.addStretch()
                
                card_layout.addLayout(header_layout)
                
                # 添加分隔线
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet("background-color: #e0e0e0; margin: 0 -8px;")
                separator.setMaximumHeight(1)
                card_layout.addWidget(separator)
                
                # 账号信息表单 - 使用三列布局提高空间利用率
                form_layout = QGridLayout()
                form_layout.setHorizontalSpacing(20)  # 水平间距稍大
                form_layout.setVerticalSpacing(10)  # 减小垂直间距
                
                # 定义标签样式
                label_style = "color: #555555; font-weight: 500; font-size: 13px;"
                
                # 定义输入框样式
                input_style = """
                    ModernLineEdit {
                        border: none;
                        border-bottom: 1px solid #dadce0;
                        background-color: transparent;
                        padding: 4px 0;
                    }
                    ModernLineEdit:focus {
                        border-bottom: 2px solid #1a73e8;
                    }
                """
                
                # 第一列 - 钱包和Twitter
                # 钱包地址
                wallet_label = QLabel("钱包地址:")
                wallet_label.setStyleSheet(label_style)
                wallet_input = ModernLineEdit(self.account_info.get(name, {}).get("wallet", ""))
                wallet_input.setObjectName(f"wallet_{name}")
                wallet_input.setPlaceholderText("请输入钱包地址")
                wallet_input.setStyleSheet(input_style)
                form_layout.addWidget(wallet_label, 0, 0)
                form_layout.addWidget(wallet_input, 0, 1)
                
                # Twitter
                twitter_label = QLabel("Twitter:")
                twitter_label.setStyleSheet(label_style)
                twitter_input = ModernLineEdit(self.account_info.get(name, {}).get("twitter", ""))
                twitter_input.setObjectName(f"twitter_{name}")
                twitter_input.setPlaceholderText("请输入Twitter账号")
                twitter_input.setStyleSheet(input_style)
                form_layout.addWidget(twitter_label, 1, 0)
                form_layout.addWidget(twitter_input, 1, 1)
                
                # 第二列 - Discord和Telegram
                # Discord
                discord_label = QLabel("Discord:")
                discord_label.setStyleSheet(label_style)
                discord_input = ModernLineEdit(self.account_info.get(name, {}).get("discord", ""))
                discord_input.setObjectName(f"discord_{name}")
                discord_input.setPlaceholderText("请输入Discord账号")
                discord_input.setStyleSheet(input_style)
                form_layout.addWidget(discord_label, 0, 2)
                form_layout.addWidget(discord_input, 0, 3)
                
                # Telegram
                telegram_label = QLabel("Telegram:")
                telegram_label.setStyleSheet(label_style)
                telegram_input = ModernLineEdit(self.account_info.get(name, {}).get("telegram", ""))
                telegram_input.setObjectName(f"telegram_{name}")
                telegram_input.setPlaceholderText("请输入Telegram账号")
                telegram_input.setStyleSheet(input_style)
                form_layout.addWidget(telegram_label, 1, 2)
                form_layout.addWidget(telegram_input, 1, 3)
                
                # 第三列 - Gmail和备注
                # Gmail
                gmail_label = QLabel("Gmail:")
                gmail_label.setStyleSheet(label_style)
                gmail_input = ModernLineEdit(self.account_info.get(name, {}).get("gmail", ""))
                gmail_input.setObjectName(f"gmail_{name}")
                gmail_input.setPlaceholderText("请输入Gmail账号")
                gmail_input.setStyleSheet(input_style)
                form_layout.addWidget(gmail_label, 0, 4)
                form_layout.addWidget(gmail_input, 0, 5)
                
                # 备注
                note_label = QLabel("备注:")
                note_label.setStyleSheet(label_style)
                note_input = ModernLineEdit(self.account_info.get(name, {}).get("note", ""))
                note_input.setObjectName(f"note_{name}")
                note_input.setPlaceholderText("其他备注信息")
                note_input.setStyleSheet(input_style)
                form_layout.addWidget(note_label, 1, 4)
                form_layout.addWidget(note_input, 1, 5)
                
                # 设置各列的拉伸比例
                for col in [1, 3, 5]:  # 输入框列
                    form_layout.setColumnStretch(col, 1)
                
                card_layout.addLayout(form_layout)
                
                # 添加卡片到容器
                self.account_content_layout.insertWidget(self.account_content_layout.count()-1, card)
        except Exception as e:
            # 捕获并处理异常，避免在没有实例时弹出Python窗口
            print(f"更新账号卡片时出错: {str(e)}")
            # 确保占位符可见
            self.account_placeholder.setVisible(True)
            # 确保占位符在布局中的位置正确
            self.account_content_layout.insertWidget(0, self.account_placeholder)
    
    def save_account_info(self):
        """保存账号信息"""
        # 检查是否有浏览器实例
        if not self.shortcuts:
            # 不再弹出消息框，而是在状态栏显示消息
            self.statusBar().showMessage("暂无浏览器实例数据。请先在主页创建浏览器实例，然后再管理账号信息。", 5000)
            return
            
        updated_account_info = {}
        
        # 遍历所有浏览器实例
        for shortcut in self.shortcuts:
            name = shortcut["name"]
            instance_info = {}
            
            # 获取各个字段的值
            wallet_input = self.findChild(ModernLineEdit, f"wallet_{name}")
            twitter_input = self.findChild(ModernLineEdit, f"twitter_{name}")
            discord_input = self.findChild(ModernLineEdit, f"discord_{name}")
            telegram_input = self.findChild(ModernLineEdit, f"telegram_{name}")
            gmail_input = self.findChild(ModernLineEdit, f"gmail_{name}")
            note_input = self.findChild(ModernLineEdit, f"note_{name}")
            
            if wallet_input:
                instance_info["wallet"] = wallet_input.text().strip()
            if twitter_input:
                instance_info["twitter"] = twitter_input.text().strip()
            if discord_input:
                instance_info["discord"] = discord_input.text().strip()
            if telegram_input:
                instance_info["telegram"] = telegram_input.text().strip()
            if gmail_input:
                instance_info["gmail"] = gmail_input.text().strip()
            if note_input:
                instance_info["note"] = note_input.text().strip()
            
            updated_account_info[name] = instance_info
        
        # 更新账号信息
        self.account_info = updated_account_info
        
        # 保存到配置
        config = self.config_manager.load_config()
        config["account_info"] = self.account_info
        self.config_manager.save_config(config)
        
        # 使用状态栏显示成功消息，而不是弹窗
        self.statusBar().showMessage("账号信息已保存", 3000)
    
    def create_script_card(self, name, description, version, url):
        """创建脚本卡片"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QWidget:hover {
                border-color: #BBBBBB;
            }
        """)
        card.setFixedHeight(64)  # 进一步降低卡片高度
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 8, 16, 8)  # 减小内边距使卡片更紧凑
        
        # 左侧信息区
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)  # 减小间距
        
        # 脚本名称和版本
        title_layout = QHBoxLayout()
        script_title = QLabel(name)
        script_title.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        script_title.setStyleSheet("color: #1a73e8; border: none;")
        
        version_label = QLabel(version)
        version_label.setStyleSheet("color: #666666; font-size: 11px; background-color: #e8eaed; padding: 2px 6px; border-radius: 10px; border: none;")
        
        title_layout.addWidget(script_title)
        title_layout.addWidget(version_label)
        title_layout.addStretch()
        
        info_layout.addLayout(title_layout)
        
        # 脚本描述
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555555; font-size: 12px; border: none;")
        info_layout.addWidget(desc_label)
        
        card_layout.addLayout(info_layout, 1)  # 添加伸缩因子
        
        # 右侧下载按钮（改为待上传按钮并置灰）
        download_btn = ModernButton("待上传", accent=True)
        download_btn.setFixedWidth(70)  # 略微加宽按钮以适应"待上传"文字
        download_btn.setFixedHeight(28)  # 保持按钮高度
        download_btn.setEnabled(False)  # 设置按钮为禁用状态（置灰）
        card_layout.addWidget(download_btn)
        
        return card

    def setup_script_page(self):
        """脚本插件页面"""
        script_page = QWidget()
        
        script_layout = QVBoxLayout(script_page)
        script_layout.setContentsMargins(32, 24, 32, 24)  # 减小上下边距
        script_layout.setSpacing(16)  # 减小整体间距
        
        # 顶部标题
        page_title = QLabel("脚本插件")
        page_title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        script_layout.addWidget(page_title)
        
        # 说明文字
        description = QLabel("管理和下载各种浏览器脚本和插件工具")
        description.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 14px; margin-bottom: 8px;")
        description.setWordWrap(True)
        script_layout.addWidget(description)
        
        # 脚本插件区域（滚动区域）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CCCCCC;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #AAAAAA;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        
        # 脚本列表容器
        script_content_widget = QWidget()
        script_content_layout = QVBoxLayout(script_content_widget)
        script_content_layout.setContentsMargins(0, 0, 0, 0)
        script_content_layout.setSpacing(10)  # 减小卡片间距
        
        # 分类标题
        category_title = QLabel("热门脚本插件")
        category_title.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        category_title.setStyleSheet("color: #333333;")
        script_content_layout.addWidget(category_title)
        
        # 热门脚本卡片 - 使用用户提供的项目
        script_card1 = self.create_script_card(
            "Monad",
            "一键交互、自动领水、一键质押",
            "v2.1.0",
            "https://example.com/monad"
        )
        script_content_layout.addWidget(script_card1)
        
        script_card2 = self.create_script_card(
            "POD Network",
            "一键交互、自动领水",
            "v1.5.2",
            "https://example.com/pod-network"
        )
        script_content_layout.addWidget(script_card2)
        
        # 第二个分类
        category_title2 = QLabel("工具类插件")
        category_title2.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        category_title2.setStyleSheet("color: #333333; margin-top: 16px;")
        script_content_layout.addWidget(category_title2)
        
        # 工具插件卡片 - 使用用户提供的项目
        script_card3 = self.create_script_card(
            "Voltix AI",
            "多开挂机",
            "v3.0.1",
            "https://example.com/voltix-ai"
        )
        script_content_layout.addWidget(script_card3)
        
        script_card4 = self.create_script_card(
            "PublicAi",
            "自动交互",
            "v2.4.3",
            "https://example.com/public-ai"
        )
        script_content_layout.addWidget(script_card4)
        
        # 添加提交新脚本的提示
        submit_container = QWidget()
        submit_container.setStyleSheet("background-color: #f0f7ff; border-radius: 4px; padding: 8px;")
        submit_layout = QHBoxLayout(submit_container)
        submit_layout.setContentsMargins(12, 8, 12, 8)
        
        info_label = QLabel("想要提交你的脚本插件？请在Discord社区联系我们")
        info_label.setStyleSheet("color: #0057b8;")
        submit_layout.addWidget(info_label)
        
        submit_btn = ModernButton("前往社区", accent=True)
        submit_btn.setFixedWidth(100)
        submit_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://discord.gg/cTZCaYefPY")))
        submit_layout.addWidget(submit_btn)
        
        script_content_layout.addWidget(submit_container)
        script_content_layout.addStretch()
        
        scroll_area.setWidget(script_content_widget)
        script_layout.addWidget(scroll_area)
        
        return script_page

    def setup_settings_page(self):
        """设置页面"""
        settings_page = QWidget()
        
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(32, 32, 32, 32)
        settings_layout.setSpacing(24)
        
        # 顶部标题
        page_title = QLabel("全局设置")
        page_title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        settings_layout.addWidget(page_title)
        
        # 设置内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 24, 0, 0)
        content_layout.setSpacing(24)
        
        # Chrome路径设置
        chrome_layout = QVBoxLayout()
        chrome_layout.setSpacing(8)
        
        chrome_label = QLabel("Chrome路径")
        chrome_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 14px;")
        
        chrome_input_layout = QHBoxLayout()
        self.chrome_path_edit = ModernLineEdit(self.chrome_path)
        browse_chrome_btn = ModernButton("浏览...")
        browse_chrome_btn.setFixedWidth(90)
        browse_chrome_btn.clicked.connect(self.browse_chrome)
        
        chrome_input_layout.addWidget(self.chrome_path_edit)
        chrome_input_layout.addWidget(browse_chrome_btn)
        
        chrome_layout.addWidget(chrome_label)
        chrome_layout.addLayout(chrome_input_layout)
        
        content_layout.addLayout(chrome_layout)
        
        # 数据根目录设置
        data_layout = QVBoxLayout()
        data_layout.setSpacing(8)
        
        data_label = QLabel("数据根目录")
        data_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 14px;")
        
        data_input_layout = QHBoxLayout()
        self.data_root_edit = ModernLineEdit(self.data_root)
        browse_data_btn = ModernButton("浏览...")
        browse_data_btn.setFixedWidth(90)
        browse_data_btn.clicked.connect(self.browse_data_root)
        
        data_input_layout.addWidget(self.data_root_edit)
        data_input_layout.addWidget(browse_data_btn)
        
        data_layout.addWidget(data_label)
        data_layout.addLayout(data_input_layout)
        
        content_layout.addLayout(data_layout)
        
        # 快捷方式保存路径设置
        shortcuts_layout = QVBoxLayout()
        shortcuts_layout.setSpacing(8)
        
        shortcuts_label = QLabel("快捷方式保存路径")
        shortcuts_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 14px;")
        
        shortcuts_input_layout = QHBoxLayout()
        self.shortcuts_dir_edit = ModernLineEdit(self.shortcuts_dir)
        browse_shortcuts_btn = ModernButton("浏览...")
        browse_shortcuts_btn.setFixedWidth(90)
        browse_shortcuts_btn.clicked.connect(self.browse_shortcuts_dir)
        
        shortcuts_input_layout.addWidget(self.shortcuts_dir_edit)
        shortcuts_input_layout.addWidget(browse_shortcuts_btn)
        
        shortcuts_layout.addWidget(shortcuts_label)
        shortcuts_layout.addLayout(shortcuts_input_layout)
        
        shortcuts_help = QLabel("默认保存在桌面，可选择其他文件夹存放快捷方式")
        shortcuts_help.setStyleSheet(f"color: {TEXT_HINT_COLOR}; font-size: 12px;")
        shortcuts_layout.addWidget(shortcuts_help)
        
        content_layout.addLayout(shortcuts_layout)
        
        # 保存按钮
        save_layout = QHBoxLayout()
        save_btn = ModernButton("保存设置", accent=True)
        save_btn.clicked.connect(self.save_settings)
        save_layout.addStretch()
        save_layout.addWidget(save_btn)
        
        content_layout.addStretch()
        content_layout.addLayout(save_layout)
        
        settings_layout.addWidget(content_widget)
        
        return settings_page

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
            try:
                # 先确保占位符可见，然后在有实例的情况下才隐藏
                if hasattr(self, 'account_placeholder'):
                    self.account_placeholder.setVisible(True)
                
                # 如果没有实例，直接返回，保持占位符可见
                if not self.shortcuts:
                    return
                
                # 有实例时，尝试更新账号卡片
                self.update_account_cards()
            except Exception as e:
                print(f"更新账号卡片时出错: {str(e)}")
                # 在异常情况下也确保显示占位符
                if hasattr(self, 'account_placeholder'):
                    self.account_placeholder.setVisible(True)
        
        # 如果切换到设置页面，更新输入框的值
        if index == 2:
            self.chrome_path_edit.setText(self.chrome_path)
            self.data_root_edit.setText(self.data_root)
            self.shortcuts_dir_edit.setText(self.shortcuts_dir)

    def browse_chrome(self):
        """浏览选择Chrome可执行文件"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Chrome可执行文件",
            os.path.dirname(self.chrome_path_edit.text()),
            "可执行文件 (*.exe)"
        )
        if path:
            self.chrome_path_edit.setText(path)
    
    def browse_data_root(self):
        """浏览选择数据根目录"""
        path = QFileDialog.getExistingDirectory(
            self,
            "选择数据根目录",
            self.data_root_edit.text() or os.getcwd()
        )
        if path:
            self.data_root_edit.setText(path)
            
    def browse_shortcuts_dir(self):
        """浏览选择快捷方式保存目录"""
        path = QFileDialog.getExistingDirectory(
            self,
            "选择快捷方式保存目录",
            self.shortcuts_dir_edit.text() or self.shortcut_manager.desktop_path
        )
        if path:
            self.shortcuts_dir_edit.setText(path)
            
    def save_settings(self):
        """保存设置"""
        chrome_path = self.chrome_path_edit.text().strip()
        data_root = self.data_root_edit.text().strip()
        shortcuts_dir = self.shortcuts_dir_edit.text().strip()
        
        if chrome_path and data_root:
            # 验证Chrome路径是否存在
            if not os.path.exists(chrome_path):
                # 使用状态栏显示错误消息
                self.statusBar().showMessage("Chrome路径不存在，请检查路径是否正确", 5000)
                return
                
            self.chrome_path = chrome_path
            self.data_root = data_root
            self.user_modified_data_root = True
            
            # 设置快捷方式保存路径
            if shortcuts_dir and os.path.exists(shortcuts_dir):
                self.shortcuts_dir = shortcuts_dir
                self.shortcut_manager.set_shortcuts_dir(shortcuts_dir)
            else:
                if shortcuts_dir:
                    # 使用状态栏显示警告消息
                    self.statusBar().showMessage("快捷方式保存路径不存在，将使用默认路径", 5000)
                self.shortcuts_dir = self.shortcut_manager.desktop_path
                self.shortcuts_dir_edit.setText(self.shortcuts_dir)
            
            # 保存配置
            self.auto_save_config()
            # 使用状态栏显示成功消息
            self.statusBar().showMessage("设置已保存", 3000)
        else:
            # 使用状态栏显示错误消息
            self.statusBar().showMessage("请填写所有必要的设置项", 5000)

    def update_browser_grid(self):
        """更新浏览器网格"""
        # 清除现有的网格项
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # 清空卡片列表
        self.card_widgets = []
        
        # 设置网格布局属性
        self.grid_layout.setSpacing(16)  # 设置基础间距
        self.grid_layout.setContentsMargins(30, 20, 30, 20)  # 调整外边距
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)  # 顶部水平居中对齐
        
        # 添加浏览器卡片
        if not self.shortcuts:
            empty_label = QLabel('暂无Chrome实例\n点击"添加新实例"创建')
            empty_label.setFont(QFont(FONT_FAMILY, 14))
            empty_label.setStyleSheet(f"color: {TEXT_HINT_COLOR};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0)
            
            # 更新批量删除按钮状态
            self.batch_btn.setEnabled(False)
            return
        else:
            # 有快捷方式时启用批量删除按钮
            self.batch_btn.setEnabled(True)
        
        # 卡片参数
        card_width = 180  # 卡片宽度
        card_spacing = 30  # 调整卡片间距
        
        # 根据窗口状态确定布局
        if self.isMaximized():
            # 最大化状态：动态计算列数，但确保间距合理
            available_width = self.grid_widget.width() - 60  # 减去左右边距
            max_cols = min(6, (available_width + card_spacing) // (card_width + card_spacing))
        else:
            # 默认大小状态：固定4列
            max_cols = 4
        
        # 添加卡片到网格
        for i, shortcut in enumerate(self.shortcuts):
            row = i // max_cols
            col = i % max_cols
            card = BrowserCard(
                shortcut["name"], 
                shortcut["data_dir"], 
                self.chrome_path,
                on_delete=self.delete_shortcut
            )
            
            # 设置选择模式状态
            if self.is_batch_mode:
                card.set_select_mode(True)
                
            self.grid_layout.addWidget(card, row, col)
            self.card_widgets.append(card)
        
        # 设置水平和垂直间距
        self.grid_layout.setHorizontalSpacing(card_spacing)  # 水平间距
        self.grid_layout.setVerticalSpacing(card_spacing)  # 垂直间距

    def changeEvent(self, event):
        """窗口状态改变事件（最大化/还原）"""
        if event.type() == event.Type.WindowStateChange:
            # 窗口状态改变时更新网格布局
            self.update_browser_grid()
        super().changeEvent(event)

    def add_shortcut(self):
        """添加新快捷方式"""
        # 查找可用的实例编号
        used_numbers = set()
        for shortcut in self.shortcuts:
            # 从实例名称中提取编号
            name = shortcut["name"]
            if name.startswith("Chrome实例"):
                try:
                    num = int(name[len("Chrome实例"):])
                    used_numbers.add(num)
                except ValueError:
                    pass
            
            # 从数据目录中提取编号
            data_dir = shortcut["data_dir"]
            dir_name = os.path.basename(data_dir)
            if dir_name.startswith("Profile"):
                try:
                    num = int(dir_name[len("Profile"):])
                    used_numbers.add(num)
                except ValueError:
                    pass
                
        # 找到可用的最小编号
        next_number = 1
        while next_number in used_numbers:
            next_number += 1
            
        dialog = AddShortcutDialog(self, next_number - 1)  # 将参数改为下一个可用编号-1，以适应对话框内部+1的逻辑
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, dir_name = dialog.get_values()
            
            if not name or not dir_name:
                # 使用状态栏显示错误
                self.statusBar().showMessage("名称和目录名不能为空！", 5000)
                return
                
            if any(s["name"] == name for s in self.shortcuts):
                # 使用状态栏显示错误
                self.statusBar().showMessage(f"名称 '{name}' 已存在！", 5000)
                return
                
            # 确保数据目录名称未被使用
            if any(os.path.basename(s["data_dir"]) == dir_name for s in self.shortcuts):
                # 使用状态栏显示错误
                self.statusBar().showMessage(f"数据目录名 '{dir_name}' 已存在！", 5000)
                return
            
            # 确保数据目录是绝对路径
            data_dir = os.path.join(self.data_root, dir_name)
            
            shortcut = {
                "name": name,
                "data_dir": data_dir
            }
            
            # 先添加到数据库
            print(f"添加新实例到数据库: 名称={name}, 数据目录={data_dir}")
            db_success = self.config_manager.db_manager.save_chrome_instance(shortcut)
            print(f"数据库添加结果: {db_success}")
            
            if db_success:
                self.shortcuts.append(shortcut)
                
                # 创建快捷方式
                success = self.shortcut_manager.create_shortcut(name, data_dir, self.chrome_path)
                if success:
                    self.statusBar().showMessage(f"Chrome实例 '{name}' 创建成功", 3000)  # 显示3秒
                
                # 强制刷新实例列表 - 直接从数据库重新加载实例数据
                print("正在从数据库重新加载实例列表...")
                instances = self.config_manager.db_manager.get_all_chrome_instances()
                print(f"从数据库加载的实例数: {len(instances)}")
                self.shortcuts = instances
                
                # 更新界面和保存配置
                self.update_browser_grid()
                self.auto_save_config()
            else:
                self.statusBar().showMessage(f"Chrome实例 '{name}' 创建失败", 3000)  # 显示3秒
    
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
    
    def auto_save_config(self):
        """自动保存配置"""
        print(f"准备保存配置...")
        print(f"当前快捷方式列表: {[s['name'] for s in self.shortcuts]}")
        
        config = {
            'chrome_path': self.chrome_path,
            'data_root': self.data_root,
            'user_modified_data_root': self.user_modified_data_root,
            'shortcuts_dir': self.shortcuts_dir,
            'shortcuts': self.shortcuts,
            'account_info': self.account_info
        }
        self.config_manager.save_config(config)
        print(f"配置已保存到数据库")
        print(f"已保存配置 - Chrome路径: {self.chrome_path}")
        print(f"已保存配置 - 数据根目录: {self.data_root}")
        print(f"已保存配置 - 快捷方式目录: {self.shortcuts_dir}")
        print(f"已保存配置 - 快捷方式列表: {[s['name'] for s in self.shortcuts]}")
        
    def delete_shortcut(self, name, data_dir):
        """删除单个快捷方式"""
        print(f"正在删除快捷方式: 名称={name}, 数据目录={data_dir}")
        print(f"删除前的快捷方式列表: {[s['name'] for s in self.shortcuts]}")
        
        # 先尝试删除实际文件
        success = self.shortcut_manager.delete_shortcut(name, data_dir)
        print(f"文件删除结果: {success}")
        
        # 只有文件删除成功时，才继续进行数据库和内存数据的删除
        if success:
            # 从快捷方式列表中删除
            self.shortcuts = [s for s in self.shortcuts if s["name"] != name]
            print(f"删除后的快捷方式列表: {[s['name'] for s in self.shortcuts]}")
            
            # 从数据库中删除该实例
            db_success = self.config_manager.db_manager.delete_chrome_instance(name)
            print(f"从数据库删除实例结果: {db_success}")
            
            # 强制刷新实例列表 - 直接从数据库重新加载实例数据
            print("正在从数据库重新加载实例列表...")
            instances = self.config_manager.db_manager.get_all_chrome_instances()
            print(f"从数据库加载的实例数: {len(instances)}")
            self.shortcuts = instances
            
            # 更新界面
            self.update_browser_grid()
            
            # 保存配置
            self.auto_save_config()
            
            self.statusBar().showMessage(f"Chrome实例 '{name}' 已删除", 3000)  # 显示3秒
        else:
            # 删除失败时提醒用户
            self.statusBar().showMessage(f"无法删除Chrome实例 '{name}'，请确保浏览器已关闭", 5000)  # 显示5秒
    
    def toggle_batch_mode(self):
        """切换批量操作模式"""
        self.is_batch_mode = not self.is_batch_mode
        self.is_all_selected = False  # 重置全选状态
        
        # 更新按钮状态
        self.batch_btn.setVisible(not self.is_batch_mode)
        self.select_all_btn.setVisible(self.is_batch_mode)
        self.confirm_delete_btn.setVisible(self.is_batch_mode)
        self.cancel_batch_btn.setVisible(self.is_batch_mode)
        
        # 更新所有卡片的选择模式
        for card in self.card_widgets:
            card.set_select_mode(self.is_batch_mode)
            if not self.is_batch_mode:
                card.set_selected(False)  # 退出批量模式时取消所有选择
                
    def toggle_select_all(self):
        """切换全选状态"""
        self.is_all_selected = not self.is_all_selected
        self.select_all_btn.setText("取消全选" if self.is_all_selected else "全选")
        
        # 更新所有卡片的选中状态
        for card in self.card_widgets:
            card.set_selected(self.is_all_selected)
    
    def delete_selected_shortcuts(self):
        """删除选中的快捷方式"""
        # 获取所有选中的卡片
        selected_cards = [card for card in self.card_widgets if card.is_selected]
        
        if not selected_cards:
            self.statusBar().showMessage("请先选择要删除的Chrome实例", 3000)
            return
        
        print(f"批量删除: 选中了{len(selected_cards)}个实例")
        
        # 执行删除
        deleted_count = 0
        failed_count = 0
        failed_names = []
        
        for card in selected_cards:
            print(f"正在删除实例: {card.name}")
            
            # 先尝试删除实际文件
            success = self.shortcut_manager.delete_shortcut(card.name, card.data_dir)
            print(f"  文件删除结果: {success}")
            
            if success:
                # 从快捷方式列表中删除
                self.shortcuts = [s for s in self.shortcuts if s["name"] != card.name]
                
                # 从数据库中删除
                db_success = self.config_manager.db_manager.delete_chrome_instance(card.name)
                print(f"  数据库删除结果: {db_success}")
                
                deleted_count += 1
            else:
                failed_count += 1
                failed_names.append(card.name)
        
        print(f"批量删除: 成功删除{deleted_count}个实例，失败{failed_count}个")
        
        if deleted_count > 0:
            # 强制刷新实例列表 - 直接从数据库重新加载实例数据
            print("批量删除后正在从数据库重新加载实例列表...")
            instances = self.config_manager.db_manager.get_all_chrome_instances()
            print(f"从数据库加载的实例数: {len(instances)}")
            self.shortcuts = instances
            
            self.update_browser_grid()
            self.auto_save_config()
            
            message = f"已删除 {deleted_count} 个Chrome实例"
            if failed_count > 0:
                message += f"，{failed_count}个实例删除失败"
            self.statusBar().showMessage(message, 5000)
        elif failed_count > 0:
            # 所有删除都失败
            failure_list = ", ".join(failed_names[:3])
            if len(failed_names) > 3:
                failure_list += "等"
            self.statusBar().showMessage(f"无法删除实例 {failure_list}，请确保浏览器已关闭", 5000)
        
        # 退出批量模式
        self.toggle_batch_mode()

    def closeEvent(self, event):
        """窗口关闭事件，关闭数据库连接"""
        # 确保数据库连接正确关闭
        if hasattr(self.config_manager, 'db_manager'):
            self.config_manager.db_manager.close()
        # 调用父类方法
        super().closeEvent(event) 