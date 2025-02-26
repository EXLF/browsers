"""
消息对话框模块
"""

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QFont

from ..constants import (
    PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR, FONT_FAMILY
)

class MessageDialogs:
    """消息对话框工具类，提供各种类型的消息对话框"""
    
    def __init__(self, parent):
        """
        初始化消息对话框工具类
        
        Args:
            parent: 父窗口实例
        """
        self.parent = parent
        
    def show_info_message(self, message, title="提示"):
        """
        显示信息消息
        
        Args:
            message: 消息内容
            title: 对话框标题
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(QFont(FONT_FAMILY, 9))
        msg_box.setStyleSheet(self._get_message_style())
        msg_box.exec()
    
    def show_error_message(self, message, title="错误"):
        """
        显示错误消息
        
        Args:
            message: 消息内容
            title: 对话框标题
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(QFont(FONT_FAMILY, 9))
        msg_box.setStyleSheet(self._get_message_style())
        msg_box.exec()
    
    def show_success_message(self, message, title="成功"):
        """
        显示成功消息
        
        Args:
            message: 消息内容
            title: 对话框标题
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(QFont(FONT_FAMILY, 9))
        msg_box.setStyleSheet(self._get_message_style())
        msg_box.exec()
    
    def show_confirm_dialog(self, message, title="确认"):
        """
        显示确认对话框
        
        Args:
            message: 消息内容
            title: 对话框标题
            
        Returns:
            bool: 用户是否确认
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(QFont(FONT_FAMILY, 9))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        msg_box.setStyleSheet(self._get_message_style())
        return msg_box.exec() == QMessageBox.StandardButton.Yes
    
    def _get_message_style(self):
        """
        获取消息对话框样式
        
        Returns:
            str: 样式表字符串
        """
        return f"""
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
        """ 