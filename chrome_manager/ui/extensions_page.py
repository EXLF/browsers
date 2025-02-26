"""
扩展管理页面UI模块
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QFileDialog, QDialog, 
    QLineEdit, QTextEdit, QFormLayout, QMessageBox,
    QCheckBox, QScrollArea, QFrame, QGroupBox, QGridLayout, QWidget,
    QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QFont

from ..constants import PRIMARY_COLOR, TEXT_PRIMARY_COLOR, TEXT_SECONDARY_COLOR
from .components import ModernButton, SectionTitle
from .message import show_message
from .cards import ChromeStoreSearchResultCard

class ExtensionCard(QFrame):
    """扩展卡片组件"""
    
    def __init__(self, extension, parent=None, on_remove=None, on_install=None):
        """
        初始化扩展卡片
        
        Args:
            extension: 扩展信息字典
            parent: 父组件
            on_remove: 删除回调
            on_install: 安装回调
        """
        super().__init__(parent)
        self.extension = extension
        self.on_remove = on_remove
        self.on_install = on_install
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        self.setFixedSize(180, 180)  # 与BrowserCard保持一致的尺寸
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)  # 减小整体间距
        
        # 顶部布局，包含删除按钮
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)
        
        # 删除按钮
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
        self.delete_btn.clicked.connect(self._on_remove_clicked)
        
        top_layout.addStretch()
        top_layout.addWidget(self.delete_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(top_layout)
        
        # 扩展图标
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)  # 图标尺寸
        
        # 尝试加载图标
        if self.extension.get('icon') and os.path.exists(self.extension.get('icon')):
            pixmap = QPixmap(self.extension.get('icon'))
            icon_label.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio))
            icon_label.setScaledContents(True)
        else:
            # 默认图标 - 使用扩展名称首字母
            extension_initial = self.extension.get('name', '扩展')[0].upper()
            icon_label.setText(extension_initial)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("""
                background-color: #4285F4;
                color: white;
                border-radius: 24px;
                font-size: 18px;
                font-weight: bold;
            """)
        
        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 名称标签
        name_label = QLabel(self.extension.get('name', '未命名扩展'))
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
        
        # 安装按钮
        install_btn = ModernButton("安装", accent=True)
        install_btn.setFixedHeight(32)
        install_btn.clicked.connect(self._on_install_clicked)
        layout.addWidget(install_btn)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _on_install_clicked(self):
        """安装按钮点击事件"""
        if self.on_install and callable(self.on_install):
            self.on_install(self.extension.get('id'))
    
    def _on_remove_clicked(self):
        """删除按钮点击事件"""
        if self.on_remove and callable(self.on_remove):
            msg_box = QMessageBox()
            msg_box.setWindowTitle("确认删除")
            msg_box.setText(f"确定要删除扩展 {self.extension.get('name')} 吗？")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                self.on_remove(self.extension.get('id'))

class AddExtensionDialog(QDialog):
    """添加扩展对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新扩展")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # 名称输入
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入扩展名称")
        form_layout.addRow("扩展名称:", self.name_input)
        
        # ID输入
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("输入扩展ID")
        form_layout.addRow("扩展ID:", self.id_input)
        
        # 描述输入
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("输入扩展描述（可选）")
        self.desc_input.setMaximumHeight(100)
        form_layout.addRow("描述:", self.desc_input)
        
        # 图标选择
        icon_layout = QHBoxLayout()
        self.icon_path_input = QLineEdit()
        self.icon_path_input.setReadOnly(True)
        self.icon_path_input.setPlaceholderText("选择扩展图标（可选）")
        
        self.select_icon_btn = QPushButton("浏览...")
        self.select_icon_btn.clicked.connect(self._select_icon)
        
        icon_layout.addWidget(self.icon_path_input)
        icon_layout.addWidget(self.select_icon_btn)
        
        form_layout.addRow("图标:", icon_layout)
        
        # CRX文件选择
        crx_layout = QHBoxLayout()
        self.crx_path_input = QLineEdit()
        self.crx_path_input.setReadOnly(True)
        self.crx_path_input.setPlaceholderText("选择CRX文件（可选）")
        
        self.select_crx_btn = QPushButton("浏览...")
        self.select_crx_btn.clicked.connect(self._select_crx)
        
        crx_layout.addWidget(self.crx_path_input)
        crx_layout.addWidget(self.select_crx_btn)
        
        form_layout.addRow("CRX文件:", crx_layout)
        
        layout.addLayout(form_layout)
        
        # 注意说明
        note_label = QLabel(
            "注意：<br>"
            "1. 扩展ID为必填项，是Chrome商店URL中的最后部分<br>"
            "2. 若提供CRX文件，将使用本地安装；否则从Chrome商店安装"
        )
        note_label.setStyleSheet("color: #666; font-size: 11px;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self._validate_and_accept)
        self.add_btn.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: white;")
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.add_btn)
        
        layout.addLayout(button_layout)
    
    def _select_icon(self):
        """选择图标文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图标文件", "", "图片文件 (*.png *.jpg *.jpeg *.ico)"
        )
        if file_path:
            self.icon_path_input.setText(file_path)
    
    def _select_crx(self):
        """选择CRX文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CRX文件", "", "Chrome扩展 (*.crx)"
        )
        if file_path:
            self.crx_path_input.setText(file_path)
    
    def _validate_and_accept(self):
        """验证输入并接受"""
        name = self.name_input.text().strip()
        ext_id = self.id_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入扩展名称")
            return
        
        if not ext_id:
            QMessageBox.warning(self, "输入错误", "请输入扩展ID")
            return
        
        self.accept()
    
    def get_extension_data(self):
        """获取扩展数据"""
        return {
            "name": self.name_input.text().strip(),
            "id": self.id_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "icon_path": self.icon_path_input.text() if self.icon_path_input.text() else None,
            "crx_path": self.crx_path_input.text() if self.crx_path_input.text() else None
        }

