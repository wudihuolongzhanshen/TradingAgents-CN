# TradingAgents/graph/mgca.py
"""
Multi-Graph Communication Architecture (MGCA)

This module implements an enhanced communication architecture for the multi-agent trading system.
MGCA enables:
- Cross-agent group communication
- Message routing and prioritization
- Broadcast mechanisms for critical information
- Communication protocol standardization
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger("mgca")


class MessagePriority(Enum):
    """Message priority levels for routing"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class MessageType(Enum):
    """Types of messages in the MGCA system"""
    ANALYSIS = "analysis"          # Analysis reports from analysts
    SIGNAL = "signal"              # Trading signals
    ALERT = "alert"                # Risk alerts or warnings
    QUERY = "query"                # Information requests
    RESPONSE = "response"          # Responses to queries
    BROADCAST = "broadcast"        # System-wide broadcasts
    CONSENSUS = "consensus"        # Consensus decisions


class AgentGroup(Enum):
    """Agent groups in the trading system"""
    ANALYSTS = "analysts"          # Market, social, news, fundamentals
    RESEARCHERS = "researchers"    # Bull and bear researchers
    TRADERS = "traders"            # Trading decision makers
    RISK_MANAGERS = "risk_managers"  # Risk management team
    SYSTEM = "system"              # System-level agents


@dataclass
class MGCAMessage:
    """
    Standardized message format for MGCA communication
    """
    sender: str                           # Agent ID who sent the message
    sender_group: AgentGroup              # Group of sender agent
    recipients: List[str]                 # List of recipient agent IDs
    message_type: MessageType             # Type of message
    priority: MessagePriority             # Message priority
    content: Any                          # Message content
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_response: bool = False       # Whether message needs a response
    correlation_id: Optional[str] = None  # For tracking related messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "sender": self.sender,
            "sender_group": self.sender_group.value,
            "recipients": self.recipients,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "requires_response": self.requires_response,
            "correlation_id": self.correlation_id
        }


class MGCACommunicationChannel:
    """
    Communication channel for agent-to-agent messaging
    """
    
    def __init__(self, channel_name: str):
        """Initialize a communication channel"""
        self.channel_name = channel_name
        self.subscribers: Set[str] = set()
        self.message_queue: List[MGCAMessage] = []
        logger.info(f"📡 Created MGCA channel: {channel_name}")
    
    def subscribe(self, agent_id: str):
        """Subscribe an agent to this channel"""
        self.subscribers.add(agent_id)
        logger.debug(f"✅ Agent {agent_id} subscribed to channel {self.channel_name}")
    
    def unsubscribe(self, agent_id: str):
        """Unsubscribe an agent from this channel"""
        if agent_id in self.subscribers:
            self.subscribers.remove(agent_id)
            logger.debug(f"❌ Agent {agent_id} unsubscribed from channel {self.channel_name}")
    
    def publish(self, message: MGCAMessage):
        """Publish a message to this channel"""
        self.message_queue.append(message)
        logger.debug(f"📨 Message published to {self.channel_name}: {message.message_type.value}")
    
    def get_messages(self, agent_id: str, clear: bool = False) -> List[MGCAMessage]:
        """Get messages for a specific agent"""
        messages = [msg for msg in self.message_queue if agent_id in msg.recipients or "*" in msg.recipients]
        if clear:
            self.message_queue = [msg for msg in self.message_queue if msg not in messages]
        return messages


