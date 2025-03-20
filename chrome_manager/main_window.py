"""
主窗口模块
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QGridLayout, QStackedWidget, QStyleFactory, QDialog, QFileDialog, QPushButton
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
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(self)
        
        # 初始化快捷方式管理器
        self.shortcut_manager = ShortcutManager(self)
        
        # 初始化变量
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.data_root = os.getcwd()  # 默认使用当前目录
        self.shortcuts_dir = self.shortcut_manager.desktop_path  # 默认使用桌面路径
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
        self.settings_btn = self.create_menu_button("设置")
        
        sidebar_layout.addWidget(self.home_btn)
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
        settings_page = self.setup_settings_page()
        self.content_stack.addWidget(settings_page)

    def create_home_page(self):
        """创建主页"""
        home_page = QWidget()
        home_layout = QVBoxLayout(home_page)
        home_layout.setContentsMargins(20, 20, 20, 20)  # 减小内边距
        home_layout.setSpacing(16)  # 减小间距
        
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
        self.settings_btn.setChecked(index == 1)
        
        # 如果切换到设置页面，更新输入框的值
        if index == 1:
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
            self.chrome_path = chrome_path
            self.data_root = data_root
            self.user_modified_data_root = True
            
            # 设置快捷方式保存路径
            if shortcuts_dir and os.path.exists(shortcuts_dir):
                self.shortcuts_dir = shortcuts_dir
                self.shortcut_manager.set_shortcuts_dir(shortcuts_dir)
            else:
                if shortcuts_dir:
                    self.message_dialogs.show_error_message("快捷方式保存路径不存在，将使用默认路径")
                self.shortcuts_dir = self.shortcut_manager.desktop_path
                self.shortcuts_dir_edit.setText(self.shortcuts_dir)
            
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
                self.message_dialogs.show_error_message("名称和目录名不能为空！")
                return
                
            if any(s["name"] == name for s in self.shortcuts):
                self.message_dialogs.show_error_message(f"名称 '{name}' 已存在！")
                return
                
            # 确保数据目录名称未被使用
            if any(os.path.basename(s["data_dir"]) == dir_name for s in self.shortcuts):
                self.message_dialogs.show_error_message(f"数据目录名 '{dir_name}' 已存在！")
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
        
        # 设置快捷方式保存路径
        shortcuts_dir = config.get('shortcuts_dir')
        if shortcuts_dir and os.path.exists(shortcuts_dir):
            self.shortcuts_dir = shortcuts_dir
            self.shortcut_manager.set_shortcuts_dir(shortcuts_dir)
        
        # 加载快捷方式
        self.shortcuts = config.get('shortcuts', [])
    
    def auto_save_config(self):
        """自动保存配置"""
        config = {
            'chrome_path': self.chrome_path,
            'data_root': self.data_root,
            'user_modified_data_root': self.user_modified_data_root,
            'shortcuts_dir': self.shortcuts_dir,
            'shortcuts': self.shortcuts
        }
        
        self.config_manager.save_config(config)

    def delete_shortcut(self, name, data_dir):
        """删除单个快捷方式"""
        # 从快捷方式列表中删除
        self.shortcuts = [s for s in self.shortcuts if s["name"] != name]
        
        # 删除实际文件
        success = self.shortcut_manager.delete_shortcut(name, data_dir)
        
        if success:
            self.update_browser_grid()
            self.auto_save_config()
            self.statusBar().showMessage(f"Chrome实例 '{name}' 已删除", 3000)  # 显示3秒
    
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
        
        # 执行删除
        deleted_count = 0
        for card in selected_cards:
            success = self.shortcut_manager.delete_shortcut(card.name, card.data_dir)
            if success:
                # 从快捷方式列表中删除
                self.shortcuts = [s for s in self.shortcuts if s["name"] != card.name]
                deleted_count += 1
        
        if deleted_count > 0:
            self.update_browser_grid()
            self.auto_save_config()
            self.statusBar().showMessage(f"已删除 {deleted_count} 个Chrome实例", 3000)
        
        # 退出批量模式
        self.toggle_batch_mode() 