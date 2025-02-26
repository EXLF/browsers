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
        
        # 如果有CRX文件，复制到扩展目录
        local_crx_path = None
        if crx_path and os.path.exists(crx_path):
            # 创建扩展专用目录
            ext_dir = os.path.join(self.extensions_dir, ext_id)
            os.makedirs(ext_dir, exist_ok=True)
            
            # 复制CRX文件
            file_name = os.path.basename(crx_path)
            local_crx_path = os.path.join(ext_dir, file_name)
            try:
                shutil.copy2(crx_path, local_crx_path)
            except Exception as e:
                return False, f"复制CRX文件失败: {str(e)}"
        
        # 保存图标
        local_icon_path = None
        if icon_path and os.path.exists(icon_path):
            ext_dir = os.path.join(self.extensions_dir, ext_id)
            os.makedirs(ext_dir, exist_ok=True)
            
            icon_filename = os.path.basename(icon_path)
            local_icon_path = os.path.join(ext_dir, icon_filename)
            try:
                shutil.copy2(icon_path, local_icon_path)
            except Exception as e:
                return False, f"复制图标文件失败: {str(e)}"
        
        # 创建扩展对象
        extension = {
            "name": name,
            "id": ext_id,
            "description": description,
            "icon": local_icon_path,
            "crx_path": local_crx_path
        }
        
        # 添加到库中
        self.extensions_library.append(extension)
        
        # 保存更新
        self.save_extensions()
        
        return True, "扩展添加成功"
    
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
        搜索Chrome商店中的扩展
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 搜索结果列表
        """
        try:
            print(f"使用Playwright搜索关键词: {keyword}")
            
            # 导入Playwright相关库
            from playwright.sync_api import sync_playwright
            import time
            
            # 使用Playwright
            with sync_playwright() as p:
                # 启动浏览器（无头模式）
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
                    search_url = f"https://chromewebstore.google.com/search/{keyword}?hl=zh-CN&utm_source=ext_sidebar"
                    print(f"访问URL: {search_url}")
                    page.goto(search_url)
                    
                    # 等待页面加载 - 增加等待时间
                    print("等待页面加载...")
                    page.wait_for_load_state("networkidle")
                    
                    # 额外等待时间，确保动态内容加载完成
                    print("额外等待2秒...")
                    time.sleep(2)
                    
                    # 等待扩展卡片元素出现
                    print("等待扩展卡片元素出现...")
                    try:
                        # 尝试多种选择器
                        selectors = [
                            "c-wiz div[role='article']",
                            "div[role='main'] div[role='article']",
                            "div[jscontroller] div[role='article']",
                            "div.Xgn82e",  # 可能的类名
                            "div.VfPpkd-WsjYwc"  # 可能的类名
                        ]
                        
                        extension_cards = None
                        used_selector = None
                        
                        # 尝试每个选择器
                        for selector in selectors:
                            print(f"尝试选择器: {selector}")
                            try:
                                # 等待选择器出现
                                page.wait_for_selector(selector, timeout=5000)
                                # 获取元素
                                cards = page.query_selector_all(selector)
                                if cards and len(cards) > 0:
                                    extension_cards = cards
                                    used_selector = selector
                                    print(f"成功使用选择器: {selector}, 找到 {len(cards)} 个元素")
                                    break
                            except Exception as selector_error:
                                print(f"选择器 {selector} 失败: {str(selector_error)}")
                                continue
                        
                        # 如果所有选择器都失败，尝试截图和保存源码
                        if not extension_cards:
                            print("所有选择器都失败，保存调试信息...")
                            
                            # 保存页面源码
                            debug_file = os.path.join(os.path.dirname(self.config_manager.config_file), "chrome_store_page_source.html")
                            with open(debug_file, 'w', encoding='utf-8') as f:
                                f.write(page.content())
                            print(f"已保存页面源码到: {debug_file}")
                            
                            # 保存截图
                            screenshot_file = os.path.join(os.path.dirname(self.config_manager.config_file), "chrome_store_screenshot.png")
                            page.screenshot(path=screenshot_file)
                            print(f"已保存页面截图到: {screenshot_file}")
                            
                            # 尝试直接打开浏览器
                            print("无法爬取扩展信息，将直接打开Chrome商店")
                            return self._open_chrome_store_in_browser(keyword)
                        
                        # 限制只处理前5个结果
                        extension_cards = extension_cards[:5]
                        print(f"找到 {len(extension_cards)} 个扩展卡片")
                        
                        # 提取扩展信息
                        extensions = []
                        for card in extension_cards:
                            try:
                                # 提取扩展ID
                                link_element = card.query_selector("a[href*='/detail/']")
                                if not link_element:
                                    print("无法找到链接元素，尝试其他选择器")
                                    link_element = card.query_selector("a")
                                
                                if link_element:
                                    href = link_element.get_attribute("href")
                                    if '/detail/' in href:
                                        ext_id = href.split("/detail/")[1].split("?")[0]
                                    else:
                                        print(f"链接不包含detail部分: {href}")
                                        continue
                                else:
                                    print("无法找到任何链接元素")
                                    continue
                                
                                # 提取扩展名称
                                name_element = card.query_selector("h2")
                                if not name_element:
                                    print("无法找到名称元素，尝试其他选择器")
                                    name_element = card.query_selector("div[role='heading']")
                                
                                name = name_element.inner_text() if name_element else "未知扩展"
                                
                                # 提取扩展描述
                                try:
                                    desc_selectors = [
                                        "div[role='article'] > div > div:nth-child(2) > div:nth-child(2)",
                                        "div[role='article'] div[jsname]",
                                        "div[role='article'] div:nth-child(2)"
                                    ]
                                    
                                    description = "暂无描述"
                                    for desc_selector in desc_selectors:
                                        desc_element = card.query_selector(desc_selector)
                                        if desc_element:
                                            description = desc_element.inner_text()
                                            if description and len(description) > 5:  # 确保描述有意义
                                                break
                                except:
                                    description = "暂无描述"
                                
                                # 提取发布者信息
                                try:
                                    publisher_selectors = [
                                        "div[role='article'] > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2)",
                                        "div[role='article'] div[jsname]:nth-child(1)",
                                        "div[role='article'] span"
                                    ]
                                    
                                    publisher = "未知发布者"
                                    for pub_selector in publisher_selectors:
                                        pub_element = card.query_selector(pub_selector)
                                        if pub_element:
                                            publisher = pub_element.inner_text()
                                            if publisher and len(publisher) > 2:  # 确保发布者有意义
                                                break
                                except:
                                    publisher = "未知发布者"
                                
                                # 提取评分信息
                                try:
                                    rating_selectors = [
                                        "div[aria-label*='评分']",
                                        "div[aria-label*='rating']",
                                        "div[jsname] div[aria-label]"
                                    ]
                                    
                                    rating_value = 0
                                    rating_count = 0
                                    
                                    for rating_selector in rating_selectors:
                                        rating_element = card.query_selector(rating_selector)
                                        if rating_element:
                                            rating_text = rating_element.get_attribute("aria-label")
                                            if rating_text:
                                                if "评分：" in rating_text:
                                                    rating_value = float(rating_text.split("评分：")[1].split("（共")[0].strip())
                                                    rating_count = int(rating_text.split("（共")[1].split("条评价）")[0].strip())
                                                elif "rating" in rating_text.lower():
                                                    # 英文格式
                                                    parts = rating_text.lower().split("rating")
                                                    if len(parts) > 1:
                                                        try:
                                                            rating_value = float(parts[0].strip())
                                                            if "reviews" in rating_text.lower():
                                                                count_part = rating_text.lower().split("reviews")[0]
                                                                count_part = count_part.split("rating")[1]
                                                                rating_count = int(''.join(filter(str.isdigit, count_part)))
                                                        except:
                                                            pass
                                                break
                                except:
                                    rating_value = 0
                                    rating_count = 0
                                
                                # 提取图标URL
                                try:
                                    icon_element = card.query_selector("img")
                                    icon_url = icon_element.get_attribute("src") if icon_element else None
                                except:
                                    icon_url = None
                                
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
                                    "icon": icon_path,
                                    "crx_path": None,
                                    "from_search": True,  # 标记为搜索结果
                                    "rating": rating_value,
                                    "rating_count": rating_count,
                                    "publisher": publisher
                                }
                                extensions.append(extension)
                                print(f"添加扩展到结果列表: {name}")
                            
                            except Exception as e:
                                print(f"处理扩展卡片时出错: {str(e)}")
                        
                        print(f"共找到 {len(extensions)} 个扩展")
                        if len(extensions) > 0:
                            return extensions
                        else:
                            # 如果没有找到任何扩展，直接打开浏览器
                            return self._open_chrome_store_in_browser(keyword)
                    
                    except Exception as e:
                        print(f"等待扩展卡片元素出现时出错: {str(e)}")
                        # 保存页面源码用于调试
                        debug_file = os.path.join(os.path.dirname(self.config_manager.config_file), "chrome_store_page_source.html")
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(page.content())
                        print(f"已保存页面源码到: {debug_file}")
                        
                        # 尝试截图
                        try:
                            screenshot_file = os.path.join(os.path.dirname(self.config_manager.config_file), "chrome_store_screenshot.png")
                            page.screenshot(path=screenshot_file)
                            print(f"已保存页面截图到: {screenshot_file}")
                        except Exception as screenshot_error:
                            print(f"保存截图失败: {str(screenshot_error)}")
                        
                        # 直接打开浏览器
                        return self._open_chrome_store_in_browser(keyword)
                
                finally:
                    # 关闭浏览器
                    browser.close()
                    print("浏览器已关闭")
        
        except Exception as e:
            print(f"搜索扩展时出错: {str(e)}")
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