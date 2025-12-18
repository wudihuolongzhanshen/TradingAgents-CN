#!/usr/bin/env python3
"""
MGCA (Multi-Graph Communication Architecture) Example

This example demonstrates the new MGCA capabilities for enhanced
multi-agent communication in the TradingAgents framework.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tradingagents.graph.mgca import (
    MGCACoordinator,
    MGCAMessage,
    MessageType,
    MessagePriority,
    AgentGroup,
)
from tradingagents.graph.mgca_integration import MGCAGraphEnhancer


def example_basic_messaging():
    """Example 1: Basic message routing"""
    print("=" * 60)
    print("Example 1: Basic Message Routing")
    print("=" * 60)
    
    # Initialize MGCA coordinator
    coordinator = MGCACoordinator()
    coordinator.initialize()
    
    # Register some agents
    coordinator.router.register_agent("market_analyst", AgentGroup.ANALYSTS)
    coordinator.router.register_agent("trader", AgentGroup.TRADERS)
    coordinator.router.register_agent("risk_manager", AgentGroup.RISK_MANAGERS)
    
    # Create and send a message
    message = MGCAMessage(
        sender="market_analyst",
        sender_group=AgentGroup.ANALYSTS,
        recipients=["trader"],
        message_type=MessageType.ANALYSIS,
        priority=MessagePriority.NORMAL,
        content="Market shows strong bullish trend. RSI: 72, MACD positive crossover.",
        metadata={"indicators": ["RSI", "MACD"]}
    )
    
    coordinator.send_message(message)
    print(f"✅ Sent analysis message from market_analyst to trader")
    
    # Retrieve messages for trader
    messages = coordinator.router.get_messages_for_agent("trader", channel="analysis")
    print(f"\n📬 Trader received {len(messages)} message(s):")
    for msg in messages:
        print(f"   From: {msg.sender}")
        print(f"   Type: {msg.message_type.value}")
        print(f"   Priority: {msg.priority.name}")
        print(f"   Content: {msg.content[:80]}...")
    
    print()


def example_broadcast():
    """Example 2: Broadcasting messages"""
    print("=" * 60)
    print("Example 2: Broadcasting Messages")
    print("=" * 60)
    
    coordinator = MGCACoordinator()
    coordinator.initialize()
    
    # Register agents from different groups
    coordinator.router.register_agent("risk_manager", AgentGroup.RISK_MANAGERS)
    coordinator.router.register_agent("trader", AgentGroup.TRADERS)
    coordinator.router.register_agent("market_analyst", AgentGroup.ANALYSTS)
    coordinator.router.register_agent("social_analyst", AgentGroup.ANALYSTS)
    
    # Create a broadcast alert
    alert = MGCAMessage(
        sender="risk_manager",
        sender_group=AgentGroup.RISK_MANAGERS,
        recipients=["*"],
        message_type=MessageType.ALERT,
        priority=MessagePriority.CRITICAL,
        content="CRITICAL: Market volatility exceeding 50%. Recommend reducing positions.",
    )
    
    # Broadcast to analysts only
    coordinator.broadcast(alert, target_groups=[AgentGroup.ANALYSTS, AgentGroup.TRADERS])
    print(f"✅ Broadcast critical alert to Analysts and Traders groups")
    
    # Check who received the message
    for agent_id in ["trader", "market_analyst", "social_analyst"]:
        messages = coordinator.router.get_messages_for_agent(
            agent_id, 
            channel="urgent",
            min_priority=MessagePriority.CRITICAL
        )
        print(f"   {agent_id}: received {len(messages)} critical message(s)")
    
    print()


def example_consensus():
    """Example 3: Consensus decision making"""
    print("=" * 60)
    print("Example 3: Consensus Decision Making")
    print("=" * 60)
    
    coordinator = MGCACoordinator()
    coordinator.initialize()
    
    # Create a consensus session for investment decision
    participants = ["bull_researcher", "bear_researcher", "market_analyst", "fundamentals_analyst"]
    coordinator.create_consensus_session(
        session_id="invest_decision_001",
        participants=participants,
        topic="Should we invest in AAPL?",
        voting_threshold=0.6
    )
    
    print(f"✅ Created consensus session with {len(participants)} participants")
    print(f"   Topic: Should we invest in AAPL?")
    print(f"   Threshold: 60% agreement required")
    
    # Agents cast their votes
    votes = [
        ("bull_researcher", "BUY", 1.0),
        ("bear_researcher", "HOLD", 1.0),
        ("market_analyst", "BUY", 1.2),  # Higher weight for market expert
        ("fundamentals_analyst", "BUY", 1.2),  # Higher weight for fundamentals
    ]
    
    print("\n🗳️ Casting votes:")
    for agent, vote, weight in votes:
        coordinator.consensus_engine.cast_vote("invest_decision_001", agent, vote, weight)
        print(f"   {agent}: {vote} (weight: {weight})")
    
    # Check consensus
    consensus = coordinator.consensus_engine.get_consensus("invest_decision_001")
    if consensus:
        print(f"\n✅ Consensus reached: {consensus}")
    else:
        print(f"\n❌ No consensus reached")
    
    print()


def example_priority_routing():
    """Example 4: Priority-based message routing"""
    print("=" * 60)
    print("Example 4: Priority-Based Message Routing")
    print("=" * 60)
    
    coordinator = MGCACoordinator()
    coordinator.initialize()
    
    coordinator.router.register_agent("trader", AgentGroup.TRADERS)
    
    # Send messages with different priorities
    messages = [
        ("Low priority analysis", MessagePriority.LOW, MessageType.ANALYSIS),
        ("Normal market update", MessagePriority.NORMAL, MessageType.SIGNAL),
        ("High priority signal", MessagePriority.HIGH, MessageType.SIGNAL),
        ("CRITICAL ALERT", MessagePriority.CRITICAL, MessageType.ALERT),
    ]
    
    print("📤 Sending messages with different priorities:")
    for content, priority, msg_type in messages:
        msg = MGCAMessage(
            sender="system",
            sender_group=AgentGroup.SYSTEM,
            recipients=["trader"],
            message_type=msg_type,
            priority=priority,
            content=content
        )
        coordinator.send_message(msg)
        print(f"   {priority.name}: {content}")
    
    # Retrieve only high-priority messages
    high_priority_msgs = coordinator.router.get_messages_for_agent(
        "trader",
        channel="default",
        min_priority=MessagePriority.HIGH
    )
    
    print(f"\n📬 Trader retrieved {len(high_priority_msgs)} high-priority messages:")
    for msg in high_priority_msgs:
        print(f"   [{msg.priority.name}] {msg.content}")
    
    print()


def example_system_stats():
    """Example 5: System statistics"""
    print("=" * 60)
    print("Example 5: MGCA System Statistics")
    print("=" * 60)
    
    coordinator = MGCACoordinator()
    coordinator.initialize()
    
    # Register multiple agents
    agents = [
        ("market_analyst", AgentGroup.ANALYSTS),
        ("social_analyst", AgentGroup.ANALYSTS),
        ("news_analyst", AgentGroup.ANALYSTS),
        ("fundamentals_analyst", AgentGroup.ANALYSTS),
        ("bull_researcher", AgentGroup.RESEARCHERS),
        ("bear_researcher", AgentGroup.RESEARCHERS),
        ("trader", AgentGroup.TRADERS),
        ("risk_manager", AgentGroup.RISK_MANAGERS),
    ]
    
    for agent_id, group in agents:
        coordinator.router.register_agent(agent_id, group)
    
    # Send some test messages
    for i in range(5):
        msg = MGCAMessage(
            sender="market_analyst",
            sender_group=AgentGroup.ANALYSTS,
            recipients=["trader"],
            message_type=MessageType.ANALYSIS,
            priority=MessagePriority.NORMAL,
            content=f"Analysis update #{i+1}"
        )
        coordinator.send_message(msg)
    
    # Get statistics
    stats = coordinator.get_stats()
    
    print(f"📊 MGCA System Statistics:")
    print(f"   Total channels: {stats['channels']}")
    print(f"   Registered agents: {stats['registered_agents']}")
    print(f"   Routing rules: {stats['routing_rules']}")
    print(f"   Active consensus sessions: {stats['active_consensus_sessions']}")
    
    print(f"\n📡 Channel Details:")
    for channel_name, details in stats['channel_details'].items():
        print(f"   {channel_name}:")
        print(f"      Subscribers: {details['subscribers']}")
        print(f"      Queued messages: {details['queued_messages']}")
    
    print()


def example_graph_enhancement():
    """Example 6: Graph enhancement with MGCA"""
    print("=" * 60)
    print("Example 6: Graph Enhancement with MGCA")
    print("=" * 60)
    
    # Create an enhancer
    config = {"mgca_enabled": True}
    enhancer = MGCAGraphEnhancer(config)
    
    # Simulate a cross-agent query
    correlation_id = enhancer.create_cross_agent_query(
        sender="trader",
        recipients=["market_analyst", "fundamentals_analyst"],
        query="What is the current market sentiment for AAPL?",
        priority=MessagePriority.HIGH
    )
    
    print(f"✅ Created cross-agent query")
    print(f"   Correlation ID: {correlation_id}")
    
    # Simulate responses
    enhancer.send_response(
        sender="market_analyst",
        recipient="trader",
        response="AAPL showing bullish momentum, RSI at 68",
        correlation_id=correlation_id
    )
    
    enhancer.send_response(
        sender="fundamentals_analyst",
        recipient="trader",
        response="AAPL P/E ratio is 28.5, slightly above sector average",
        correlation_id=correlation_id
    )
    
    print(f"✅ Responses sent from analysts to trader")
    
    # Broadcast an alert
    enhancer.broadcast_alert(
        sender="risk_manager",
        alert_content="Portfolio exposure to tech sector exceeds 40% limit",
        target_groups=[AgentGroup.TRADERS],
        priority=MessagePriority.CRITICAL
    )
    
    print(f"✅ Alert broadcast to traders")
    
    # Get system stats
    stats = enhancer.get_system_stats()
    print(f"\n📊 System has {stats['registered_agents']} registered agents across {stats['channels']} channels")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("MGCA (Multi-Graph Communication Architecture) Demo")
    print("=" * 60 + "\n")
    
    try:
        example_basic_messaging()
        example_broadcast()
        example_consensus()
        example_priority_routing()
        example_system_stats()
        example_graph_enhancement()
        
        print("=" * 60)
        print("✅ All MGCA examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
