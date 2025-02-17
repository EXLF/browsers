import pytest
from src.core.instruction_parser import InstructionParser

@pytest.fixture
def parser():
    """创建指令解析器实例"""
    return InstructionParser()

def test_basic_instruction(parser):
    """测试基本指令解析"""
    instruction = "点击按钮1并获取文本"
    actions = parser.parse(instruction)
    
    assert actions is not None
    assert len(actions) == 3
    assert actions[0]["type"] == "click"
    assert actions[0]["target"] == "button[data-button='1']"
    assert actions[1]["type"] == "wait"
    assert actions[2]["type"] == "get_text"
    assert actions[2]["target"] == "#page1-content"

def test_complex_instruction(parser):
    """测试复杂指令解析"""
    instruction = "依次点击按钮2和按钮3，并获取它们的文本内容"
    actions = parser.parse(instruction)
    
    assert actions is not None
    assert len(actions) >= 5  # 至少包含5个操作：点击、等待、获取文本、点击、获取文本
    
    # 验证第一组操作（按钮2）
    assert actions[0]["type"] == "click"
    assert actions[0]["target"] == "button[data-button='2']"
    assert actions[1]["type"] == "wait"
    assert actions[2]["type"] == "get_text"
    assert actions[2]["target"] == "#page2-content"
    
    # 验证第二组操作（按钮3）
    assert actions[3]["type"] == "click"
    assert actions[3]["target"] == "button[data-button='3']"
    assert actions[4]["type"] == "get_text"
    assert actions[4]["target"] == "#page3-content"

def test_invalid_instruction(parser):
    """测试无效指令"""
    instruction = "执行一些不支持的操作"
    actions = parser.parse(instruction)
    assert actions is None 