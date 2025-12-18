# MGCA - Multi-Graph Communication Architecture

## 概述 (Overview)

MGCA（Multi-Graph Communication Architecture，多图通信架构）是TradingAgents-CN中的一个增强功能，为多智能体系统提供了更强大和灵活的通信能力。

### 核心特性 (Core Features)

- **🔀 跨智能体组通信**: 允许不同组的智能体直接通信，突破传统的线性通信模式
- **📮 消息路由与优先级**: 智能消息路由系统，支持基于优先级的消息处理
- **📢 广播机制**: 向所有智能体或特定组广播重要信息
- **🤝 共识决策引擎**: 帮助多个智能体就交易决策达成共识
- **📊 标准化通信协议**: 统一的消息格式，确保不同智能体间的互操作性

## 架构设计 (Architecture Design)

### 组件结构 (Components)

```
MGCA System
├── MGCACoordinator (协调器)
│   ├── MGCARouter (路由器)
│   │   ├── Channels (通信频道)
│   │   ├── Routing Rules (路由规则)
│   │   └── Agent Registry (智能体注册表)
│   └── MGCAConsensusEngine (共识引擎)
│       └── Consensus Sessions (共识会话)
└── MGCAGraphEnhancer (图增强器)
    └── MGCAStateAdapter (状态适配器)
```

### 消息类型 (Message Types)

1. **ANALYSIS**: 分析报告（来自分析师）
2. **SIGNAL**: 交易信号
3. **ALERT**: 风险警报或警告
4. **QUERY**: 信息查询请求
5. **RESPONSE**: 查询响应
6. **BROADCAST**: 系统级广播
7. **CONSENSUS**: 共识决策消息

### 消息优先级 (Message Priorities)

1. **LOW** (低): 一般性信息，非紧急
2. **NORMAL** (正常): 常规消息，默认优先级
3. **HIGH** (高): 重要消息，需优先处理
4. **CRITICAL** (紧急): 紧急消息，立即处理

### 智能体分组 (Agent Groups)

1. **ANALYSTS**: 分析师组（市场、社交媒体、新闻、基本面分析师）
2. **RESEARCHERS**: 研究员组（多头和空头研究员）
3. **TRADERS**: 交易员组
4. **RISK_MANAGERS**: 风险管理组
5. **SYSTEM**: 系统级智能体

## 快速开始 (Quick Start)

### 基本使用

```python
from tradingagents.graph.mgca import (
    MGCACoordinator,
    MGCAMessage,
    MessageType,
    MessagePriority,
    AgentGroup,
)

# 初始化协调器
coordinator = MGCACoordinator()
coordinator.initialize()

# 注册智能体
coordinator.router.register_agent("market_analyst", AgentGroup.ANALYSTS)
coordinator.router.register_agent("trader", AgentGroup.TRADERS)

# 创建并发送消息
message = MGCAMessage(
    sender="market_analyst",
    sender_group=AgentGroup.ANALYSTS,
    recipients=["trader"],
    message_type=MessageType.ANALYSIS,
    priority=MessagePriority.NORMAL,
    content="市场显示强烈的看涨趋势"
)

coordinator.send_message(message)

# 接收消息
messages = coordinator.router.get_messages_for_agent("trader", channel="analysis")
for msg in messages:
    print(f"收到来自 {msg.sender} 的消息: {msg.content}")
```

### 广播消息

```python
# 创建警报消息
alert = MGCAMessage(
    sender="risk_manager",
    sender_group=AgentGroup.RISK_MANAGERS,
    recipients=["*"],
    message_type=MessageType.ALERT,
    priority=MessagePriority.CRITICAL,
    content="市场波动率超过50%，建议减少持仓"
)

# 广播给特定组
coordinator.broadcast(alert, target_groups=[AgentGroup.ANALYSTS, AgentGroup.TRADERS])
```

### 共识决策

```python
# 创建共识会话
coordinator.create_consensus_session(
    session_id="invest_001",
    participants=["bull_researcher", "bear_researcher", "market_analyst"],
    topic="是否投资AAPL?",
    voting_threshold=0.6  # 60%同意即达成共识
)

# 投票
coordinator.consensus_engine.cast_vote("invest_001", "bull_researcher", "BUY", weight=1.0)
coordinator.consensus_engine.cast_vote("invest_001", "bear_researcher", "HOLD", weight=1.0)
coordinator.consensus_engine.cast_vote("invest_001", "market_analyst", "BUY", weight=1.2)

# 检查共识结果
consensus = coordinator.consensus_engine.get_consensus("invest_001")
print(f"共识结果: {consensus}")  # 输出: BUY
```

## 集成到现有图 (Integration with Existing Graph)

### 使用图增强器

