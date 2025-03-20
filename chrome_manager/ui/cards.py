"""
卡片UI组件模块
"""

import os
import sys
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QMessageBox, QHBoxLayout, QCheckBox, QPushButton, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QPixmap

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
        self.setFixedSize(180, 180)  # 卡片尺寸
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)  # 进一步减小整体间距
        
        # 顶部布局，包含选择框和删除按钮
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)
        
        # 选择框（默认隐藏）
        self.select_checkbox = QCheckBox()
        self.select_checkbox.setVisible(False)
        self.select_checkbox.stateChanged.connect(self.on_selection_changed)
        self.select_checkbox.setStyleSheet("""
            QCheckBox {
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #E0E0E0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4285F4;
                border-radius: 3px;
                background-color: #4285F4;
                image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>');
            }
        """)
        
        # 删除按钮 - 改进样式和大小
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F2F2F2;
                color: #666666;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                text-align: center;
                padding: 0px;
                line-height: 20px;
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
        
        # Chrome图标 - 使用指定图片作为图标
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)  # 图标尺寸
        
        # 图标图片路径
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "image.png")
        
        # 检查图片是否存在
        if os.path.exists(icon_path):
            # 加载图片
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap)
            icon_label.setScaledContents(True)  # 确保图标填充整个标签
        else:
            # 如果图片不存在，尝试提取Chrome图标作为备选
            chrome_pixmap = extract_icon_from_exe(self.chrome_path)
            
            if chrome_pixmap:
                # 如果成功提取到图标，则使用它
                icon_label.setPixmap(chrome_pixmap)
                icon_label.setScaledContents(True)  # 确保图标填充整个标签
            else:
                # 如果无法提取图标，则使用CSS绘制的Chrome风格图标作为最后备选
                icon_label.setStyleSheet("""
                    QLabel {
                        background-color: transparent;
                        border-radius: 24px;
                        background: qradialgradient(
                            cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, 
                            stop:0 #4285F4, stop:0.3 #4285F4, 
                            stop:0.31 white, stop:0.34 white, 
                            stop:0.35 #4285F4, stop:0.37 #4285F4,
                            stop:0.38 #34A853, stop:0.50 #34A853,
                            stop:0.51 #FBBC05, stop:0.63 #FBBC05,
                            stop:0.64 #EA4335, stop:0.76 #EA4335,
                            stop:0.77 #4285F4, stop:1 #4285F4
                        );
                    }
                """)
        
        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 名称标签 - 简单文本
        name_label = QLabel(self.name)
        name_label.setFixedHeight(20)  # 固定高度
        name_label.setStyleSheet("""
            color: #333333;
            font-size: 13px;
            font-weight: 500;
            background-color: transparent;
            border: none;
            padding: 0;
            margin: 0;
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 启动按钮
        launch_btn = ModernButton("启动", accent=True)
        launch_btn.setFixedHeight(32)
        launch_btn.clicked.connect(self.launch_browser)
        layout.addWidget(launch_btn)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)

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
        """设置选择模式"""
        self.is_select_mode = enabled
        self.select_checkbox.setVisible(enabled)
        self.delete_btn.setVisible(not enabled)
        
    def set_selected(self, selected):
        """设置选中状态"""
        self.is_selected = selected
        self.select_checkbox.setChecked(selected)
        
    def on_selection_changed(self, state):
        """选择状态改变事件"""
        self.is_selected = state == Qt.CheckState.Checked.value
        
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