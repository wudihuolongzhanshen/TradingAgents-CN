#!/usr/bin/env python3
"""
Unit tests for MGCA (Multi-Graph Communication Architecture)
"""

import unittest
from datetime import datetime
from tradingagents.graph.mgca import (
    MGCACoordinator,
    MGCARouter,
    MGCAMessage,
    MGCACommunicationChannel,
    MGCAConsensusEngine,
    MessageType,
    MessagePriority,
    AgentGroup,
)
from tradingagents.graph.mgca_integration import (
    MGCAStateAdapter,
    MGCAGraphEnhancer,
)


class TestMGCAMessage(unittest.TestCase):
    """Test MGCA message functionality"""
    
    def test_message_creation(self):
        """Test creating a basic message"""
        msg = MGCAMessage(
            sender="test_agent",
            sender_group=AgentGroup.ANALYSTS,
            recipients=["recipient1"],
            message_type=MessageType.ANALYSIS,
            priority=MessagePriority.NORMAL,
            content="Test content"
        )
        
        self.assertEqual(msg.sender, "test_agent")
        self.assertEqual(msg.sender_group, AgentGroup.ANALYSTS)
        self.assertEqual(msg.recipients, ["recipient1"])
        self.assertEqual(msg.message_type, MessageType.ANALYSIS)
        self.assertEqual(msg.priority, MessagePriority.NORMAL)
        self.assertEqual(msg.content, "Test content")
    
    def test_message_to_dict(self):
        """Test message serialization"""
        msg = MGCAMessage(
            sender="test_agent",
            sender_group=AgentGroup.ANALYSTS,
            recipients=["recipient1"],
            message_type=MessageType.ANALYSIS,
            priority=MessagePriority.NORMAL,
            content="Test content"
        )
        
        msg_dict = msg.to_dict()
        
        self.assertIn("sender", msg_dict)
        self.assertIn("message_type", msg_dict)
        self.assertIn("priority", msg_dict)
        self.assertEqual(msg_dict["sender"], "test_agent")


class TestMGCACommunicationChannel(unittest.TestCase):
    """Test communication channel functionality"""
    
    def test_channel_creation(self):
        """Test creating a channel"""
        channel = MGCACommunicationChannel("test_channel")
        self.assertEqual(channel.channel_name, "test_channel")
        self.assertEqual(len(channel.subscribers), 0)
        self.assertEqual(len(channel.message_queue), 0)
    
    def test_subscribe_unsubscribe(self):
        """Test subscribing and unsubscribing"""
        channel = MGCACommunicationChannel("test_channel")
        
        channel.subscribe("agent1")
        self.assertIn("agent1", channel.subscribers)
        
        channel.unsubscribe("agent1")
        self.assertNotIn("agent1", channel.subscribers)
    
    def test_publish_and_get_messages(self):
        """Test publishing and retrieving messages"""
        channel = MGCACommunicationChannel("test_channel")
        
        msg = MGCAMessage(
            sender="sender",
            sender_group=AgentGroup.ANALYSTS,
            recipients=["agent1"],
            message_type=MessageType.ANALYSIS,
            priority=MessagePriority.NORMAL,
            content="Test"
        )
        
        channel.publish(msg)
        self.assertEqual(len(channel.message_queue), 1)
        
        messages = channel.get_messages("agent1")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Test")
    
    def test_get_messages_with_clear(self):
        """Test clearing messages after retrieval"""
        channel = MGCACommunicationChannel("test_channel")
        
        msg = MGCAMessage(
            sender="sender",
            sender_group=AgentGroup.ANALYSTS,
            recipients=["agent1"],
            message_type=MessageType.ANALYSIS,
            priority=MessagePriority.NORMAL,
            content="Test"
        )
        
        channel.publish(msg)
        messages = channel.get_messages("agent1", clear=True)
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(len(channel.message_queue), 0)