class InstallExtensionDialog(QDialog):
    """安装扩展对话框"""
    
    def __init__(self, extension_name, instances, parent=None):
        """
        初始化安装扩展对话框
        
        Args:
            extension_name: 扩展名称
            instances: 浏览器实例列表
            parent: 父组件
        """
        super().__init__(parent)
        self.extension_name = extension_name
        self.instances = instances
        self.selected_instances = []
        
        self.setWindowTitle("安装扩展")
        self.setMinimumWidth(350)
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel(f"将扩展 {self.extension_name} 安装到:")
        title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title_label)
        
        # 实例列表
        self.checkboxes = []
        
        # 全选
        select_all_layout = QHBoxLayout()
        select_all_checkbox = QCheckBox("全选")
        select_all_checkbox.stateChanged.connect(self._toggle_select_all)
        select_all_layout.addWidget(select_all_checkbox)
        select_all_layout.addStretch()
        
        layout.addLayout(select_all_layout)
        
        # 创建实例选择区域
        instances_group = QGroupBox()
        instances_layout = QVBoxLayout(instances_group)
        
        for instance in self.instances:
            checkbox = QCheckBox(instance.get('name', '未命名实例'))
            self.checkboxes.append((checkbox, instance.get('name')))
            instances_layout.addWidget(checkbox)
        
        # 添加滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(instances_group)
        scroll_area.setMaximumHeight(200)
        
        layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.install_btn = QPushButton("安装")
        self.install_btn.clicked.connect(self._process_selection)
        self.install_btn.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: white;")
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.install_btn)
        
        layout.addLayout(button_layout)
    
    def _toggle_select_all(self, state):
        """切换全选状态"""
        for checkbox, _ in self.checkboxes:
            checkbox.setChecked(state == Qt.CheckState.Checked.value)
    
    def _process_selection(self):
        """处理选择"""
        self.selected_instances = []
        
        for checkbox, name in self.checkboxes:
            if checkbox.isChecked():
                self.selected_instances.append(name)
        
        if not self.selected_instances:
            QMessageBox.warning(self, "选择错误", "请至少选择一个浏览器实例")
            return
        
        self.accept()
    
    def get_selected_instances(self):
        """获取选中的实例"""
        return self.selected_instances