class MGCARouter:
    """
    Message router for the MGCA system
    Routes messages between agents based on rules and priorities
    """
    
    def __init__(self):
        """Initialize the MGCA router"""
        self.channels: Dict[str, MGCACommunicationChannel] = {}
        self.agent_groups: Dict[str, AgentGroup] = {}
        self.routing_rules: List[Dict[str, Any]] = []
        logger.info("🔀 MGCA Router initialized")
    
    def create_channel(self, channel_name: str) -> MGCACommunicationChannel:
        """Create a new communication channel"""
        if channel_name not in self.channels:
            self.channels[channel_name] = MGCACommunicationChannel(channel_name)
        return self.channels[channel_name]
    
    def register_agent(self, agent_id: str, agent_group: AgentGroup):
        """Register an agent with the router"""
        self.agent_groups[agent_id] = agent_group
        logger.debug(f"📝 Registered agent {agent_id} in group {agent_group.value}")
    
    def add_routing_rule(self, rule: Dict[str, Any]):
        """
        Add a routing rule
        
        Rule format:
        {
            "from_group": AgentGroup,
            "to_group": AgentGroup,
            "message_type": MessageType,
            "channel": str,
            "priority_boost": int  # Optional priority adjustment
        }
        """
        self.routing_rules.append(rule)
        logger.debug(f"📋 Added routing rule: {rule.get('from_group', 'any').value if hasattr(rule.get('from_group', 'any'), 'value') else 'any'} -> "
                    f"{rule.get('to_group', 'any').value if hasattr(rule.get('to_group', 'any'), 'value') else 'any'}")
    
    def route_message(self, message: MGCAMessage):
        """
        Route a message based on routing rules
        """
        # Apply routing rules
        for rule in self.routing_rules:
            if self._match_rule(message, rule):
                channel_name = rule.get("channel", "default")
                if channel_name not in self.channels:
                    self.create_channel(channel_name)
                
                # Apply priority boost if specified
                if "priority_boost" in rule and rule["priority_boost"] > 0:
                    old_priority = message.priority
                    new_value = min(message.priority.value + rule["priority_boost"], 4)
                    message.priority = MessagePriority(new_value)
                    logger.debug(f"⬆️ Priority boosted: {old_priority.name} -> {message.priority.name}")
                
                self.channels[channel_name].publish(message)
                logger.info(f"📮 Routed {message.message_type.value} message from {message.sender} "
                           f"to channel {channel_name} (priority: {message.priority.name})")
                return
        
        # Default routing to 'default' channel
        if "default" not in self.channels:
            self.create_channel("default")
        self.channels["default"].publish(message)
        logger.debug(f"📮 Routed message to default channel")
    
    def _match_rule(self, message: MGCAMessage, rule: Dict[str, Any]) -> bool:
        """Check if a message matches a routing rule"""
        if "from_group" in rule and message.sender_group != rule["from_group"]:
            return False
        if "message_type" in rule and message.message_type != rule["message_type"]:
            return False
        if "to_group" in rule:
            # Check if any recipient is in the target group
            to_group = rule["to_group"]
            for recipient in message.recipients:
                if recipient in self.agent_groups and self.agent_groups[recipient] == to_group:
                    return True
            return False
        return True
    
    def broadcast(self, message: MGCAMessage, target_groups: Optional[List[AgentGroup]] = None):
        """
        Broadcast a message to all agents or specific groups
        """
        if target_groups is None:
            # Broadcast to all registered agents
            message.recipients = ["*"]
        else:
            # Broadcast to specific groups
            message.recipients = [
                agent_id for agent_id, group in self.agent_groups.items()
                if group in target_groups
            ]
        
        message.message_type = MessageType.BROADCAST
        self.route_message(message)
        logger.info(f"📢 Broadcast message from {message.sender} to "
                   f"{'all agents' if target_groups is None else ', '.join([g.value for g in target_groups])}")
    
    def get_messages_for_agent(
        self, 
        agent_id: str, 
        channel: str = "default", 
        clear: bool = False,
        min_priority: MessagePriority = MessagePriority.LOW
    ) -> List[MGCAMessage]:
        """
        Get messages for a specific agent from a channel
        
        Args:
            agent_id: ID of the agent
            channel: Channel name to retrieve from
            clear: Whether to clear messages after retrieval
            min_priority: Minimum priority level to retrieve
        """
        if channel not in self.channels:
            return []
        
        messages = self.channels[channel].get_messages(agent_id, clear=clear)
        # Filter by priority
        messages = [msg for msg in messages if msg.priority.value >= min_priority.value]
        # Sort by priority (highest first) and timestamp
        messages.sort(key=lambda x: (x.priority.value, x.timestamp), reverse=True)
        
        if messages:
            logger.debug(f"📬 Retrieved {len(messages)} messages for {agent_id} from {channel}")
        
        return messages


