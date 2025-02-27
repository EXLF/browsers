"""
主窗口模块
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QGridLayout, QStackedWidget, QStyleFactory, QDialog, 
    QFileDialog, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from .constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR, 
    TEXT_SECONDARY_COLOR, TEXT_HINT_COLOR, FONT_FAMILY
)
from .config import ConfigManager
from .shortcuts import ShortcutManager
from .extensions import ExtensionManager
from .ui.components import ModernButton, ModernLineEdit
from .ui.dialogs import AddShortcutDialog
from .ui.cards import BrowserCard
from .ui.message import MessageDialogs
from .ui.extensions_page import ExtensionsPage

class ChromeShortcutManager(QMainWindow):
    """Chrome多实例快捷方式管理器主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和固定大小
        self.setWindowTitle("Chrome多实例快捷方式管理器")
        self.setMinimumSize(1200, 800)
        self.setFixedSize(1200, 800)  # 设置固定大小
        
        # 允许最大化按钮
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        # 初始化消息对话框工具类
        self.message_dialogs = MessageDialogs(self)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(self)
        
        # 初始化快捷方式管理器
        self.shortcut_manager = ShortcutManager(self)
        
        # 初始化扩展管理器
        self.extension_manager = ExtensionManager(self.config_manager)
        
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
        
        # 设置应用整体样式 - 极简样式
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: #FAFAFA;
                font-family: 'Microsoft YaHei UI', 'SimHei', sans-serif;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                width: 8px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: #CCCCCC;
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            QLabel {{
                color: #333333;
            }}
            QLineEdit {{
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border: 1px solid #1A73E8;
            }}
            QPushButton {{
                padding: 6px 12px;
            }}
        """)
        
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
        self.sidebar_widget.setFixedWidth(220)  # 增加宽度
        
        # 简化侧边栏样式
        self.sidebar_widget.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-right: 1px solid #E0E0E0;
            }}
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)  # 增加内边距
        sidebar_layout.setSpacing(12)  # 增加间距
        
        # 标题
        title_label = QLabel("Chrome多实例管理器")
        title_label.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR}; margin-bottom: 8px;")
        title_label.setWordWrap(True)
        sidebar_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("轻松管理多个Chrome实例和扩展")
        subtitle_label.setFont(QFont(FONT_FAMILY, 10))
        subtitle_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR};")
        subtitle_label.setWordWrap(True)
        sidebar_layout.addWidget(subtitle_label)
        
        sidebar_layout.addSpacing(30)
        
        # 菜单按钮
        self.home_btn = self.create_menu_button("主页", True)
        self.extensions_btn = self.create_menu_button("扩展插件")
        self.settings_btn = self.create_menu_button("设置")
        
        sidebar_layout.addWidget(self.home_btn)
        sidebar_layout.addWidget(self.extensions_btn)
        sidebar_layout.addWidget(self.settings_btn)
        
        # 版本信息
        sidebar_layout.addStretch()
        version_label = QLabel("Version 1.0")
        version_label.setStyleSheet(f"color: {TEXT_HINT_COLOR};")
        version_label.setFont(QFont(FONT_FAMILY, 9))
        sidebar_layout.addWidget(version_label)
        
        # 连接信号
        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        self.extensions_btn.clicked.connect(lambda: self.switch_page(1))
        self.settings_btn.clicked.connect(lambda: self.switch_page(2))

    def create_menu_button(self, text, is_active=False):
        """创建菜单按钮"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        btn.setFixedHeight(46)  # 增加高度
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                text-align: left;
                color: {TEXT_PRIMARY_COLOR};
                font-size: 14px;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }}
            QPushButton:hover {{
                background-color: rgba(26, 115, 232, 0.1);
            }}
            QPushButton:checked {{
                background-color: rgba(26, 115, 232, 0.15);
                color: #1A73E8;
                font-weight: bold;
                border-left: 4px solid #1A73E8;
            }}
        """)
        
        return btn

    def setup_content_area(self):
        """设置右侧内容区"""
        self.content_stack = QStackedWidget()
        
        # 主页（浏览器网格视图）
        home_page = self.create_home_page()
        self.content_stack.addWidget(home_page)
        
        # 扩展管理页面
        extensions_page = self.create_extensions_page()
        self.content_stack.addWidget(extensions_page)
        
        # 设置页面
        settings_page = self.create_settings_page()
        self.content_stack.addWidget(settings_page)

    def create_home_page(self):
        """创建主页"""
        home_page = QWidget()
        home_layout = QVBoxLayout(home_page)
        home_layout.setContentsMargins(30, 30, 30, 30)  # 增加内边距
        home_layout.setSpacing(20)  # 增加间距
        
        # 顶部操作栏
        top_bar = QHBoxLayout()
        
        page_title = QLabel("我的浏览器")
        page_title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        page_title.setStyleSheet("color: #202124;")
        
        # 添加新实例按钮
        add_btn = QPushButton("添加新实例")
        add_btn.setFixedSize(140, 40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A73E8;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }
            QPushButton:hover {
                background-color: #1765CC;
            }
            QPushButton:pressed {
                background-color: #185ABC;
            }
        """)
        add_btn.clicked.connect(self.add_shortcut)
        
        # 批量操作按钮
        self.batch_btn = QPushButton("批量删除")
        self.batch_btn.setFixedSize(120, 40)
        self.batch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.batch_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #5F6368;
                border: 1px solid #DADCE0;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }
            QPushButton:hover {
                background-color: #F8F9FA;
                color: #202124;
                border-color: #D2E3FC;
            }
            QPushButton:pressed {
                background-color: #F1F3F4;
            }
        """)
        self.batch_btn.clicked.connect(self.toggle_batch_mode)
        
        # 批量删除确认按钮（初始隐藏）
        self.confirm_delete_btn = QPushButton("删除选中")
        self.confirm_delete_btn.setFixedSize(120, 40)
        self.confirm_delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #EA4335;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }
            QPushButton:hover {
                background-color: #D93025;
            }
            QPushButton:pressed {
                background-color: #C5221F;
            }
        """)
        self.confirm_delete_btn.setVisible(False)
        self.confirm_delete_btn.clicked.connect(self.delete_selected_shortcuts)
        
        # 取消批量操作按钮（初始隐藏）
        self.cancel_batch_btn = QPushButton("取消")
        self.cancel_batch_btn.setFixedSize(100, 40)
        self.cancel_batch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_batch_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #5F6368;
                border: 1px solid #DADCE0;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }
            QPushButton:hover {
                background-color: #F8F9FA;
                color: #202124;
            }
            QPushButton:pressed {
                background-color: #F1F3F4;
            }
        """)
        self.cancel_batch_btn.setVisible(False)
        self.cancel_batch_btn.clicked.connect(self.toggle_batch_mode)
        
        top_bar.addWidget(page_title)
        top_bar.addStretch()
        top_bar.addWidget(self.batch_btn)
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
                background: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.3);
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
        self.grid_layout.setSpacing(24)  # 增加卡片间距
        
        scroll_area.setWidget(self.grid_widget)
        home_layout.addWidget(scroll_area)
        
        # 批量操作状态
        self.is_batch_mode = False
        self.card_widgets = []  # 保存所有卡片组件
        
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

    def create_extensions_page(self):
        """创建扩展管理页面"""
        extensions_page = ExtensionsPage(
            parent=self,
            extension_manager=self.extension_manager,
            config_manager=self.config_manager
        )
        return extensions_page

    def switch_page(self, index):
        """切换页面"""
        self.content_stack.setCurrentIndex(index)
        
        # 更新菜单按钮状态
        self.home_btn.setChecked(index == 0)
        self.extensions_btn.setChecked(index == 1)
        self.settings_btn.setChecked(index == 2)
        
        # 如果切换到设置页面，更新输入框的值
        if index == 2:
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
        
        # 清空卡片列表
        self.card_widgets = []
        
        # 设置网格布局属性
        self.grid_layout.setSpacing(24)  # 设置基础间距
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
                self.statusBar().showMessage(f"Chrome实例 '{name}' 创建成功", 3000)  # 显示3秒
            
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

    def delete_shortcut(self, name, data_dir):
        """删除单个快捷方式"""
        # 从快捷方式列表中删除
        self.shortcuts = [s for s in self.shortcuts if s["name"] != name]
        
        # 显示正在删除的状态
        self.statusBar().showMessage(f"正在删除 Chrome 实例 '{name}'...", 0)  # 不自动消失
        
        # 使用异步方法删除实际文件
        self.shortcut_manager.delete_shortcut_async(
            name, 
            data_dir,
            success_callback=lambda success: self._on_delete_shortcut_finished(success, name),
            error_callback=self._on_delete_shortcut_error
        )
    
    def _on_delete_shortcut_finished(self, success, name):
        """删除快捷方式完成回调"""
        if success:
            self.update_browser_grid()
            self.auto_save_config()
            self.statusBar().showMessage(f"Chrome实例 '{name}' 已删除", 3000)  # 显示3秒
    
    def _on_delete_shortcut_error(self, error_message):
        """删除快捷方式错误回调"""
        self.statusBar().showMessage(f"删除失败: {error_message}", 5000)

    def toggle_batch_mode(self):
        """切换批量操作模式"""
        self.is_batch_mode = not self.is_batch_mode
        
        # 更新按钮状态
        self.batch_btn.setVisible(not self.is_batch_mode)
        self.confirm_delete_btn.setVisible(self.is_batch_mode)
        self.cancel_batch_btn.setVisible(self.is_batch_mode)
        
        # 更新所有卡片的选择模式
        for card in self.card_widgets:
            card.set_select_mode(self.is_batch_mode)
    
    def delete_selected_shortcuts(self):
        """删除选中的快捷方式"""
        # 获取所有选中的卡片
        selected_cards = [card for card in self.card_widgets if card.is_selected]
        
        if not selected_cards:
            self.statusBar().showMessage("请先选择要删除的Chrome实例", 3000)
            return
        
        # 显示正在删除的状态
        total_count = len(selected_cards)
        self.statusBar().showMessage(f"正在删除 {total_count} 个Chrome实例...", 0)  # 不自动消失
        
        # 保存要删除的卡片信息
        self.cards_to_delete = selected_cards.copy()
        self.deleted_count = 0
        self.total_to_delete = total_count
        
        # 开始删除第一个
        self._delete_next_card()
        
        # 退出批量模式
        self.toggle_batch_mode()
    
    def _delete_next_card(self):
        """删除下一个卡片"""
        if not self.cards_to_delete:
            # 所有卡片都已处理完毕
            if self.deleted_count > 0:
                self.update_browser_grid()
                self.auto_save_config()
                self.statusBar().showMessage(f"已删除 {self.deleted_count} 个Chrome实例", 3000)
            return
        
        # 取出下一个要删除的卡片
        card = self.cards_to_delete.pop(0)
        
        # 从快捷方式列表中删除
        self.shortcuts = [s for s in self.shortcuts if s["name"] != card.name]
        
        # 更新状态栏
        remaining = len(self.cards_to_delete)
        self.statusBar().showMessage(f"正在删除 {self.total_to_delete - remaining}/{self.total_to_delete} 个Chrome实例...", 0)
        
        # 使用异步方法删除实际文件
        self.shortcut_manager.delete_shortcut_async(
            card.name, 
            card.data_dir,
            success_callback=lambda success: self._on_batch_delete_finished(success),
            error_callback=self._on_delete_shortcut_error
        )
    
    def _on_batch_delete_finished(self, success):
        """批量删除单个项目完成回调"""
        if success:
            self.deleted_count += 1
        
        # 继续删除下一个
        self._delete_next_card() 