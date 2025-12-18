# TradingAgents/graph/mgca_integration.py
"""
Integration module for MGCA with the existing TradingAgents graph
"""

from typing import Dict, Any, List, Optional
from tradingagents.agents.utils.agent_states import AgentState, InvestDebateState, RiskDebateState
from .mgca import (
    MGCACoordinator,
    MGCAMessage,
    MessageType,
    MessagePriority,
    AgentGroup
)

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger("mgca_integration")


class MGCAStateAdapter:
    """
    Adapter to integrate MGCA with existing AgentState
    """
    
    def __init__(self, coordinator: MGCACoordinator):
        """Initialize the adapter"""
        self.coordinator = coordinator
        logger.info("🔌 MGCA State Adapter initialized")
    
    def extract_analyst_reports(self, state: AgentState) -> List[MGCAMessage]:
        """
        Extract analyst reports from state and convert to MGCA messages
        """
        messages = []
        
        # Market analyst report
        if state.get("market_report"):
            msg = MGCAMessage(
                sender="market_analyst",
                sender_group=AgentGroup.ANALYSTS,
                recipients=["*"],  # Broadcast to all
                message_type=MessageType.ANALYSIS,
                priority=MessagePriority.NORMAL,
                content=state["market_report"],
                metadata={"report_type": "market"}
            )
            messages.append(msg)
        
        # Social media analyst report
        if state.get("sentiment_report"):
            msg = MGCAMessage(
                sender="social_analyst",
                sender_group=AgentGroup.ANALYSTS,
                recipients=["*"],
                message_type=MessageType.ANALYSIS,
                priority=MessagePriority.NORMAL,
                content=state["sentiment_report"],
                metadata={"report_type": "sentiment"}
            )
            messages.append(msg)
        
        # News analyst report
        if state.get("news_report"):
            msg = MGCAMessage(
                sender="news_analyst",
                sender_group=AgentGroup.ANALYSTS,
                recipients=["*"],
                message_type=MessageType.ANALYSIS,
                priority=MessagePriority.NORMAL,
                content=state["news_report"],
                metadata={"report_type": "news"}
            )
            messages.append(msg)
        
        # Fundamentals analyst report
        if state.get("fundamentals_report"):
            msg = MGCAMessage(
                sender="fundamentals_analyst",
                sender_group=AgentGroup.ANALYSTS,
                recipients=["*"],
                message_type=MessageType.ANALYSIS,
                priority=MessagePriority.NORMAL,
                content=state["fundamentals_report"],
                metadata={"report_type": "fundamentals"}
            )
            messages.append(msg)
        
        return messages
    
    def extract_investment_signals(self, state: AgentState) -> List[MGCAMessage]:
        """
        Extract investment signals from debate state
        """
        messages = []
        
        if state.get("investment_debate_state"):
            debate_state = state["investment_debate_state"]
            
            # Bull researcher signal
            if debate_state.get("bull_history"):
                msg = MGCAMessage(
                    sender="bull_researcher",
                    sender_group=AgentGroup.RESEARCHERS,
                    recipients=["trader", "risk_managers"],
                    message_type=MessageType.SIGNAL,
                    priority=MessagePriority.HIGH,
                    content=debate_state["bull_history"],
                    metadata={"signal_type": "bullish"}
                )
                messages.append(msg)
            
            # Bear researcher signal
            if debate_state.get("bear_history"):
                msg = MGCAMessage(
                    sender="bear_researcher",
                    sender_group=AgentGroup.RESEARCHERS,
                    recipients=["trader", "risk_managers"],
                    message_type=MessageType.SIGNAL,
                    priority=MessagePriority.HIGH,
                    content=debate_state["bear_history"],
                    metadata={"signal_type": "bearish"}
                )
                messages.append(msg)
        
        return messages
    
    def extract_risk_alerts(self, state: AgentState) -> List[MGCAMessage]:
        """
        Extract risk management alerts
        """
        messages = []
        
        if state.get("risk_debate_state"):
            risk_state = state["risk_debate_state"]
            
            # Risky manager alert
            if risk_state.get("current_risky_response"):
                msg = MGCAMessage(
                    sender="risky_manager",
                    sender_group=AgentGroup.RISK_MANAGERS,
                    recipients=["trader", "safe_manager", "neutral_manager"],
                    message_type=MessageType.ALERT,
                    priority=MessagePriority.HIGH,
                    content=risk_state["current_risky_response"],
                    metadata={"risk_level": "high"}
                )
                messages.append(msg)
            
            # Safe manager alert
            if risk_state.get("current_safe_response"):
                msg = MGCAMessage(
                    sender="safe_manager",
                    sender_group=AgentGroup.RISK_MANAGERS,
                    recipients=["trader", "risky_manager", "neutral_manager"],
                    message_type=MessageType.ALERT,
                    priority=MessagePriority.NORMAL,
                    content=risk_state["current_safe_response"],
                    metadata={"risk_level": "low"}
                )
                messages.append(msg)
            
            # Neutral manager assessment
            if risk_state.get("current_neutral_response"):
                msg = MGCAMessage(
                    sender="neutral_manager",
                    sender_group=AgentGroup.RISK_MANAGERS,
                    recipients=["trader", "risky_manager", "safe_manager"],
                    message_type=MessageType.ALERT,
                    priority=MessagePriority.NORMAL,
                    content=risk_state["current_neutral_response"],
                    metadata={"risk_level": "medium"}
                )
                messages.append(msg)
        
        return messages
    
    def inject_messages_into_state(self, state: AgentState, messages: List[MGCAMessage]) -> AgentState:
        """
        Inject MGCA messages into the agent state for agents to access
        """
        # Validate state is a dictionary
        if not isinstance(state, dict):
            logger.warning(f"⚠️ State is not a dictionary, cannot inject messages")
            return state
        
        # Create a new field in state for MGCA messages if it doesn't exist
        if "mgca_messages" not in state:
            state["mgca_messages"] = []
        
        # Validate existing field is a list
        if not isinstance(state["mgca_messages"], list):
            logger.warning(f"⚠️ mgca_messages field is not a list, resetting")
            state["mgca_messages"] = []
        
        # Add new messages
        state["mgca_messages"].extend([msg.to_dict() for msg in messages])
        
        return state
    
    def sync_state_to_mgca(self, state: AgentState):
        """
        Synchronize agent state to MGCA system
        Extracts information from state and routes it through MGCA
        """
        # Extract and route analyst reports
        analyst_messages = self.extract_analyst_reports(state)
        for msg in analyst_messages:
            self.coordinator.send_message(msg)
        
        # Extract and route investment signals
        signal_messages = self.extract_investment_signals(state)
        for msg in signal_messages:
            self.coordinator.send_message(msg)
        
        # Extract and route risk alerts
        alert_messages = self.extract_risk_alerts(state)
        for msg in alert_messages:
            self.coordinator.send_message(msg)
        
        total_messages = len(analyst_messages) + len(signal_messages) + len(alert_messages)
        if total_messages > 0:
            logger.info(f"📤 Synced {total_messages} messages from state to MGCA")
    
    def sync_mgca_to_state(self, state: AgentState, agent_id: str) -> AgentState:
        """
        Synchronize MGCA messages back to agent state
        Allows agents to access cross-agent communications
        """
        # Get messages for this agent from all channels
        messages = []
        for channel_name in self.coordinator.router.channels.keys():
            channel_messages = self.coordinator.router.get_messages_for_agent(
                agent_id=agent_id,
                channel=channel_name,
                clear=False  # Don't clear, let multiple agents read
            )
            messages.extend(channel_messages)
        
        if messages:
            state = self.inject_messages_into_state(state, messages)
            logger.info(f"📥 Synced {len(messages)} MGCA messages to state for {agent_id}")
        
        return state


