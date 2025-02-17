import pytest
from src.core.memory_system import MemorySystem

@pytest.fixture
def memory_system():
    """创建记忆系统实例"""
    system = MemorySystem()
    # 确保测试前清空记忆
    system.clear_memory()
    return system

def test_button1_operation(memory_system):
    """测试按钮1的操作记忆"""
    instruction = "点击按钮1并获取页面1的文本"
    actions = [
        {"type": "click", "target": "button[data-button='1']"},
        {"type": "wait", "time": 1000},  # 等待页面加载
        {"type": "get_text", "target": "#page1-content"}
    ]
    
    # 存储操作
    assert memory_system.store_operation(instruction, actions)
    
    # 测试完全相同的指令
    similar_ops = memory_system.find_similar_operations(instruction)
    assert len(similar_ops) > 0
    assert similar_ops[0]["actions"] == actions
    
    # 测试相似的指令
    similar_instruction = "帮我点击第一个按钮，然后读取内容"
    similar_ops = memory_system.find_similar_operations(similar_instruction)
    assert len(similar_ops) > 0
    assert similar_ops[0]["actions"] == actions

def test_button2_operation(memory_system):
    """测试按钮2的操作记忆"""
    instruction = "点击按钮2并获取页面2的文本"
    actions = [
        {"type": "click", "target": "button[data-button='2']"},
        {"type": "wait", "time": 1000},
        {"type": "get_text", "target": "#page2-content"}
    ]
    
    assert memory_system.store_operation(instruction, actions)
    
    # 测试相似指令
    similar_instruction = "进入第二个页面并读取内容"
    similar_ops = memory_system.find_similar_operations(similar_instruction)
    assert len(similar_ops) > 0
    assert similar_ops[0]["actions"] == actions

def test_button3_operation(memory_system):
    """测试按钮3的操作记忆"""
    instruction = "点击按钮3并获取页面3的文本"
    actions = [
        {"type": "click", "target": "button[data-button='3']"},
        {"type": "wait", "time": 1000},
        {"type": "get_text", "target": "#page3-content"}
    ]
    
    assert memory_system.store_operation(instruction, actions)
    
    # 测试相似指令
    similar_instruction = "打开第三个页面看看内容"
    similar_ops = memory_system.find_similar_operations(similar_instruction)
    assert len(similar_ops) > 0
    assert similar_ops[0]["actions"] == actions

def test_instruction_variations(memory_system):
    """测试不同表达方式的指令"""
    # 存储标准操作
    standard_instruction = "点击按钮1并获取文本"
    actions = [
        {"type": "click", "target": "button[data-button='1']"},
        {"type": "wait", "time": 1000},
        {"type": "get_text", "target": "#page1-content"}
    ]
    memory_system.store_operation(standard_instruction, actions)
    
    # 测试各种表达方式
    variations = [
        "请帮我点击第一个按钮，然后获取内容",
        "进入页面1，查看文本信息",
        "点击1号按钮，读取页面内容",
        "打开第一个页面的内容给我看看"
    ]
    
    for instruction in variations:
        similar_ops = memory_system.find_similar_operations(instruction)
        assert len(similar_ops) > 0
        assert similar_ops[0]["actions"] == actions
        assert similar_ops[0]["similarity"] > 0.7  # 相似度阈值可以根据实际情况调整

def test_store_and_retrieve_operation(memory_system):
    """测试存储和检索操作"""
    # 测试数据
    instruction = "点击按钮1并获取文本"
    actions = [
        {"type": "click", "target": "button[data-button='1']"},
        {"type": "wait", "time": 1000},
        {"type": "get_text", "target": "#page1-content"}
    ]
    
    # 测试存储
    assert memory_system.store_operation(instruction, actions)
    
    # 测试检索
    similar_ops = memory_system.find_similar_operations(instruction)
    assert len(similar_ops) > 0
    assert similar_ops[0]["instruction"] == instruction
    assert similar_ops[0]["actions"] == actions
    assert similar_ops[0]["similarity"] > 0.9  # 相同指令应该有很高的相似度

def test_similar_instruction_retrieval(memory_system):
    """测试相似指令的检索"""
    # 存储原始操作
    original_instruction = "点击按钮1并获取文本"
    actions = [{"type": "click", "target": "button[data-button='1']"}]
    memory_system.store_operation(original_instruction, actions)
    
    # 测试相似指令
    similar_instruction = "请帮我点击第一个按钮"
    similar_ops = memory_system.find_similar_operations(similar_instruction)
    
    assert len(similar_ops) > 0
    assert similar_ops[0]["similarity"] > 0.7  # 相似指令应该有较高的相似度

def test_different_instruction_retrieval(memory_system):
    """测试不相关指令的检索"""
    # 存储原始操作
    original_instruction = "点击按钮1并获取文本"
    actions = [{"type": "click", "target": "button[data-button='1']"}]
    memory_system.store_operation(original_instruction, actions)
    
    # 测试不相关指令
    different_instruction = "关闭浏览器"
    different_ops = memory_system.find_similar_operations(different_instruction)
    
    assert len(different_ops) == 0  # 不相关指令应该找不到匹配

def test_multiple_operations(memory_system):
    """测试多个操作的存储和检索"""
    instructions_and_actions = [
        (
            "点击按钮1",
            [{"type": "click", "target": "button[data-button='1']"}]
        ),
        (
            "点击按钮2",
            [{"type": "click", "target": "button[data-button='2']"}]
        ),
        (
            "点击按钮3",
            [{"type": "click", "target": "button[data-button='3']"}]
        )
    ]
    
    # 存储所有操作
    for instruction, actions in instructions_and_actions:
        assert memory_system.store_operation(instruction, actions)
    
    # 测试检索每个操作
    for instruction, actions in instructions_and_actions:
        similar_ops = memory_system.find_similar_operations(instruction)
        assert len(similar_ops) > 0
        assert similar_ops[0]["actions"] == actions

def test_clear_memory(memory_system):
    """测试清空记忆"""
    # 先存储一些数据
    instruction = "测试指令"
    actions = [{"type": "test"}]
    memory_system.store_operation(instruction, actions)
    
    # 确认数据已存储
    assert len(memory_system.find_similar_operations(instruction)) > 0
    
    # 清空记忆
    assert memory_system.clear_memory()
    
    # 确认数据已清空
    assert len(memory_system.find_similar_operations(instruction)) == 0 