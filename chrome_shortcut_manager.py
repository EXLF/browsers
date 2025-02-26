import os
import json
import sys
import ctypes
import winshell
from win32com.client import Dispatch
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTreeWidget, QTreeWidgetItem, QFileDialog, 
                           QMessageBox, QDialog, QFormLayout, QFrame,
                           QGraphicsDropShadowEffect, QStyleFactory,
                           QHeaderView, QSizePolicy, QStackedWidget,
                           QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer, QSize, QRect, QRectF
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon, QPixmap, QPainter, QPen, QPainterPath, QBrush, QFontDatabase

# 加载字体
def load_system_font():
    """加载系统默认字体，为UI提供更好的字体支持"""
    # 尝试加载微软雅黑字体，如果失败则使用系统默认字体
    try:
        if os.path.exists("C:/Windows/Fonts/msyh.ttc"):
            font_id = QFontDatabase.addApplicationFont("C:/Windows/Fonts/msyh.ttc")
            if font_id >= 0:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    return font_families[0]
    except Exception:
        pass
    
    # 如果无法加载微软雅黑，返回系统默认字体
    return QApplication.font().family()

# 颜色常量
PRIMARY_COLOR = "#2382FE"
SUCCESS_COLOR = "#4CAF50"
DANGER_COLOR = "#F44336"
WARNING_COLOR = "#FF9800"
BACKGROUND_COLOR = "#FFFFFF"
SURFACE_COLOR = "#F8F9FA"
BORDER_COLOR = "#E0E0E0"
TEXT_PRIMARY_COLOR = "#333333"
TEXT_SECONDARY_COLOR = "#666666"
TEXT_HINT_COLOR = "#999999"

# 在应用程序启动后设置字体
FONT_FAMILY = None

class ModernLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global FONT_FAMILY
        self.setFont(QFont(FONT_FAMILY, 9))
        self.setMinimumHeight(36)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 12px;
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                selection-background-color: {PRIMARY_COLOR}40;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {PRIMARY_COLOR};
            }}
            QLineEdit:hover:!focus {{
                border: 1px solid #B0B0B0;
            }}
            QLineEdit:disabled {{
                background-color: {SURFACE_COLOR};
                color: {TEXT_HINT_COLOR};
            }}
        """)

class ModernButton(QPushButton):
    def __init__(self, text="", icon=None, accent=False, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        global FONT_FAMILY
        self.accent = accent
        self.setFont(QFont(FONT_FAMILY, 9))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        
        # 设置图标
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(18, 18))
        
        # 根据是否是强调按钮设置样式
        self._update_style()
    
    def _update_style(self):
        if self.accent:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PRIMARY_COLOR};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #1C75E5;
                }}
                QPushButton:pressed {{
                    background-color: #1567D3;
                }}
                QPushButton:disabled {{
                    background-color: {SURFACE_COLOR};
                    color: {TEXT_HINT_COLOR};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {SURFACE_COLOR};
                    color: {TEXT_PRIMARY_COLOR};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #EAECEF;
                }}
                QPushButton:pressed {{
                    background-color: #DEE2E6;
                }}
                QPushButton:disabled {{
                    background-color: {SURFACE_COLOR};
                    color: {TEXT_HINT_COLOR};
                }}
            """)

