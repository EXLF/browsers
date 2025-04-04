"""
主页模块，用于管理浏览器实例
"""

import os
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QGridLayout, QApplication, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ...constants import (
    TEXT_PRIMARY_COLOR, TEXT_SECONDARY_COLOR, TEXT_HINT_COLOR, FONT_FAMILY
)
from ..components import ModernButton
from ..dialogs import AddShortcutDialog, BatchAddShortcutDialog
from ..cards import BrowserCard
from chrome_manager.shortcuts import log_time

class HomePage(QWidget):
    """主页类，用于管理浏览器实例"""
    
    def __init__(self, parent=None):
        """初始化主页"""
        super().__init__(parent)
        self.main_window = parent
        self.is_batch_mode = False
        self.is_all_selected = False
        self.card_widgets = []
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        home_layout = QVBoxLayout(self)
        home_layout.setContentsMargins(32, 24, 32, 24)  # 减小上下边距
        
        # 顶部操作栏
        top_bar = QHBoxLayout()
        
        page_title = QLabel("浏览器实例管理")
        page_title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        
        # 添加新实例按钮
        add_btn = ModernButton("添加新实例", accent=True)
        add_btn.clicked.connect(self.add_shortcut)
        
        # 批量添加按钮
        batch_add_btn = ModernButton("批量添加")
        batch_add_btn.clicked.connect(self.batch_add_shortcuts)
        
        # 批量操作按钮
        self.batch_btn = ModernButton("批量删除")
        self.batch_btn.clicked.connect(self.toggle_batch_mode)
        
        # 全选按钮（初始隐藏）
        self.select_all_btn = ModernButton("全选")
        self.select_all_btn.setVisible(False)
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        
        # 批量删除确认按钮（初始隐藏）
        self.confirm_delete_btn = ModernButton("删除选中", accent=True)
        self.confirm_delete_btn.setVisible(False)
        self.confirm_delete_btn.clicked.connect(self.delete_selected_shortcuts)
        
        # 取消批量操作按钮（初始隐藏）
        self.cancel_batch_btn = ModernButton("取消")
        self.cancel_batch_btn.setVisible(False)
        self.cancel_batch_btn.clicked.connect(self.toggle_batch_mode)
        
        top_bar.addWidget(page_title)
        top_bar.addStretch()
        top_bar.addWidget(self.batch_btn)
        top_bar.addWidget(self.select_all_btn)
        top_bar.addWidget(self.confirm_delete_btn)
        top_bar.addWidget(self.cancel_batch_btn)
        top_bar.addWidget(batch_add_btn)
        top_bar.addWidget(add_btn)
        
        home_layout.addLayout(top_bar)
        
        # 浏览器网格区域
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
        
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(16)
        
        scroll_area.setWidget(self.grid_widget)
        home_layout.addWidget(scroll_area)
    
    def update_browser_grid(self):
        """更新浏览器网格"""
        # 清除现有的网格项
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # 清空卡片列表
        self.card_widgets = []
        
        # 设置网格布局属性
        self.grid_layout.setSpacing(16)  # 设置基础间距
        self.grid_layout.setContentsMargins(30, 20, 30, 20)  # 调整外边距
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)  # 顶部水平居中对齐
        
        # 添加浏览器卡片
        if not self.main_window.shortcuts:
            empty_label = QLabel('暂无Chrome实例\n点击"添加新实例"创建')
            empty_label.setFont(QFont(FONT_FAMILY, 14))
            empty_label.setStyleSheet(f"color: {TEXT_HINT_COLOR};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0)
            
            # 更新批量删除按钮状态
            self.batch_btn.setEnabled(False)
            return
        else:
            # 有快捷方式时启用批量删除按钮
            self.batch_btn.setEnabled(True)
        
        # 对实例列表按照后缀数字从小到大排序
        sorted_shortcuts = sorted(self.main_window.shortcuts, key=self._extract_instance_number)
        
        # 卡片参数
        card_width = 180  # 卡片宽度
        card_spacing = 30  # 调整卡片间距
        
        # 根据窗口状态确定布局
        if self.main_window.isMaximized():
            # 最大化状态：动态计算列数，但确保间距合理
            available_width = self.grid_widget.width() - 60  # 减去左右边距
            max_cols = min(6, (available_width + card_spacing) // (card_width + card_spacing))
        else:
            # 默认大小状态：固定4列
            max_cols = 4
        
        # 添加卡片到网格
        for i, shortcut in enumerate(sorted_shortcuts):
            row = i // max_cols
            col = i % max_cols
            card = BrowserCard(
                shortcut["name"], 
                shortcut["data_dir"], 
                self.main_window.chrome_path,
                on_delete=self.delete_shortcut
            )
            
            # 设置选择模式状态
            if self.is_batch_mode:
                card.set_select_mode(True)
                
            self.grid_layout.addWidget(card, row, col)
            self.card_widgets.append(card)
        
        # 设置水平和垂直间距
        self.grid_layout.setHorizontalSpacing(card_spacing)  # 水平间距
        self.grid_layout.setVerticalSpacing(card_spacing)  # 垂直间距
    
    def _extract_instance_number(self, shortcut):
        """从实例名称中提取数字用于排序"""
        name = shortcut["name"]
        try:
            # 提取"Chrome实例"后面的数字
            if name.startswith("Chrome实例"):
                return int(name[len("Chrome实例"):])
            
            # 如果不是以Chrome实例开头，尝试其他方式提取数字
            # 从末尾开始寻找数字
            digits = ""
            for char in reversed(name):
                if char.isdigit():
                    digits = char + digits
                elif digits:  # 如果已经找到了数字，且当前字符不是数字，则中断
                    break
            
            if digits:
                return int(digits)
        except (ValueError, IndexError):
            pass
        
        # 如果无法提取数字，返回一个大数作为默认值（放在最后）
        return float('inf')
    
    def add_shortcut(self):
        """添加新快捷方式"""
        # 查找可用的实例编号
        next_number = self._find_next_available_number()
            
        dialog = AddShortcutDialog(self.main_window, next_number - 1)  # 将参数改为下一个可用编号-1，以适应对话框内部+1的逻辑
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, dir_name = dialog.get_values()
            
            if not name or not dir_name:
                # 使用状态栏显示错误
                self.main_window.statusBar().showMessage("名称和目录名不能为空！", 5000)
                return
                
            if any(s["name"] == name for s in self.main_window.shortcuts):
                # 使用状态栏显示错误
                self.main_window.statusBar().showMessage(f"名称 '{name}' 已存在！", 5000)
                return
                
            # 确保数据目录名称未被使用
            if any(os.path.basename(s["data_dir"]) == dir_name for s in self.main_window.shortcuts):
                # 使用状态栏显示错误
                self.main_window.statusBar().showMessage(f"数据目录名 '{dir_name}' 已存在！", 5000)
                return
            
            # 确保数据目录是绝对路径
            data_dir = os.path.join(self.main_window.data_root, dir_name)
            
            shortcut = {
                "name": name,
                "data_dir": data_dir
            }
            
            # 先添加到数据库
            print(f"添加新实例到数据库: 名称={name}, 数据目录={data_dir}")
            db_success = self.main_window.config_manager.db_manager.save_chrome_instance(shortcut)
            print(f"数据库添加结果: {db_success}")
            
            if db_success:
                self.main_window.shortcuts.append(shortcut)
                
                # 创建快捷方式
                success = self.main_window.shortcut_manager.create_shortcut(name, data_dir, self.main_window.chrome_path)
                if success:
                    self.main_window.statusBar().showMessage(f"Chrome实例 '{name}' 创建成功", 3000)  # 显示3秒
                    
                    # 强制刷新实例列表 - 直接从数据库重新加载实例数据
                    print("正在从数据库重新加载实例列表...")
                    instances = self.main_window.config_manager.db_manager.get_all_chrome_instances()
                    print(f"从数据库加载的实例数: {len(instances)}")
                    self.main_window.shortcuts = instances
                    
                    # 更新界面和保存配置
                    self.update_browser_grid()
                    self.main_window.auto_save_config()
                else:
                    self.main_window.statusBar().showMessage(f"Chrome实例 '{name}' 创建失败", 3000)  # 显示3秒
    
    def _find_next_available_number(self):
        """查找下一个可用的实例编号"""
        used_numbers = set()
        for shortcut in self.main_window.shortcuts:
            # 从实例名称中提取编号
            name = shortcut["name"]
            if name.startswith("Chrome实例"):
                try:
                    num = int(name[len("Chrome实例"):])
                    used_numbers.add(num)
                except ValueError:
                    pass
            
            # 从数据目录中提取编号
            data_dir = shortcut["data_dir"]
            dir_name = os.path.basename(data_dir)
            if dir_name.startswith("Profile"):
                try:
                    num = int(dir_name[len("Profile"):])
                    used_numbers.add(num)
                except ValueError:
                    pass
                
        # 找到可用的最小编号
        next_number = 1
        while next_number in used_numbers:
            next_number += 1
            
        return next_number
    
    def batch_add_shortcuts(self):
        """批量添加快捷方式"""
        next_number = self._find_next_available_number()
        
        dialog = BatchAddShortcutDialog(self.main_window, next_number)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            start_number, count, prefix = dialog.get_values()
            
            if start_number is None or count is None or not prefix:
                self.main_window.statusBar().showMessage("输入错误，请检查数值设置", 5000)
                return
                
            if count <= 0 or count > 50:
                self.main_window.statusBar().showMessage("创建数量必须在1-50之间", 5000)
                return
            
            # 先对页面做一次UI更新，告知用户操作已开始
            self.main_window.statusBar().showMessage(f"开始创建 {count} 个实例，请稍候...", 3000)
            self.main_window.setEnabled(False)  # 暂时禁用UI，避免用户点击其他按钮
            QApplication.processEvents()  # 确保消息显示
            
            # 使用定时器处理批量创建，避免UI卡死
            self.batch_create_index = 0
            self.batch_create_count = count
            self.batch_create_start_number = start_number
            self.batch_create_prefix = prefix
            self.batch_create_success_count = 0
            self.batch_create_timer = QTimer()
            self.batch_create_timer.timeout.connect(self._process_next_create)
            self.batch_create_timer.start(100)  # 延迟100毫秒后开始处理
    
    def _process_next_create(self):
        """处理下一个创建操作"""
        if self.batch_create_index >= self.batch_create_count:
            # 所有创建已完成
            self.batch_create_timer.stop()
            
            # 终止操作后启用UI
            self.main_window.setEnabled(True)
            
            # 通知用户已完成
            self.main_window.statusBar().showMessage(f"成功创建 {self.batch_create_success_count} 个实例", 3000)
            
            # 强制刷新实例列表 - 直接从数据库重新加载实例数据
            instances = self.main_window.config_manager.db_manager.get_all_chrome_instances()
            self.main_window.shortcuts = instances
            
            # 更新UI
            self.update_browser_grid()
            
            # 保存配置
            self.main_window.auto_save_config()
            
            return
        
        # 计算当前实例编号
        current_number = self.batch_create_start_number + self.batch_create_index
        
        # 创建实例名称和数据目录名
        name = f"{self.batch_create_prefix}{current_number}"
        dir_name = f"Profile{current_number}"
        
        # 跳过已存在的实例
        if any(s["name"] == name for s in self.main_window.shortcuts) or \
           any(os.path.basename(s["data_dir"]) == dir_name for s in self.main_window.shortcuts):
            self.batch_create_index += 1
            self.batch_create_timer.start(50)  # 快速跳到下一个
            return
        
        # 确保数据目录是绝对路径
        data_dir = os.path.join(self.main_window.data_root, dir_name)
        
        shortcut = {
            "name": name,
            "data_dir": data_dir
        }
        
        # 添加到数据库
        db_success = self.main_window.config_manager.db_manager.save_chrome_instance(shortcut)
        
        if db_success:
            self.main_window.shortcuts.append(shortcut)
            
            # 创建快捷方式
            success = self.main_window.shortcut_manager.create_shortcut(name, data_dir, self.main_window.chrome_path)
            if success:
                self.batch_create_success_count += 1
        
        # 增加索引，准备处理下一个
        self.batch_create_index += 1
        
        # 更新状态栏
        self.main_window.statusBar().showMessage(f"正在创建实例 {self.batch_create_index}/{self.batch_create_count}...", 1000)
        
        # 处理事件，确保UI响应
        QApplication.processEvents()
        
        # 使用定时器继续下一个
        self.batch_create_timer.start(200)
    
    def delete_shortcut(self, name, data_dir):
        """删除单个快捷方式"""
        log_time(f"开始删除单个快捷方式: {name}")
        
        # 构建数据目录路径
        data_dir = os.path.join(self.main_window.data_root, data_dir)
        log_time(f"数据目录路径: {data_dir}")
        
        # 第一个确认对话框已经在cards.py中显示了，这里直接执行删除操作
        log_time("用户确认删除")
        
        # 先保存配置，确保状态一致
        log_time("保存配置确保状态一致")
        self.main_window.auto_save_config()
        
        # 启动删除操作
        start_time = time.time()
        log_time("启动后台删除操作")
        success = self.main_window.shortcut_manager.delete_shortcut(name, data_dir)
        elapsed = time.time() - start_time
        log_time(f"删除操作启动耗时: {elapsed:.4f}秒")
        
        if success:
            # 从内存中移除快捷方式
            log_time("从内存中移除快捷方式")
            self.main_window.shortcuts = [s for s in self.main_window.shortcuts if s["name"] != name]
            
            # 更新UI
            log_time("更新UI显示")
            # 使用单次触发的计时器在下一个事件循环中更新UI
            QTimer.singleShot(0, self.update_browser_grid)
            
            # 显示成功消息
            self.main_window.statusBar().showMessage(f"实例 {name} 正在后台删除中...", 3000)
            log_time("单个删除操作完成")
        else:
            log_time(f"删除操作启动失败")
            self.main_window.statusBar().showMessage("删除失败，请查看日志", 5000)
        
        # 立即返回，不阻塞UI
        return True
    
    def toggle_batch_mode(self):
        """切换批量操作模式"""
        self.is_batch_mode = not self.is_batch_mode
        self.is_all_selected = False  # 重置全选状态
        
        # 更新按钮状态
        self.batch_btn.setVisible(not self.is_batch_mode)
        self.select_all_btn.setVisible(self.is_batch_mode)
        self.confirm_delete_btn.setVisible(self.is_batch_mode)
        self.cancel_batch_btn.setVisible(self.is_batch_mode)
        
        # 更新所有卡片的选择模式
        for card in self.card_widgets:
            card.set_select_mode(self.is_batch_mode)
            if not self.is_batch_mode:
                card.set_selected(False)  # 退出批量模式时取消所有选择
                
    def toggle_select_all(self):
        """切换全选状态"""
        self.is_all_selected = not self.is_all_selected
        self.select_all_btn.setText("取消全选" if self.is_all_selected else "全选")
        
        # 更新所有卡片的选中状态
        for card in self.card_widgets:
            card.set_selected(self.is_all_selected)
    
    def delete_selected_shortcuts(self):
        """删除多个选中的实例"""
        log_time("开始批量删除操作")
        
        # 收集选中的卡片
        self.cards_to_delete = []
        for card in self.card_widgets:
            if card.is_selected:
                self.cards_to_delete.append(card)
        
        if not self.cards_to_delete:
            log_time("没有选中实例")
            self.main_window.statusBar().showMessage("请先选择要删除的实例", 3000)
            return
        
        # 记录数量
        count = len(self.cards_to_delete)
        log_time(f"选中了 {count} 个实例待删除")
        
        # 退出批量模式
        self.toggle_batch_mode()
        
        # 启动定时器处理删除
        self.delete_index = 0
        self.delete_count = 0
        
        # 先对页面做一次UI更新，告知用户操作已开始
        self.main_window.statusBar().showMessage(f"开始删除 {count} 个实例，请稍候...", 3000)
        self.main_window.setEnabled(False)  # 暂时禁用UI，避免用户点击其他按钮
        QApplication.processEvents()  # 确保消息显示
        
        # 使用定时器延迟执行，让UI有时间更新
        self.delete_timer = QTimer()
        self.delete_timer.setSingleShot(True)
        self.delete_timer.timeout.connect(self._process_next_delete)
        self.delete_timer.start(100)  # 延迟100毫秒后开始处理

    def _process_next_delete(self):
        """处理下一个删除操作"""
        if self.delete_index >= len(self.cards_to_delete):
            # 所有删除已完成
            self.delete_timer.stop()
            
            # 终止操作后启用UI
            self.main_window.setEnabled(True)
            
            # 通知用户已完成
            self.main_window.statusBar().showMessage(f"成功删除 {self.delete_count} 个实例", 3000)
            
            # 最后，确保所有的更改都被保存到数据库中
            # 这一步很重要，因为之前的delete_shortcut操作可能没有正确更新内存中的实例列表
            # 使用定时器，确保所有UI事件都被处理
            QTimer.singleShot(800, self._sync_after_batch_delete)
            
            return
        
        # 获取当前卡片
        card = self.cards_to_delete[self.delete_index]
        name = card.name
        data_dir = card.data_dir
        log_time(f"批量删除第 {self.delete_index+1}/{len(self.cards_to_delete)} 个: {name}")
        
        # 启动删除操作
        start_time = time.time()
        success = self.main_window.shortcut_manager.delete_shortcut(name, data_dir)
        elapsed = time.time() - start_time
        log_time(f"删除操作启动耗时: {elapsed:.4f}秒")
        
        if success:
            # 从内存中移除快捷方式
            log_time(f"从内存中移除快捷方式: {name}")
            self.main_window.shortcuts = [s for s in self.main_window.shortcuts if s["name"] != name]
            self.delete_count += 1
            
            # 直接更新UI，移除当前卡片的显示
            card.setVisible(False)
            card.deleteLater()
            QApplication.processEvents()
        else:
            log_time(f"删除 {name} 失败")
            
        # 增加索引，准备处理下一个
        self.delete_index += 1
        
        # 在处理下一个前保存配置
        if self.delete_index < len(self.cards_to_delete):
            # 先更新UI显示
            QApplication.processEvents()
            # 使用较短的延时继续下一个
            self.delete_timer.start(200)
        else:
            # 这是最后一个，使用较长的延时让最后一个删除有时间处理
            self.delete_timer.start(500)
    
    def _sync_after_batch_delete(self):
        """批量删除完成后同步内存与文件系统，确保数据一致性"""
        try:
            log_time("执行批量删除后的数据同步...")
            
            # 从文件系统重新检查哪些实例存在，哪些已被删除
            if hasattr(self.main_window, '_sync_shortcuts_with_filesystem'):
                self.main_window._sync_shortcuts_with_filesystem()
            
            # 强制保存当前内存中的实例列表到数据库
            self.main_window.auto_save_config()
            
            # 重新加载并更新UI
            self.update_browser_grid()
            
            log_time("批量删除后的数据同步完成")
        except Exception as e:
            log_time(f"批量删除后同步数据时出错: {str(e)}") 