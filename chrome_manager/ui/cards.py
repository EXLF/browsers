"""
卡片UI组件模块
"""

import os
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from ..constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, BORDER_COLOR, 
    TEXT_PRIMARY_COLOR, TEXT_SECONDARY_COLOR, FONT_FAMILY
)
from .components import ModernButton

class BrowserCard(QFrame):
    """浏览器实例卡片组件"""
    
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
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR}; font-weight: bold; font-size: 12pt;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 数据目录标签
        dir_label = QLabel(self.data_dir)
        dir_label.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 8pt;")
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
            # 修复命令行参数格式
            cmd = [
                self.chrome_path,
                f'--user-data-dir={self.data_dir}'  # 移除多余的引号
            ]
            print(f"启动Chrome命令: {cmd}")
            subprocess.Popen(cmd)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动Chrome失败：{str(e)}") 