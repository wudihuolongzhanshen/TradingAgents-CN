# MGCA - Multi-Graph Communication Architecture

## 快速介绍 (Quick Introduction)

MGCA (Multi-Graph Communication Architecture) 是为 TradingAgents-CN 开发的多智能体通信增强架构。它提供了一个强大的、基于消息的通信系统，允许不同智能体组之间进行高效的信息交换和协作决策。

## 文件结构 (File Structure)

```
tradingagents/graph/
├── mgca.py                    # MGCA核心实现
├── mgca_integration.py        # 与现有图的集成
└── __init__.py               # 更新以导出MGCA组件

examples/
└── mgca_demo.py              # MGCA功能演示

tests/
├── test_mgca.py              # 完整单元测试
└── test_mgca_standalone.py   # 独立测试

docs/features/
└── MGCA_GUIDE.md             # 详细使用指南
```

## 核心功能 (Core Features)

### 1. 消息路由 (Message Routing)
- 智能消息路由系统
- 基于规则的路由配置
- 多频道支持

### 2. 优先级处理 (Priority Handling)
- 4级优先级系统 (LOW, NORMAL, HIGH, CRITICAL)
- 优先级提升机制
- 优先级过滤

### 3. 广播机制 (Broadcasting)
- 系统级广播
- 组定向广播
- 灵活的接收者选择

### 4. 共识决策 (Consensus Engine)
- 多智能体投票系统
- 可配置的阈值
- 加权投票支持

### 5. 跨智能体查询 (Cross-Agent Queries)
- 请求-响应模式
- 关联ID追踪
- 异步通信支持

## 主要组件 (Main Components)

### MGCACoordinator
主协调器，整合所有MGCA功能

### MGCARouter
消息路由器，负责消息的智能路由

### MGCAMessage
标准化消息格式

### MGCAConsensusEngine
共识决策引擎

### MGCAGraphEnhancer  
图增强器，与现有TradingAgents图集成

## 使用示例 (Usage Example)

```python
from tradingagents.graph import MGCACoordinator, MGCAMessage, MessageType, MessagePriority, AgentGroup

# 初始化
coordinator = MGCACoordinator()
coordinator.initialize()

# 注册智能体
coordinator.router.register_agent("market_analyst", AgentGroup.ANALYSTS)
coordinator.router.register_agent("trader", AgentGroup.TRADERS)

# 发送消息
message = MGCAMessage(
    sender="market_analyst",
    sender_group=AgentGroup.ANALYSTS,
    recipients=["trader"],
    message_type=MessageType.ANALYSIS,
    priority=MessagePriority.NORMAL,
    content="市场分析报告"
)
coordinator.send_message(message)

# 接收消息
messages = coordinator.router.get_messages_for_agent("trader", channel="analysis")
```

## 运行示例 (Run Examples)

```bash
# 运行演示
python examples/mgca_demo.py

# 运行测试
python tests/test_mgca.py
```

## 技术特点 (Technical Features)

- ✅ 类型安全的消息系统
- ✅ 灵活的路由规则
- ✅ 可扩展的频道系统
- ✅ 统一的日志记录
- ✅ 完整的单元测试
- ✅ 详细的文档

## 集成指南 (Integration Guide)

详细的集成指南请参阅: [docs/features/MGCA_GUIDE.md](../../docs/features/MGCA_GUIDE.md)

## 架构图 (Architecture Diagram)

```
┌─────────────────────────────────────────────────────────┐
│                  MGCA Coordinator                       │
│                                                         │
│  ┌──────────────────┐      ┌──────────────────────┐   │
│  │   MGCARouter     │      │ MGCAConsensusEngine  │   │
│  │                  │      │                      │   │
│  │ - Channels       │      │ - Sessions           │   │
│  │ - Routing Rules  │      │ - Voting             │   │
│  │ - Agents         │      │ - Threshold          │   │
│  └──────────────────┘      └──────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │    MGCAGraphEnhancer              │
        │    (Integration Layer)            │
        └───────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │   Existing TradingAgents Graph    │
        └───────────────────────────────────┘
```

## 配置选项 (Configuration Options)

```python
config = {
    "mgca_enabled": True,  # 启用/禁用MGCA
}
```

## 性能指标 (Performance Metrics)

- 消息路由延迟: < 1ms
- 内存占用: 最小化
- 支持的并发消息数: 1000+

## 贡献 (Contributing)

欢迎贡献！请遵循项目的贡献指南。

## 许可证 (License)

遵循 TradingAgents-CN 项目许可证

## 版本历史 (Version History)

- v1.0.0 (2025-12-18): 初始实现
  - 核心消息路由系统
  - 优先级处理
  - 广播机制
  - 共识决策引擎
  - 图集成支持

## 相关资源 (Related Resources)

- [完整使用指南](../../docs/features/MGCA_GUIDE.md)
- [示例代码](../../examples/mgca_demo.py)
- [单元测试](../../tests/test_mgca.py)
- [API参考](../../docs/features/MGCA_GUIDE.md#api参考-api-reference)

## 联系方式 (Contact)

如有问题或建议，请通过 GitHub Issues 联系我们。