class MGCAGraphEnhancer:
    """
    Enhances the existing trading graph with MGCA capabilities
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the enhancer"""
        self.config = config or {}
        self.coordinator = MGCACoordinator()
        self.adapter = MGCAStateAdapter(self.coordinator)
        self.enabled = self.config.get("mgca_enabled", True)
        
        if self.enabled:
            # Initialize MGCA system
            self.coordinator.initialize()
            
            # Register agents
            self._register_agents()
            
            logger.info("🚀 MGCA Graph Enhancer initialized and ready")
        else:
            logger.info("⏸️ MGCA is disabled in configuration")
    
    def _register_agents(self):
        """Register all agents with the MGCA system"""
        # Analysts
        self.coordinator.router.register_agent("market_analyst", AgentGroup.ANALYSTS)
        self.coordinator.router.register_agent("social_analyst", AgentGroup.ANALYSTS)
        self.coordinator.router.register_agent("news_analyst", AgentGroup.ANALYSTS)
        self.coordinator.router.register_agent("fundamentals_analyst", AgentGroup.ANALYSTS)
        
        # Researchers
        self.coordinator.router.register_agent("bull_researcher", AgentGroup.RESEARCHERS)
        self.coordinator.router.register_agent("bear_researcher", AgentGroup.RESEARCHERS)
        
        # Traders
        self.coordinator.router.register_agent("trader", AgentGroup.TRADERS)
        
        # Risk managers
        self.coordinator.router.register_agent("risky_manager", AgentGroup.RISK_MANAGERS)
        self.coordinator.router.register_agent("safe_manager", AgentGroup.RISK_MANAGERS)
        self.coordinator.router.register_agent("neutral_manager", AgentGroup.RISK_MANAGERS)
        
        logger.info("✅ Registered 10 agents with MGCA system")
    
    def enhance_node(self, node_func):
        """
        Decorator to enhance a graph node with MGCA capabilities
        """
        def enhanced_node(state: AgentState, *args, **kwargs):
            if not self.enabled:
                return node_func(state, *args, **kwargs)
            
            # Get agent ID from state or function name
            agent_id = state.get("sender", node_func.__name__)
            
            # Sync MGCA messages to state before node execution
            state = self.adapter.sync_mgca_to_state(state, agent_id)
            
            # Execute original node
            result = node_func(state, *args, **kwargs)
            
            # Sync state back to MGCA after node execution
            if isinstance(result, dict):
                self.adapter.sync_state_to_mgca(result)
            
            return result
        
        return enhanced_node
    
    def create_cross_agent_query(
        self, 
        sender: str, 
        recipients: List[str], 
        query: str,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """
        Create a cross-agent query message
        Returns a correlation ID for tracking responses
        """
        import uuid
        correlation_id = str(uuid.uuid4())
        
        sender_group = self.coordinator.router.agent_groups.get(sender, AgentGroup.SYSTEM)
        
        message = MGCAMessage(
            sender=sender,
            sender_group=sender_group,
            recipients=recipients,
            message_type=MessageType.QUERY,
            priority=priority,
            content=query,
            requires_response=True,
            correlation_id=correlation_id
        )
        
        try:
            self.coordinator.send_message(message)
            logger.info(f"❓ Cross-agent query sent from {sender} to {', '.join(recipients)}")
        except Exception as e:
            logger.error(f"❌ Failed to send cross-agent query: {e}")
            raise
        
        return correlation_id
    
    def send_response(
        self, 
        sender: str, 
        recipient: str, 
        response: str,
        correlation_id: str,
        priority: MessagePriority = MessagePriority.NORMAL
    ):
        """
        Send a response to a query
        """
        sender_group = self.coordinator.router.agent_groups.get(sender, AgentGroup.SYSTEM)
        
        message = MGCAMessage(
            sender=sender,
            sender_group=sender_group,
            recipients=[recipient],
            message_type=MessageType.RESPONSE,
            priority=priority,
            content=response,
            correlation_id=correlation_id
        )
        
        self.coordinator.send_message(message)
        logger.info(f"💬 Response sent from {sender} to {recipient}")
    
    def broadcast_alert(
        self, 
        sender: str, 
        alert_content: str,
        target_groups: Optional[List[AgentGroup]] = None,
        priority: MessagePriority = MessagePriority.HIGH
    ):
        """
        Broadcast an alert to all agents or specific groups
        """
        sender_group = self.coordinator.router.agent_groups.get(sender, AgentGroup.SYSTEM)
        
        message = MGCAMessage(
            sender=sender,
            sender_group=sender_group,
            recipients=["*"],
            message_type=MessageType.ALERT,
            priority=priority,
            content=alert_content
        )
        
        self.coordinator.broadcast(message, target_groups)
        logger.info(f"🚨 Alert broadcast from {sender}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get MGCA system statistics"""
        return self.coordinator.get_stats()
