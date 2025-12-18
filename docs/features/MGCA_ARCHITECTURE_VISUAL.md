# MGCA Architecture Visualization

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TradingAgents-CN System                          │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    MGCA Coordinator                               │ │
│  │                                                                   │ │
│  │  ┌──────────────────────────┐    ┌──────────────────────────┐   │ │
│  │  │      MGCARouter          │    │  MGCAConsensusEngine     │   │ │
│  │  │                          │    │                          │   │ │
│  │  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │   │ │
│  │  │  │    Channels     │    │    │  │   Sessions      │    │   │ │
│  │  │  │  - analysis     │    │    │  │   - Voting      │    │   │ │
│  │  │  │  - signals      │    │    │  │   - Threshold   │    │   │ │
│  │  │  │  - risk_alerts  │    │    │  │   - Results     │    │   │ │
│  │  │  │  - consensus    │    │    │  └─────────────────┘    │   │ │
│  │  │  │  - urgent       │    │    │                          │   │ │
│  │  │  └─────────────────┘    │    └──────────────────────────┘   │ │
│  │  │                          │                                    │ │
│  │  │  ┌─────────────────┐    │                                    │ │
│  │  │  │ Routing Rules   │    │                                    │ │
│  │  │  │  - Type-based   │    │                                    │ │
│  │  │  │  - Group-based  │    │                                    │ │
│  │  │  │  - Priority     │    │                                    │ │
│  │  │  └─────────────────┘    │                                    │ │
│  │  │                          │                                    │ │
│  │  │  ┌─────────────────┐    │                                    │ │
│  │  │  │ Agent Registry  │    │                                    │ │
│  │  │  │  - ANALYSTS     │    │                                    │ │
│  │  │  │  - RESEARCHERS  │    │                                    │ │
│  │  │  │  - TRADERS      │    │                                    │ │
│  │  │  │  - RISK_MGRS    │    │                                    │ │
│  │  │  └─────────────────┘    │                                    │ │
│  │  └──────────────────────────┘                                    │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                   MGCAGraphEnhancer                               │ │
│  │                   (Integration Layer)                             │ │
│  │                                                                   │ │
│  │  ┌──────────────────────────┐    ┌──────────────────────────┐   │ │
│  │  │   MGCAStateAdapter       │    │   Node Enhancement       │   │ │
│  │  │                          │    │                          │   │ │
│  │  │  - Extract Reports       │    │  - Pre-execution sync    │   │ │
│  │  │  - Extract Signals       │    │  - Post-execution sync   │   │ │
│  │  │  - Extract Alerts        │    │  - Message injection     │   │ │
│  │  │  - State Sync            │    │                          │   │ │
│  │  └──────────────────────────┘    └──────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   Existing TradingAgents Graph                          │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Analysts │  │Research  │  │ Traders  │  │   Risk   │             │
│  │  Team    │→│   Team   │→│          │→│   Mgmt   │             │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Message Flow

```
┌────────────┐                                           ┌────────────┐
│  Market    │                                           │  Trader    │
│  Analyst   │                                           │            │
└─────┬──────┘                                           └─────▲──────┘
      │                                                        │
      │ 1. Create Analysis                                    │
      │    Message                                            │
      ▼                                                        │
┌─────────────────────────────────────────────────────────────┴──────┐
│                        MGCACoordinator                              │
│                                                                     │
│  2. Route Message                                                   │
│     ├─ Check routing rules                                         │
│     ├─ Apply priority boost                                        │
│     └─ Select channel                                              │
│                                                                     │
│  3. Publish to Channel                                             │
│     ├─ Add to message queue                                        │
│     └─ Notify subscribers                                          │
│                                                                     │
│  4. Retrieve Messages                                              │
│     ├─ Filter by recipient                                         │
│     ├─ Filter by priority                                          │
│     └─ Sort by timestamp                                           │
└─────────────────────────────────────────────────────────────────────┘
```

## Consensus Flow