```python
from tradingagents.graph.mgca_integration import MGCAGraphEnhancer

# 创建增强器
config = {"mgca_enabled": True}
enhancer = MGCAGraphEnhancer(config)

# 创建跨智能体查询
correlation_id = enhancer.create_cross_agent_query(
    sender="trader",
    recipients=["market_analyst", "fundamentals_analyst"],
    query="AAPL当前的市场情绪如何？",
    priority=MessagePriority.HIGH
)

# 发送响应
enhancer.send_response(
    sender="market_analyst",
    recipient="trader",
    response="AAPL显示看涨势头，RSI为68",
    correlation_id=correlation_id
)
```

### 增强节点功能

```python
# 使用装饰器增强节点
@enhancer.enhance_node
def my_analyst_node(state: AgentState):
    # 节点执行前会自动同步MGCA消息到state
    # 节点执行后会自动将state同步回MGCA
    
    # 访问MGCA消息
    mgca_messages = state.get("mgca_messages", [])
    
    # 处理消息...
    
    return state
```

## 高级功能 (Advanced Features)

### 自定义路由规则

```python
# 添加自定义路由规则
coordinator.router.add_routing_rule({
    "from_group": AgentGroup.ANALYSTS,
    "to_group": AgentGroup.TRADERS,
    "message_type": MessageType.SIGNAL,
    "channel": "signals",
    "priority_boost": 1  # 自动提升优先级
})
```

### 创建自定义频道

```python
# 创建专用频道
custom_channel = coordinator.router.create_channel("high_frequency_signals")

# 订阅频道
custom_channel.subscribe("trader_1")
custom_channel.subscribe("trader_2")

# 向频道发布消息
custom_channel.publish(message)
```

### 优先级过滤

```python
# 只获取高优先级消息
high_priority_msgs = coordinator.router.get_messages_for_agent(
    "trader",
    channel="default",
    min_priority=MessagePriority.HIGH
)
```

## 配置选项 (Configuration Options)

在配置文件中启用/禁用MGCA:

```python
config = {
    "mgca_enabled": True,  # 启用MGCA
    # 其他配置...
}
```

## 性能考虑 (Performance Considerations)

- **消息队列大小**: MGCA使用内存中的消息队列，大量消息可能影响内存使用
- **消息清理**: 使用 `clear=True` 参数定期清理已读消息
- **批量处理**: 建议批量处理消息而非单个处理以提高效率

## 最佳实践 (Best Practices)

1. **合理使用优先级**: 不要过度使用CRITICAL优先级，保留给真正紧急的情况
2. **清晰的命名**: 为智能体和频道使用清晰、描述性的名称
3. **消息大小**: 保持消息内容简洁，大型数据使用引用而非直接包含
4. **错误处理**: 始终处理可能的消息路由失败情况
5. **监控统计**: 定期检查系统统计信息，识别潜在问题

## 示例代码 (Examples)

完整的示例代码请参考: `examples/mgca_demo.py`

运行示例:
```bash
cd /path/to/TradingAgents-CN
python examples/mgca_demo.py
```

## API参考 (API Reference)

### MGCACoordinator

主协调器类，整合路由器和共识引擎。

#### 方法:
- `initialize()`: 初始化系统
- `send_message(message)`: 发送消息
- `broadcast(message, target_groups)`: 广播消息
- `create_consensus_session(...)`: 创建共识会话
- `get_stats()`: 获取系统统计信息

### MGCAMessage

标准化消息类。

#### 属性:
- `sender`: 发送者ID
- `sender_group`: 发送者组
- `recipients`: 接收者列表
- `message_type`: 消息类型
- `priority`: 优先级
- `content`: 消息内容
- `metadata`: 元数据
- `timestamp`: 时间戳
- `requires_response`: 是否需要响应
- `correlation_id`: 关联ID

### MGCARouter

消息路由器。

#### 方法:
- `register_agent(agent_id, agent_group)`: 注册智能体
- `create_channel(channel_name)`: 创建频道
- `add_routing_rule(rule)`: 添加路由规则
- `route_message(message)`: 路由消息
- `get_messages_for_agent(...)`: 获取智能体消息

### MGCAConsensusEngine

共识决策引擎。

#### 方法:
- `create_session(...)`: 创建共识会话
- `cast_vote(session_id, agent_id, vote, weight)`: 投票
- `get_consensus(session_id)`: 获取共识结果
- `close_session(session_id)`: 关闭会话

## 故障排除 (Troubleshooting)

### 消息未收到

- 检查智能体是否已注册
- 确认接收者ID正确
- 检查频道名称是否正确
- 验证优先级过滤设置

### 共识无法达成

- 检查投票阈值设置是否合理
- 确认所有参与者都已投票
- 验证投票权重设置

### 性能问题

- 定期清理已读消息
- 考虑使用批量处理
- 检查消息队列大小

## 未来改进 (Future Improvements)

- 持久化消息存储
- 分布式MGCA支持
- 消息加密和安全性增强
- 更高级的路由算法
- 可视化监控界面

## 贡献 (Contributing)

欢迎贡献！请参阅项目的贡献指南。

## 许可证 (License)

遵循TradingAgents-CN项目的许可证。

## 联系方式 (Contact)

如有问题或建议，请通过GitHub Issues联系我们。
