"""
对话框组件模块
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout,
    QGraphicsDropShadowEffect, QFileDialog
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QMouseEvent

from ..constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR, 
    TEXT_SECONDARY_COLOR, FONT_FAMILY
)
from .components import ModernLineEdit, ModernButton

class ModernDialog(QDialog):
    """现代风格的对话框基类"""
    
    def __init__(self, parent=None, title="对话框", width=450, height=250, frameless=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        
        if frameless:
            # 无边框窗口
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
            # 允许鼠标拖动窗口
            self.dragging = False
            self.drag_position = QPoint()
        else:
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
            
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # 设置样式 - 使用边框
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BACKGROUND_COLOR};
                border: 1px solid #E0E0E0;
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # 移除透明背景设置，避免显示异常
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件，用于实现窗口拖动"""
        if hasattr(self, 'dragging') and event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if hasattr(self, 'dragging'):
            self.dragging = False
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件，实现窗口拖动"""
        if hasattr(self, 'dragging') and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

class AddShortcutDialog(ModernDialog):
    """添加Chrome快捷方式对话框"""
    
    def __init__(self, parent=None, shortcut_count=0):
        super().__init__(parent, "添加Chrome快捷方式", 450, 330, frameless=True)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 标题和关闭按钮
        title_bar = QHBoxLayout()
        title_bar.setSpacing(0)
        
        title_label = QLabel("添加新的Chrome实例")
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR}; font-weight: bold; font-size: 12pt;")
        
        close_btn = ModernButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 15px;
                color: {TEXT_SECONDARY_COLOR};
                font-size: 16pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.05);
                color: {TEXT_PRIMARY_COLOR};
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
        """)
        close_btn.clicked.connect(self.reject)
        
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        title_bar.addWidget(close_btn)
        
        layout.addLayout(title_bar)
        layout.addSpacing(8)
        
        # 表单
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)
        
        # 快捷方式名称
        name_layout = QVBoxLayout()
        name_layout.setSpacing(8)
        name_label = QLabel("快捷方式名称")
        name_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR};")
        self.name_edit = ModernLineEdit(f"Chrome实例{shortcut_count + 1}")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        form_layout.addLayout(name_layout)
        
        # 数据目录名
        dir_layout = QVBoxLayout()
        dir_layout.setSpacing(8)
        dir_label = QLabel("数据目录名")
        dir_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR};")
        self.dir_edit = ModernLineEdit(f"Profile{shortcut_count + 1}")
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_edit)
        form_layout.addLayout(dir_layout)
        
        layout.addLayout(form_layout)
        layout.addSpacing(4)
        
        # 添加说明文本
        help_text = QLabel("数据目录名会作为Chrome用户数据存储目录的名称，\n不同实例应使用不同的数据目录名以避免冲突。")
        help_text.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 9pt;")
        help_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(help_text)
        
        layout.addStretch(1)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.cancel_button = ModernButton("取消")
        self.ok_button = ModernButton("确定", accent=True)
        
        # 优化按钮样式
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #F5F5F5;
                color: {TEXT_PRIMARY_COLOR};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #EAEAEA;
            }}
            QPushButton:pressed {{
                background-color: #DADADA;
            }}
        """)
        
        self.ok_button.setStyleSheet(f"""
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
        """)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)

    def get_values(self):
        return self.name_edit.text().strip(), self.dir_edit.text().strip()

class SettingsDialog(ModernDialog):
    """全局设置对话框"""
    
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
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR}; font-weight: bold; font-size: 16pt;")
        layout.addWidget(title_label)
        
        # Chrome路径设置
        chrome_layout = QVBoxLayout()
        chrome_layout.setSpacing(8)
        
        chrome_label = QLabel("Chrome路径")
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