"""
卡片UI组件模块
"""

import os
import sys
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QMessageBox, QHBoxLayout, 
    QCheckBox, QPushButton, QWidget, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor

# 导入提取图标所需的库
if sys.platform == 'win32':
    try:
        import win32com.client
    except ImportError:
        print("无法导入win32com模块，将使用备用图标")

from ..constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, BORDER_COLOR, 
    TEXT_PRIMARY_COLOR, TEXT_SECONDARY_COLOR, FONT_FAMILY
)
from .components import ModernButton

# 添加图标提取函数
def extract_icon_from_exe(exe_path):
    """
    从exe文件中提取图标
    
    Args:
        exe_path: exe文件路径
        
    Returns:
        QPixmap: 提取的图标
    """
    try:
        if not os.path.exists(exe_path):
            return None
            
        if sys.platform == 'win32':
            # 使用快捷方式方法提取图标（更可靠）
            try:
                # 创建临时快捷方式
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut("temp.lnk")
                shortcut.TargetPath = exe_path
                # 使用Chrome的默认图标
                shortcut.IconLocation = f"{exe_path}, 0"
                shortcut.Save()
                
                # 从快捷方式创建QIcon并获取像素图
                if os.path.exists("temp.lnk"):
                    icon = QIcon("temp.lnk")
                    # 清理临时文件
                    os.remove("temp.lnk")
                    
                    if not icon.isNull():
                        return icon.pixmap(48, 48)
            except Exception as e:
                print(f"创建临时快捷方式提取图标时出错: {str(e)}")
        
        # 尝试直接从exe创建QIcon
        icon = QIcon(exe_path)
        if not icon.isNull():
            return icon.pixmap(48, 48)
            
        return None
    except Exception as e:
        print(f"提取图标时出错: {str(e)}")
        return None