class BatchInstallDialog(QDialog):
    """批量安装对话框"""
    
    def __init__(self, extensions, instances, parent=None):
        """
        初始化批量安装对话框
        
        Args:
            extensions: 扩展列表
            instances: 浏览器实例列表
            parent: 父组件
        """
        super().__init__(parent)
        self.extensions = extensions
        self.instances = instances
        self.selected_extensions = []
        self.selected_instances = []
        
        self.setWindowTitle("批量安装扩展")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 扩展选择区域
        extensions_section = QGroupBox("选择要安装的扩展")
        extensions_section.setFlat(True)
        extensions_layout = QVBoxLayout(extensions_section)
        
        # 扩展全选
        ext_select_all_layout = QHBoxLayout()
        ext_select_all_checkbox = QCheckBox("全选")
        ext_select_all_checkbox.stateChanged.connect(lambda state: self._toggle_select_all(state, self.ext_checkboxes))
        ext_select_all_layout.addWidget(ext_select_all_checkbox)
        ext_select_all_layout.addStretch()
        
        extensions_layout.addLayout(ext_select_all_layout)
        
        # 扩展列表
        self.ext_checkboxes = []
        extensions_group = QGroupBox()
        extensions_group_layout = QVBoxLayout(extensions_group)
        
        for ext in self.extensions:
            checkbox = QCheckBox(f"{ext.get('name', '未命名扩展')} (ID: {ext.get('id', 'N/A')})")
            self.ext_checkboxes.append((checkbox, ext.get('id')))
            extensions_group_layout.addWidget(checkbox)
        
        # 添加扩展滚动区域
        ext_scroll_area = QScrollArea()
        ext_scroll_area.setWidgetResizable(True)
        ext_scroll_area.setWidget(extensions_group)
        ext_scroll_area.setMaximumHeight(200)
        
        extensions_layout.addWidget(ext_scroll_area)
        layout.addWidget(extensions_section)
        
        # 实例选择区域
        instances_section = QGroupBox("选择目标浏览器实例")
        instances_section.setFlat(True)
        instances_layout = QVBoxLayout(instances_section)
        
        # 实例全选
        inst_select_all_layout = QHBoxLayout()
        inst_select_all_checkbox = QCheckBox("全选")
        inst_select_all_checkbox.stateChanged.connect(lambda state: self._toggle_select_all(state, self.inst_checkboxes))
        inst_select_all_layout.addWidget(inst_select_all_checkbox)
        inst_select_all_layout.addStretch()
        
        instances_layout.addLayout(inst_select_all_layout)
        
        # 实例列表
        self.inst_checkboxes = []
        instances_group = QGroupBox()
        instances_group_layout = QVBoxLayout(instances_group)
        
        for instance in self.instances:
            checkbox = QCheckBox(instance.get('name', '未命名实例'))
            self.inst_checkboxes.append((checkbox, instance.get('name')))
            instances_group_layout.addWidget(checkbox)
        
        # 添加实例滚动区域
        inst_scroll_area = QScrollArea()
        inst_scroll_area.setWidgetResizable(True)
        inst_scroll_area.setWidget(instances_group)
        inst_scroll_area.setMaximumHeight(150)
        
        instances_layout.addWidget(inst_scroll_area)
        layout.addWidget(instances_section)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.install_btn = QPushButton("批量安装")
        self.install_btn.clicked.connect(self._process_selection)
        self.install_btn.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: white;")
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.install_btn)
        
        layout.addLayout(button_layout)
    
    def _toggle_select_all(self, state, checkboxes):
        """切换全选状态"""
        for checkbox, _ in checkboxes:
            checkbox.setChecked(state == Qt.CheckState.Checked.value)
    
    def _process_selection(self):
        """处理选择"""
        self.selected_extensions = []
        self.selected_instances = []
        
        for checkbox, ext_id in self.ext_checkboxes:
            if checkbox.isChecked():
                self.selected_extensions.append(ext_id)
        
        for checkbox, name in self.inst_checkboxes:
            if checkbox.isChecked():
                self.selected_instances.append(name)
        
        if not self.selected_extensions:
            QMessageBox.warning(self, "选择错误", "请至少选择一个扩展")
            return
        
        if not self.selected_instances:
            QMessageBox.warning(self, "选择错误", "请至少选择一个浏览器实例")
            return
        
        self.accept()
    
    def get_selected_data(self):
        """获取选中的数据"""
        return {
            'extensions': self.selected_extensions,
            'instances': self.selected_instances
        }