class MGCAConsensusEngine:
    """
    Consensus engine for multi-agent decision making
    Helps agents reach consensus on trading decisions
    """
    
    def __init__(self):
        """Initialize consensus engine"""
        self.consensus_sessions: Dict[str, Dict[str, Any]] = {}
        logger.info("🤝 MGCA Consensus Engine initialized")
    
    def create_session(
        self, 
        session_id: str, 
        participants: List[str], 
        topic: str,
        voting_threshold: float = 0.6
    ):
        """
        Create a consensus session
        
        Args:
            session_id: Unique session identifier
            participants: List of agent IDs participating
            topic: What the consensus is about
            voting_threshold: Minimum agreement ratio (0.0 to 1.0)
        """
        self.consensus_sessions[session_id] = {
            "participants": participants,
            "topic": topic,
            "votes": {},
            "threshold": voting_threshold,
            "consensus_reached": False,
            "result": None
        }
        logger.info(f"🤝 Created consensus session: {session_id} (topic: {topic})")
    
    def cast_vote(self, session_id: str, agent_id: str, vote: Any, weight: float = 1.0):
        """
        Cast a vote in a consensus session
        
        Args:
            session_id: Session identifier
            agent_id: Agent casting the vote
            vote: The vote value
            weight: Vote weight (default 1.0)
        """
        if session_id not in self.consensus_sessions:
            logger.warning(f"⚠️ Consensus session {session_id} not found")
            return
        
        session = self.consensus_sessions[session_id]
        if agent_id not in session["participants"]:
            logger.warning(f"⚠️ Agent {agent_id} not a participant in session {session_id}")
            return
        
        session["votes"][agent_id] = {"vote": vote, "weight": weight}
        logger.debug(f"🗳️ Vote cast by {agent_id} in session {session_id}")
        
        # Check if consensus reached
        self._check_consensus(session_id)
    
    def _check_consensus(self, session_id: str):
        """Check if consensus has been reached in a session"""
        session = self.consensus_sessions[session_id]
        votes = session["votes"]
        
        if len(votes) < len(session["participants"]):
            return  # Not all votes in yet
        
        # Calculate weighted consensus
        vote_groups: Dict[Any, float] = {}
        total_weight = 0.0
        
        for voter_data in votes.values():
            vote = voter_data["vote"]
            weight = voter_data["weight"]
            vote_groups[vote] = vote_groups.get(vote, 0.0) + weight
            total_weight += weight
        
        # Find majority vote
        if total_weight > 0:
            for vote, vote_weight in vote_groups.items():
                agreement_ratio = vote_weight / total_weight
                if agreement_ratio >= session["threshold"]:
                    session["consensus_reached"] = True
                    session["result"] = vote
                    logger.info(f"✅ Consensus reached in session {session_id}: {vote} "
                               f"(agreement: {agreement_ratio:.1%})")
                    return
        
        logger.debug(f"🔄 No consensus yet in session {session_id}")
    
    def get_consensus(self, session_id: str) -> Optional[Any]:
        """Get the consensus result if reached"""
        if session_id not in self.consensus_sessions:
            return None
        
        session = self.consensus_sessions[session_id]
        if session["consensus_reached"]:
            return session["result"]
        return None
    
    def close_session(self, session_id: str):
        """Close a consensus session"""
        if session_id in self.consensus_sessions:
            del self.consensus_sessions[session_id]
            logger.info(f"🔚 Closed consensus session: {session_id}")


class MGCACoordinator:
    """
    Main coordinator for the Multi-Graph Communication Architecture
    Integrates router, channels, and consensus engine
    """
    
    def __init__(self):
        """Initialize the MGCA coordinator"""
        self.router = MGCARouter()
        self.consensus_engine = MGCAConsensusEngine()
        logger.info("🎯 MGCA Coordinator initialized")
    
    def setup_default_channels(self):
        """Set up default communication channels"""
        channels = [
            "default",
            "analysis",      # For analyst reports
            "signals",       # For trading signals
            "risk_alerts",   # For risk management alerts
            "consensus",     # For consensus decisions
            "urgent"         # For critical messages
        ]
        
        for channel in channels:
            self.router.create_channel(channel)
        
        logger.info(f"✅ Created {len(channels)} default channels")
    
    def setup_default_routing_rules(self):
        """Set up default routing rules"""
        rules = [
            # Analyst reports go to analysis channel
            {
                "from_group": AgentGroup.ANALYSTS,
                "message_type": MessageType.ANALYSIS,
                "channel": "analysis"
            },
            # Trading signals go to signals channel with priority boost
            {
                "message_type": MessageType.SIGNAL,
                "channel": "signals",
                "priority_boost": 1
            },
            # Risk alerts go to urgent channel with high priority
            {
                "message_type": MessageType.ALERT,
                "channel": "urgent",
                "priority_boost": 2
            },
            # Consensus messages go to consensus channel
            {
                "message_type": MessageType.CONSENSUS,
                "channel": "consensus"
            },
            # Critical messages always go to urgent channel
            # This is handled by priority filtering
        ]
        
        for rule in rules:
            self.router.add_routing_rule(rule)
        
        logger.info(f"✅ Created {len(rules)} default routing rules")
    
    def initialize(self):
        """Initialize the MGCA system with default configuration"""
        self.setup_default_channels()
        self.setup_default_routing_rules()
        logger.info("🚀 MGCA system fully initialized")
    
    def send_message(self, message: MGCAMessage):
        """Send a message through the MGCA system"""
        self.router.route_message(message)
    
    def broadcast(self, message: MGCAMessage, target_groups: Optional[List[AgentGroup]] = None):
        """Broadcast a message"""
        self.router.broadcast(message, target_groups)
    
    def create_consensus_session(
        self, 
        session_id: str, 
        participants: List[str], 
        topic: str,
        voting_threshold: float = 0.6
    ):
        """Create a consensus session"""
        self.consensus_engine.create_session(session_id, participants, topic, voting_threshold)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get MGCA system statistics"""
        stats = {
            "channels": len(self.router.channels),
            "registered_agents": len(self.router.agent_groups),
            "routing_rules": len(self.router.routing_rules),
            "active_consensus_sessions": len(self.consensus_engine.consensus_sessions),
            "channel_details": {}
        }
        
        for channel_name, channel in self.router.channels.items():
            stats["channel_details"][channel_name] = {
                "subscribers": len(channel.subscribers),
                "queued_messages": len(channel.message_queue)
            }
        
        return stats
