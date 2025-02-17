import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.memory_system import MemorySystem

def main():
    print("开始测试记忆系统...")
    
    # 创建记忆系统实例
    memory = MemorySystem()
    
    # 测试数据
    instruction = "点击按钮1并获取文本"
    actions = [
        {"type": "click", "target": "button[data-button='1']"},
        {"type": "wait", "time": 1000},
        {"type": "get_text", "target": "#page1-content"}
    ]
    
    # 测试存储
    print("\n测试存储操作...")
    success = memory.store_operation(instruction, actions)
    print(f"存储结果: {'成功' if success else '失败'}")
    
    # 测试检索
    print("\n测试检索操作...")
    similar_ops = memory.find_similar_operations(instruction)
    print(f"找到 {len(similar_ops)} 个相似操作")
    
    if similar_ops:
        print("\n第一个匹配结果:")
        print(f"- 指令: {similar_ops[0]['instruction']}")
        print(f"- 相似度: {similar_ops[0]['similarity']}")
        print(f"- 操作: {similar_ops[0]['actions']}")
    
    # 测试相似指令
    print("\n测试相似指令...")
    similar_instruction = "帮我点击第一个按钮，然后读取内容"
    similar_ops = memory.find_similar_operations(similar_instruction)
    print(f"找到 {len(similar_ops)} 个相似操作")
    
    if similar_ops:
        print("\n最佳匹配:")
        print(f"- 原始指令: {similar_ops[0]['instruction']}")
        print(f"- 相似度: {similar_ops[0]['similarity']}")

if __name__ == "__main__":
    main() 