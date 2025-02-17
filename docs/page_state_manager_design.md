# 页面状态管理器设计文档

## 1. 功能概述

页面状态管理器(PageStateManager)负责跟踪和管理Web页面的状态，确保操作的可靠性和正确性。主要功能包括：
- 页面状态的捕获和存储
- 状态转换的验证
- 页面加载状态的监控
- 元素状态的验证
- 状态恢复机制

## 2. 核心数据结构

### 2.1 页面状态(PageState)
```python
class PageState:
    url: str                      # 页面URL
    title: str                    # 页面标题
    current_element: str          # 当前焦点元素
    visible_elements: List[str]   # 可见元素列表
    dom_snapshot: str            # DOM快照(简化版)
    timestamp: datetime          # 状态捕获时间戳
```

### 2.2 状态转换(StateTransition)
```python
class StateTransition:
    from_state: PageState        # 起始状态
    to_state: PageState          # 目标状态
    action: Dict[str, Any]       # 触发转换的操作
    success: bool                # 转换是否成功
    error: Optional[str]         # 错误信息
```

## 3. 核心功能设计

### 3.1 状态捕获
- 使用Playwright的API捕获页面状态
- 定期自动捕获
- 操作执行前后捕获
- 支持自定义捕获时机

### 3.2 状态比较
- DOM结构对比
- 可见元素对比
- URL和标题对比
- 支持自定义比较规则

### 3.3 状态验证
- 元素存在性验证
- 元素可见性验证
- 元素可交互性验证
- 页面加载完成验证

### 3.4 状态恢复
- 基于URL的恢复
- 基于操作序列的恢复
- 支持自定义恢复策略

## 4. 接口设计

### 4.1 主要类
```python
class PageStateManager:
    def capture_state(self) -> PageState:
        """捕获当前页面状态"""
        pass
        
    def validate_state(self, expected: PageState) -> bool:
        """验证当前状态是否符合预期"""
        pass
        
    def wait_for_state(self, expected: PageState, timeout: int) -> bool:
        """等待直到达到预期状态"""
        pass
        
    def recover_state(self, target: PageState) -> bool:
        """尝试恢复到目标状态"""
        pass
        
    def track_transition(self, action: Dict[str, Any]) -> StateTransition:
        """跟踪状态转换"""
        pass
```

### 4.2 辅助类
```python
class StateValidator:
    """状态验证器"""
    pass

class StateComparator:
    """状态比较器"""
    pass

class StateRecoveryStrategy:
    """状态恢复策略"""
    pass
```

## 5. 实现步骤

1. 基础框架搭建
   - 创建核心类
   - 实现基本接口
   - 添加日志系统

2. 状态捕获实现
   - 实现DOM快照
   - 实现元素状态捕获
   - 实现页面信息捕获

3. 状态验证实现
   - 实现基本验证规则
   - 实现自定义验证支持
   - 实现超时处理

4. 状态恢复实现
   - 实现基本恢复策略
   - 实现自定义恢复支持
   - 实现恢复失败处理

5. 测试用例编写
   - 单元测试
   - 集成测试
   - 异常场景测试

## 6. 测试计划

### 6.1 单元测试
- 状态捕获测试
- 状态比较测试
- 状态验证测试
- 状态恢复测试

### 6.2 集成测试
- 与执行引擎集成测试
- 与记忆系统集成测试
- 完整操作流程测试

### 6.3 性能测试
- 状态捕获性能
- 状态比较性能
- 内存使用监控

## 7. 注意事项

1. 性能考虑
   - 避免过于频繁的状态捕获
   - 优化DOM快照大小
   - 合理设置超时时间

2. 可靠性考虑
   - 完善的错误处理
   - 状态恢复的可靠性
   - 异常情况的处理

3. 扩展性考虑
   - 支持自定义验证规则
   - 支持自定义恢复策略
   - 支持自定义状态比较 