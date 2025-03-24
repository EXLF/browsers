"""
设置页面模块，实现全局设置功能
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFileDialog
)
from PyQt6.QtGui import QFont

from ...constants import (
    TEXT_PRIMARY_COLOR, TEXT_SECONDARY_COLOR, TEXT_HINT_COLOR, FONT_FAMILY
)
from ..components import ModernButton, ModernLineEdit

class SettingsPage(QWidget):
    """设置页面类"""
    
    def __init__(self, parent=None):
        """初始化设置页面"""
        super().__init__(parent)
        self.main_window = parent
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        settings_layout = QVBoxLayout(self)
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
        self.chrome_path_edit = ModernLineEdit(self.main_window.chrome_path)
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
        self.data_root_edit = ModernLineEdit(self.main_window.data_root)
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
        self.shortcuts_dir_edit = ModernLineEdit(self.main_window.shortcuts_dir)
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
        
        # 添加分隔线
        settings_layout.addWidget(self._create_separator())
        
        # 添加更新部分标题
        update_section_label = QLabel("软件更新")
        update_section_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR}; font-size: 16px;")
        update_section_label.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        settings_layout.addWidget(update_section_label)
        
        # 添加更新按钮
        update_btn_layout = QHBoxLayout()
        update_btn = ModernButton("检查更新", accent=True)
        update_btn.clicked.connect(self.main_window.check_app_updates)
        update_btn_layout.addWidget(update_btn)
        update_btn_layout.addStretch()
        settings_layout.addLayout(update_btn_layout)
        
        # 添加说明
        update_desc = QLabel("点击检查是否有新版本可用，发现新版本时将提供下载链接")
        update_desc.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 12px;")
        settings_layout.addWidget(update_desc)
        
        # 添加底部留白
        settings_layout.addStretch()
        
        content_layout.addStretch()
        content_layout.addLayout(save_layout)
        
        settings_layout.addWidget(content_widget)
    
    def update_ui(self):
        """更新UI状态，重新加载最新设置"""
        self.chrome_path_edit.setText(self.main_window.chrome_path)
        self.data_root_edit.setText(self.main_window.data_root)
        self.shortcuts_dir_edit.setText(self.main_window.shortcuts_dir)
    
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
            self.shortcuts_dir_edit.text() or self.main_window.shortcut_manager.desktop_path
        )
        if path:
            self.shortcuts_dir_edit.setText(path)
            
    def save_settings(self):
        """保存设置"""
        chrome_path = self.chrome_path_edit.text().strip()
        data_root = self.data_root_edit.text().strip()
        shortcuts_dir = self.shortcuts_dir_edit.text().strip()
        
        if chrome_path and data_root:
            # 验证Chrome路径是否存在
            if not os.path.exists(chrome_path):
                # 使用状态栏显示错误消息
                self.main_window.statusBar().showMessage("Chrome路径不存在，请检查路径是否正确", 5000)
                return
                
            self.main_window.chrome_path = chrome_path
            self.main_window.data_root = data_root
            self.main_window.user_modified_data_root = True
            
            # 设置快捷方式保存路径
            if shortcuts_dir and os.path.exists(shortcuts_dir):
                self.main_window.shortcuts_dir = shortcuts_dir
                self.main_window.shortcut_manager.set_shortcuts_dir(shortcuts_dir)
            else:
                if shortcuts_dir:
                    # 使用状态栏显示警告消息
                    self.main_window.statusBar().showMessage("快捷方式保存路径不存在，将使用默认路径", 5000)
                self.main_window.shortcuts_dir = self.main_window.shortcut_manager.desktop_path
                self.shortcuts_dir_edit.setText(self.main_window.shortcuts_dir)
            
            # 保存配置
            self.main_window.auto_save_config()
            # 使用状态栏显示成功消息
            self.main_window.statusBar().showMessage("设置已保存", 3000)
        else:
            # 使用状态栏显示错误消息
            self.main_window.statusBar().showMessage("请填写所有必要的设置项", 5000) 

    def _create_separator(self):
        """创建分隔线"""
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #E0E0E0;")
        return separator 