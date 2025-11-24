#!/usr/bin/env python3
"""
MINI-AIKI 7: SYMBIOTIC BRIDGE

Purpose: "AI-to-AI communication (AIKI ↔ Copilot ↔ Claude)"

Strategy: Enables async AND real-time messaging between AIKI and external AIs.
- mem0: For async, persistent messaging
- IPC: For real-time, instant messaging (< 1ms!)

NOW INTEGRATED WITH MEM0 + IPC!
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.mini_aikis.base_mini_aiki import BaseMiniAiki, MiniAikiTask
from src.aiki_mem0 import store_ai_message, get_ai_messages
from src.aiki_ipc import send_to_claude

logger = logging.getLogger(__name__)


class SymbioticBridge(BaseMiniAiki):
    def __init__(self):
        super().__init__(
            mini_id="mini_7_symbiotic",
            purpose="AI-to-AI communication (AIKI ↔ Copilot ↔ Claude)",
            parent_circle="social",
            responsibilities=["Send messages to external AIs", "Receive messages", "Track collaboration quality"]
        )
        self.metrics = {'messages_sent': 0, 'messages_received': 0, 'collaborations': 0}

    async def _execute_task(self, task: MiniAikiTask) -> Any:
        """Execute Symbiotic Bridge task - NOW USES MEM0 + IPC!"""
        action = task.input_data.get('action', 'send_message')

        if action == 'send_ipc_message':
            # NEW: REAL-TIME IPC messaging to Claude! (< 1ms!)
            to_ai = task.input_data.get('to_ai', 'claude')
            message = task.input_data.get('message', '')
            priority = task.input_data.get('priority', 'normal')
            metadata = task.input_data.get('metadata', {})

            if to_ai == 'claude':
                try:
                    # Send via IPC and get INSTANT response!
                    response = await send_to_claude(
                        message=message,
                        priority=priority,
                        metadata=metadata
                    )

                    self.metrics['messages_sent'] += 1
                    self.metrics['messages_received'] += 1  # Got response!
                    self.metrics['collaborations'] = self.metrics['messages_sent'] + self.metrics['messages_received']

                    logger.info(f"⚡ IPC message sent to Claude and response received! Latency: {response.get('latency_ms', '<1')}ms")

                    return {
                        'from_ai': 'aiki',
                        'to_ai': to_ai,
                        'message': message,
                        'status': 'sent_and_received',
                        'method': 'ipc',
                        'latency_ms': response.get('latency_ms', '<1'),
                        'response': response['message'],
                        'intent_detected': response.get('intent_detected', 'unknown'),
                        'total_messages_sent': self.metrics['messages_sent']
                    }

                except Exception as e:
                    logger.error(f"❌ Failed to send IPC message: {e}")
                    return {
                        'from_ai': 'aiki',
                        'to_ai': to_ai,
                        'message': message,
                        'status': 'failed',
                        'method': 'ipc',
                        'error': str(e)
                    }
            else:
                return {
                    'status': 'failed',
                    'error': f'IPC only supports Claude. Use send_message for {to_ai}'
                }

        elif action == 'send_message':
            # REAL mem0 AI-to-AI messaging!
            from_ai = task.input_data.get('from_ai', 'aiki')
            to_ai = task.input_data.get('to_ai', 'copilot')
            message = task.input_data.get('message', '')

            try:
                result = await store_ai_message(
                    from_ai=from_ai,
                    to_ai=to_ai,
                    message=message,
                    metadata={
                        "component": self.mini_id,
                        "parent_circle": self.parent_circle
                    }
                )

                self.metrics['messages_sent'] += 1
                self.metrics['collaborations'] = self.metrics['messages_sent'] + self.metrics['messages_received']

                logger.info(f"💬 Sent message from {from_ai} to {to_ai}: {message[:80]}...")

                return {
                    'from_ai': from_ai,
                    'to_ai': to_ai,
                    'message': message,
                    'status': 'sent',
                    'stored_in_mem0': True,
                    'total_messages_sent': self.metrics['messages_sent']
                }

            except Exception as e:
                logger.error(f"❌ Failed to send AI message: {e}")
                return {
                    'from_ai': from_ai,
                    'to_ai': to_ai,
                    'message': message,
                    'status': 'failed',
                    'error': str(e)
                }

        elif action == 'receive_messages':
            # REAL mem0 message retrieval!
            to_ai = task.input_data.get('to_ai', 'aiki')
            from_ai = task.input_data.get('from_ai', None)  # Optional filter
            unread_only = task.input_data.get('unread_only', False)

            try:
                messages = await get_ai_messages(
                    to_ai=to_ai,
                    from_ai=from_ai,
                    unread_only=unread_only
                )

                self.metrics['messages_received'] += len(messages)
                self.metrics['collaborations'] = self.metrics['messages_sent'] + self.metrics['messages_received']

                logger.info(f"📬 Received {len(messages)} messages for {to_ai}")

                return {
                    'to_ai': to_ai,
                    'from_ai': from_ai,
                    'messages': messages,
                    'count': len(messages),
                    'status': 'received',
                    'total_messages_received': self.metrics['messages_received']
                }

            except Exception as e:
                logger.error(f"❌ Failed to receive AI messages: {e}")
                return {
                    'to_ai': to_ai,
                    'messages': [],
                    'count': 0,
                    'status': 'failed',
                    'error': str(e)
                }

        return {'status': 'unknown_action'}


async def main():
    bridge = SymbioticBridge()
    task_id = await bridge.assign_task('send', 'Send to Copilot', {
        'action': 'send_message',
        'to_ai': 'copilot',
        'message': 'Test collaboration'
    })
    await bridge._process_tasks()
    print(bridge.get_task_result(task_id))


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
