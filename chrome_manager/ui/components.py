"""
基础UI组件模块
"""

from PyQt6.QtWidgets import QLineEdit, QPushButton, QWidget, QLabel
from PyQt6.QtCore import Qt, QSize, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QColor

from ..constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, BORDER_COLOR, TEXT_PRIMARY_COLOR, 
    TEXT_HINT_COLOR, SURFACE_COLOR, FONT_FAMILY, TEXT_SECONDARY_COLOR,
    SUCCESS_COLOR, DANGER_COLOR, WARNING_COLOR
)

class ModernLineEdit(QLineEdit):
    """现代风格的输入框组件"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    """现代风格的按钮组件"""
    
    def __init__(self, text="", icon=None, accent=False, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.accent = accent
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
    """危险操作按钮组件"""
    
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

class StatusWidget(QWidget):
    """状态显示组件"""
    
    def __init__(self, status="未创建", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status
        self.setFixedHeight(24)
        self.setMinimumWidth(70)
    
    def paintEvent(self, event):
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
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.status) 