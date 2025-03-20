"""
扩展插件管理模块，负责Chrome扩展的管理和安装
"""

import os
import json
import subprocess
import shutil
import re
import requests
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon, QPixmap

class ExtensionManager:
    """扩展插件管理类"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.extensions_library = []  # 存储所有扩展
        self.extensions_dir = os.path.join(os.path.dirname(self.config_manager.config_file), "extensions")
        
        # 确保扩展目录存在
        os.makedirs(self.extensions_dir, exist_ok=True)
        
        # 加载扩展库
        self.load_extensions()
    
    def load_extensions(self):
        """从配置加载扩展库"""
        # 加载配置
        config = self.config_manager.load_config()
        if 'extensions' in config:
            self.extensions_library = config['extensions']
        else:
            # 如果配置中没有扩展库，初始化一个空列表
            self.extensions_library = []
            # 更新配置对象
            config['extensions'] = self.extensions_library
            self.config_manager.save_config(config)
    
    def add_extension(self, name, ext_id, description="", icon_path=None, crx_path=None):
        """
        添加扩展到库
        
        Args:
            name: 扩展名称
            ext_id: 扩展ID
            description: 扩展描述
            icon_path: 图标路径
            crx_path: CRX文件路径
        
        Returns:
            bool: 添加是否成功
        """
        # 检查扩展是否已存在
        for ext in self.extensions_library:
            if ext.get('id') == ext_id:
                return False, "该扩展已存在于库中"
        
        # 创建扩展专用目录
        ext_dir = os.path.join(self.extensions_dir, ext_id)
        try:
            os.makedirs(ext_dir, exist_ok=True)
        except Exception as e:
            return False, f"创建扩展目录失败: {str(e)}"
        
        # 如果有CRX文件，复制到扩展目录
        local_crx_path = None
        if crx_path and os.path.exists(crx_path):
            file_name = os.path.basename(crx_path)
            local_crx_path = os.path.join(ext_dir, file_name)
            try:
                import shutil
                shutil.copy2(crx_path, local_crx_path)
            except Exception as e:
                return False, f"复制CRX文件失败: {str(e)}"
        
        # 保存图标
        local_icon_path = None
        if icon_path:
            # 首先检查图标文件是否存在
            if not os.path.exists(icon_path):
                print(f"警告: 图标文件不存在: {icon_path}")
                # 不返回错误，继续添加扩展，但不设置图标
            else:
                icon_filename = f"{ext_id}_icon.png"
                local_icon_path = os.path.join(ext_dir, icon_filename)
                
                # 添加重试机制
                max_retries = 5  # 增加重试次数
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        # 先尝试清理旧文件
                        try:
                            if os.path.exists(local_icon_path):
                                import time
                                # 等待一小段时间，让其他进程释放文件
                                time.sleep(0.5)  # 增加等待时间
                                os.remove(local_icon_path)
                                # 再等待一小段时间，确保文件被完全删除
                                time.sleep(0.5)  # 增加等待时间
                        except Exception as e:
                            print(f"清理旧图标文件失败: {str(e)}")
                            # 继续尝试复制，可能会覆盖
                        
                        # 复制新文件
                        import shutil
                        shutil.copy2(icon_path, local_icon_path)
                        
                        # 验证文件是否成功复制
                        if os.path.exists(local_icon_path):
                            print(f"成功复制图标文件到: {local_icon_path}")
                            break
                        else:
                            raise Exception("文件复制后不存在")
                            
                    except FileNotFoundError:
                        retry_count += 1
                        print(f"图标文件不存在，重试 {retry_count}/{max_retries}")
                        if retry_count == max_retries:
                            print(f"无法找到图标文件: {icon_path}")
                            # 不返回错误，继续添加扩展，但不设置图标
                            local_icon_path = None
                            break
                        import time
                        time.sleep(1)  # 增加等待时间
                        
                    except PermissionError:
                        retry_count += 1
                        print(f"文件访问被拒绝，重试 {retry_count}/{max_retries}")
                        if retry_count == max_retries:
                            print("复制图标文件失败: 文件访问被拒绝，请确保没有其他程序正在使用该文件")
                            # 不返回错误，继续添加扩展，但不设置图标
                            local_icon_path = None
                            break
                        import time
                        time.sleep(2)  # 增加等待时间到2秒
                        
                    except Exception as e:
                        retry_count += 1
                        print(f"复制图标文件时出错: {str(e)}，重试 {retry_count}/{max_retries}")
                        if retry_count == max_retries:
                            print(f"复制图标文件失败: {str(e)}")
                            # 不返回错误，继续添加扩展，但不设置图标
                            local_icon_path = None
                            break
                        import time
                        time.sleep(2)  # 增加等待时间到2秒
        
        # 创建扩展对象
        extension = {
            "name": name,
            "id": ext_id,
            "description": description,
            "icon": local_icon_path,
            "crx_path": local_crx_path
        }
        
        try:
            # 先尝试保存配置
            self.extensions_library.append(extension)
            self.save_extensions()
            return True, "扩展添加成功"
        except Exception as e:
            # 如果保存失败，清理已创建的文件
            try:
                if local_icon_path and os.path.exists(local_icon_path):
                    os.remove(local_icon_path)
                if local_crx_path and os.path.exists(local_crx_path):
                    os.remove(local_crx_path)
                if os.path.exists(ext_dir) and not os.listdir(ext_dir):
                    os.rmdir(ext_dir)
            except:
                pass
            
            # 从库中移除
            if extension in self.extensions_library:
                self.extensions_library.remove(extension)
            
            return False, f"保存配置失败: {str(e)}"
    
    def remove_extension(self, ext_id):
        """
        从库中删除扩展
        
        Args:
            ext_id: 扩展ID
        
        Returns:
            bool: 删除是否成功
        """
        for i, ext in enumerate(self.extensions_library):
            if ext.get('id') == ext_id:
                # 删除扩展文件
                ext_dir = os.path.join(self.extensions_dir, ext_id)
                if os.path.exists(ext_dir):
                    try:
                        shutil.rmtree(ext_dir)
                    except Exception as e:
                        print(f"删除扩展目录失败: {str(e)}")
                
                # 从库中移除
                self.extensions_library.pop(i)
                self.save_extensions()
                return True
        
        return False
    
    def save_extensions(self):
        """保存扩展库到配置"""
        config = self.config_manager.load_config()
        config['extensions'] = self.extensions_library
        self.config_manager.save_config(config)
    
    def get_extension(self, ext_id):
        """
        获取指定ID的扩展信息
        
        Args:
            ext_id: 扩展ID
        
        Returns:
            dict: 扩展信息
        """
        for ext in self.extensions_library:
            if ext.get('id') == ext_id:
                return ext
        return None
    
    def get_all_extensions(self):
        """获取所有扩展"""
        return self.extensions_library
    
    def install_extension_to_instances(self, extension_id, instance_names):
        """
        安装扩展到指定的浏览器实例
        
        Args:
            extension_id: 扩展ID
            instance_names: 实例名称列表
        
        Returns:
            dict: 安装结果，格式为 {实例名: (成功与否, 消息)}
        """
        results = {}
        extension = self.get_extension(extension_id)
        
        if not extension:
            return {name: (False, "扩展不存在") for name in instance_names}
        
        # 获取所有Chrome实例
        config = self.config_manager.load_config()
        instances = []
        for shortcut in config.get('shortcuts', []):
            if shortcut.get('name') in instance_names:
                instances.append(shortcut)
        
        for instance in instances:
            instance_name = instance.get('name')
            data_dir = instance.get('data_dir')
            
            # 记录实例已安装的扩展
            if 'installed_extensions' not in instance:
                instance['installed_extensions'] = []
            
            # 检查是否已经安装
            if extension_id in instance.get('installed_extensions', []):
                results[instance_name] = (False, "扩展已安装")
                continue
            
            # 根据扩展类型执行安装
            success = False
            message = ""
            
            try:
                chrome_path = config.get('chrome_path')
                
                if extension.get('crx_path') and os.path.exists(extension.get('crx_path')):
                    # 使用本地CRX文件安装
                    success, message = self._install_crx_extension(
                        chrome_path, data_dir, extension.get('crx_path'), instance_name
                    )
                else:
                    # 从Chrome商店安装
                    success, message = self._install_from_store(
                        chrome_path, data_dir, extension_id, instance_name
                    )
                
                if success:
                    # 更新实例的已安装扩展列表
                    if 'installed_extensions' not in instance:
                        instance['installed_extensions'] = []
                    instance['installed_extensions'].append(extension_id)
                    
                    # 保存配置
                    self.config_manager.save_config(config)
            
            except Exception as e:
                success = False
                message = f"安装时出错: {str(e)}"
            
            results[instance_name] = (success, message)
        
        return results
    
    def _install_crx_extension(self, chrome_path, user_data_dir, crx_path, instance_name):
        """
        使用CRX文件安装扩展
        
        Args:
            chrome_path: Chrome可执行文件路径
            user_data_dir: 用户数据目录
            crx_path: CRX文件路径
            instance_name: 实例名称
        
        Returns:
            tuple: (成功与否, 消息)
        """
        if not os.path.exists(crx_path):
            return False, "CRX文件不存在"
        
        try:
            cmd = [
                chrome_path,
                f'--user-data-dir={user_data_dir}',
                f'--load-extension={crx_path}'
            ]
            subprocess.Popen(cmd)
            return True, f"已启动 {instance_name} 并尝试安装扩展"
        except Exception as e:
            return False, f"安装失败: {str(e)}"
    
    def _install_from_store(self, chrome_path, user_data_dir, extension_id, instance_name):
        """
        从Chrome商店安装扩展
        
        Args:
            chrome_path: Chrome可执行文件路径
            user_data_dir: 用户数据目录
            extension_id: 扩展ID
            instance_name: 实例名称
        
        Returns:
            tuple: (成功与否, 消息)
        """
        try:
            # 使用Chrome商店URL
            install_url = f"https://chrome.google.com/webstore/detail/{extension_id}"
            
            # 构建命令 - 简化参数，只保留必要的参数
            cmd = [
                chrome_path,
                f'--user-data-dir={user_data_dir}',  # 路径中有空格时subprocess会自动处理
                install_url
            ]
            
            # 启动进程
            subprocess.Popen(cmd)
            return True, f"已启动 {instance_name} 并打开扩展安装页面，请在浏览器中点击'添加至Chrome'按钮完成安装"
        except Exception as e:
            return False, f"安装失败: {str(e)}"
    
    def get_installed_extensions(self, instance_name):
        """
        获取实例已安装的扩展
        
        Args:
            instance_name: 实例名称
        
        Returns:
            list: 已安装的扩展ID列表
        """
        config = self.config_manager.load_config()
        for shortcut in config.get('shortcuts', []):
            if shortcut.get('name') == instance_name:
                return shortcut.get('installed_extensions', [])
        return []
    
    def search_extensions(self, keyword):
        """
        搜索Chrome商店中的扩展 - 公共接口
        
        此方法是一个公共接口，可以同步调用或通过ExtensionSearchWorker异步调用
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 搜索结果列表
        """
        # 直接调用实现方法
        return self.search_extensions_impl(keyword)
    
    def search_extensions_impl(self, keyword, progress_callback=None):
        """
        搜索Chrome商店中的扩展 - 实现方法
        
        此方法包含实际的搜索逻辑，可以被search_extensions直接调用，
        也可以被ExtensionSearchWorker在后台线程中调用
        
        Args:
            keyword: 搜索关键词
            progress_callback: 进度回调函数，用于报告进度
            
        Returns:
            list: 搜索结果列表
        """
        try:
            if progress_callback:
                progress_callback.emit(f"使用Playwright搜索关键词: {keyword}")
            else:
                print(f"使用Playwright搜索关键词: {keyword}")
            
            # 导入Playwright相关库
            from playwright.sync_api import sync_playwright
            import time
            
            # 使用Playwright
            with sync_playwright() as p:
                # 启动浏览器（无头模式）
                if progress_callback:
                    progress_callback.emit("正在启动浏览器...")
                else:
                    print("正在启动浏览器...")
                    
                browser = p.chromium.launch(headless=True)
                
                try:
                    # 创建新页面
                    page = browser.new_page()
                    
                    # 设置用户代理
                    page.set_extra_http_headers({
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    })
                    
                    # 访问Chrome商店搜索页面 - 更新URL格式
                    search_url = f"https://chromewebstore.google.com/search/{keyword}?hl=zh-CN"
                    if progress_callback:
                        progress_callback.emit(f"访问URL: {search_url}")
                    else:
                        print(f"访问URL: {search_url}")
                        
                    page.goto(search_url)
                    
                    # 等待页面加载 - 增加等待时间
                    if progress_callback:
                        progress_callback.emit("等待页面加载...")
                    else:
                        print("等待页面加载...")
                        
                    page.wait_for_load_state("networkidle")
                    
                    # 额外等待时间，确保动态内容加载完成
                    if progress_callback:
                        progress_callback.emit("额外等待5秒...")
                    else:
                        print("额外等待5秒...")
                        
                    time.sleep(5)  # 增加等待时间
                    
                    # 等待扩展卡片元素出现
                    if progress_callback:
                        progress_callback.emit("等待扩展卡片元素出现...")
                    else:
                        print("等待扩展卡片元素出现...")
                        
                    try:
                        # 尝试多种选择器
                        selectors = [
                            "div.QAB7uc div.Cb7Kte",  # 主选择器
                            "div.Cb7Kte",             # 备用选择器1
                            "div[role='main'] div[role='article']",  # 备用选择器2
                            "c-wiz div[role='article']",  # 备用选择器3
                            "div.R6nElb"              # 备用选择器4
                        ]
                        
                        extension_cards = None
                        used_selector = None
                        
                        # 尝试每个选择器
                        for selector in selectors:
                            if progress_callback:
                                progress_callback.emit(f"尝试选择器: {selector}")
                            else:
                                print(f"尝试选择器: {selector}")
                                
                            try:
                                # 等待选择器出现
                                page.wait_for_selector(selector, timeout=3000)
                                # 获取元素
                                cards = page.query_selector_all(selector)
                                if cards and len(cards) > 0:
                                    extension_cards = cards
                                    used_selector = selector
                                    if progress_callback:
                                        progress_callback.emit(f"成功使用选择器: {selector}, 找到 {len(cards)} 个元素")
                                    else:
                                        print(f"成功使用选择器: {selector}, 找到 {len(cards)} 个元素")
                                    break
                            except Exception as selector_error:
                                if progress_callback:
                                    progress_callback.emit(f"选择器 {selector} 失败: {str(selector_error)}")
                                else:
                                    print(f"选择器 {selector} 失败: {str(selector_error)}")
                                continue
                        
                        if not extension_cards or len(extension_cards) == 0:
                            if progress_callback:
                                progress_callback.emit("未找到扩展卡片，尝试保存调试信息...")
                            else:
                                print("未找到扩展卡片，尝试保存调试信息...")
                            
                            # 保存页面源码
                            debug_file = os.path.join(os.path.dirname(self.config_manager.config_file), "chrome_store_page_source.html")
                            with open(debug_file, 'w', encoding='utf-8') as f:
                                f.write(page.content())
                            if progress_callback:
                                progress_callback.emit(f"已保存页面源码到: {debug_file}")
                            else:
                                print(f"已保存页面源码到: {debug_file}")
                            
                            # 保存截图
                            screenshot_file = os.path.join(os.path.dirname(self.config_manager.config_file), "chrome_store_screenshot.png")
                            page.screenshot(path=screenshot_file)
                            if progress_callback:
                                progress_callback.emit(f"已保存页面截图到: {screenshot_file}")
                            else:
                                print(f"已保存页面截图到: {screenshot_file}")
                            
                            # 尝试直接打开浏览器
                            if progress_callback:
                                progress_callback.emit("无法爬取扩展信息，将直接打开Chrome商店")
                            else:
                                print("无法爬取扩展信息，将直接打开Chrome商店")
                            return self._open_chrome_store_in_browser(keyword)
                        
                        # 限制只处理前8个结果
                        extension_cards = extension_cards[:8]
                        if progress_callback:
                            progress_callback.emit(f"找到 {len(extension_cards)} 个扩展卡片")
                        else:
                            print(f"找到 {len(extension_cards)} 个扩展卡片")
                        
                        # 提取扩展信息
                        extensions = []
                        for i, card in enumerate(extension_cards):
                            if progress_callback:
                                progress_callback.emit(f"正在处理第 {i+1}/{len(extension_cards)} 个扩展...")
                            
                            try:
                                # 根据使用的选择器调整提取逻辑
                                if used_selector == "div.QAB7uc div.Cb7Kte" or used_selector == "div.Cb7Kte":
                                    # 提取扩展ID - 从data-item-id属性
                                    ext_id = card.get_attribute("data-item-id")
                                    if not ext_id:
                                        print("无法获取扩展ID")
                                        continue
                                    
                                    # 提取链接
                                    link_element = card.query_selector("a.q6LNgd")
                                    href = link_element.get_attribute("href") if link_element else None
                                    
                                    # 提取扩展名称
                                    name_element = card.query_selector("h2.CiI2if")
                                    name = name_element.inner_text() if name_element else "未知扩展"
                                    
                                    # 提取描述
                                    desc_element = card.query_selector("p.g3IrHd")
                                    description = desc_element.inner_text() if desc_element else "无描述"
                                    
                                    # 提取发布者信息
                                    publisher_element = card.query_selector("span.cJI8ee")
                                    publisher = publisher_element.inner_text() if publisher_element else "未知发布者"
                                    
                                    # 提取评分
                                    rating_element = card.query_selector("span.Vq0ZA")
                                    rating = rating_element.inner_text() if rating_element else "0.0"
                                    
                                    # 提取评分数量
                                    rating_count_element = card.query_selector("span.Y30PE")
                                    rating_count = rating_count_element.inner_text() if rating_count_element else "(0)"
                                    # 去除括号
                                    rating_count = rating_count.strip("()")
                                else:
                                    # 备用提取逻辑 - 适用于其他选择器
                                    # 提取链接和ID
                                    link_element = card.query_selector("a[href*='/detail/']")
                                    if not link_element:
                                        link_element = card.query_selector("a")
                                    
                                    ext_id = None
                                    href = None
                                    if link_element:
                                        href = link_element.get_attribute("href")
                                        if href and '/detail/' in href:
                                            ext_id = href.split("/detail/")[1].split("?")[0]
                                    
                                    if not ext_id:
                                        print("无法获取扩展ID")
                                        continue
                                    
                                    # 提取名称
                                    name_element = card.query_selector("h2") or card.query_selector("div[role='heading']")
                                    name = name_element.inner_text() if name_element else "未知扩展"
                                    
                                    # 提取描述
                                    desc_selectors = [
                                        "div[role='article'] > div > div:nth-child(2)",
                                        "div[role='article'] div:nth-child(2)",
                                        "p"
                                    ]
                                    
                                    description = "无描述"
                                    for desc_selector in desc_selectors:
                                        desc_element = card.query_selector(desc_selector)
                                        if desc_element:
                                            text = desc_element.inner_text()
                                            if text and len(text) > 5:
                                                description = text
                                                break
                                    
                                    # 提取发布者
                                    publisher_selectors = [
                                        "span",
                                        "div[role='article'] span"
                                    ]
                                    
                                    publisher = "未知发布者"
                                    for pub_selector in publisher_selectors:
                                        pub_element = card.query_selector(pub_selector)
                                        if pub_element:
                                            text = pub_element.inner_text()
                                            if text and len(text) > 2:
                                                publisher = text
                                                break
                                    
                                    # 提取评分
                                    rating_selectors = [
                                        "div[aria-label*='星']",
                                        "div[aria-label*='rating']"
                                    ]
                                    
                                    rating = "0.0"
                                    for rating_selector in rating_selectors:
                                        rating_element = card.query_selector(rating_selector)
                                        if rating_element:
                                            rating_text = rating_element.get_attribute("aria-label")
                                            if rating_text:
                                                import re
                                                rating_match = re.search(r'(\d+(\.\d+)?)', rating_text)
                                                if rating_match:
                                                    rating = rating_match.group(1)
                                                break
                                    
                                    # 评分数量
                                    rating_count = "0"
                                
                                # 提取图标URL
                                icon_element = card.query_selector("img")
                                icon_url = None
                                if icon_element:
                                    # 尝试获取srcset属性，它通常包含更高质量的图像
                                    srcset = icon_element.get_attribute("srcset")
                                    if srcset:
                                        # 从srcset中提取第一个URL
                                        icon_url = srcset.split(" ")[0]
                                    else:
                                        # 如果没有srcset，使用src
                                        icon_url = icon_element.get_attribute("src")
                                
                                # 下载图标
                                icon_path = None
                                if icon_url and ext_id:
                                    try:
                                        # 创建扩展目录
                                        ext_dir = os.path.join(self.extensions_dir, ext_id)
                                        os.makedirs(ext_dir, exist_ok=True)
                                        
                                        # 下载图标
                                        icon_response = requests.get(icon_url)
                                        if icon_response.status_code == 200:
                                            icon_path = os.path.join(ext_dir, f"{ext_id}_icon.png")
                                            with open(icon_path, 'wb') as f:
                                                f.write(icon_response.content)
                                    except Exception as e:
                                        print(f"下载图标失败: {str(e)}")
                                
                                # 创建扩展对象
                                extension = {
                                    "name": name,
                                    "id": ext_id,
                                    "description": description,
                                    "publisher": publisher,
                                    "rating": rating,
                                    "rating_count": rating_count,
                                    "icon": icon_path,
                                    "from_search": True
                                }
                                
                                extensions.append(extension)
                                
                            except Exception as ext_error:
                                print(f"处理扩展卡片时出错: {str(ext_error)}")
                                import traceback
                                traceback.print_exc()
                        
                        if progress_callback:
                            progress_callback.emit(f"成功获取 {len(extensions)} 个扩展信息")
                        else:
                            print(f"成功获取 {len(extensions)} 个扩展信息")
                            
                        return extensions
                    
                    except Exception as e:
                        if progress_callback:
                            progress_callback.emit(f"等待扩展卡片元素出现时出错: {str(e)}")
                        else:
                            print(f"等待扩展卡片元素出现时出错: {str(e)}")
                            
                        # 保存页面源码用于调试
                        debug_file = os.path.join(os.path.dirname(self.config_manager.config_file), "chrome_store_page_source.html")
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(page.content())
                        if progress_callback:
                            progress_callback.emit(f"已保存页面源码到: {debug_file}")
                        else:
                            print(f"已保存页面源码到: {debug_file}")
                        
                        # 尝试截图
                        try:
                            screenshot_file = os.path.join(os.path.dirname(self.config_manager.config_file), "chrome_store_screenshot.png")
                            page.screenshot(path=screenshot_file)
                            if progress_callback:
                                progress_callback.emit(f"已保存页面截图到: {screenshot_file}")
                            else:
                                print(f"已保存页面截图到: {screenshot_file}")
                        except Exception as screenshot_error:
                            print(f"保存截图失败: {str(screenshot_error)}")
                        
                        # 直接打开浏览器
                        return self._open_chrome_store_in_browser(keyword)
                
                finally:
                    # 关闭浏览器
                    browser.close()
                    if progress_callback:
                        progress_callback.emit("浏览器已关闭")
                    else:
                        print("浏览器已关闭")
        
        except Exception as e:
            if progress_callback:
                progress_callback.emit(f"搜索扩展时出错: {str(e)}")
            else:
                print(f"搜索扩展时出错: {str(e)}")
                import traceback
                traceback.print_exc()
            # 直接打开浏览器
            return self._open_chrome_store_in_browser(keyword)
    
    def _open_chrome_store_in_browser(self, keyword):
        """
        在用户浏览器中直接打开Chrome商店
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 空列表，表示需要用户手动操作
        """
        try:
            # 获取Chrome路径
            config = self.config_manager.load_config()
            chrome_path = config.get('chrome_path')
            
            if not chrome_path or not os.path.exists(chrome_path):
                print("Chrome路径无效，无法打开浏览器")
                return []
            
            # 构建URL
            search_url = f"https://chromewebstore.google.com/search/{keyword}?hl=zh-CN&utm_source=ext_sidebar"
            
            # 打开浏览器
            subprocess.Popen([chrome_path, search_url])
            print(f"已在浏览器中打开Chrome商店: {search_url}")
            
            # 返回空列表，表示需要用户手动操作
            return [{
                "name": "请在浏览器中选择扩展",
                "id": "manual_selection",
                "description": "已在浏览器中打开Chrome商店，请手动选择并安装扩展。",
                "icon": None,
                "crx_path": None,
                "from_search": True,
                "is_manual_prompt": True
            }]
            
        except Exception as e:
            print(f"打开浏览器失败: {str(e)}")
            return [] 