class DangerButton(ModernButton):
    def __init__(self, text="", icon=None, *args, **kwargs):
        super().__init__(text, icon, False, *args, **kwargs)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {DANGER_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #E53935;
            }}
            QPushButton:pressed {{
                background-color: #D32F2F;
            }}
            QPushButton:disabled {{
                background-color: {SURFACE_COLOR};
                color: {TEXT_HINT_COLOR};
            }}
        """)

class ModernDialog(QDialog):
    def __init__(self, parent=None, title="对话框", width=450, height=250):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # 设置样式
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BACKGROUND_COLOR};
                border-radius: 8px;
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class AddShortcutDialog(ModernDialog):
    def __init__(self, parent=None, shortcut_count=0):
        super().__init__(parent, "添加Chrome快捷方式", 450, 280)
        global FONT_FAMILY
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("添加新的Chrome实例")
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # 表单
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)
        
        # 快捷方式名称
        name_layout = QVBoxLayout()
        name_layout.setSpacing(8)
        name_label = QLabel("快捷方式名称")
        name_label.setFont(QFont(FONT_FAMILY, 9))
        name_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR};")
        self.name_edit = ModernLineEdit(f"Chrome实例{shortcut_count + 1}")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        form_layout.addLayout(name_layout)
        
        # 数据目录名
        dir_layout = QVBoxLayout()
        dir_layout.setSpacing(8)
        dir_label = QLabel("数据目录名")
        dir_label.setFont(QFont(FONT_FAMILY, 9))
        dir_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR};")
        self.dir_edit = ModernLineEdit(f"Profile{shortcut_count + 1}")
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_edit)
        form_layout.addLayout(dir_layout)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.cancel_button = ModernButton("取消")
        self.ok_button = ModernButton("确定", accent=True)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)

    def get_values(self):
        return self.name_edit.text().strip(), self.dir_edit.text().strip()

class StatusWidget(QWidget):
    def __init__(self, status="未创建", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status
        self.setFixedHeight(24)
        self.setMinimumWidth(70)
    
    def paintEvent(self, event):
        global FONT_FAMILY
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置颜色
        if self.status == "已创建":
            bg_color = QColor(SUCCESS_COLOR).lighter(170)
            text_color = QColor(SUCCESS_COLOR).darker(150)
        elif self.status == "创建失败":
            bg_color = QColor(DANGER_COLOR).lighter(170)
            text_color = QColor(DANGER_COLOR).darker(150)
        else:
            bg_color = QColor(WARNING_COLOR).lighter(170)
            text_color = QColor(WARNING_COLOR).darker(150)
        
        # 绘制背景
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), 12, 12)
        painter.fillPath(path, bg_color)
        
        # 绘制文本
        painter.setPen(text_color)
        painter.setFont(QFont(FONT_FAMILY, 8))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.status)

class BrowserCard(QFrame):
    def __init__(self, name, data_dir, chrome_path, parent=None):
        super().__init__(parent)
        self.name = name
        self.data_dir = data_dir
        self.chrome_path = chrome_path
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(200, 200)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BACKGROUND_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
            }}
            QFrame:hover {{
                border: 1px solid {PRIMARY_COLOR};
                background-color: {PRIMARY_COLOR}10;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Chrome图标
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        # 尝试从Chrome可执行文件中提取图标
        try:
            chrome_icon = QIcon(self.chrome_path)
            if not chrome_icon.isNull():
                pixmap = chrome_icon.pixmap(64, 64)
                icon_label.setPixmap(pixmap)
            else:
                # 如果无法从Chrome获取图标，使用一个简单的文本替代
                icon_label.setText("Chrome")
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                icon_label.setStyleSheet(f"""
                    background-color: {PRIMARY_COLOR};
                    color: white;
                    border-radius: 32px;
                    font-size: 12px;
                    font-weight: bold;
                """)
        except Exception:
            # 如果出现任何错误，使用文本替代
            icon_label.setText("Chrome")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet(f"""
                background-color: {PRIMARY_COLOR};
                color: white;
                border-radius: 32px;
                font-size: 12px;
                font-weight: bold;
            """)
        
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 名称标签
        name_label = QLabel(self.name)
        name_label.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR};")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 数据目录标签
        dir_label = QLabel(self.data_dir)
        dir_label.setFont(QFont(FONT_FAMILY, 8))
        dir_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR};")
        dir_label.setWordWrap(True)
        dir_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(dir_label)
        
        # 启动按钮
        launch_btn = ModernButton("启动", accent=True)
        launch_btn.setFixedHeight(32)
        launch_btn.clicked.connect(self.launch_browser)
        layout.addWidget(launch_btn)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def launch_browser(self):
        """启动浏览器实例"""
        try:
            import subprocess
            subprocess.Popen([
                self.chrome_path,
                f'--user-data-dir="{self.data_dir}"'
            ])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动Chrome失败：{str(e)}")

class SettingsDialog(ModernDialog):
    def __init__(self, parent=None, chrome_path="", data_root=""):
        super().__init__(parent, "全局设置", 600, 300)
        self.chrome_path = chrome_path
        self.data_root = data_root
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("全局设置")
        title_label.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Chrome路径设置
        chrome_layout = QVBoxLayout()
        chrome_layout.setSpacing(8)
        
        chrome_label = QLabel("Chrome路径")
        chrome_label.setFont(QFont(FONT_FAMILY, 9))
        chrome_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR};")
        
        chrome_input_layout = QHBoxLayout()
        self.chrome_path_edit = ModernLineEdit(self.chrome_path)
        browse_chrome_btn = ModernButton("浏览...")
        browse_chrome_btn.setFixedWidth(90)
        browse_chrome_btn.clicked.connect(self.browse_chrome)
        
        chrome_input_layout.addWidget(self.chrome_path_edit)
        chrome_input_layout.addWidget(browse_chrome_btn)
        
        chrome_layout.addWidget(chrome_label)
        chrome_layout.addLayout(chrome_input_layout)
        
        layout.addLayout(chrome_layout)
        
        # 数据根目录设置
        data_layout = QVBoxLayout()
        data_layout.setSpacing(8)
        
        data_label = QLabel("数据根目录")
        data_label.setFont(QFont(FONT_FAMILY, 9))
        data_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR};")
        
        data_input_layout = QHBoxLayout()
        self.data_root_edit = ModernLineEdit(self.data_root)
        browse_data_btn = ModernButton("浏览...")
        browse_data_btn.setFixedWidth(90)
        browse_data_btn.clicked.connect(self.browse_data_root)
        
        data_input_layout.addWidget(self.data_root_edit)
        data_input_layout.addWidget(browse_data_btn)
        
        data_layout.addWidget(data_label)
        data_layout.addLayout(data_input_layout)
        
        layout.addLayout(data_layout)
        
        layout.addStretch()
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.cancel_button = ModernButton("取消")
        self.ok_button = ModernButton("保存", accent=True)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def browse_chrome(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Chrome可执行文件",
            os.path.dirname(self.chrome_path_edit.text()),
            "可执行文件 (*.exe)"
        )
        if path:
            self.chrome_path_edit.setText(path)
    
    def browse_data_root(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择数据根目录",
            self.data_root_edit.text() or os.getcwd()
        )
        if path:
            self.data_root_edit.setText(path)
    
    def get_values(self):
        return self.chrome_path_edit.text().strip(), self.data_root_edit.text().strip()

class ChromeShortcutManager(QMainWindow):
    def __init__(self):
        super().__init__()
        global FONT_FAMILY
        self.user_modified_data_root = False
        
        # 设置窗口标题和大小
        self.setWindowTitle("Chrome多实例快捷方式管理器")
        self.setMinimumSize(1200, 800)
        
        # 应用全局字体
        self.setFont(QFont(FONT_FAMILY, 9))
        
        # 初始化变量
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.data_root = os.getcwd()  # 默认使用当前目录
        print(f"初始化数据根目录: {self.data_root}")
        
        self.desktop_path = winshell.desktop()
        
        # 配置文件路径
        appdata_dir = os.getenv('APPDATA')
        print(f"APPDATA目录: {appdata_dir}")
        self.config_file = os.path.join(appdata_dir, 'ChromeShortcuts', 'config.json')
        print(f"配置文件路径: {self.config_file}")
        
        self.shortcuts = []
        
        # 创建UI
        self.init_ui()
        
        # 确保配置目录存在
        self.ensure_config_dir()
        
        # 加载配置
        self.load_config()
        
        # 确保数据根目录不为空
        if not self.data_root:
            self.data_root = os.getcwd()
            print(f"数据根目录为空，重置为当前目录: {self.data_root}")
        
        # 更新快捷方式列表
        self.update_browser_grid()

    def init_ui(self):
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
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(200)
        self.sidebar_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {SURFACE_COLOR};
                border-right: 1px solid {BORDER_COLOR};
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
        btn = QPushButton(text)
        btn.setFont(QFont(FONT_FAMILY, 9))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
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
        self.content_stack.setCurrentIndex(index)
        
        # 更新菜单按钮状态
        self.home_btn.setChecked(index == 0)
        self.settings_btn.setChecked(index == 1)

    def show_settings(self):
        dialog = SettingsDialog(self, self.chrome_path, self.data_root)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            chrome_path, data_root = dialog.get_values()
            if chrome_path and data_root:
                self.chrome_path = chrome_path
                self.data_root = data_root
                self.user_modified_data_root = True
                self.auto_save_config()
                self.show_success_message("设置已保存")

    def update_browser_grid(self):
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
        dialog = AddShortcutDialog(self, len(self.shortcuts))
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, dir_name = dialog.get_values()
            
            if not name or not dir_name:
                self.show_error_message("名称和目录名不能为空！")
                return
                
            if any(s["name"] == name for s in self.shortcuts):
                self.show_error_message(f"名称 '{name}' 已存在！")
                return
            
            # 确保数据目录是绝对路径
            data_dir = os.path.join(self.data_root, dir_name)
            
            # 显示将要创建的数据目录路径
            msg = f"将在以下位置创建数据目录:\n{data_dir}\n\n是否继续?"
            if not self.show_confirm_dialog("确认创建", msg):
                return
                
            shortcut = {
                "name": name,
                "data_dir": data_dir
            }
            
            self.shortcuts.append(shortcut)
            self.update_browser_grid()
            self.auto_save_config()
            
            try:
                self.create_shortcut(name, data_dir)
                self.show_success_message(f"Chrome实例 '{name}' 创建成功！")
            except Exception as e:
                self.show_error_message(f"创建快捷方式失败：{str(e)}")

    def create_shortcut(self, name, data_dir):
        """创建快捷方式"""
        shortcut_path = os.path.join(self.desktop_path, f"{name}.lnk")
        
        os.makedirs(data_dir, exist_ok=True)
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = self.chrome_path
        shortcut.Arguments = f'--user-data-dir="{data_dir}"'
        shortcut.Description = f"Chrome - {name}"
        shortcut.IconLocation = f"{self.chrome_path}, 0"
        shortcut.WorkingDirectory = os.path.dirname(self.chrome_path)
        shortcut.save()

    def load_config(self):
        """加载配置"""
        print(f"尝试加载配置文件: {self.config_file}")
        print(f"配置文件是否存在: {os.path.exists(self.config_file)}")
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"成功读取配置文件内容: {config}")
                    
                    # 加载Chrome路径
                    self.chrome_path = config.get('chrome_path', self.chrome_path)
                    print(f"加载Chrome路径: {self.chrome_path}")
                    
                    # 始终加载保存的数据根目录
                    saved_data_root = config.get('data_root')
                    print(f"配置文件中的数据根目录: {saved_data_root}")
                    
                    if saved_data_root and os.path.exists(saved_data_root):
                        self.data_root = saved_data_root
                        self.user_modified_data_root = True
                        print(f"已设置数据根目录为: {self.data_root}")
                    else:
                        if not saved_data_root:
                            print("配置文件中数据根目录为空，使用默认值")
                        elif not os.path.exists(saved_data_root):
                            print(f"配置文件中的数据根目录不存在: {saved_data_root}，使用默认值")
                    
                    # 加载快捷方式
                    self.shortcuts = config.get('shortcuts', [])
                    print(f"加载了 {len(self.shortcuts)} 个快捷方式")
                    
            except Exception as e:
                self.show_error_message(f"加载配置文件失败：{str(e)}")
                print(f"加载配置文件错误: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("配置文件不存在，将使用默认设置")

    def auto_save_config(self):
        """自动保存配置"""
        try:
            print(f"保存配置 - Chrome路径: {self.chrome_path}")
            print(f"保存配置 - 数据根目录: {self.data_root}")
            
            # 确保数据根目录不为空
            if not self.data_root:
                self.data_root = os.getcwd()
                print(f"数据根目录为空，使用当前目录: {self.data_root}")
            
            # 确保目录存在
            if not os.path.exists(self.data_root):
                try:
                    os.makedirs(self.data_root, exist_ok=True)
                    print(f"创建数据根目录: {self.data_root}")
                except Exception as e:
                    print(f"创建数据根目录失败: {str(e)}")
            
            # 准备配置数据
            config = {
                'chrome_path': self.chrome_path,
                'data_root': self.data_root,
                'user_modified_data_root': self.user_modified_data_root,
                'shortcuts': self.shortcuts
            }
            
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            print(f"确保配置目录存在: {config_dir}")
            os.makedirs(config_dir, exist_ok=True)
            
            # 保存配置文件
            print(f"正在保存配置到: {self.config_file}")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"配置已成功保存，数据根目录: {self.data_root}")
            
            # 验证配置文件是否已创建
            if os.path.exists(self.config_file):
                print(f"配置文件已成功创建: {self.config_file}")
                print(f"配置文件大小: {os.path.getsize(self.config_file)} 字节")
            else:
                print(f"警告: 配置文件未能创建: {self.config_file}")
                
        except Exception as e:
            error_msg = f"保存配置文件失败：{str(e)}"
            self.show_error_message(error_msg)
            print(f"保存配置错误: {error_msg}")
            import traceback
            traceback.print_exc()

    def show_info_message(self, message):
        """显示信息消息"""
        global FONT_FAMILY
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("提示")
        msg_box.setText(message)
        msg_box.setFont(QFont(FONT_FAMILY, 9))
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BACKGROUND_COLOR};
            }}
            QLabel {{
                color: {TEXT_PRIMARY_COLOR};
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
                min-height: 30px;
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{
                background-color: #1C75E5;
            }}
            QPushButton:pressed {{
                background-color: #1567D3;
            }}
        """)
        msg_box.exec()

    def show_error_message(self, message):
        """显示错误消息"""
        global FONT_FAMILY
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("错误")
        msg_box.setText(message)
        msg_box.setFont(QFont(FONT_FAMILY, 9))
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BACKGROUND_COLOR};
            }}
            QLabel {{
                color: {TEXT_PRIMARY_COLOR};
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
                min-height: 30px;
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{
                background-color: #1C75E5;
            }}
            QPushButton:pressed {{
                background-color: #1567D3;
            }}
        """)
        msg_box.exec()

    def show_success_message(self, message):
        """显示成功消息"""
        global FONT_FAMILY
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("成功")
        msg_box.setText(message)
        msg_box.setFont(QFont(FONT_FAMILY, 9))
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BACKGROUND_COLOR};
            }}
            QLabel {{
                color: {TEXT_PRIMARY_COLOR};
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
                min-height: 30px;
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{
                background-color: #1C75E5;
            }}
            QPushButton:pressed {{
                background-color: #1567D3;
            }}
        """)
        msg_box.exec()

    def show_confirm_dialog(self, title, message):
        """显示确认对话框"""
        global FONT_FAMILY
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(QFont(FONT_FAMILY, 9))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BACKGROUND_COLOR};
            }}
            QLabel {{
                color: {TEXT_PRIMARY_COLOR};
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
                min-height: 30px;
                font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{
                background-color: #1C75E5;
            }}
            QPushButton:pressed {{
                background-color: #1567D3;
            }}
        """)
        return msg_box.exec() == QMessageBox.StandardButton.Yes

    def ensure_config_dir(self):
        """确保配置目录存在"""
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir, exist_ok=True)
                print(f"创建配置目录: {config_dir}")
            except Exception as e:
                print(f"创建配置目录失败: {str(e)}")
                self.show_error_message(f"创建配置目录失败: {str(e)}")
        else:
            print(f"配置目录已存在: {config_dir}")

def main():
    try:
        # 启用高DPI支持
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        
        app = QApplication(sys.argv)
        
        # 设置全局样式
        app.setStyle(QStyleFactory.create('Fusion'))
        
        # 设置全局字体
        global FONT_FAMILY
        FONT_FAMILY = load_system_font()
        
        # 添加调试信息
        print(f"加载字体: {FONT_FAMILY}")
        print(f"Python版本: {sys.version}")
        try:
            from PyQt6.QtCore import QLibraryInfo
            print(f"PyQt6版本: {QLibraryInfo.version().toString()}")
        except Exception as e:
            print(f"无法获取PyQt6版本: {str(e)}")
        
        window = ChromeShortcutManager()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"程序启动错误: {str(e)}")
        print("详细错误信息:")
        import traceback
        traceback.print_exc()
        print("\n系统信息:")
        print(f"Python版本: {sys.version}")
        print(f"操作系统: {sys.platform}")
        print(f"当前工作目录: {os.getcwd()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 