class TestMGCARouter(unittest.TestCase):
    """Test message router functionality"""
    
    def setUp(self):
        """Set up router for tests"""
        self.router = MGCARouter()
    
    def test_router_initialization(self):
        """Test router initialization"""
        self.assertEqual(len(self.router.channels), 0)
        self.assertEqual(len(self.router.agent_groups), 0)
        self.assertEqual(len(self.router.routing_rules), 0)
    
    def test_create_channel(self):
        """Test creating a channel"""
        channel = self.router.create_channel("test_channel")
        self.assertIn("test_channel", self.router.channels)
        self.assertEqual(channel.channel_name, "test_channel")
    
    def test_register_agent(self):
        """Test registering an agent"""
        self.router.register_agent("agent1", AgentGroup.ANALYSTS)
        self.assertIn("agent1", self.router.agent_groups)
        self.assertEqual(self.router.agent_groups["agent1"], AgentGroup.ANALYSTS)
    
    def test_add_routing_rule(self):
        """Test adding a routing rule"""
        rule = {
            "from_group": AgentGroup.ANALYSTS,
            "message_type": MessageType.ANALYSIS,
            "channel": "analysis"
        }
        self.router.add_routing_rule(rule)
        self.assertEqual(len(self.router.routing_rules), 1)
    
    def test_route_message(self):
        """Test routing a message"""
        self.router.register_agent("sender", AgentGroup.ANALYSTS)
        self.router.register_agent("recipient", AgentGroup.TRADERS)
        
        msg = MGCAMessage(
            sender="sender",
            sender_group=AgentGroup.ANALYSTS,
            recipients=["recipient"],
            message_type=MessageType.ANALYSIS,
            priority=MessagePriority.NORMAL,
            content="Test"
        )
        
        self.router.route_message(msg)
        self.assertIn("default", self.router.channels)
    
    def test_broadcast(self):
        """Test broadcasting a message"""
        self.router.register_agent("agent1", AgentGroup.ANALYSTS)
        self.router.register_agent("agent2", AgentGroup.TRADERS)
        
        msg = MGCAMessage(
            sender="system",
            sender_group=AgentGroup.SYSTEM,
            recipients=[],
            message_type=MessageType.BROADCAST,
            priority=MessagePriority.HIGH,
            content="Broadcast test"
        )
        
        self.router.broadcast(msg, target_groups=[AgentGroup.ANALYSTS])
        self.assertEqual(msg.recipients, ["agent1"])


class TestMGCAConsensusEngine(unittest.TestCase):
    """Test consensus engine functionality"""
    
    def setUp(self):
        """Set up consensus engine for tests"""
        self.engine = MGCAConsensusEngine()
    
    def test_create_session(self):
        """Test creating a consensus session"""
        self.engine.create_session(
            session_id="test_session",
            participants=["agent1", "agent2", "agent3"],
            topic="Test topic",
            voting_threshold=0.6
        )
        
        self.assertIn("test_session", self.engine.consensus_sessions)
        session = self.engine.consensus_sessions["test_session"]
        self.assertEqual(len(session["participants"]), 3)
        self.assertEqual(session["topic"], "Test topic")
    
    def test_cast_vote(self):
        """Test casting a vote"""
        self.engine.create_session(
            session_id="test_session",
            participants=["agent1", "agent2"],
            topic="Test",
            voting_threshold=0.5
        )
        
        self.engine.cast_vote("test_session", "agent1", "YES", weight=1.0)
        session = self.engine.consensus_sessions["test_session"]
        self.assertIn("agent1", session["votes"])
    
    def test_consensus_reached(self):
        """Test consensus detection"""
        self.engine.create_session(
            session_id="test_session",
            participants=["agent1", "agent2", "agent3"],
            topic="Test",
            voting_threshold=0.6
        )
        
        # Cast votes - 2 out of 3 vote YES (66% > 60%)
        self.engine.cast_vote("test_session", "agent1", "YES", weight=1.0)
        self.engine.cast_vote("test_session", "agent2", "YES", weight=1.0)
        self.engine.cast_vote("test_session", "agent3", "NO", weight=1.0)
        
        consensus = self.engine.get_consensus("test_session")
        self.assertEqual(consensus, "YES")
    
    def test_no_consensus(self):
        """Test when consensus is not reached"""
        self.engine.create_session(
            session_id="test_session",
            participants=["agent1", "agent2"],
            topic="Test",
            voting_threshold=0.8  # 80% threshold
        )
        
        # Cast votes - 1 out of 2 vote YES (50% < 80%)
        self.engine.cast_vote("test_session", "agent1", "YES", weight=1.0)
        self.engine.cast_vote("test_session", "agent2", "NO", weight=1.0)
        
        consensus = self.engine.get_consensus("test_session")
        self.assertIsNone(consensus)


