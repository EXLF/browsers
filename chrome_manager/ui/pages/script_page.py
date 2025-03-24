"""
脚本插件页面模块，实现脚本和插件管理功能
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QDesktopServices

from ...constants import (
    TEXT_PRIMARY_COLOR, TEXT_SECONDARY_COLOR, TEXT_HINT_COLOR, FONT_FAMILY
)
from ..components import ModernButton

class ScriptPage(QWidget):
    """脚本插件页面类"""
    
    def __init__(self, parent=None):
        """初始化脚本插件页面"""
        super().__init__(parent)
        self.main_window = parent
        self._init_ui()
    
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
        script_content_layout.setSpacing(10)  # 减小卡片间距
        
        # 分类标题
        category_title = QLabel("热门脚本插件")
        category_title.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        category_title.setStyleSheet("color: #333333;")
        script_content_layout.addWidget(category_title)
        
        # 热门脚本卡片 - 使用用户提供的项目
        script_card1 = self.create_script_card(
            "Monad",
            "一键交互、自动领水、一键质押",
            "v2.1.0",
            "https://example.com/monad"
        )
        script_content_layout.addWidget(script_card1)
        
        script_card2 = self.create_script_card(
            "POD Network",
            "一键交互、自动领水",
            "v1.5.2",
            "https://example.com/pod-network"
        )
        script_content_layout.addWidget(script_card2)
        
        # 第二个分类
        category_title2 = QLabel("工具类插件")
        category_title2.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        category_title2.setStyleSheet("color: #333333; margin-top: 16px;")
        script_content_layout.addWidget(category_title2)
        
        # 工具插件卡片 - 使用用户提供的项目
        script_card3 = self.create_script_card(
            "Voltix AI",
            "多开挂机",
            "v3.0.1",
            "https://example.com/voltix-ai"
        )
        script_content_layout.addWidget(script_card3)
        
        script_card4 = self.create_script_card(
            "PublicAi",
            "自动交互",
            "v2.4.3",
            "https://example.com/public-ai"
        )
        script_content_layout.addWidget(script_card4)
        
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
    
    def create_script_card(self, name, description, version, url):
        """创建脚本卡片"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QWidget:hover {
                border-color: #BBBBBB;
            }
        """)
        card.setFixedHeight(64)  # 进一步降低卡片高度
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 8, 16, 8)  # 减小内边距使卡片更紧凑
        
        # 左侧信息区
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)  # 减小间距
        
        # 脚本名称和版本
        title_layout = QHBoxLayout()
        script_title = QLabel(name)
        script_title.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        script_title.setStyleSheet("color: #1a73e8; border: none;")
        
        version_label = QLabel(version)
        version_label.setStyleSheet("color: #666666; font-size: 11px; background-color: #e8eaed; padding: 2px 6px; border-radius: 10px; border: none;")
        
        title_layout.addWidget(script_title)
        title_layout.addWidget(version_label)
        title_layout.addStretch()
        
        info_layout.addLayout(title_layout)
        
        # 脚本描述
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555555; font-size: 12px; border: none;")
        info_layout.addWidget(desc_label)
        
        card_layout.addLayout(info_layout, 1)  # 添加伸缩因子
        
        # 右侧下载按钮（改为待上传按钮并置灰）
        download_btn = ModernButton("待上传", accent=True)
        download_btn.setFixedWidth(70)  # 略微加宽按钮以适应"待上传"文字
        download_btn.setFixedHeight(28)  # 保持按钮高度
        download_btn.setEnabled(False)  # 设置按钮为禁用状态（置灰）
        card_layout.addWidget(download_btn)
        
        return card 