class ExtensionsPage(QWidget):
    """扩展管理页面"""
    
    def __init__(self, parent=None, extension_manager=None, config_manager=None):
        super().__init__(parent)
        self.extension_manager = extension_manager
        self.config_manager = config_manager
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = SectionTitle("扩展插件管理")
        layout.addWidget(title)
        
        # 操作区域
        actions_layout = QHBoxLayout()
        
        self.add_ext_btn = ModernButton("添加新扩展", accent=True)
        self.add_ext_btn.clicked.connect(self.add_extension)
        
        self.batch_install_btn = ModernButton("批量安装", accent=False)
        self.batch_install_btn.clicked.connect(self.batch_install)
        
        # 添加刷新按钮
        self.refresh_btn = ModernButton("刷新列表", accent=False)
        self.refresh_btn.clicked.connect(self.load_extensions)
        
        actions_layout.addWidget(self.add_ext_btn)
        actions_layout.addWidget(self.batch_install_btn)
        actions_layout.addWidget(self.refresh_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        # 添加搜索功能
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索Chrome商店:")
        search_label.setStyleSheet(f"color: {TEXT_PRIMARY_COLOR}; font-size: 13px;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索扩展插件")
        self.search_input.setMinimumWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4285F4;
            }
        """)
        
        self.search_btn = ModernButton("搜索", accent=True)
        self.search_btn.clicked.connect(self.search_extensions)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        
        layout.addLayout(search_layout)
        layout.addSpacing(10)
        
        # 说明文本
        help_text = QLabel('提示: 点击"安装"按钮将在浏览器中打开Chrome商店页面，请在页面中点击"添加至Chrome"按钮完成扩展安装。安装成功后，请点击"刷新列表"更新状态。如果安装失败，请检查网络连接或尝试手动安装。')
        help_text.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 12px; background-color: #F5F5F5; padding: 8px; border-radius: 4px;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        layout.addSpacing(10)
        
        # 搜索结果区域
        search_results_layout = QVBoxLayout()
        search_results_layout.setContentsMargins(0, 0, 0, 0)
        search_results_layout.setSpacing(16)
        
        # 搜索结果标题
        self.search_results_title = QLabel("搜索结果")
        self.search_results_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333333;
            margin-top: 16px;
        """)
        self.search_results_title.setVisible(False)
        search_results_layout.addWidget(self.search_results_title)
        
        # 搜索结果滚动区域
        self.search_results_scroll = QScrollArea()
        self.search_results_scroll.setWidgetResizable(True)
        self.search_results_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #CCCCCC;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        
        # 搜索结果内容区域
        search_results_widget = QWidget()
        search_results_widget.setStyleSheet("background-color: transparent;")
        
        # 使用垂直布局替代网格布局
        self.search_results_grid = QVBoxLayout()
        self.search_results_grid.setSpacing(16)
        self.search_results_grid.setContentsMargins(0, 10, 0, 0)
        self.search_results_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        search_results_widget.setLayout(self.search_results_grid)
        self.search_results_scroll.setWidget(search_results_widget)
        self.search_results_scroll.setVisible(False)
        
        search_results_layout.addWidget(self.search_results_scroll)
        layout.addLayout(search_results_layout)
        
        # 扩展库区域
        extensions_title = QLabel("扩展库")
        extensions_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(extensions_title)
        
        # 创建网格布局用于显示扩展卡片
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)  # 设置卡片间距
        self.grid_layout.setContentsMargins(0, 10, 0, 0)
        
        # 创建滚动区域
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.grid_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent; 
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #CCCCCC;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        
        layout.addWidget(scroll_area, 1)  # 给予滚动区域伸缩空间
        
        # 加载扩展
        self.load_extensions()
    
    def load_extensions(self):
        """加载扩展列表"""
        # 清空现有内容
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 获取扩展列表
        extensions = self.extension_manager.get_all_extensions()
        
        if not extensions:
            # 创建空状态显示
            empty_label = QLabel("扩展库为空，请添加扩展")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #888; font-size: 14px; padding: 20px;")
            self.grid_layout.addWidget(empty_label, 0, 0)
            return
        
        # 计算每行可以放置的卡片数量
        # 假设每个卡片宽度为180，间距为16
        card_width = 180
        card_spacing = 16
        available_width = self.width() - 40  # 减去左右边距
        max_cols = max(1, available_width // (card_width + card_spacing))
        
        # 添加扩展卡片到网格
        for i, extension in enumerate(extensions):
            row = i // max_cols
            col = i % max_cols
            
            card = ExtensionCard(
                extension, 
                on_remove=self.remove_extension,
                on_install=self.install_extension
            )
            self.grid_layout.addWidget(card, row, col)
        
        # 更新网格布局
        self.grid_layout.update()
    
    def add_extension(self):
        """添加新扩展"""
        dialog = AddExtensionDialog(self)
        if dialog.exec():
            extension_data = dialog.get_extension_data()
            
            # 调用扩展管理器添加扩展
            success, message = self.extension_manager.add_extension(
                extension_data['name'],
                extension_data['id'],
                extension_data['description'],
                extension_data['icon_path'],
                extension_data['crx_path']
            )
            
            if success:
                show_message("成功", message, QMessageBox.Icon.Information)
                self.load_extensions()  # 刷新列表
            else:
                show_message("错误", message, QMessageBox.Icon.Warning)
    
    def remove_extension(self, extension_id):
        """删除扩展"""
        if self.extension_manager.remove_extension(extension_id):
            show_message("成功", "扩展已从库中删除", QMessageBox.Icon.Information)
            self.load_extensions()  # 刷新列表
        else:
            show_message("错误", "删除扩展失败", QMessageBox.Icon.Warning)
    
    def install_extension(self, extension_id):
        """安装扩展到实例"""
        extension = self.extension_manager.get_extension(extension_id)
        if not extension:
            show_message("错误", "找不到指定的扩展", QMessageBox.Icon.Warning)
            return
        
        # 获取所有实例
        config = self.config_manager.load_config()
        instances = config.get('shortcuts', [])
        if not instances:
            show_message("错误", "没有可用的浏览器实例", QMessageBox.Icon.Warning)
            return
        
        # 显示安装对话框
        dialog = InstallExtensionDialog(extension.get('name', '未命名扩展'), instances, self)
        if dialog.exec():
            selected_instances = dialog.get_selected_instances()
            
            # 执行安装
            results = self.extension_manager.install_extension_to_instances(extension_id, selected_instances)
            
            # 显示结果
            success_count = sum(1 for success, _ in results.values() if success)
            total_count = len(results)
            
            result_message = f"成功启动 {success_count}/{total_count} 个实例进行安装\n\n"
            for instance, (success, msg) in results.items():
                status = "✓" if success else "✗"
                result_message += f"{status} {instance}: {msg}\n"
            
            show_message("安装结果", result_message, QMessageBox.Icon.Information)
    
    def batch_install(self):
        """批量安装扩展"""
        # 获取所有扩展和实例
        extensions = self.extension_manager.get_all_extensions()
        config = self.config_manager.load_config()
        instances = config.get('shortcuts', [])
        
        if not extensions:
            show_message("错误", "扩展库为空，请先添加扩展", QMessageBox.Icon.Warning)
            return
        
        if not instances:
            show_message("错误", "没有可用的浏览器实例", QMessageBox.Icon.Warning)
            return
        
        # 显示批量安装对话框
        dialog = BatchInstallDialog(extensions, instances, self)
        if dialog.exec():
            selected_data = dialog.get_selected_data()
            selected_extensions = selected_data['extensions']
            selected_instances = selected_data['instances']
            
            # 执行批量安装
            all_results = {}
            for ext_id in selected_extensions:
                results = self.extension_manager.install_extension_to_instances(ext_id, selected_instances)
                all_results[ext_id] = results
            
            # 显示结果
            total_operations = len(selected_extensions) * len(selected_instances)
            success_count = sum(
                1 for ext_results in all_results.values() 
                for success, _ in ext_results.values() 
                if success
            )
            
            result_message = f"批量安装完成: {success_count}/{total_operations} 个操作成功\n\n"
            
            # 详细结果太长，只显示摘要
            if len(selected_extensions) > 3:
                result_message += "已启动多个Chrome实例执行安装，请在各实例中确认安装结果"
            else:
                for ext_id in selected_extensions:
                    ext = self.extension_manager.get_extension(ext_id)
                    ext_name = ext.get('name', ext_id) if ext else ext_id
                    
                    result_message += f"\n{ext_name}:\n"
                    for instance, (success, msg) in all_results[ext_id].items():
                        status = "✓" if success else "✗"
                        result_message += f"  {status} {instance}: {msg}\n"
            
            show_message("批量安装结果", result_message, QMessageBox.Icon.Information)
    
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        # 窗口大小变化时重新加载扩展卡片布局
        self.load_extensions() 

    def search_extensions(self):
        """搜索扩展"""
        keyword = self.search_input.text().strip()
        if not keyword:
            show_message("错误", "请输入关键词进行搜索", QMessageBox.Icon.Warning)
            return
        
        # 显示搜索中状态
        self.search_results_title.setText("正在搜索...")
        self.search_results_title.setVisible(True)
        self.search_results_scroll.setVisible(False)
        
        # 清空现有内容
        for i in reversed(range(self.search_results_grid.count())):
            widget = self.search_results_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 获取搜索结果
        results = self.extension_manager.search_extensions(keyword)
        
        # 更新标题
        self.search_results_title.setText(f"搜索结果 - {keyword}")
        self.search_results_title.setVisible(True)
        
        if not results:
            # 创建空状态显示
            empty_label = QLabel("没有找到匹配的扩展")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #888; font-size: 14px; padding: 20px;")
            self.search_results_grid.addWidget(empty_label)
            self.search_results_scroll.setVisible(True)
            return
        
        # 检查已安装的扩展
        installed_ids = [ext.get('id') for ext in self.extension_manager.extensions_library]
        
        # 使用列表布局替代网格布局
        for i, result in enumerate(results):
            # 检查是否已安装
            is_installed = result.get('id') in installed_ids
            
            # 使用新的卡片组件
            card = ChromeStoreSearchResultCard(
                result, 
                on_add=self.add_search_result,
                is_installed=is_installed
            )
            self.search_results_grid.addWidget(card)
        
        # 更新布局
        self.search_results_grid.update()
        self.search_results_scroll.setVisible(True)
    
    def add_search_result(self, extension):
        """添加搜索结果到扩展库"""
        # 调用扩展管理器添加扩展
        success, message = self.extension_manager.add_extension(
            extension.get('name', '未命名扩展'),
            extension.get('id', ''),
            extension.get('description', ''),
            extension.get('icon'),
            None  # 没有CRX文件
        )
        
        if success:
            show_message("成功", f"扩展 {extension.get('name')} 已添加到库中", QMessageBox.Icon.Information)
            self.load_extensions()  # 刷新扩展库列表
        else:
            show_message("错误", message, QMessageBox.Icon.Warning) 