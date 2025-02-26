"""
对话框组件模块
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout,
    QGraphicsDropShadowEffect, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ..constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR, 
    TEXT_SECONDARY_COLOR, FONT_FAMILY
)
from .components import ModernLineEdit, ModernButton

class ModernDialog(QDialog):
    """现代风格的对话框基类"""
    
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
    """添加Chrome快捷方式对话框"""
    
    def __init__(self, parent=None, shortcut_count=0):
        super().__init__(parent, "添加Chrome快捷方式", 450, 280)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("添加新的Chrome实例")
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR}; margin-bottom: 8px; font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)
        
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