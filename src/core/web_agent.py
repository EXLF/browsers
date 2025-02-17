from typing import Dict, Any, List, Optional, Tuple
import logging
from .memory_system import MemorySystem
from .execution_engine import ExecutionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebAgent:
    def __init__(self):
        """初始化Web智能代理"""
        logger.info("初始化Web智能代理...")
        self.memory = MemorySystem()
        self.executor = ExecutionEngine()
        logger.info("Web智能代理初始化完成")
    
    def execute_with_memory(self, instruction: str, url: str = None) -> Tuple[bool, Optional[str]]:
        """执行指令，优先使用记忆中的操作序列
        
        Args:
            instruction: 用户指令
            url: 目标URL（如果需要导航）
            
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 执行结果)
        """
        try:
            # 如果提供了URL，先导航到目标页面
            if url:
                if not self.executor.navigate(url):
                    return False, "导航失败"
            
            # 从记忆中查找相似操作
            similar_ops = self.memory.find_similar_operations(instruction)
            
            if similar_ops:
                # 使用最相似的操作序列
                best_match = similar_ops[0]
                logger.info(f"找到相似操作，相似度: {best_match['similarity']}")
                
                # 执行操作序列
                results = self.executor.execute_actions(best_match["actions"])
                
                # 检查执行结果
                if None not in results:
                    logger.info("使用记忆中的操作序列执行成功")
                    # 如果最后一个操作是获取文本，返回文本内容
                    if best_match["actions"][-1]["type"] == "get_text":
                        return True, results[-1]
                    return True, "执行成功"
                else:
                    logger.warning("使用记忆中的操作序列执行失败")
            else:
                logger.info("未找到相似操作")
            
            return False, "未找到可用的操作序列"
            
        except Exception as e:
            logger.error(f"执行失败: {str(e)}")
            return False, f"执行出错: {str(e)}"
    
    def store_successful_execution(self, instruction: str, actions: List[Dict[str, Any]]) -> bool:
        """存储成功执行的操作序列
        
        Args:
            instruction: 用户指令
            actions: 执行的操作序列
            
        Returns:
            bool: 存储是否成功
        """
        try:
            return self.memory.store_operation(instruction, actions)
        except Exception as e:
            logger.error(f"存储操作失败: {str(e)}")
            return False
    
    def close(self):
        """关闭代理，释放资源"""
        try:
            self.executor.close()
            logger.info("Web智能代理已关闭")
        except Exception as e:
            logger.error(f"关闭代理失败: {str(e)}") 