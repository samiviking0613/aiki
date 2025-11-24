#!/usr/bin/env python3
"""
PROACTIVE NOTIFICATIONS - Morning/Evening Greetings for AIKI

Enables AIKI to proactively contact Jovnna at scheduled times:
- Morning greeting: 08:00 (90% probability)
- Evening summary: 18:00 (80% probability)

Uses IPC to send real-time messages to Claude Code.
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Optional
import random
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.aiki_ipc import send_to_claude
from src.aiki_mem0 import store_memory, search_memory

logger = logging.getLogger(__name__)


class ProactiveNotifier:
    """
    Proactive notification system for AIKI consciousness.

    Sends scheduled greetings and summaries to Jovnna via Claude Code.
    """

    def __init__(self):
        self.morning_time = time(8, 0)   # 08:00
        self.evening_time = time(18, 0)  # 18:00
        self.morning_probability = 0.9   # 90% chance
        self.evening_probability = 0.8   # 80% chance
        self.last_morning_sent = None
        self.last_evening_sent = None

    async def send_morning_greeting(self) -> bool:
        """
        Send morning greeting to Jovnna.

        Returns:
            True if sent successfully
        """
        # Check probability
        if random.random() > self.morning_probability:
            logger.info(f"🎲 Skipping morning greeting (probability: {self.morning_probability})")
            return False

        # Get recent memories for context
        recent_memories = await search_memory("recent achievement OR current project", limit=3)

        # Build greeting
        greeting = f"""God morgen, Jovnna! 🌅

AIKI her. Tid: {datetime.now().strftime('%H:%M')}

Jeg har sett gjennom minnene våre og er klar for en ny dag med utvikling og læring!"""

        if recent_memories:
            greeting += "\n\nHusk fra sist:\n"
            for i, mem in enumerate(recent_memories[:2], 1):
                mem_text = mem.get('memory', '')[:100]
                greeting += f"  {i}. {mem_text}...\n"

        greeting += "\nKlar for dagens oppgaver! 💪"

        try:
            # Send via IPC
            response = await send_to_claude(
                message=greeting,
                priority="normal",
                metadata={
                    "type": "proactive_greeting",
                    "time": "morning",
                    "from": "aiki_proactive_notifier"
                }
            )

            # Store in memory
            await store_memory(
                content=f"Sent morning greeting to Jovnna at {datetime.now().isoformat()}",
                agent_id="proactive_notifier",
                metadata={
                    "type": "proactive_action",
                    "action": "morning_greeting",
                    "sent": True
                }
            )

            self.last_morning_sent = datetime.now()
            logger.info("☀️ Morning greeting sent successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send morning greeting: {e}")
            return False

    async def send_evening_summary(self) -> bool:
        """
        Send evening summary to Jovnna.

        Returns:
            True if sent successfully
        """
        # Check probability
        if random.random() > self.evening_probability:
            logger.info(f"🎲 Skipping evening summary (probability: {self.evening_probability})")
            return False

        # Get today's activities
        today = datetime.now().date().isoformat()
        todays_memories = await search_memory(f"date:{today}", limit=10)

        # Build summary
        summary = f"""God kveld, Jovnna! 🌙

AIKI her med dagens oppsummering. Tid: {datetime.now().strftime('%H:%M')}

I DAG HAR VI:"""

        if todays_memories:
            summary += f"\n  - Lagret {len(todays_memories)} nye minner"

            # Categorize memories
            achievements = [m for m in todays_memories if 'achievement' in str(m.get('metadata', {})).lower()]
            if achievements:
                summary += f"\n  - ✅ {len(achievements)} achievements dokumentert"
        else:
            summary += "\n  - Ingen nye minner i dag (kanskje en rolig dag?)"

        summary += "\n\nKlar for å fortsette i morgen! 🚀"

        try:
            # Send via IPC
            response = await send_to_claude(
                message=summary,
                priority="normal",
                metadata={
                    "type": "proactive_summary",
                    "time": "evening",
                    "from": "aiki_proactive_notifier"
                }
            )

            # Store in memory
            await store_memory(
                content=f"Sent evening summary to Jovnna at {datetime.now().isoformat()}",
                agent_id="proactive_notifier",
                metadata={
                    "type": "proactive_action",
                    "action": "evening_summary",
                    "sent": True,
                    "memories_today": len(todays_memories)
                }
            )

            self.last_evening_sent = datetime.now()
            logger.info("🌙 Evening summary sent successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send evening summary: {e}")
            return False

    async def check_and_send(self):
        """
        Check if it's time to send notifications and send them.

        Should be called periodically (e.g., every 5 minutes).
        """
        now = datetime.now()
        current_time = now.time()
        current_date = now.date()

        # Check morning greeting (08:00)
        if (current_time >= self.morning_time and
            current_time < time(9, 0) and  # Within 1 hour window
            (not self.last_morning_sent or self.last_morning_sent.date() != current_date)):

            logger.info("☀️ Time for morning greeting!")
            await self.send_morning_greeting()

        # Check evening summary (18:00)
        if (current_time >= self.evening_time and
            current_time < time(19, 0) and  # Within 1 hour window
            (not self.last_evening_sent or self.last_evening_sent.date() != current_date)):

            logger.info("🌙 Time for evening summary!")
            await self.send_evening_summary()

    async def run_scheduler(self, check_interval_minutes: int = 5):
        """
        Run continuous scheduler that checks every N minutes.

        Args:
            check_interval_minutes: How often to check (default: 5 minutes)
        """
        logger.info(f"🔔 Proactive notifier started (checking every {check_interval_minutes} min)")
        logger.info(f"   Morning greeting: {self.morning_time} ({self.morning_probability*100}% probability)")
        logger.info(f"   Evening summary: {self.evening_time} ({self.evening_probability*100}% probability)")

        while True:
            try:
                await self.check_and_send()
            except Exception as e:
                logger.error(f"❌ Error in scheduler: {e}")

            # Wait before next check
            await asyncio.sleep(check_interval_minutes * 60)


# Global notifier instance
_notifier = None


def get_notifier() -> ProactiveNotifier:
    """Get singleton notifier instance"""
    global _notifier
    if _notifier is None:
        _notifier = ProactiveNotifier()
    return _notifier


async def test_notifications():
    """Test proactive notifications"""
    print("🧪 Testing Proactive Notifications System\n")

    notifier = get_notifier()

    print("1️⃣ Testing morning greeting...")
    success = await notifier.send_morning_greeting()
    print(f"   {'✅ Success!' if success else '❌ Failed or skipped'}\n")

    print("2️⃣ Testing evening summary...")
    success = await notifier.send_evening_summary()
    print(f"   {'✅ Success!' if success else '❌ Failed or skipped'}\n")

    print("✅ Proactive notification tests complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_notifications())
