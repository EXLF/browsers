from typing import Dict, Any, List, Optional
import logging
from playwright.sync_api import sync_playwright, Page, Browser, Playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionEngine:
    def __init__(self):
        """初始化执行引擎，启动浏览器"""
        logger.info("初始化执行引擎...")
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._init_browser()
        logger.info("执行引擎初始化完成")
    
    def _init_browser(self):
        """初始化浏览器"""
        try:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=False,  # 调试时设为False以查看浏览器操作
            )
            self._page = self._browser.new_page()
            logger.info("浏览器初始化成功")
        except Exception as e:
            logger.error(f"浏览器初始化失败: {str(e)}")
            self.close()
            raise
    
    def navigate(self, url: str) -> bool:
        """导航到指定URL
        
        Args:
            url: 目标URL
            
        Returns:
            bool: 导航是否成功
        """
        try:
            self._page.goto(url)
            self._page.wait_for_load_state("networkidle")
            logger.info(f"成功导航到: {url}")
            return True
        except Exception as e:
            logger.error(f"导航失败: {str(e)}")
            return False
    
    def click(self, selector: str) -> bool:
        """点击指定元素
        
        Args:
            selector: 元素选择器
            
        Returns:
            bool: 点击是否成功
        """
        try:
            self._page.click(selector)
            logger.info(f"成功点击元素: {selector}")
            return True
        except Exception as e:
            logger.error(f"点击失败: {str(e)}")
            return False
    
    def get_text(self, selector: str) -> Optional[str]:
        """获取指定元素的文本内容
        
        Args:
            selector: 元素选择器
            
        Returns:
            Optional[str]: 元素文本内容，失败返回None
        """
        try:
            element = self._page.query_selector(selector)
            if element:
                text = element.text_content()
                logger.info(f"成功获取文本: {text[:50]}...")
                return text
            else:
                logger.warning(f"未找到元素: {selector}")
                return None
        except Exception as e:
            logger.error(f"获取文本失败: {str(e)}")
            return None
    
    def execute_action(self, action: Dict[str, Any]) -> Any:
        """执行单个操作
        
        Args:
            action: 操作描述字典
            
        Returns:
            Any: 操作结果
        """
        action_type = action.get("type")
        if not action_type:
            logger.error("操作类型未指定")
            return None
            
        try:
            if action_type == "click":
                return self.click(action["target"])
            elif action_type == "get_text":
                return self.get_text(action["target"])
            elif action_type == "wait":
                self._page.wait_for_timeout(action["time"])
                return True
            else:
                logger.error(f"未知的操作类型: {action_type}")
                return None
        except Exception as e:
            logger.error(f"执行操作失败: {str(e)}")
            return None
    
    def execute_actions(self, actions: List[Dict[str, Any]]) -> List[Any]:
        """执行一系列操作
        
        Args:
            actions: 操作列表
            
        Returns:
            List[Any]: 操作结果列表
        """
        results = []
        for action in actions:
            result = self.execute_action(action)
            results.append(result)
            if result is None:  # 如果某个操作失败，停止执行
                break
        return results
    
    def close(self):
        """关闭浏览器和Playwright"""
        try:
            if self._page:
                self._page.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
            logger.info("执行引擎已关闭")
        except Exception as e:
            logger.error(f"关闭执行引擎失败: {str(e)}") 