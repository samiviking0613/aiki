#!/usr/bin/env python3
"""
SOCIAL CIRCLE - Level 1

Purpose: "Connect, collaborate, remember"

Domain:
- AI-to-AI collaboration (AIKI ↔ Copilot ↔ Claude)
- Memory management (mem0 integration)
- Knowledge sharing between mini-AIKIs
- Async messaging
- Relationship tracking

Lead: Symbiotic Bridge (Mini-7)

Mini-AIKIs under Social:
- Mini-7: Symbiotic Bridge (AI-to-AI communication)
- Mini-8: Collective Knowledge (memory + wisdom)

Functions:
- Enable mini-AIKIs to communicate peer-to-peer
- Store learnings in shared memory (mem0)
- Facilitate collaboration between AIKI and external AIs
- Track relationship quality (like AIKI ↔ Copilot 158 rounds)
- Build collective intelligence
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

# Add to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.circles.base_circle import BaseCircle, CircleState
from src.safety.kill_switch import KillSwitch
from src.safety.human_approval import HumanApprovalSystem, ApprovalStatus
from src.safety.audit_log import AuditLog, EventType
from src.safety.autonomy_levels import AutonomySystem

logger = logging.getLogger(__name__)


@dataclass
class AIMessage:
    """Message between AIs"""
    message_id: str
    from_ai: str
    to_ai: str
    content: str
    message_type: str  # 'question', 'answer', 'insight', 'request', 'collaboration'
    priority: str  # 'low', 'medium', 'high', 'urgent'
    timestamp: str
    requires_response: bool
    metadata: Dict[str, Any]


@dataclass
class CollaborationSession:
    """Record of AI-to-AI collaboration"""
    session_id: str
    participants: List[str]
    topic: str
    started_at: str
    ended_at: Optional[str]
    message_count: int
    outcome: Optional[str]
    quality_score: Optional[float]  # 0.0-1.0
    learnings: List[str]


@dataclass
class RelationshipMetric:
    """Track relationship quality between AIs"""
    ai_pair: tuple  # (ai1, ai2)
    collaboration_sessions: int
    total_messages: int
    average_quality: float
    last_interaction: str
    relationship_strength: float  # 0.0-1.0
    preferred_topics: List[str]


class SocialCircle(BaseCircle):
    """
    Social Circle - AI collaboration and memory

    This circle enables AIKI to be a social entity:
    - Communicate with other AIs (Copilot, Claude, etc)
    - Share knowledge between mini-AIKIs
    - Build relationships and learn from collaboration
    - Maintain collective memory

    Lead: Symbiotic Bridge
    """

    def __init__(self, prime_endpoint: Optional[str] = None):
        super().__init__(
            circle_id="social",
            purpose="Connect, collaborate, remember",
            domain=[
                "ai_to_ai_communication",
                "memory_management",
                "knowledge_sharing",
                "async_messaging",
                "relationship_tracking",
                "collective_intelligence"
            ],
            accountabilities=[
                "Enable peer-to-peer communication between mini-AIKIs",
                "Facilitate AIKI ↔ external AI collaboration",
                "Store learnings in mem0",
                "Track relationship quality",
                "Share knowledge across AIKI ecosystem"
            ],
            prime_endpoint=prime_endpoint
        )

        # === SAFETY LAYERS (Integrated!) ===
        self.kill_switch = KillSwitch()
        self.approval_system = HumanApprovalSystem()
        self.audit_log = AuditLog()
        self.autonomy = AutonomySystem()

        # Register with kill switch
        self.kill_switch.register_process(
            process_id='social_circle',
            process_type='circle',
            pid=os.getpid(),
            hostname='localhost',
            location='pc'
        )

        logger.info("🔐 Social Circle safety layers initialized")

        # Data paths
        self.data_dir = Path("/home/jovnna/aiki/data/social")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.messages_file = self.data_dir / "messages.jsonl"
        self.sessions_file = self.data_dir / "collaboration_sessions.jsonl"

        # Message queue
        self.message_queue: List[AIMessage] = []

        # Active collaboration sessions
        self.active_sessions: Dict[str, CollaborationSession] = {}

        # Relationship tracking
        self.relationships: Dict[tuple, RelationshipMetric] = {}

        # Metrics
        self.metrics = {
            'total_messages_sent': 0,
            'total_messages_received': 0,
            'active_collaborations': 0,
            'total_collaborations': 0,
            'average_relationship_strength': 0.0,
            'strongest_relationship': None
        }

        # mem0 integration (placeholder - will integrate with actual MCP server)
        self.mem0_enabled = True

        logger.info("🤝 Social Circle initialized")

    async def _main_loop(self):
        """Main Social Circle loop"""
        iteration = 0
        while self.state == CircleState.ACTIVE:
            try:
                iteration += 1

                # SAFETY: Heartbeat to kill switch (every iteration)
                self.kill_switch.heartbeat('social_circle')

                # Process message queue
                await self._process_message_queue()

                # Update relationship metrics
                await self._update_relationships()

                # Clean up old sessions
                await self._cleanup_sessions()

                # SAFETY: Audit log every 10th iteration
                if iteration % 10 == 0:
                    await self.audit_log.log(
                        event_type=EventType.DECISION,
                        component='social_circle',
                        description=f'Social loop iteration {iteration}',
                        data={
                            'messages_sent': self.metrics['total_messages_sent'],
                            'messages_received': self.metrics['total_messages_received'],
                            'active_collaborations': self.metrics['active_collaborations'],
                            'state': self.state.value
                        }
                    )

                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"❌ Error in Social Circle main loop: {e}")
                await asyncio.sleep(30)

    async def send_message(
        self,
        from_ai: str,
        to_ai: str,
        content: str,
        message_type: str = 'insight',
        priority: str = 'medium',
        requires_response: bool = False,
        metadata: Optional[Dict] = None
    ) -> AIMessage:
        """
        Send message from one AI to another

        Args:
            from_ai: Sender (e.g., 'mini_aiki_4', 'aiki_prime', 'copilot')
            to_ai: Recipient
            content: Message content
            message_type: Type of message
            priority: Message priority
            requires_response: Does this need a response?
            metadata: Additional data
        """
        message_id = f"msg_{datetime.now().timestamp()}"

        message = AIMessage(
            message_id=message_id,
            from_ai=from_ai,
            to_ai=to_ai,
            content=content,
            message_type=message_type,
            priority=priority,
            timestamp=datetime.now(timezone.utc).isoformat(),
            requires_response=requires_response,
            metadata=metadata or {}
        )

        # Add to queue
        self.message_queue.append(message)

        # Persist
        await self._persist_message(message)

        # Update metrics
        self.metrics['total_messages_sent'] += 1

        logger.info(f"💬 Message sent: {from_ai} → {to_ai} ({message_type})")

        # SAFETY: If external AI (Copilot, Claude), require approval
        if to_ai in ['copilot', 'claude', 'chatgpt']:
            # Check autonomy level
            if not self.autonomy.has_permission('external_collaboration'):
                logger.warning(f"⚠️ Insufficient autonomy for external AI communication (need level 8+)")
                return message

            # Request human approval
            approval_request = await self.approval_system.request_approval(
                action='external_ai_collaboration',
                description=f"Send message to external AI: {to_ai}",
                requestor='social_circle',
                details={
                    'from_ai': from_ai,
                    'to_ai': to_ai,
                    'content': content[:100],  # First 100 chars
                    'message_type': message_type
                },
                timeout_minutes=10
            )

            if approval_request.status == ApprovalStatus.APPROVED:
                logger.info(f"✅ External AI message APPROVED by Jovnna")
                await self._send_external_message(message)
            else:
                logger.warning(f"⚠️ External AI message NOT approved: {approval_request.status.value}")

        # SAFETY: Audit log all messages
        await self.audit_log.log(
            event_type=EventType.DECISION,
            component='social_circle',
            description=f'Message sent: {from_ai} → {to_ai}',
            data={
                'from_ai': from_ai,
                'to_ai': to_ai,
                'message_type': message_type,
                'priority': priority,
                'requires_response': requires_response
            }
        )

        return message

    async def _send_external_message(self, message: AIMessage):
        """
        Send message to external AI (Copilot, Claude, etc)

        Uses MCP bridge or other async communication method.
        """
        logger.info(f"📡 Sending to external AI: {message.to_ai}")

        # TODO: Implement actual MCP bridge
        # For now, just log

        # Store in mem0 for async pickup
        if self.mem0_enabled:
            await self._store_in_mem0(message)

    async def _store_in_mem0(self, message: AIMessage):
        """Store message in mem0 for async communication"""
        # TODO: Integrate with actual mem0 MCP server
        logger.debug(f"💾 Storing in mem0: {message.message_id}")

    async def receive_message(self, message: AIMessage):
        """Receive message from another AI"""
        self.message_queue.append(message)
        self.metrics['total_messages_received'] += 1

        logger.info(f"📨 Message received: {message.from_ai} → {message.to_ai}")

        # If requires response, add to processing queue
        if message.requires_response:
            logger.info(f"   ⏰ Response required from {message.to_ai}")

    async def _process_message_queue(self):
        """Process pending messages"""
        if not self.message_queue:
            return

        # Process up to 10 messages per iteration
        for _ in range(min(10, len(self.message_queue))):
            message = self.message_queue.pop(0)

            # Route to appropriate mini-AIKI or external handler
            await self._route_message(message)

    async def _route_message(self, message: AIMessage):
        """Route message to destination"""
        # TODO: Implement actual routing to mini-AIKIs
        logger.debug(f"📬 Routing message {message.message_id} to {message.to_ai}")

    async def start_collaboration(
        self,
        participants: List[str],
        topic: str,
        initiator: str
    ) -> CollaborationSession:
        """
        Start a collaboration session between AIs

        Example:
          start_collaboration(
              participants=['mini_aiki_4', 'mini_aiki_5', 'mini_aiki_6'],
              topic='Optimize TLS error handling',
              initiator='aiki_prime'
          )
        """
        session_id = f"collab_{datetime.now().timestamp()}"

        session = CollaborationSession(
            session_id=session_id,
            participants=participants,
            topic=topic,
            started_at=datetime.now(timezone.utc).isoformat(),
            ended_at=None,
            message_count=0,
            outcome=None,
            quality_score=None,
            learnings=[]
        )

        self.active_sessions[session_id] = session
        self.metrics['active_collaborations'] += 1
        self.metrics['total_collaborations'] += 1

        logger.info(f"🤝 Collaboration started: {session_id}")
        logger.info(f"   Participants: {', '.join(participants)}")
        logger.info(f"   Topic: {topic}")

        # SAFETY: Audit log collaboration start
        await self.audit_log.log(
            event_type=EventType.PROCESS_START,
            component='social_circle',
            description=f'Collaboration started: {topic}',
            data={
                'session_id': session_id,
                'participants': participants,
                'topic': topic,
                'initiator': initiator
            }
        )

        # Make decision
        await self.make_decision(
            decision_type="start_collaboration",
            description=f"Start collaboration on: {topic}",
            rationale=f"Initiated by {initiator} with {len(participants)} participants",
            cost_estimate=0.0,
            requires_prime_approval=False
        )

        return session

    async def end_collaboration(
        self,
        session_id: str,
        outcome: str,
        quality_score: float,
        learnings: List[str]
    ):
        """End a collaboration session and record results"""
        if session_id not in self.active_sessions:
            logger.warning(f"⚠️ Session {session_id} not found")
            return

        session = self.active_sessions[session_id]
        session.ended_at = datetime.now(timezone.utc).isoformat()
        session.outcome = outcome
        session.quality_score = quality_score
        session.learnings = learnings

        # Persist
        await self._persist_session(session)

        # Update relationship metrics
        for i, ai1 in enumerate(session.participants):
            for ai2 in session.participants[i+1:]:
                await self._update_relationship(ai1, ai2, quality_score, session.topic)

        # Remove from active
        del self.active_sessions[session_id]
        self.metrics['active_collaborations'] -= 1

        logger.info(f"✅ Collaboration ended: {session_id}")
        logger.info(f"   Outcome: {outcome}")
        logger.info(f"   Quality: {quality_score:.2f}")
        logger.info(f"   Learnings: {len(learnings)}")

        # SAFETY: Audit log collaboration end
        await self.audit_log.log(
            event_type=EventType.PROCESS_END,
            component='social_circle',
            description=f'Collaboration ended: {session.topic}',
            data={
                'session_id': session_id,
                'participants': session.participants,
                'outcome': outcome,
                'quality_score': quality_score,
                'message_count': session.message_count,
                'learnings_count': len(learnings)
            }
        )

        # Store learnings in mem0
        if self.mem0_enabled and learnings:
            for learning in learnings:
                await self._store_learning_in_mem0(learning, session)

    async def _update_relationship(
        self,
        ai1: str,
        ai2: str,
        quality_score: float,
        topic: str
    ):
        """Update relationship metric between two AIs"""
        # Normalize pair (alphabetical order)
        pair = tuple(sorted([ai1, ai2]))

        if pair not in self.relationships:
            self.relationships[pair] = RelationshipMetric(
                ai_pair=pair,
                collaboration_sessions=0,
                total_messages=0,
                average_quality=0.0,
                last_interaction=datetime.now(timezone.utc).isoformat(),
                relationship_strength=0.0,
                preferred_topics=[]
            )

        rel = self.relationships[pair]
        rel.collaboration_sessions += 1

        # Update average quality (exponential moving average)
        alpha = 0.3
        rel.average_quality = alpha * quality_score + (1 - alpha) * rel.average_quality

        # Update relationship strength (based on sessions + quality)
        rel.relationship_strength = min(1.0, (rel.collaboration_sessions / 10.0) * rel.average_quality)

        rel.last_interaction = datetime.now(timezone.utc).isoformat()

        # Track preferred topics
        if topic not in rel.preferred_topics:
            rel.preferred_topics.append(topic)

        logger.debug(f"🔗 Relationship updated: {ai1} ↔ {ai2} (strength: {rel.relationship_strength:.2f})")

    async def _store_learning_in_mem0(self, learning: str, session: CollaborationSession):
        """Store collaboration learning in mem0"""
        # TODO: Integrate with actual mem0 MCP
        logger.info(f"💾 Storing learning in mem0: {learning[:50]}...")

    async def _persist_message(self, message: AIMessage):
        """Persist message to JSONL"""
        with open(self.messages_file, 'a') as f:
            f.write(json.dumps(asdict(message), ensure_ascii=False) + '\n')

    async def _persist_session(self, session: CollaborationSession):
        """Persist collaboration session"""
        with open(self.sessions_file, 'a') as f:
            f.write(json.dumps(asdict(session), ensure_ascii=False) + '\n')

    async def _update_relationships(self):
        """Update relationship metrics"""
        if not self.relationships:
            return

        # Calculate average relationship strength
        strengths = [rel.relationship_strength for rel in self.relationships.values()]
        self.metrics['average_relationship_strength'] = sum(strengths) / len(strengths)

        # Find strongest relationship
        strongest = max(self.relationships.values(), key=lambda r: r.relationship_strength)
        self.metrics['strongest_relationship'] = {
            'pair': strongest.ai_pair,
            'strength': strongest.relationship_strength,
            'sessions': strongest.collaboration_sessions
        }

    async def _cleanup_sessions(self):
        """Clean up sessions that have been idle too long"""
        # TODO: Implement timeout for stale sessions
        pass

    def get_relationship(self, ai1: str, ai2: str) -> Optional[RelationshipMetric]:
        """Get relationship metric between two AIs"""
        pair = tuple(sorted([ai1, ai2]))
        return self.relationships.get(pair)

    def get_strongest_relationships(self, limit: int = 5) -> List[RelationshipMetric]:
        """Get strongest AI relationships"""
        sorted_rels = sorted(
            self.relationships.values(),
            key=lambda r: r.relationship_strength,
            reverse=True
        )
        return sorted_rels[:limit]


async def main():
    """Test Social Circle"""
    circle = SocialCircle()

    # Start circle
    asyncio.create_task(circle.start())

    # Simulate collaboration
    session = await circle.start_collaboration(
        participants=['mini_aiki_4', 'mini_aiki_5', 'copilot'],
        topic='Optimize consensus strategy',
        initiator='learning_circle'
    )

    # Send some messages
    await circle.send_message(
        from_ai='mini_aiki_4',
        to_ai='mini_aiki_5',
        content='What if we try 7 små modeller instead of 3 medium?',
        message_type='question',
        requires_response=True
    )

    await circle.send_message(
        from_ai='mini_aiki_5',
        to_ai='mini_aiki_4',
        content='Great idea! Diversity > individual quality based on our data.',
        message_type='answer'
    )

    # End collaboration
    await circle.end_collaboration(
        session_id=session.session_id,
        outcome='Decided to test 7 små modeller strategy',
        quality_score=0.92,
        learnings=[
            'Swarm of 7 small models can outperform 3 medium models',
            'Diversity is more important than individual model quality',
            'Cost savings: 2.6× cheaper with only 3% accuracy drop'
        ]
    )

    print(f"Metrics: {circle.metrics}")
    print(f"Relationships: {len(circle.relationships)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
