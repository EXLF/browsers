"""
脚本插件页面模块，实现脚本和插件管理功能
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QGridLayout, QMessageBox
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QFont, QDesktopServices

from ...constants import (
    TEXT_PRIMARY_COLOR, TEXT_SECONDARY_COLOR, TEXT_HINT_COLOR, FONT_FAMILY
)
from ..components import ModernButton
from ...script_updater import ScriptUpdater

class ScriptPage(QWidget):
    """脚本插件页面类"""
    
    def __init__(self, parent=None):
        """初始化脚本插件页面"""
        super().__init__(parent)
        self.main_window = parent
        self._init_ui()
        
        # 创建定时器，每5分钟自动检查一次更新
        self.auto_update_timer = QTimer(self)
        self.auto_update_timer.setInterval(5 * 60 * 1000)  # 5分钟
        self.auto_update_timer.timeout.connect(self._check_updates)
        self.auto_update_timer.start()
        
        # 首次打开时延迟1秒自动检查更新
        QTimer.singleShot(1000, self._check_updates)
    
    def _init_ui(self):
        """初始化UI"""
        script_layout = QVBoxLayout(self)
        script_layout.setContentsMargins(32, 24, 32, 24)  # 减小上下边距
        script_layout.setSpacing(16)  # 减小整体间距
        
        # 顶部标题
        page_title = QLabel("脚本插件")
        page_title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        script_layout.addWidget(page_title)
        
        # 说明文字
        description = QLabel("管理和下载各种浏览器脚本和插件工具")
        description.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 14px; margin-bottom: 8px;")
        description.setWordWrap(True)
        script_layout.addWidget(description)
        
        # 脚本插件区域（滚动区域）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CCCCCC;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #AAAAAA;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        
        # 脚本列表容器
        script_content_widget = QWidget()
        script_content_layout = QVBoxLayout(script_content_widget)
        script_content_layout.setContentsMargins(0, 0, 0, 0)
        script_content_layout.setSpacing(16)  # 调整间距
        
        # 分类标题
        category_title = QLabel("热门脚本插件")
        category_title.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        category_title.setStyleSheet("color: #333333;")
        script_content_layout.addWidget(category_title)
        
        # 创建网格布局容器用于脚本卡片
        self.scripts_grid = QGridLayout()
        self.scripts_grid.setSpacing(16)  # 设置卡片之间的间距
        
        # 添加网格布局到主布局
        script_content_layout.addLayout(self.scripts_grid)
        
        # 添加提交新脚本的提示
        submit_container = QWidget()
        submit_container.setStyleSheet("background-color: #f0f7ff; border-radius: 4px; padding: 8px;")
        submit_layout = QHBoxLayout(submit_container)
        submit_layout.setContentsMargins(12, 8, 12, 8)
        
        info_label = QLabel("想要提交你的脚本插件？请在Discord社区联系我们")
        info_label.setStyleSheet("color: #0057b8;")
        submit_layout.addWidget(info_label)
        
        submit_btn = ModernButton("前往社区", accent=True)
        submit_btn.setFixedWidth(100)
        submit_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://discord.gg/cTZCaYefPY")))
        submit_layout.addWidget(submit_btn)
        
        script_content_layout.addWidget(submit_container)
        script_content_layout.addStretch()
        
        scroll_area.setWidget(script_content_widget)
        script_layout.addWidget(scroll_area)
        
        # 添加检查更新按钮
        self.refresh_btn = ModernButton("检查脚本更新", accent=False)
        self.refresh_btn.setFixedWidth(120)
        self.refresh_btn.clicked.connect(self._check_updates)
        
        # 创建按钮布局
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 8, 0, 8)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)
        script_layout.addWidget(button_container)
        
        # 初始化脚本更新器
        self.script_updater = ScriptUpdater(self.main_window)
        self.script_updater.update_available.connect(self._on_updates_available)
        self.script_updater.update_complete.connect(self._on_update_complete)
    
    def create_script_card(self, name, description, version, url):
        """创建脚本卡片"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
            QWidget:hover {
                border-color: #BBBBBB;
                border-width: 2px;
            }
        """)
        # 不再固定高度，让卡片根据内容自适应
        card.setMinimumWidth(240)
        card.setMinimumHeight(120)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)  # 调整内边距
        
        # 脚本名称和版本放在标题区域
        title_layout = QHBoxLayout()
        script_title = QLabel(name)
        script_title.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        script_title.setStyleSheet("color: #1a73e8; border: none;")
        
        version_label = QLabel(version)
        version_label.setStyleSheet("color: #666666; font-size: 11px; background-color: #e8eaed; padding: 2px 6px; border-radius: 10px; border: none;")
        
        title_layout.addWidget(script_title)
        title_layout.addWidget(version_label)
        title_layout.addStretch()
        
        card_layout.addLayout(title_layout)
        
        # 脚本描述
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555555; font-size: 12px; border: none; margin-top: 4px;")
        card_layout.addWidget(desc_label)
        
        # 添加空间，使布局更美观
        card_layout.addStretch()
        
        # 下载按钮放在卡片底部
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        download_btn = ModernButton("待上传", accent=True)
        download_btn.setFixedWidth(70)
        download_btn.setFixedHeight(28)
        download_btn.setEnabled(False)  # 设置按钮为禁用状态（置灰）
        button_layout.addWidget(download_btn)
        
        card_layout.addLayout(button_layout)
        
        return card
        
    def _check_updates(self):
        """检查脚本更新"""
        # 如果按钮已经禁用，说明正在检查更新，跳过这次检查
        if not self.refresh_btn.isEnabled():
            return
            
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("正在检查...")
        self.main_window.statusBar().showMessage("正在检查脚本更新...")
        self.script_updater.start()

    def _on_updates_available(self, scripts):
        """处理可用脚本"""
        # 恢复按钮状态
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("检查脚本更新")
        
        # 清除现有脚本卡片
        while self.scripts_grid.count():
            item = self.scripts_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not scripts:
            # 添加提示信息
            no_scripts_label = QLabel("暂无可用脚本，请稍后再试")
            no_scripts_label.setStyleSheet(f"""
                color: {TEXT_SECONDARY_COLOR};
                font-size: 14px;
                padding: 20px;
                background-color: #f5f5f5;
                border-radius: 8px;
            """)
            no_scripts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scripts_grid.addWidget(no_scripts_label, 0, 0, 1, 2)  # 跨越两列显示
            return
        
        # 添加脚本卡片
        row, col = 0, 0
        for script in scripts:
            card = self.create_script_card(
                script["name"],
                script["description"],
                script["version"],
                script.get("download_url", "")
            )
            
            # 修改下载按钮文本和状态
            for child in card.findChildren(ModernButton):
                if "待上传" in child.text():
                    child.setText("下载")
                    child.setEnabled(True)
                    child.clicked.connect(lambda checked, s=script: self._download_script(s))
            
            self.scripts_grid.addWidget(card, row, col)
            
            # 更新行列位置
            col += 1
            if col > 1:  # 每行最多2个卡片
                col = 0
                row += 1

    def _download_script(self, script):
        """处理脚本下载请求"""
        disk_type = script.get("download_type", "unknown")
        
        message = f"您将跳转到云盘下载 {script['name']} 脚本"
        
        reply = QMessageBox.question(
            self,
            "下载确认",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.script_updater.download_script(script)
            if success:
                self.main_window.statusBar().showMessage(msg, 5000)
            else:
                QMessageBox.warning(self, "下载失败", msg)

    def _on_update_complete(self, success, message):
        """更新检查完成"""
        # 恢复按钮状态
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("检查脚本更新")
        
        if success:
            self.main_window.statusBar().showMessage(message, 5000)
        else:
            QMessageBox.warning(self, "更新检查失败", message) 