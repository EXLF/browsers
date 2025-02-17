from typing import List, Dict, Any, Optional
import logging
import json
import requests
from src.utils.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstructionParser:
    def __init__(self):
        """初始化指令解析器"""
        logger.info("初始化指令解析器...")
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = "https://api.deepseek.com/chat/completions"
        
        # 定义操作模板
        self.action_templates = {
            "click": {
                "type": "click",
                "target": None  # 将由解析结果填充
            },
            "get_text": {
                "type": "get_text",
                "target": None
            },
            "wait": {
                "type": "wait",
                "time": 1000  # 默认等待时间
            }
        }
        
        # 定义提示模板
        self.prompt_template = """请将以下自然语言指令转换为Web操作序列。

规则：
1. 只返回JSON格式的操作序列，不要包含任何其他文字说明
2. 返回的JSON必须是一个数组，包含按顺序执行的操作
3. 每个操作必须包含type字段和对应的参数

可用的操作类型：
1. 点击元素：{{"type": "click", "target": "CSS选择器"}}
2. 获取文本：{{"type": "get_text", "target": "CSS选择器"}}
3. 等待操作：{{"type": "wait", "time": 1000}}

页面元素映射：
- 按钮1 -> button[data-button='1']
- 按钮2 -> button[data-button='2']
- 按钮3 -> button[data-button='3']
- 页面1内容 -> #page1-content
- 页面2内容 -> #page2-content
- 页面3内容 -> #page3-content

用户指令：{instruction}

请直接返回JSON数组，例如：
[
    {{"type": "click", "target": "button[data-button='1']"}},
    {{"type": "wait", "time": 1000}},
    {{"type": "get_text", "target": "#page1-content"}}
]"""
        
        logger.info("指令解析器初始化完成")
    
    def parse(self, instruction: str) -> Optional[List[Dict[str, Any]]]:
        """解析自然语言指令为操作序列
        
        Args:
            instruction: 用户输入的自然语言指令
            
        Returns:
            Optional[List[Dict[str, Any]]]: 解析后的操作序列，解析失败返回None
        """
        try:
            # 构建完整的提示
            prompt = self.prompt_template.format(instruction=instruction)
            
            # 准备请求数据
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个Web自动化指令解析器，负责将自然语言指令转换为具体的操作序列。请只返回JSON格式的操作序列，不要返回其他解释性文字。"},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
            
            logger.info(f"发送请求到 DeepSeek API: {self.api_url}")
            logger.info(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 发送请求
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            # 解析响应
            try:
                response_data = response.json()
                logger.info(f"API 响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                
                content = response_data["choices"][0]["message"]["content"].strip()
                logger.info(f"解析到的内容: {content}")
                
                # 如果内容已经是一个JSON数组，直接解析
                if content.startswith("[") and content.endswith("]"):
                    actions = json.loads(content)
                else:
                    # 尝试从内容中提取JSON数组
                    start = content.find("[")
                    end = content.rfind("]") + 1
                    if start == -1 or end == 0:
                        raise ValueError("未找到有效的JSON数组")
                    
                    actions_json = content[start:end]
                    logger.info(f"提取的JSON部分: {actions_json}")
                    actions = json.loads(actions_json)
                
                logger.info(f"解析后的操作序列: {json.dumps(actions, ensure_ascii=False, indent=2)}")
                
                # 验证并补充操作序列
                if not self._validate_actions(actions):
                    return None
                
                logger.info(f"成功解析指令: {instruction}")
                return actions
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"指令解析失败: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response Status Code: {e.response.status_code}")
                logger.error(f"Response Text: {e.response.text}")
            return None
    
    def _validate_actions(self, actions: List[Dict[str, Any]]) -> bool:
        """验证操作序列是否有效
        
        Args:
            actions: 待验证的操作序列
            
        Returns:
            bool: 是否有效
        """
        try:
            if not actions:
                logger.error("操作序列为空")
                return False
                
            for action in actions:
                # 检查必需字段
                if "type" not in action:
                    logger.error("操作缺少type字段")
                    return False
                
                # 检查操作类型
                if action["type"] not in self.action_templates:
                    logger.error(f"未知的操作类型: {action['type']}")
                    return False
                
                # 检查目标选择器（除了wait操作）
                if action["type"] != "wait" and "target" not in action:
                    logger.error(f"{action['type']}操作缺少target字段")
                    return False
                
                # 检查wait操作的时间字段
                if action["type"] == "wait" and "time" not in action:
                    logger.error("wait操作缺少time字段")
                    return False
            
            # 检查操作序列的完整性
            for i in range(len(actions) - 1):
                current = actions[i]
                next_action = actions[i + 1]
                
                # 如果当前操作是点击，下一个操作应该是等待
                if current["type"] == "click" and next_action["type"] != "wait":
                    # 自动插入等待操作
                    actions.insert(i + 1, {"type": "wait", "time": 1000})
                    logger.info("自动插入等待操作")
            
            return True
            
        except Exception as e:
            logger.error(f"操作序列验证失败: {str(e)}")
            return False 