```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│   Bull     │  │   Bear     │  │  Market    │  │Fundamental │
│ Researcher │  │ Researcher │  │  Analyst   │  │  Analyst   │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │               │
      │ BUY          │ HOLD          │ BUY          │ BUY
      │ weight:1.0   │ weight:1.0    │ weight:1.2   │ weight:1.2
      │               │               │               │
      ▼               ▼               ▼               ▼
┌──────────────────────────────────────────────────────────────┐
│                  MGCAConsensusEngine                         │
│                                                              │
│  1. Collect Votes                                           │
│     ├─ BUY:  3 votes (weight: 3.4)                         │
│     └─ HOLD: 1 vote  (weight: 1.0)                         │
│                                                              │
│  2. Calculate Agreement                                     │
│     ├─ Total weight: 4.4                                    │
│     ├─ BUY ratio: 3.4/4.4 = 77.3%                          │
│     └─ Threshold: 60%                                       │
│                                                              │
│  3. Determine Consensus                                     │
│     └─ ✅ Consensus Reached: BUY (77.3% > 60%)             │
└──────────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────┐
│  Trader    │
│  (Action)  │
└────────────┘
```

## Priority Routing

```
Message Priority Levels:
┌─────────────┬──────────┬────────────────────────────────┐
│  Priority   │  Value   │  Use Case                      │
├─────────────┼──────────┼────────────────────────────────┤
│  LOW        │    1     │  General information           │
│  NORMAL     │    2     │  Regular updates               │
│  HIGH       │    3     │  Important signals             │
│  CRITICAL   │    4     │  Urgent alerts                 │
└─────────────┴──────────┴────────────────────────────────┘

Routing with Priority Boost:
┌────────────────┐
│ Alert Message  │  Priority: NORMAL (2)
└────────┬───────┘
         │
         ▼
    ┌─────────┐
    │  Router │  + Priority Boost (+2)
    └────┬────┘
         │
         ▼
┌────────────────┐
│ Urgent Channel │  Priority: CRITICAL (4)
└────────────────┘
```

## Agent Groups Communication

```
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Groups                               │
│                                                                 │
│  ┌──────────────┐                    ┌──────────────┐         │
│  │   ANALYSTS   │◄──────┬───────────►│  RESEARCHERS │         │
│  │              │       │            │              │         │
│  │ - market     │       │            │ - bull       │         │
│  │ - social     │       │            │ - bear       │         │
│  │ - news       │       │            └──────▲───────┘         │
│  │ - fundament. │       │                   │                 │
│  └──────┬───────┘       │                   │                 │
│         │               │                   │                 │
│         │          ┌────▼────┐              │                 │
│         │          │  MGCA   │              │                 │
│         └─────────►│ Router  │◄─────────────┘                 │
│                    └────┬────┘                                 │
│                         │                                      │
│         ┌───────────────┴────────────────┐                    │
│         │                                │                    │
│    ┌────▼─────┐                   ┌──────▼──────┐            │
│    │ TRADERS  │                   │ RISK_MGRS   │            │
│    │          │                   │             │            │
│    │ - trader │                   │ - risky     │            │
│    └──────────┘                   │ - safe      │            │
│                                   │ - neutral   │            │
│                                   └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## Integration with Existing Graph

```
Original Flow:
Analysts → Researchers → Trader → Risk Management → Final Decision

Enhanced with MGCA:
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Analysts                                                  │
│    ├─► Analysis Channel ──┐                               │
│    │                       │                               │
│  Researchers               ▼                               │
│    ├─► Signals Channel ──► MGCA ──► Message Distribution  │
│    │                       ▲                               │
│  Risk Mgmt                 │                               │
│    └─► Alerts Channel ────┘                               │
│                                                            │
│  All agents can:                                          │
│    • Send direct messages                                 │
│    • Query other agents                                   │
│    • Participate in consensus                             │
│    • Receive broadcasts                                   │
└────────────────────────────────────────────────────────────┘
```

## Configuration

```python
# Enable MGCA
config = {
    "mgca_enabled": True,  # Turn on/off MGCA
}

# Initialize
from tradingagents.graph import MGCAGraphEnhancer
enhancer = MGCAGraphEnhancer(config)

# Automatic integration
# - Agents are automatically registered
# - Channels are created
# - Routing rules are set up
```

## Key Benefits

```
┌─────────────────────────────────────────────────────────────┐
│  Before MGCA                │  After MGCA                   │
├─────────────────────────────┼───────────────────────────────┤
│  Linear communication       │  Multi-directional            │
│  No prioritization          │  4-level priority system      │
│  No direct queries          │  Query/response support       │
│  Manual consensus           │  Automated consensus          │
│  No broadcasting            │  Group/system broadcasts      │
│  Fixed message flow         │  Flexible routing             │
└─────────────────────────────┴───────────────────────────────┘
```
