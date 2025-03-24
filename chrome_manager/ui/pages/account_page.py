"""
账号管理页面模块，实现账号信息管理功能
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ...constants import (
    TEXT_PRIMARY_COLOR, TEXT_SECONDARY_COLOR, TEXT_HINT_COLOR, FONT_FAMILY
)
from ..components import ModernButton, ModernLineEdit

class AccountPage(QWidget):
    """账号管理页面类"""
    
    def __init__(self, parent=None):
        """初始化账号管理页面"""
        super().__init__(parent)
        self.main_window = parent
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        account_layout = QVBoxLayout(self)
        account_layout.setContentsMargins(32, 24, 32, 24)  # 减小上下边距
        account_layout.setSpacing(16)  # 减小整体间距
        
        # 顶部标题
        page_title = QLabel("账号管理")
        page_title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        account_layout.addWidget(page_title)
        
        # 说明文字
        description = QLabel("管理每个浏览器实例对应的账号信息，包括钱包和社交媒体账号")
        description.setStyleSheet(f"color: {TEXT_SECONDARY_COLOR}; font-size: 14px; margin-bottom: 8px;")
        description.setWordWrap(True)
        account_layout.addWidget(description)
        
        # 账号信息区域（滚动区域）
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
        
        # 背景容器
        background_widget = QWidget()
        background_widget.setStyleSheet("background-color: white; border-radius: 8px;")
        background_layout = QVBoxLayout(background_widget)
        background_layout.setContentsMargins(0, 0, 0, 0)
        
        # 内容容器
        self.account_content_widget = QWidget()
        self.account_content_widget.setStyleSheet("background-color: transparent;")
        self.account_content_layout = QVBoxLayout(self.account_content_widget)
        self.account_content_layout.setContentsMargins(16, 16, 16, 16)  # 内边距
        self.account_content_layout.setSpacing(12)  # 减小卡片之间的间距
        
        # 先添加一个占位符，后续会根据实际情况更新
        self.account_placeholder = QLabel("暂无浏览器实例数据。请先在主页创建浏览器实例，然后在此处管理对应的账号信息。")
        self.account_placeholder.setStyleSheet(f"""
            color: #505050; 
            font-size: 15px;
            margin: 40px 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px dashed #cccccc;
        """)
        self.account_placeholder.setWordWrap(True)
        self.account_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.account_content_layout.addWidget(self.account_placeholder)
        
        # 添加弹性空间
        self.account_content_layout.addStretch()
        
        # 将内容添加到背景容器
        background_layout.addWidget(self.account_content_widget)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(background_widget)
        account_layout.addWidget(scroll_area)
        
        # 保存按钮
        save_btn_layout = QHBoxLayout()
        save_account_btn = ModernButton("保存账号信息", accent=True)
        save_account_btn.clicked.connect(self.save_account_info)
        save_account_btn.setMinimumWidth(120)
        save_btn_layout.addStretch()
        save_btn_layout.addWidget(save_account_btn)
        account_layout.addLayout(save_btn_layout)
        
        # 预先检查是否有实例，初始设置占位符状态
        self.account_placeholder.setVisible(True)
    
    def update_cards(self):
        """更新账号管理卡片"""
        try:
            # 清除现有的所有卡片
            for i in reversed(range(self.account_content_layout.count()-1)):  # 保留最后的stretch
                item = self.account_content_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    # 不要删除占位符标签
                    if widget != self.account_placeholder:
                        widget.setParent(None)
            
            # 如果没有浏览器实例，显示占位符并返回
            if not self.main_window.shortcuts:
                self.account_placeholder.setVisible(True)
                # 确保占位符在布局中的位置正确
                self.account_content_layout.insertWidget(0, self.account_placeholder)
                return
            
            # 有实例时隐藏占位符
            self.account_placeholder.setVisible(False)
            
            # 为每个浏览器实例创建一个账号信息卡片
            for shortcut in self.main_window.shortcuts:
                name = shortcut["name"]
                data_dir = shortcut["data_dir"]
                
                # 创建卡片容器
                card = QWidget()
                card.setObjectName(f"account_card_{name}")
                card.setStyleSheet("""
                    QWidget {
                        background-color: #f8f9fa;
                        border-radius: 6px;
                    }
                """)
                
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(16, 12, 16, 12)  # 减小内边距
                card_layout.setSpacing(8)  # 减小间距
                
                # 标题和数据目录在一行
                header_layout = QHBoxLayout()
                header_layout.setSpacing(10)
                
                # 标题
                title = QLabel(name)
                title.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
                title.setStyleSheet("color: #1a73e8;")
                header_layout.addWidget(title)
                header_layout.addStretch()
                
                card_layout.addLayout(header_layout)
                
                # 添加分隔线
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet("background-color: #e0e0e0; margin: 0 -8px;")
                separator.setMaximumHeight(1)
                card_layout.addWidget(separator)
                
                # 账号信息表单 - 使用三列布局提高空间利用率
                form_layout = QGridLayout()
                form_layout.setHorizontalSpacing(20)  # 水平间距稍大
                form_layout.setVerticalSpacing(10)  # 减小垂直间距
                
                # 定义标签样式
                label_style = "color: #555555; font-weight: 500; font-size: 13px;"
                
                # 定义输入框样式
                input_style = """
                    ModernLineEdit {
                        border: none;
                        border-bottom: 1px solid #dadce0;
                        background-color: transparent;
                        padding: 4px 0;
                    }
                    ModernLineEdit:focus {
                        border-bottom: 2px solid #1a73e8;
                    }
                """
                
                # 第一列 - 钱包和Twitter
                # 钱包地址
                wallet_label = QLabel("钱包地址:")
                wallet_label.setStyleSheet(label_style)
                wallet_input = ModernLineEdit(self.main_window.account_info.get(name, {}).get("wallet", ""))
                wallet_input.setObjectName(f"wallet_{name}")
                wallet_input.setPlaceholderText("请输入钱包地址")
                wallet_input.setStyleSheet(input_style)
                form_layout.addWidget(wallet_label, 0, 0)
                form_layout.addWidget(wallet_input, 0, 1)
                
                # Twitter
                twitter_label = QLabel("Twitter:")
                twitter_label.setStyleSheet(label_style)
                twitter_input = ModernLineEdit(self.main_window.account_info.get(name, {}).get("twitter", ""))
                twitter_input.setObjectName(f"twitter_{name}")
                twitter_input.setPlaceholderText("请输入Twitter账号")
                twitter_input.setStyleSheet(input_style)
                form_layout.addWidget(twitter_label, 1, 0)
                form_layout.addWidget(twitter_input, 1, 1)
                
                # 第二列 - Discord和Telegram
                # Discord
                discord_label = QLabel("Discord:")
                discord_label.setStyleSheet(label_style)
                discord_input = ModernLineEdit(self.main_window.account_info.get(name, {}).get("discord", ""))
                discord_input.setObjectName(f"discord_{name}")
                discord_input.setPlaceholderText("请输入Discord账号")
                discord_input.setStyleSheet(input_style)
                form_layout.addWidget(discord_label, 0, 2)
                form_layout.addWidget(discord_input, 0, 3)
                
                # Telegram
                telegram_label = QLabel("Telegram:")
                telegram_label.setStyleSheet(label_style)
                telegram_input = ModernLineEdit(self.main_window.account_info.get(name, {}).get("telegram", ""))
                telegram_input.setObjectName(f"telegram_{name}")
                telegram_input.setPlaceholderText("请输入Telegram账号")
                telegram_input.setStyleSheet(input_style)
                form_layout.addWidget(telegram_label, 1, 2)
                form_layout.addWidget(telegram_input, 1, 3)
                
                # 第三列 - Gmail和备注
                # Gmail
                gmail_label = QLabel("Gmail:")
                gmail_label.setStyleSheet(label_style)
                gmail_input = ModernLineEdit(self.main_window.account_info.get(name, {}).get("gmail", ""))
                gmail_input.setObjectName(f"gmail_{name}")
                gmail_input.setPlaceholderText("请输入Gmail账号")
                gmail_input.setStyleSheet(input_style)
                form_layout.addWidget(gmail_label, 0, 4)
                form_layout.addWidget(gmail_input, 0, 5)
                
                # 备注
                note_label = QLabel("备注:")
                note_label.setStyleSheet(label_style)
                note_input = ModernLineEdit(self.main_window.account_info.get(name, {}).get("note", ""))
                note_input.setObjectName(f"note_{name}")
                note_input.setPlaceholderText("其他备注信息")
                note_input.setStyleSheet(input_style)
                form_layout.addWidget(note_label, 1, 4)
                form_layout.addWidget(note_input, 1, 5)
                
                # 设置各列的拉伸比例
                for col in [1, 3, 5]:  # 输入框列
                    form_layout.setColumnStretch(col, 1)
                
                card_layout.addLayout(form_layout)
                
                # 添加卡片到容器
                self.account_content_layout.insertWidget(self.account_content_layout.count()-1, card)
        except Exception as e:
            # 捕获并处理异常，避免在没有实例时弹出Python窗口
            print(f"更新账号卡片时出错: {str(e)}")
            # 确保占位符可见
            self.account_placeholder.setVisible(True)
            # 确保占位符在布局中的位置正确
            self.account_content_layout.insertWidget(0, self.account_placeholder)
    
    def save_account_info(self):
        """保存账号信息"""
        # 检查是否有浏览器实例
        if not self.main_window.shortcuts:
            # 不再弹出消息框，而是在状态栏显示消息
            self.main_window.statusBar().showMessage("暂无浏览器实例数据。请先在主页创建浏览器实例，然后再管理账号信息。", 5000)
            return
            
        updated_account_info = {}
        
        # 遍历所有浏览器实例
        for shortcut in self.main_window.shortcuts:
            name = shortcut["name"]
            instance_info = {}
            
            # 获取各个字段的值
            wallet_input = self.findChild(ModernLineEdit, f"wallet_{name}")
            twitter_input = self.findChild(ModernLineEdit, f"twitter_{name}")
            discord_input = self.findChild(ModernLineEdit, f"discord_{name}")
            telegram_input = self.findChild(ModernLineEdit, f"telegram_{name}")
            gmail_input = self.findChild(ModernLineEdit, f"gmail_{name}")
            note_input = self.findChild(ModernLineEdit, f"note_{name}")
            
            if wallet_input:
                instance_info["wallet"] = wallet_input.text().strip()
            if twitter_input:
                instance_info["twitter"] = twitter_input.text().strip()
            if discord_input:
                instance_info["discord"] = discord_input.text().strip()
            if telegram_input:
                instance_info["telegram"] = telegram_input.text().strip()
            if gmail_input:
                instance_info["gmail"] = gmail_input.text().strip()
            if note_input:
                instance_info["note"] = note_input.text().strip()
            
            updated_account_info[name] = instance_info
        
        # 更新账号信息
        self.main_window.account_info = updated_account_info
        
        # 保存到配置
        config = self.main_window.config_manager.load_config()
        config["account_info"] = self.main_window.account_info
        self.main_window.config_manager.save_config(config)
        
        # 使用状态栏显示成功消息，而不是弹窗
        self.main_window.statusBar().showMessage("账号信息已保存", 3000) 