import os
import pytest
from pathlib import Path
from src.core.execution_engine import ExecutionEngine

# 获取demo页面的绝对路径
DEMO_DIR = Path(__file__).parent.parent.parent / "demo_pages"

@pytest.fixture
def engine():
    """创建执行引擎实例"""
    engine = ExecutionEngine()
    yield engine
    engine.close()

def test_navigation(engine):
    """测试页面导航"""
    # 构建index.html的文件URL
    index_path = f"file://{DEMO_DIR.resolve()}/index.html"
    
    # 测试导航到主页
    assert engine.navigate(index_path)

def test_click_and_get_text(engine):
    """测试点击操作和文本获取"""
    # 导航到主页
    index_path = f"file://{DEMO_DIR.resolve()}/index.html"
    assert engine.navigate(index_path)
    
    # 测试点击按钮1
    assert engine.click("button[data-button='1']")
    
    # 等待页面加载
    engine._page.wait_for_timeout(1000)
    
    # 获取页面1的文本内容
    text = engine.get_text("#page1-content")
    assert text is not None
    assert "这是页面1的核心内容" in text

def test_execute_actions(engine):
    """测试执行操作序列"""
    # 导航到主页
    index_path = f"file://{DEMO_DIR.resolve()}/index.html"
    assert engine.navigate(index_path)
    
    # 定义操作序列
    actions = [
        {"type": "click", "target": "button[data-button='1']"},
        {"type": "wait", "time": 1000},
        {"type": "get_text", "target": "#page1-content"}
    ]
    
    # 执行操作序列
    results = engine.execute_actions(actions)
    
    # 验证结果
    assert len(results) == 3
    assert results[0] is True  # 点击成功
    assert results[1] is True  # 等待成功
    assert results[2] is not None  # 获取文本成功
    assert "这是页面1的核心内容" in results[2]

def test_error_handling(engine):
    """测试错误处理"""
    # 导航到主页
    index_path = f"file://{DEMO_DIR.resolve()}/index.html"
    assert engine.navigate(index_path)
    
    # 测试点击不存在的元素
    assert not engine.click("#non-existent-button")
    
    # 测试获取不存在的元素的文本
    assert engine.get_text("#non-existent-element") is None
    
    # 测试执行未知类型的操作
    result = engine.execute_action({"type": "unknown", "target": "something"})
    assert result is None

def test_multiple_pages(engine):
    """测试多个页面的操作"""
    # 导航到主页
    index_path = f"file://{DEMO_DIR.resolve()}/index.html"
    assert engine.navigate(index_path)
    
    # 测试所有按钮和页面
    for button_num in range(1, 4):
        # 点击按钮
        assert engine.click(f"button[data-button='{button_num}']")
        
        # 等待页面加载
        engine._page.wait_for_timeout(1000)
        
        # 获取页面内容
        text = engine.get_text(f"#page{button_num}-content")
        assert text is not None
        assert f"这是页面{button_num}的核心内容" in text
        
        # 返回主页
        assert engine.navigate(index_path) 