class TestMGCACoordinator(unittest.TestCase):
    """Test MGCA coordinator functionality"""
    
    def setUp(self):
        """Set up coordinator for tests"""
        self.coordinator = MGCACoordinator()
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization"""
        self.assertIsNotNone(self.coordinator.router)
        self.assertIsNotNone(self.coordinator.consensus_engine)
    
    def test_setup_default_channels(self):
        """Test setting up default channels"""
        self.coordinator.setup_default_channels()
        
        expected_channels = ["default", "analysis", "signals", "risk_alerts", "consensus", "urgent"]
        for channel in expected_channels:
            self.assertIn(channel, self.coordinator.router.channels)
    
    def test_setup_default_routing_rules(self):
        """Test setting up default routing rules"""
        self.coordinator.setup_default_routing_rules()
        self.assertGreater(len(self.coordinator.router.routing_rules), 0)
    
    def test_full_initialization(self):
        """Test full system initialization"""
        self.coordinator.initialize()
        
        # Check channels are created
        self.assertGreater(len(self.coordinator.router.channels), 0)
        
        # Check routing rules are set
        self.assertGreater(len(self.coordinator.router.routing_rules), 0)
    
    def test_get_stats(self):
        """Test getting system statistics"""
        self.coordinator.initialize()
        stats = self.coordinator.get_stats()
        
        self.assertIn("channels", stats)
        self.assertIn("registered_agents", stats)
        self.assertIn("routing_rules", stats)
        self.assertIn("active_consensus_sessions", stats)


class TestMGCAGraphEnhancer(unittest.TestCase):
    """Test graph enhancer functionality"""
    
    def setUp(self):
        """Set up graph enhancer for tests"""
        config = {"mgca_enabled": True}
        self.enhancer = MGCAGraphEnhancer(config)
    
    def test_enhancer_initialization(self):
        """Test enhancer initialization"""
        self.assertIsNotNone(self.enhancer.coordinator)
        self.assertIsNotNone(self.enhancer.adapter)
        self.assertTrue(self.enhancer.enabled)
    
    def test_disabled_enhancer(self):
        """Test enhancer when disabled"""
        config = {"mgca_enabled": False}
        enhancer = MGCAGraphEnhancer(config)
        self.assertFalse(enhancer.enabled)
    
    def test_create_cross_agent_query(self):
        """Test creating a cross-agent query"""
        correlation_id = self.enhancer.create_cross_agent_query(
            sender="trader",
            recipients=["market_analyst"],
            query="Test query",
            priority=MessagePriority.HIGH
        )
        
        self.assertIsNotNone(correlation_id)
        self.assertTrue(len(correlation_id) > 0)
    
    def test_broadcast_alert(self):
        """Test broadcasting an alert"""
        # Should not raise an exception
        self.enhancer.broadcast_alert(
            sender="risk_manager",
            alert_content="Test alert",
            target_groups=[AgentGroup.TRADERS],
            priority=MessagePriority.CRITICAL
        )
    
    def test_get_system_stats(self):
        """Test getting system statistics"""
        stats = self.enhancer.get_system_stats()
        
        self.assertIn("channels", stats)
        self.assertIn("registered_agents", stats)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMGCAMessage))
    suite.addTests(loader.loadTestsFromTestCase(TestMGCACommunicationChannel))
    suite.addTests(loader.loadTestsFromTestCase(TestMGCARouter))
    suite.addTests(loader.loadTestsFromTestCase(TestMGCAConsensusEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestMGCACoordinator))
    suite.addTests(loader.loadTestsFromTestCase(TestMGCAGraphEnhancer))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
