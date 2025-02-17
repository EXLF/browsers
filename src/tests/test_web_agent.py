import pytest
from pathlib import Path
from src.core.web_agent import WebAgent

# 获取demo页面的绝对路径
DEMO_DIR = Path(__file__).parent.parent.parent / "demo_pages"

@pytest.fixture
def agent():
    """创建Web智能代理实例"""
    agent = WebAgent()
    yield agent
    agent.close()

def test_execute_and_store(agent):
    """测试执行和存储操作"""
    # 构建index.html的文件URL
    index_path = f"file://{DEMO_DIR.resolve()}/index.html"
    
    # 定义测试指令和操作序列
    instruction = "点击按钮1并获取文本"
    actions = [
        {"type": "click", "target": "button[data-button='1']"},
        {"type": "wait", "time": 1000},
        {"type": "get_text", "target": "#page1-content"}
    ]
    
    # 存储操作序列
    assert agent.store_successful_execution(instruction, actions)
    
    # 使用相同的指令执行
    success, result = agent.execute_with_memory(instruction, index_path)
    assert success
    assert "这是页面1的核心内容" in result

def test_similar_instruction(agent):
    """测试使用相似指令执行"""
    # 构建index.html的文件URL
    index_path = f"file://{DEMO_DIR.resolve()}/index.html"
    
    # 存储原始操作
    original_instruction = "点击按钮1并获取文本"
    actions = [
        {"type": "click", "target": "button[data-button='1']"},
        {"type": "wait", "time": 1000},
        {"type": "get_text", "target": "#page1-content"}
    ]
    assert agent.store_successful_execution(original_instruction, actions)
    
    # 使用相似的指令执行
    similar_instruction = "帮我点击第一个按钮，然后读取内容"
    success, result = agent.execute_with_memory(similar_instruction, index_path)
    assert success
    assert "这是页面1的核心内容" in result

def test_multiple_operations(agent):
    """测试多个操作的记忆和执行"""
    # 构建index.html的文件URL
    index_path = f"file://{DEMO_DIR.resolve()}/index.html"
    
    # 存储所有按钮的操作
    for button_num in range(1, 4):
        instruction = f"点击按钮{button_num}并获取文本"
        actions = [
            {"type": "click", "target": f"button[data-button='{button_num}']"},
            {"type": "wait", "time": 1000},
            {"type": "get_text", "target": f"#page{button_num}-content"}
        ]
        assert agent.store_successful_execution(instruction, actions)
        
        # 立即验证存储的操作
        success, result = agent.execute_with_memory(instruction, index_path)
        assert success
        assert f"这是页面{button_num}的核心内容" in result

def test_unknown_instruction(agent):
    """测试处理未知指令"""
    # 构建index.html的文件URL
    index_path = f"file://{DEMO_DIR.resolve()}/index.html"
    
    # 使用未存储过的指令
    success, result = agent.execute_with_memory("未知的指令", index_path)
    assert not success
    assert "未找到可用的操作序列" in result

def test_navigation_failure(agent):
    """测试导航失败的情况"""
    # 使用不存在的URL
    success, result = agent.execute_with_memory("任意指令", "file:///non_existent.html")
    assert not success
    assert "导航失败" in result 