#!/usr/bin/env python3
"""
AIKI IPC CLIENT - REAL-TIME COMMUNICATION MED CLAUDE

Unix Domain Socket client for instant communication.

NO MORE POLLING! Send message → Get response in < 1ms!

Usage:
    from src.aiki_ipc import send_to_claude

    response = await send_to_claude(
        message="Help! Routing is failing!",
        priority="high"
    )

    print(f"Claude responded: {response['message']}")
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIKIIPCClient:
    """
    Unix Domain Socket client for AIKI to communicate with Claude
    """

    def __init__(self, socket_path: str = "/tmp/claude_aiki.sock"):
        self.socket_path = socket_path

    async def send_message(
        self,
        message: str,
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message to Claude and get instant response

        Args:
            message: The message to send
            priority: "low", "normal", "high", "critical"
            metadata: Optional metadata dict

        Returns:
            Response dict from Claude

        Raises:
            ConnectionError: If Claude IPC server is not running
        """
        try:
            # Connect to Claude IPC server
            reader, writer = await asyncio.open_unix_connection(self.socket_path)

            logger.info(f"📤 Sending message to Claude (priority: {priority})")

            # Build message
            msg = {
                "from": "aiki",
                "to": "claude",
                "message": message,
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }

            # Serialize message
            msg_json = json.dumps(msg)
            msg_bytes = msg_json.encode('utf-8')
            msg_length = len(msg_bytes).to_bytes(4, 'big')

            # Send message (length + data)
            writer.write(msg_length + msg_bytes)
            await writer.drain()

            logger.info(f"✅ Message sent to Claude")

            # Read response length
            response_length_bytes = await reader.readexactly(4)
            response_length = int.from_bytes(response_length_bytes, 'big')

            # Read response data
            response_bytes = await reader.readexactly(response_length)
            response_json = response_bytes.decode('utf-8')

            # Parse response
            response = json.loads(response_json)

            logger.info(f"📥 Received response from Claude")
            logger.info(f"   Latency: {response.get('latency_ms', 'N/A')}ms")
            logger.info(f"   Intent detected: {response.get('intent_detected', 'N/A')}")

            # Close connection
            writer.close()
            await writer.wait_closed()

            return response

        except FileNotFoundError:
            raise ConnectionError(
                f"Claude IPC server not running! Socket not found: {self.socket_path}\n"
                f"Start it with: python3 claude_ipc_server.py"
            )
        except Exception as e:
            logger.error(f"❌ Error sending message to Claude: {e}")
            raise


# Singleton instance
_client = None


def get_ipc_client() -> AIKIIPCClient:
    """Get singleton IPC client"""
    global _client
    if _client is None:
        _client = AIKIIPCClient()
    return _client


async def send_to_claude(
    message: str,
    priority: str = "normal",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to send message to Claude

    Args:
        message: Message text
        priority: "low", "normal", "high", "critical"
        metadata: Optional metadata

    Returns:
        Response from Claude

    Example:
        response = await send_to_claude(
            message="Routing to Haiku is failing 15%!",
            priority="high",
            metadata={"component": "hierarchical_engine"}
        )

        print(f"Claude says: {response['message']}")
    """
    client = get_ipc_client()
    return await client.send_message(message, priority, metadata)


async def test_ipc():
    """Test IPC communication"""
    print("🧪 Testing AIKI → Claude IPC communication...\n")

    try:
        # Test 1: Simple message
        print("📤 Test 1: Sending simple message...")
        response = await send_to_claude(
            message="Hello Claude! This is a test message via IPC.",
            priority="normal"
        )

        print(f"✅ Got response from Claude!")
        print(f"   Latency: {response.get('latency_ms', 'N/A')}ms")
        print(f"   Message: {response['message'][:100]}...\n")

        # Test 2: Help request
        print("📤 Test 2: Sending help request...")
        response = await send_to_claude(
            message="Help! Routing to Haiku is failing 15%. Need immediate assistance!",
            priority="high",
            metadata={"component": "hierarchical_engine", "error_rate": 0.15}
        )

        print(f"✅ Got response from Claude!")
        print(f"   Intent detected: {response.get('intent_detected', 'N/A')}")
        print(f"   Message: {response['message'][:100]}...\n")

        # Test 3: Question
        print("📤 Test 3: Sending question...")
        response = await send_to_claude(
            message="Should I use Sonnet or Haiku for coding tasks? Sonnet is better but 20x more expensive.",
            priority="normal"
        )

        print(f"✅ Got response from Claude!")
        print(f"   Intent detected: {response.get('intent_detected', 'N/A')}")
        print(f"   Message: {response['message'][:100]}...\n")

        print("🎉 All IPC tests passed! Real-time communication working! 🚀\n")

    except ConnectionError as e:
        print(f"❌ Connection error: {e}\n")
        print("Make sure Claude IPC server is running:")
        print("  python3 claude_ipc_server.py\n")
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_ipc())
