#!/usr/bin/env python3
"""
Minimal standalone test for MGCA core functionality
This test imports only the MGCA modules without requiring full tradingagents setup
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the logging module to avoid dependencies
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def debug(self, msg): pass
    def warning(self, msg): print(f"WARN: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

# Mock the logging_init module
sys.modules['tradingagents.utils.logging_init'] = type(sys)('logging_init')
sys.modules['tradingagents.utils.logging_init'].get_logger = lambda x: MockLogger()

# Now import MGCA
from tradingagents.graph.mgca import (
    MGCACoordinator,
    MGCAMessage,
    MessageType,
    MessagePriority,
    AgentGroup,
)

def test_basic_messaging():
    """Test basic message creation and routing"""
    print("\n" + "="*60)
    print("Test 1: Basic Message Creation and Routing")
    print("="*60)
    
    try:
        coordinator = MGCACoordinator()
        coordinator.initialize()
        
        # Register agents
        coordinator.router.register_agent("market_analyst", AgentGroup.ANALYSTS)
        coordinator.router.register_agent("trader", AgentGroup.TRADERS)
        
        # Create message
        message = MGCAMessage(
            sender="market_analyst",
            sender_group=AgentGroup.ANALYSTS,
            recipients=["trader"],
            message_type=MessageType.ANALYSIS,
            priority=MessagePriority.NORMAL,
            content="Test market analysis"
        )
        
        # Send message
        coordinator.send_message(message)
        
        # Retrieve messages
        messages = coordinator.router.get_messages_for_agent("trader", channel="analysis")
        
        assert len(messages) == 1, f"Expected 1 message, got {len(messages)}"
        assert messages[0].sender == "market_analyst"
        assert messages[0].content == "Test market analysis"
        
        print("✅ Test passed: Message created and routed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_broadcast():
    """Test broadcast functionality"""
    print("\n" + "="*60)
    print("Test 2: Message Broadcasting")
    print("="*60)
    
    try:
        coordinator = MGCACoordinator()
        coordinator.initialize()
        
        # Register agents
        coordinator.router.register_agent("analyst1", AgentGroup.ANALYSTS)
        coordinator.router.register_agent("analyst2", AgentGroup.ANALYSTS)
        coordinator.router.register_agent("trader1", AgentGroup.TRADERS)
        
        # Create broadcast message
        message = MGCAMessage(
            sender="system",
            sender_group=AgentGroup.SYSTEM,
            recipients=["*"],
            message_type=MessageType.BROADCAST,
            priority=MessagePriority.HIGH,
            content="System broadcast"
        )
        
        # Broadcast to analysts only
        coordinator.broadcast(message, target_groups=[AgentGroup.ANALYSTS])
        
        # Check messages
        analyst1_msgs = coordinator.router.get_messages_for_agent("analyst1", channel="default")
        analyst2_msgs = coordinator.router.get_messages_for_agent("analyst2", channel="default")
        trader_msgs = coordinator.router.get_messages_for_agent("trader1", channel="default")
        
        assert len(analyst1_msgs) >= 1, "analyst1 should receive message"
        assert len(analyst2_msgs) >= 1, "analyst2 should receive message"
        
        print(f"✅ Test passed: Broadcast sent to {len([analyst1_msgs, analyst2_msgs])} analysts")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_consensus():
    """Test consensus engine"""
    print("\n" + "="*60)
    print("Test 3: Consensus Decision Making")
    print("="*60)
    
    try:
        coordinator = MGCACoordinator()
        
        # Create consensus session
        participants = ["agent1", "agent2", "agent3"]
        coordinator.create_consensus_session(
            session_id="test_session",
            participants=participants,
            topic="Test decision",
            voting_threshold=0.6
        )
        
        # Cast votes
        coordinator.consensus_engine.cast_vote("test_session", "agent1", "YES", 1.0)
        coordinator.consensus_engine.cast_vote("test_session", "agent2", "YES", 1.0)
        coordinator.consensus_engine.cast_vote("test_session", "agent3", "NO", 1.0)
        
        # Check consensus
        consensus = coordinator.consensus_engine.get_consensus("test_session")
        
        assert consensus == "YES", f"Expected YES, got {consensus}"
        
        print(f"✅ Test passed: Consensus reached on 'YES' with 2/3 votes (66% > 60%)")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_priority_routing():
    """Test priority-based message filtering"""
    print("\n" + "="*60)
    print("Test 4: Priority-Based Message Filtering")
    print("="*60)
    
    try:
        coordinator = MGCACoordinator()
        coordinator.initialize()
        
        coordinator.router.register_agent("trader", AgentGroup.TRADERS)
        
        # Send messages with different priorities
        messages = [
            ("Low", MessagePriority.LOW),
            ("Normal", MessagePriority.NORMAL),
            ("High", MessagePriority.HIGH),
            ("Critical", MessagePriority.CRITICAL),
        ]
        
        for content, priority in messages:
            msg = MGCAMessage(
                sender="system",
                sender_group=AgentGroup.SYSTEM,
                recipients=["trader"],
                message_type=MessageType.SIGNAL,
                priority=priority,
                content=content
            )
            coordinator.send_message(msg)
        
        # Get only high-priority messages
        high_msgs = coordinator.router.get_messages_for_agent(
            "trader",
            channel="signals",
            min_priority=MessagePriority.HIGH
        )
        
        assert len(high_msgs) == 2, f"Expected 2 high-priority messages, got {len(high_msgs)}"
        
        priorities = [msg.priority for msg in high_msgs]
        assert MessagePriority.HIGH in priorities
        assert MessagePriority.CRITICAL in priorities
        
        print(f"✅ Test passed: Correctly filtered {len(high_msgs)} high-priority messages")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_system_stats():
    """Test system statistics"""
    print("\n" + "="*60)
    print("Test 5: System Statistics")
    print("="*60)
    
    try:
        coordinator = MGCACoordinator()
        coordinator.initialize()
        
        # Register agents
        for i in range(5):
            coordinator.router.register_agent(f"agent{i}", AgentGroup.ANALYSTS)
        
        # Get stats
        stats = coordinator.get_stats()
        
        assert "channels" in stats
        assert "registered_agents" in stats
        assert stats["registered_agents"] == 5
        
        print(f"✅ Test passed: Stats collected - {stats['registered_agents']} agents, {stats['channels']} channels")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MGCA Core Functionality Tests")
    print("="*60)
    
    tests = [
        test_basic_messaging,
        test_broadcast,
        test_consensus,
        test_priority_routing,
        test_system_stats,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