class BrowserCard(QFrame):
    """浏览器实例卡片组件"""
    
    def __init__(self, name, data_dir, chrome_path, parent=None, on_delete=None):
        super().__init__(parent)
        self.name = name
        self.data_dir = data_dir
        self.chrome_path = chrome_path
        self.on_delete = on_delete  # 删除回调函数
        self.is_select_mode = False  # 是否处于选择模式
        self.is_selected = False     # 是否被选中
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(180, 180)  # 卡片大小
        
        # 基础样式，无阴影
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #4285F4;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        
        # 顶部布局，包含选择框和删除按钮
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        
        # 选择框（默认隐藏）
        self.select_checkbox = QCheckBox()
        self.select_checkbox.setVisible(False)
        self.select_checkbox.stateChanged.connect(self.on_selection_changed)
        self.select_checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #1A73E8;
                background-color: #1A73E8;
            }
        """)
        
        # 删除按钮
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F2F2F2;
                color: #666666;
                font-size: 14px;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #FF5252;
                color: white;
            }
        """)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        
        top_layout.addWidget(self.select_checkbox, 0, Qt.AlignmentFlag.AlignLeft)
        top_layout.addStretch()
        top_layout.addWidget(self.delete_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(top_layout)
        
        # Chrome图标 - 简单样式
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 尝试加载图标，简单实现
        # 首先检查是否能从Chrome提取图标
        chrome_pixmap = extract_icon_from_exe(self.chrome_path)
        if chrome_pixmap:
            icon_label.setPixmap(chrome_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            # 失败则使用简单的文字
            icon_label.setText("C")
            icon_label.setStyleSheet("""
                background-color: #4285F4;
                color: white;
                border-radius: 24px;
                font-size: 20px;
                font-weight: bold;
            """)
        
        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 名称标签
        name_label = QLabel(self.name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #333333;
            margin-top: 6px;
        """)
        layout.addWidget(name_label)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 启动按钮
        launch_btn = QPushButton("启动")
        launch_btn.setFixedHeight(32)
        launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A73E8;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1765CC;
            }
        """)
        launch_btn.clicked.connect(self.launch_browser)
        layout.addWidget(launch_btn)

    def on_delete_clicked(self):
        """删除按钮点击事件"""
        if self.on_delete and callable(self.on_delete):
            msg_box = QMessageBox()
            msg_box.setWindowTitle("确认删除")
            msg_box.setText(f"确定要删除 {self.name} 吗？")
            msg_box.setInformativeText("此操作将删除快捷方式和对应的数据目录，删除后将无法恢复！")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            
            # 设置字体和样式
            font = QFont("Microsoft YaHei UI", 9)
            msg_box.setFont(font)
            
            # 应用现代化样式
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    border-radius: 8px;
                }
                QLabel {
                    color: #1F1F1F;
                    font-size: 14px;
                    padding: 10px;
                }
                QLabel#qt_msgbox_label {
                    font-weight: 500;
                    font-size: 15px;
                    padding-bottom: 0px;
                }
                QLabel#qt_msgbox_informativelabel {
                    color: #666666;
                    font-size: 13px;
                    padding-top: 0px;
                }
                QLabel#qt_msgboxex_icon_label {
                    padding: 15px;
                }
                QPushButton {
                    background-color: #F5F5F5;
                    color: #333333;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 24px;
                    min-width: 90px;
                    font-size: 13px;
                    font-weight: 500;
                    margin: 0px 5px;
                }
                QPushButton:hover {
                    background-color: #EEEEEE;
                }
                QPushButton:pressed {
                    background-color: #E0E0E0;
                }
                QPushButton[text="删除"] {
                    background-color: #FF4D4F;
                    color: white;
                }
                QPushButton[text="删除"]:hover {
                    background-color: #FF7875;
                }
                QPushButton[text="删除"]:pressed {
                    background-color: #D9363E;
                }
                QPushButton[text="取消"] {
                    background-color: white;
                    border: 1px solid #D9D9D9;
                }
                QPushButton[text="取消"]:hover {
                    background-color: #FAFAFA;
                    border-color: #40A9FF;
                    color: #40A9FF;
                }
            """)
            
            # 自定义按钮文本
            yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
            no_button = msg_box.button(QMessageBox.StandardButton.No)
            if yes_button:
                yes_button.setText("删除")
            if no_button:
                no_button.setText("取消")
            
            ret = msg_box.exec()
            if ret == QMessageBox.StandardButton.Yes:
                self.on_delete(self.name, self.data_dir)
    
    def set_select_mode(self, enabled):
        """设置是否进入选择模式"""
        self.is_select_mode = enabled
        self.select_checkbox.setVisible(enabled)
        self.delete_btn.setVisible(not enabled)
        self.is_selected = False
        self.select_checkbox.setChecked(False)
    
    def on_selection_changed(self, state):
        """选择状态变化事件"""
        self.is_selected = (state == Qt.CheckState.Checked.value)
        
    def launch_browser(self):
        """启动浏览器实例"""
        try:
            import subprocess
            # 修复命令行参数格式
            cmd = [
                self.chrome_path,
                f'--user-data-dir={self.data_dir}'  # 移除多余的引号
            ]
            print(f"启动Chrome命令: {cmd}")
            subprocess.Popen(cmd)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动Chrome失败：{str(e)}")

class ChromeStoreSearchResultCard(QFrame):
    """Chrome商店搜索结果卡片组件"""
    
    def __init__(self, extension, parent=None, on_add=None, is_installed=False):
        """
        初始化Chrome商店搜索结果卡片
        
        Args:
            extension: 扩展信息字典
            parent: 父组件
            on_add: 添加回调
            is_installed: 是否已安装
        """
        super().__init__(parent)
        self.extension = extension
        self.on_add = on_add
        self.is_installed = is_installed
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        # 直接打印扩展信息，用于调试
        print(f"设置卡片UI，扩展信息: {self.extension}")
        
        # 设置简洁的样式，去掉边框和悬停效果
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                margin: 0;
                padding: 0;
            }
        """)
        
        # 基本尺寸和比例
        self.setMinimumWidth(500)
        self.setMinimumHeight(100)
        self.setMaximumHeight(130)
        
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 12, 0, 12)  # 只保留上下边距
        main_layout.setSpacing(15)
        
        # 左侧图标区域
        icon_container = QWidget()
        icon_container.setFixedSize(80, 80)
        icon_container.setStyleSheet("background-color: transparent;")
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)  # 稍微减小图标尺寸
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setScaledContents(True)
        
        # 设置图标
        if self.extension.get('icon') and os.path.exists(self.extension.get('icon')):
            pixmap = QPixmap(self.extension.get('icon'))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            # 默认显示首字母
            initial = self.extension.get('name', '?')[0].upper()
            icon_label.setText(initial)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("""
                background-color: #4285F4;
                color: white;
                font-size: 28px;
                font-weight: bold;
                border-radius: 32px;
            """)
        
        icon_layout.addWidget(icon_label)
        main_layout.addWidget(icon_container)
        
        # 中间信息区域
        info_container = QWidget()
        info_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(4)  # 减小间距
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # 扩展名称
        name = self.extension.get('name', '未命名扩展')
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 500;
            color: #202124;
        """)
        info_layout.addWidget(name_label)
        
        # 发布者和评分信息放在同一行
        meta_info_layout = QHBoxLayout()
        meta_info_layout.setSpacing(12)
        meta_info_layout.setContentsMargins(0, 0, 0, 0)
        
        # 发布者信息
        publisher = self.extension.get('publisher', '')
        if publisher:
            publisher_label = QLabel(f"发布者: {publisher}")
            publisher_label.setStyleSheet("font-size: 13px; color: #5F6368;")
            meta_info_layout.addWidget(publisher_label)
        
        # 评分信息
        rating = self.extension.get('rating', '')
        if rating:
            rating_count = self.extension.get('rating_count', '')
            rating_text = f"评分: {rating}" + (f" ({rating_count})" if rating_count else "")
            rating_label = QLabel(rating_text)
            rating_label.setStyleSheet("font-size: 13px; color: #5F6368;")
            meta_info_layout.addWidget(rating_label)
        
        meta_info_layout.addStretch()
        info_layout.addLayout(meta_info_layout)
        
        # 描述信息
        description = self.extension.get('description', '无描述')
        if len(description) > 150:
            description = description[:150] + "..."
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 13px; color: #3C4043; margin-top: 2px;")
        info_layout.addWidget(desc_label)
        
        main_layout.addWidget(info_container, 1)
        
        # 右侧按钮区域
        button_container = QWidget()
        button_container.setFixedWidth(80)
        button_layout = QVBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        if self.is_installed:
            status_label = QLabel("已添加")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_label.setStyleSheet("""
                color: #0F9D58; 
                font-size: 13px; 
                font-weight: 500;
                padding: 6px 10px;
                background-color: #E6F4EA;
                border-radius: 4px;
            """)
            button_layout.addWidget(status_label)
        else:
            add_btn = QPushButton("添加")
            add_btn.setFixedSize(70, 32)
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1A73E8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 10px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #1557B0;
                }
            """)
            add_btn.clicked.connect(self._on_add_clicked)
            button_layout.addWidget(add_btn)
        
        main_layout.addWidget(button_container)
    
    def _on_add_clicked(self):
        """添加按钮点击事件"""
        if self.on_add and callable(self.on_add):
            self.on_add(self.extension) 