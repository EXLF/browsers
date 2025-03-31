"""
快捷方式管理模块，负责创建和管理Chrome快捷方式
"""

import os
import sys
import winshell
import time
import datetime  # 添加datetime模块
import threading
from win32com.client import Dispatch
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QEventLoop, QObject
import subprocess

from .constants import FONT_FAMILY, PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_PRIMARY_COLOR

# 添加全局进程缓存，减少重复检查
_chrome_processes_cache = None
_chrome_cache_time = 0
_chrome_cache_max_age = 2.0  # 缓存最长2秒有效

# 辅助调试函数
def log_time(message):
    """记录带时间戳的消息"""
    thread_id = threading.get_native_id()
    # 使用datetime模块获取微秒级时间戳
    now = datetime.datetime.now()
    timestamp = now.strftime("%H:%M:%S") + f".{now.microsecond // 1000:03d}"
    print(f"[{timestamp}] [线程 {thread_id}] {message}")

class DeleteShortcutThread(QThread):
    """负责在后台删除快捷方式和数据目录的线程"""
    
    delete_finished = pyqtSignal(bool, str)
    dir_delete_progress = pyqtSignal(str)  # 删除进度信号
    
    def __init__(self, shortcut_path, data_dir):
        super().__init__()
        self.shortcut_path = shortcut_path
        self.data_dir = data_dir
        self.is_chrome_running_cached = False  # 缓存Chrome运行状态
        self.last_progress_time = 0  # 上次发送进度的时间
        self.progress_interval = 0.3  # 至少间隔0.3秒发送一次进度
        # 优先级将在run方法中设置
        
    def run(self):
        # 设置线程优先级为低，让UI线程优先处理
        try:
            self.setPriority(QThread.Priority.LowestPriority)  # 使用最低优先级
            log_time(f"删除线程启动，优先级设置为最低")
        except Exception as e:
            log_time(f"设置线程优先级失败: {str(e)}")
        
        try:
            # 1. 删除快捷方式文件
            shortcut_deleted = False
            if os.path.exists(self.shortcut_path):
                try:
                    log_time(f"开始删除快捷方式文件: {self.shortcut_path}")
                    os.remove(self.shortcut_path)
                    shortcut_deleted = True
                    log_time(f"快捷方式文件删除成功")
                    self._emit_progress(f"快捷方式文件删除成功: {self.shortcut_path}")
                except Exception as e:
                    log_time(f"快捷方式文件删除失败: {str(e)}")
                    self._emit_progress(f"快捷方式文件删除失败: {str(e)}")
            else:
                log_time(f"快捷方式文件不存在: {self.shortcut_path}")
                self._emit_progress(f"快捷方式文件不存在: {self.shortcut_path}")
                shortcut_deleted = True  # 如果文件不存在，视为删除成功
            
            # 短暂暂停，确保UI可以响应
            log_time("暂停线程20毫秒，让UI可以响应")
            self.msleep(20)  # 增加到20毫秒
            
            # 2. 异步预检查Chrome进程 - 先启动检查，但增加跳过逻辑
            # 优化: 如果目录不存在，直接跳过检查
            if not os.path.exists(self.data_dir):
                log_time(f"数据目录不存在，跳过Chrome进程检查: {self.data_dir}")
                self.chrome_running_result = False
            else:
                self._async_check_chrome_running()
            
            # 3. 删除数据目录
            if os.path.exists(self.data_dir) and os.path.isdir(self.data_dir):
                try:
                    # 检查是否有Chrome进程使用该数据目录
                    log_time(f"检查Chrome进程是否使用数据目录: {self.data_dir}")
                    
                    # 等待异步检查完成，最多等待300毫秒
                    wait_start = time.time()
                    max_wait = 0.3  # 减少等待时间到300毫秒
                    check_interval = 30  # 每30毫秒检查一次
                    
                    while time.time() - wait_start < max_wait and not hasattr(self, 'chrome_running_result'):
                        self.msleep(check_interval)
                    
                    # 使用检查结果（如果有），否则假设没有运行中的Chrome
                    is_running = getattr(self, 'chrome_running_result', False)
                    
                    if is_running:
                        log_time("数据目录正在被Chrome使用，无法删除")
                        self._emit_progress(f"数据目录正在被Chrome使用，无法删除: {self.data_dir}")
                        self.delete_finished.emit(shortcut_deleted, "Chrome正在运行，无法删除数据目录")
                        return
                    
                    # 开始删除数据目录
                    log_time(f"开始删除数据目录: {self.data_dir}")
                    self._emit_progress(f"开始删除数据目录: {self.data_dir}")
                    
                    # 使用优化的目录删除方法，而不是直接用shutil.rmtree
                    start_time = time.time()
                    success = self._delete_directory_optimized(self.data_dir)
                    elapsed = time.time() - start_time
                    
                    log_time(f"目录删除操作完成，耗时: {elapsed:.2f}秒，结果: {'成功' if success else '部分失败'}")
                    
                    if success:
                        self._emit_progress(f"数据目录删除成功: {self.data_dir}")
                        self.delete_finished.emit(True, "")
                    else:
                        self._emit_progress(f"数据目录删除不完全: {self.data_dir}")
                        self.delete_finished.emit(shortcut_deleted, "部分文件无法删除")
                    return
                except Exception as e:
                    log_time(f"数据目录删除失败: {str(e)}")
                    self._emit_progress(f"数据目录删除失败: {str(e)}")
                    self.delete_finished.emit(shortcut_deleted, str(e))
                    return
            else:
                log_time(f"数据目录不存在或不是目录: {self.data_dir}")
                self._emit_progress(f"数据目录不存在或不是目录: {self.data_dir}")
                self.delete_finished.emit(shortcut_deleted, "")
                return
        except Exception as e:
            # 捕获所有异常，确保线程正常结束
            log_time(f"删除操作发生异常: {str(e)}")
            self.delete_finished.emit(False, f"删除操作发生异常: {str(e)}")
    
    def _emit_progress(self, message):
        """控制进度信号发送频率，避免过于频繁更新UI"""
        current_time = time.time()
        if current_time - self.last_progress_time >= self.progress_interval:
            self.dir_delete_progress.emit(message)
            self.last_progress_time = current_time
            # 发送后暂停一小段时间，让UI有时间处理
            self.msleep(10)
    
    def _async_check_chrome_running(self):
        """在单独的线程中异步检查Chrome是否运行，优化过的版本"""
        # 创建一个线程来执行检查
        check_thread = threading.Thread(
            target=self._check_chrome_thread,
            args=(self.data_dir,),
            daemon=True
        )
        check_thread.start()
        log_time("启动异步Chrome进程检查线程")
    
    def _check_chrome_thread(self, data_dir):
        """在单独线程中执行Chrome进程检查，使用优化的算法和缓存机制"""
        import os  # 确保在函数内部导入os
        import psutil  # 确保在函数内部导入psutil
        
        try:
            # 快速路径: 如果目录不存在，直接返回False
            if not os.path.exists(data_dir):
                log_time(f"数据目录不存在，跳过Chrome进程检查")
                self.chrome_running_result = False
                return
                
            # 设置低优先级
            try:
                process = psutil.Process(os.getpid())
                if hasattr(process, "nice"):
                    process.nice(19)  # Linux/macOS: 设置最低优先级
                elif hasattr(process, "ionice"):
                    process.ionice(psutil.IOPRIO_CLASS_IDLE)  # 设置IO最低优先级
            except Exception as e:
                log_time(f"设置Chrome检查线程优先级出错: {str(e)}")
            
            start_time = time.time()
            
            # 使用更高效的进程检查方法及缓存进程列表
            is_running = self._is_chrome_running_optimized(data_dir)
            
            elapsed = time.time() - start_time
            log_time(f"Chrome进程检查完成，耗时: {elapsed:.3f}秒，结果: {is_running}")
            
            # 存储结果供主线程使用
            self.chrome_running_result = is_running
        except Exception as e:
            log_time(f"Chrome进程检查线程出错: {str(e)}")
            self.chrome_running_result = False  # 出错时假设没有运行
    
    def _delete_directory_optimized(self, directory):
        """优化的目录删除方法，分批删除文件以避免长时间阻塞"""
        try:
            import shutil
            
            # 如果目录不大，直接删除
            try:
                # 检查目录大小
                total_size = 0
                file_count = 0
                
                log_time("开始统计目录文件数量")
                for root, dirs, files in os.walk(directory):
                    file_count += len(files)
                    if file_count > 20:  # 如果文件数超过20，就采用分批删除 (降低阈值加快测试)
                        break
                log_time(f"目录文件数量统计完成: {file_count}个文件")
                        
                # 文件数少，直接使用rmtree
                if file_count <= 20:
                    log_time(f"文件数少于20，使用直接删除方法")
                    self._emit_progress(f"文件数较少({file_count}个)，执行快速删除")
                    shutil.rmtree(directory)
                    return True
            except Exception as e:
                log_time(f"检查目录大小出错: {str(e)}，将使用分批删除方法")
                pass  # 如果检查出错，采用下面的分批删除方法
            
            # 文件数多，使用分批删除方法
            # 1. 首先收集所有文件和子目录
            log_time("开始收集所有文件和目录")
            all_items = []
            for root, dirs, files in os.walk(directory, topdown=False):
                # 先收集文件
                for name in files:
                    all_items.append(os.path.join(root, name))
                # 再收集目录
                for name in dirs:
                    all_items.append(os.path.join(root, name))
            
            # 添加根目录
            all_items.append(directory)
            log_time(f"收集完成，共有{len(all_items)}项需要删除")
            
            # 2. 分批删除文件和目录
            # 进一步增大批次大小，减少进度更新频率
            batch_size = 20  # 增加到20个文件每批
            total_batches = (len(all_items) + batch_size - 1) // batch_size
            log_time(f"将分{total_batches}批处理删除")
            
            # 减少进度更新频率，仅在完成一定百分比时更新
            progress_step = max(1, total_batches // 5)  # 最多显示5次进度
            
            for i in range(0, len(all_items), batch_size):
                batch = all_items[i:i+batch_size]
                batch_num = i // batch_size + 1
                
                # 仅在关键进度点发送进度信息
                if batch_num % progress_step == 0 or batch_num == 1 or batch_num == total_batches:
                    progress_msg = f"删除进度: {batch_num}/{total_batches} 批"
                    log_time(progress_msg)
                    self._emit_progress(progress_msg)
                
                # 删除当前批次的文件和目录
                for item in batch:
                    try:
                        if os.path.isfile(item):
                            os.unlink(item)
                        elif os.path.isdir(item):
                            try:
                                os.rmdir(item)  # 尝试删除目录
                            except OSError:
                                pass  # 忽略非空目录错误，后续批次会处理
                    except Exception as e:
                        # 忽略单个文件删除错误，继续处理
                        log_time(f"删除项目时出错 {item}: {str(e)}")
                
                # 使用msleep代替time.sleep，保证UI响应性
                if batch_num % progress_step == 0:  # 只在发送进度时暂停
                    log_time(f"批次{batch_num}完成，暂停50毫秒")
                    self.msleep(50)  # 增加到50毫秒
            
            # 3. 最后检查根目录是否已删除
            if os.path.exists(directory):
                try:
                    log_time("尝试最终清理目录")
                    shutil.rmtree(directory)  # 最后尝试一次完整删除
                    log_time("最终清理成功")
                except Exception as e:
                    log_time(f"最终清理时出错: {str(e)}")
                    self._emit_progress(f"最终清理时出错: {str(e)}")
                    return False
            
            log_time("目录删除完成")
            return True
        except Exception as e:
            log_time(f"优化删除过程中出错: {str(e)}")
            self._emit_progress(f"优化删除过程中出错: {str(e)}")
            return False
    
    def _is_chrome_running_optimized(self, data_dir):
        """优化的Chrome进程检查，缓存进程列表，减少IO和CPU开销"""
        global _chrome_processes_cache, _chrome_cache_time, _chrome_cache_max_age
        
        try:
            import psutil
            import time
            
            # 检查是否可以使用缓存
            current_time = time.time()
            use_cache = (_chrome_processes_cache is not None and 
                         current_time - _chrome_cache_time < _chrome_cache_max_age)
            
            # 将路径转换为统一格式以提高匹配精度
            normalized_data_dir = os.path.normpath(data_dir).lower()
            
            # 获取Chrome进程列表
            if use_cache:
                chrome_processes = _chrome_processes_cache
                log_time(f"使用缓存的Chrome进程列表，{len(chrome_processes)}个进程")
            else:
                # 首先尝试基于名称过滤进程，减少遍历量
                chrome_processes = []
                try:
                    # 两种获取方式
                    try:
                        # 更高效的过滤方式
                        for proc in psutil.process_iter(['name']):
                            try:
                                if not proc.info['name']:
                                    continue
                                name = proc.info['name'].lower()
                                if 'chrome' in name or 'chromium' in name:
                                    chrome_processes.append(proc)
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                continue
                    except Exception:
                        # 备用方法
                        for proc in psutil.process_iter():
                            try:
                                name = proc.name().lower()
                                if 'chrome' in name or 'chromium' in name:
                                    chrome_processes.append(proc)
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                continue
                                
                    # 更新缓存
                    _chrome_processes_cache = chrome_processes
                    _chrome_cache_time = current_time
                    log_time(f"更新Chrome进程缓存，找到{len(chrome_processes)}个进程")
                    
                except Exception as e:
                    log_time(f"获取进程列表时出错: {str(e)}")
                    # 无法获取进程列表，返回保守结果
                    return False
            
            # 如果没有Chrome进程，快速返回
            if not chrome_processes:
                return False
                
            # 然后只检查Chrome进程的命令行
            profile_markers = ['--user-data-dir=', '--profile-directory=']
            
            # 一次获取所有命令行，避免多次调用
            for proc in chrome_processes:
                try:
                    cmdline = proc.cmdline()
                    if not cmdline:
                        continue
                        
                    # 直接检查命令行参数，不再拼接字符串
                    for arg in cmdline:
                        if not isinstance(arg, str):
                            continue
                            
                        arg_lower = arg.lower()
                        for marker in profile_markers:
                            if marker in arg_lower and normalized_data_dir in arg_lower:
                                log_time(f"找到运行中的Chrome进程，使用数据目录: {data_dir}")
                                return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            return False
        except Exception as e:
            log_time(f"检查Chrome进程时出错: {str(e)}")
            return False  # 出错时保守地返回False

class ShortcutManager:
    """快捷方式管理类，负责创建和管理Chrome快捷方式"""
    
    def __init__(self, main_window):
        """
        初始化快捷方式管理器
        
        Args:
            main_window: 主窗口实例，用于显示消息对话框
        """
        self.main_window = main_window
        self.desktop_path = winshell.desktop()
        self.shortcuts_dir = self.desktop_path  # 默认使用桌面路径
        self.delete_threads = []  # 保存所有删除线程的引用，防止被垃圾回收
    
    def set_shortcuts_dir(self, path):
        """
        设置快捷方式保存目录
        
        Args:
            path: 快捷方式保存目录路径
        """
        if path and os.path.exists(path):
            self.shortcuts_dir = path
        else:
            self.shortcuts_dir = self.desktop_path  # 如果路径无效，使用桌面路径
    
    def create_shortcut(self, name, data_dir, chrome_path):
        """
        创建Chrome快捷方式
        
        Args:
            name: 快捷方式名称
            data_dir: 数据目录路径
            chrome_path: Chrome可执行文件路径
            
        Returns:
            bool: 是否创建成功
        """
        success = False
        retry_count = 0
        max_retries = 3
        
        while not success and retry_count < max_retries:
            try:
                # 提取数据目录名称作为Profile名称
                profile_name = os.path.basename(data_dir)
                
                # 创建更简洁的显示名称
                display_name = name
                
                # 创建快捷方式路径
                shortcut_path = os.path.join(self.shortcuts_dir, f"{display_name}.lnk")
                
                # 确保数据目录存在
                os.makedirs(data_dir, exist_ok=True)
                
                # 确保快捷方式目录存在
                os.makedirs(os.path.dirname(shortcut_path), exist_ok=True)
                
                # 创建快捷方式
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = chrome_path
                shortcut.Arguments = f'--user-data-dir="{data_dir}"'
                shortcut.Description = f"Chrome - {display_name}"
                shortcut.IconLocation = f"{chrome_path}, 0"
                shortcut.WorkingDirectory = os.path.dirname(chrome_path)
                shortcut.save()
                
                # 验证快捷方式创建成功
                if os.path.exists(shortcut_path):
                    print(f"快捷方式已创建: {shortcut_path}")
                    success = True
                else:
                    print(f"快捷方式创建后未找到: {shortcut_path}")
                    retry_count += 1
                    time.sleep(0.5)  # 重试前等待一段时间
            except Exception as e:
                # 使用状态栏显示错误消息
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(f"创建快捷方式失败：{str(e)}", 5000)
                print(f"创建快捷方式错误: {str(e)}")
                import traceback
                traceback.print_exc()
                retry_count += 1
                time.sleep(0.5)  # 重试前等待一段时间
                
        return success
    
    def delete_shortcut(self, name, data_dir):
        """
        删除Chrome快捷方式和数据目录 - 完全在后台线程中执行所有操作
        
        Args:
            name: 快捷方式名称
            data_dir: 数据目录路径
            
        Returns:
            bool: 返回True表示删除操作已启动（不代表删除成功）
        """
        try:
            log_time(f"启动删除操作: {name}, {data_dir}")
            
            # 构建快捷方式路径
            shortcut_path = os.path.join(self.shortcuts_dir, f"{name}.lnk")
            log_time(f"尝试删除快捷方式文件: {shortcut_path}")
            
            # 创建后台线程处理所有删除操作
            delete_thread = DeleteShortcutThread(shortcut_path, data_dir)
            
            # 使用Qt.ConnectionType.QueuedConnection确保信号在主线程中处理
            delete_thread.delete_finished.connect(
                self._on_delete_finished, 
                type=Qt.ConnectionType.QueuedConnection
            )
            delete_thread.dir_delete_progress.connect(
                self._on_delete_progress, 
                type=Qt.ConnectionType.QueuedConnection
            )
            
            # 将线程保存到列表中，防止被垃圾回收
            self.delete_threads.append(delete_thread)
            
            # 确保UI在启动线程前处理所有事件
            log_time("删除线程启动前处理所有事件")
            self._process_events_completely()
            
            # 启动线程
            log_time("启动删除线程")
            delete_thread.start()
            
            # 显示状态消息
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"正在后台删除文件，请稍候...", 3000)
            
            # 强制处理任何挂起的事件，确保UI可以立即响应
            log_time("删除线程启动后再次处理所有事件")
            self._process_events_completely()
            
            # 立即返回True，表示删除操作已启动
            log_time("删除操作启动成功，返回True")
            return True
            
        except Exception as e:
            # 使用状态栏显示错误消息
            log_time(f"启动删除操作失败: {str(e)}")
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"启动删除操作失败：{str(e)}", 5000)
            print(f"启动删除操作失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _process_events_completely(self):
        """优化的事件处理函数，避免嵌套事件循环"""
        # 直接使用processEvents，不创建新的事件循环
        QApplication.processEvents()
        QApplication.processEvents()  # 再次处理可能产生的新事件
    
    def _on_delete_progress(self, message):
        """
        删除过程中的进度更新回调
        
        Args:
            message: 进度消息
        """
        log_time(f"删除进度: {message}")
        
        # 更新状态栏，但只显示较短时间，不阻塞其他消息
        if hasattr(self.main_window, 'statusBar'):
            if "进度" in message or "批次" in message or "快速删除" in message:
                # 对于进度消息，在状态栏上显示
                self.main_window.statusBar().showMessage(message, 1000)
        
        # 强制处理所有UI事件，确保界面响应
        QApplication.processEvents()
    
    def _on_delete_finished(self, success, error_msg):
        """
        数据目录删除线程完成的回调方法
        
        Args:
            success: 是否成功删除
            error_msg: 错误消息
        """
        log_time(f"删除操作完成: 成功={success}, 错误={error_msg}")
        
        if success:
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"数据目录删除成功完成", 3000)
            log_time(f"数据目录删除成功完成")
        else:
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"数据目录删除失败：{error_msg}", 5000)
            log_time(f"数据目录删除失败: {error_msg}")
        
        # 清理已完成的线程
        old_count = len(self.delete_threads)
        self.delete_threads = [t for t in self.delete_threads if t.isRunning()]
        log_time(f"清理完成的线程: {old_count} -> {len(self.delete_threads)}")
        
        # 使用标准的processEvents处理所有挂起的UI事件
        self._process_events_completely()
    
    def is_chrome_running(self, data_dir):
        """
        检查与特定数据目录相关的Chrome进程是否在运行
        
        Args:
            data_dir: 数据目录路径
            
        Returns:
            bool: 是否有相关Chrome进程在运行
        """
        try:
            import psutil
            for proc in psutil.process_iter(['name', 'cmdline']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        # 检查命令行中是否包含数据目录路径
                        if data_dir.lower() in cmdline.lower():
                            print(f"找到运行中的Chrome进程，使用数据目录: {data_dir}")
                            return True
            return False
        except Exception as e:
            print(f"检查Chrome进程时出错: {str(e)}")
            return False  # 出错时保守地返回False
    
    def launch_browser(self, shortcut):
        """启动浏览器实例"""
        try:
            # 验证Chrome路径
            if not os.path.exists(self.chrome_path):
                # 使用状态栏显示错误消息
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(f"未找到Chrome浏览器，请在设置中指定正确的Chrome路径", 5000)
                return False
                
            # 确保数据目录存在
            data_dir = os.path.join(self.data_root, shortcut.data_dir)
            os.makedirs(data_dir, exist_ok=True)
            
            # 构建启动命令
            cmd = [
                f'"{self.chrome_path}"',  # 使用引号包裹路径，处理路径中的空格
                f'--user-data-dir="{data_dir}"',  # 指定用户数据目录
                '--no-first-run',  # 跳过首次运行设置
                '--no-default-browser-check',  # 跳过默认浏览器检查
            ]
            
            # 如果有其他启动参数，添加到命令中
            if shortcut.extra_args:
                cmd.extend(shortcut.extra_args.split())
                
            # 启动进程
            subprocess.Popen(' '.join(cmd), shell=True)
            return True
            
        except Exception as e:
            # 使用状态栏显示错误消息
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"启动Chrome时发生错误：{str(e)}", 5000)
            return False
    
    def show_error_message(self, message):
        """显示错误消息"""
        # 此方法已不再使用，改为使用状态栏显示消息
        # 保留方法签名以防有代码调用，但内部实现改为使用状态栏
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(message, 5000) 