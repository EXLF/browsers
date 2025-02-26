"""
主窗口模块
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QGridLayout, QStackedWidget, QStyleFactory, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR, 
    TEXT_SECONDARY_COLOR, TEXT_HINT_COLOR, FONT_FAMILY
)
from .config import ConfigManager
from .shortcuts import ShortcutManager
from .ui.components import ModernButton
from .ui.dialogs import AddShortcutDialog, SettingsDialog
from .ui.cards import BrowserCard
from .ui.message import MessageDialogs

class ChromeShortcutManager(QMainWindow):
    """Chrome多实例快捷方式管理器主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和大小
        self.setWindowTitle("Chrome多实例快捷方式管理器")
        self.setMinimumSize(1200, 800)
        
        # 初始化消息对话框工具类
        self.message_dialogs = MessageDialogs(self)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(self)
        
        # 初始化快捷方式管理器
        self.shortcut_manager = ShortcutManager(self)
        
        # 初始化变量
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.data_root = os.getcwd()  # 默认使用当前目录
        self.user_modified_data_root = False
        self.shortcuts = []
        
        # 创建UI
        self.init_ui()
        
        # 加载配置
        self.load_config()
        
        # 更新快捷方式列表
        self.update_browser_grid()

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
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("Chrome多实例管理器")
        title_label.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR};")
        title_label.setWordWrap(True)
        sidebar_layout.addWidget(title_label)
        
        sidebar_layout.addSpacing(24)
        
        # 菜单按钮
        self.home_btn = self.create_menu_button("主页", True)
        self.settings_btn = self.create_menu_button("设置")
        
        sidebar_layout.addWidget(self.home_btn)
        sidebar_layout.addWidget(self.settings_btn)
        
        # 版本信息
        sidebar_layout.addStretch()
        version_label = QLabel("Version 1.0")
        version_label.setStyleSheet(f"color: {TEXT_HINT_COLOR};")
        version_label.setFont(QFont(FONT_FAMILY, 8))
        sidebar_layout.addWidget(version_label)
        
        # 连接信号
        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        self.settings_btn.clicked.connect(self.show_settings)

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
        
        # 主页（浏览器网格视图）
        home_page = QWidget()
        home_layout = QVBoxLayout(home_page)
        home_layout.setContentsMargins(32, 32, 32, 32)
        home_layout.setSpacing(24)
        
        # 顶部操作栏
        top_bar = QHBoxLayout()
        
        page_title = QLabel("我的浏览器")
        page_title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        
        add_btn = ModernButton("添加新实例", accent=True)
        add_btn.clicked.connect(self.add_shortcut)
        
        top_bar.addWidget(page_title)
        top_bar.addStretch()
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
        """)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(24)
        
        scroll_area.setWidget(self.grid_widget)
        home_layout.addWidget(scroll_area)
        
        self.content_stack.addWidget(home_page)

    def switch_page(self, index):
        """切换页面"""
        self.content_stack.setCurrentIndex(index)
        
        # 更新菜单按钮状态
        self.home_btn.setChecked(index == 0)
        self.settings_btn.setChecked(index == 1)

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self, self.chrome_path, self.data_root)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            chrome_path, data_root = dialog.get_values()
            if chrome_path and data_root:
                self.chrome_path = chrome_path
                self.data_root = data_root
                self.user_modified_data_root = True
                self.auto_save_config()
                self.message_dialogs.show_success_message("设置已保存")

    def update_browser_grid(self):
        """更新浏览器网格"""
        # 清除现有的网格项
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # 添加浏览器卡片
        row = 0
        col = 0
        max_cols = 4  # 每行最多显示4个卡片
        
        for shortcut in self.shortcuts:
            card = BrowserCard(shortcut["name"], shortcut["data_dir"], self.chrome_path)
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 添加空白卡片提示
        if not self.shortcuts:
            empty_label = QLabel('暂无Chrome实例\n点击"添加新实例"创建')
            empty_label.setFont(QFont(FONT_FAMILY, 14))
            empty_label.setStyleSheet(f"color: {TEXT_HINT_COLOR};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0, 1, max_cols)

    def add_shortcut(self):
        """添加新快捷方式"""
        dialog = AddShortcutDialog(self, len(self.shortcuts))
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, dir_name = dialog.get_values()
            
            if not name or not dir_name:
                self.message_dialogs.show_error_message("名称和目录名不能为空！")
                return
                
            if any(s["name"] == name for s in self.shortcuts):
                self.message_dialogs.show_error_message(f"名称 '{name}' 已存在！")
                return
            
            # 确保数据目录是绝对路径
            data_dir = os.path.join(self.data_root, dir_name)
            
            # 显示将要创建的数据目录路径
            msg = f"将在以下位置创建数据目录:\n{data_dir}\n\n是否继续?"
            if not self.message_dialogs.show_confirm_dialog(msg, "确认创建"):
                return
                
            shortcut = {
                "name": name,
                "data_dir": data_dir
            }
            
            self.shortcuts.append(shortcut)
            self.update_browser_grid()
            self.auto_save_config()
            
            # 创建快捷方式
            success = self.shortcut_manager.create_shortcut(name, data_dir, self.chrome_path)
            if success:
                self.message_dialogs.show_success_message(f"Chrome实例 '{name}' 创建成功！")
            
    def load_config(self):
        """加载配置"""
        config = self.config_manager.load_config()
        
        # 设置Chrome路径
        self.chrome_path = config.get('chrome_path', self.chrome_path)
        
        # 设置数据根目录
        self.data_root = config.get('data_root', self.data_root)
        self.user_modified_data_root = config.get('user_modified_data_root', False)
        
        # 加载快捷方式
        self.shortcuts = config.get('shortcuts', [])
    
    def auto_save_config(self):
        """自动保存配置"""
        config = {
            'chrome_path': self.chrome_path,
            'data_root': self.data_root,
            'user_modified_data_root': self.user_modified_data_root,
            'shortcuts': self.shortcuts
        }
        
        self.config_manager.save_config(config) 