"""
主窗口模块
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QGridLayout, QStackedWidget, QStyleFactory, QDialog, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        self.settings_btn.clicked.connect(lambda: self.switch_page(1))

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
        home_page = self.create_home_page()
        self.content_stack.addWidget(home_page)
        
        # 设置页面
        settings_page = self.create_settings_page()
        self.content_stack.addWidget(settings_page)

    def create_home_page(self):
        """创建主页"""
        home_page = QWidget()
        home_layout = QVBoxLayout(home_page)
        home_layout.setContentsMargins(20, 20, 20, 20)  # 减小内边距
        home_layout.setSpacing(16)  # 减小间距
        
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
        
        return home_page
        
    def create_settings_page(self):
        """创建设置页面"""
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
        self.settings_btn.setChecked(index == 1)
        
        # 如果切换到设置页面，更新输入框的值
        if index == 1:
            self.chrome_path_edit.setText(self.chrome_path)
            self.data_root_edit.setText(self.data_root)

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
            
    def save_settings(self):
        """保存设置"""
        chrome_path = self.chrome_path_edit.text().strip()
        data_root = self.data_root_edit.text().strip()
        
        if chrome_path and data_root:
            self.chrome_path = chrome_path
            self.data_root = data_root
            self.user_modified_data_root = True
            self.auto_save_config()
            self.message_dialogs.show_success_message("设置已保存")
            self.switch_page(0)  # 保存后返回主页
        else:
            self.message_dialogs.show_error_message("Chrome路径和数据根目录不能为空！")

    def update_browser_grid(self):
        """更新浏览器网格"""
        # 清除现有的网格项
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # 设置网格布局属性
        self.grid_layout.setSpacing(16)  # 设置基础间距
        self.grid_layout.setContentsMargins(0, 0, 0, 0)  # 移除外边距
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)  # 严格左上对齐
        
        # 添加浏览器卡片
        if not self.shortcuts:
            empty_label = QLabel('暂无Chrome实例\n点击"添加新实例"创建')
            empty_label.setFont(QFont(FONT_FAMILY, 14))
            empty_label.setStyleSheet(f"color: {TEXT_HINT_COLOR};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0)
            return
        
        # 固定每行最多显示的卡片数量
        # 根据窗口宽度调整，窗口越宽，每行显示的卡片越多
        card_width = 180  # 卡片宽度
        card_spacing = 16  # 卡片间距
        
        # 获取当前可用宽度
        available_width = self.grid_widget.width() - 20  # 预留一点边距
        
        # 计算每行最多能放几个卡片
        cols_per_row = max(1, (available_width + card_spacing) // (card_width + card_spacing))
        
        # 添加卡片到网格
        for i, shortcut in enumerate(self.shortcuts):
            row = i // cols_per_row
            col = i % cols_per_row
            card = BrowserCard(shortcut["name"], shortcut["data_dir"], self.chrome_path)
            self.grid_layout.addWidget(card, row, col)
        
        # 确保卡片之间的水平间距设置正确
        self.grid_layout.setHorizontalSpacing(card_spacing)

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 窗口大小改变时更新网格布局
        self.update_browser_grid()

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