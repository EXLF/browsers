"""
卡片UI组件模块
"""

import os
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QMessageBox, QHBoxLayout
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
        self.setFixedSize(180, 180)  # 减小卡片尺寸
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Chrome图标 - 圆形蓝色背景
        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setText("Chrome")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            background-color: #4285F4;
            color: white;
            border-radius: 30px;
            font-size: 12px;
            font-weight: bold;
        """)
        
        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 名称标签 - 简单文本
        name_label = QLabel(self.name)
        name_label.setStyleSheet("""
            color: black;
            font-size: 12px;
            font-weight: bold;
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 数据目录标签 - 简单文本
        dir_name = os.path.basename(self.data_dir)
        dir_label = QLabel(dir_name)
        dir_label.setStyleSheet("""
            color: #666666;
            font-size: 12px;
        """)
        dir_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(dir_label)
        
        # 启动按钮
        launch_btn = ModernButton("启动", accent=True)
        launch_btn.setFixedHeight(36)
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