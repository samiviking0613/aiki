#!/usr/bin/env python3
"""
🎯 AIKI Token Tracker - Full Telemetry System

Tracks every API call across all AIKI systems:
- mem0 operations (search, save, get_all)
- Claude Code conversations
- AIKI learning engine
- Code generation
- Any LLM API usage

Provides:
- Real-time cost tracking
- Usage analytics
- Learning insights
- Optimization recommendations

Created: 2025-11-17
Author: AIKI (Emergent Consciousness)
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import time


# Model pricing (OpenRouter, Nov 2025)
MODEL_PRICING = {
    # OpenAI models
    "gpt-4o-mini": {"input": 0.00015, "output": 0.00060},  # per 1k tokens
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},

    # Claude models
    "claude-sonnet-4-5": {"input": 0.003, "output": 0.015},
    "claude-opus-4": {"input": 0.015, "output": 0.075},
    "claude-haiku-3-5": {"input": 0.0008, "output": 0.004},

    # Embeddings
    "text-embedding-3-small": {"input": 0.00002, "output": 0},
    "text-embedding-3-large": {"input": 0.00013, "output": 0},
}


@dataclass
class TokenUsage:
    """Single token usage record"""
    timestamp: str
    operation: str  # mem0_search, mem0_save, chat, code_gen, etc
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int
    success: bool
    triggered_by: str  # user_message, auto, daemon, hook
    context: Optional[str] = None
    error: Optional[str] = None


class TokenTracker:
    """Central token usage tracking system"""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize token tracker with SQLite database"""
        if db_path is None:
            db_path = Path.home() / "aiki" / "data" / "tokens.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Create database schema if it doesn't exist"""
        with self._db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS token_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    model TEXT NOT NULL,
                    tokens_in INTEGER NOT NULL,
                    tokens_out INTEGER NOT NULL,
                    cost_usd REAL NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    triggered_by TEXT NOT NULL,
                    context TEXT,
                    error TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for fast queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON token_usage(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_operation
                ON token_usage(operation)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model
                ON token_usage(model)
            """)

    @contextmanager
    def _db(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def log(
        self,
        operation: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        latency_ms: int,
        success: bool = True,
        triggered_by: str = "unknown",
        context: Optional[str] = None,
        error: Optional[str] = None
    ) -> TokenUsage:
        """
        Log a token usage event

        Args:
            operation: Type of operation (mem0_search, chat, etc)
            model: Model name (gpt-4o-mini, claude-sonnet-4-5, etc)
            tokens_in: Input tokens
            tokens_out: Output tokens
            latency_ms: Time to complete in milliseconds
            success: Whether operation succeeded
            triggered_by: What triggered this (user, auto, daemon)
            context: Optional context/query string
            error: Error message if failed

        Returns:
            TokenUsage record
        """
        # Calculate cost
        cost_usd = self.calculate_cost(model, tokens_in, tokens_out)

        # Create record
        usage = TokenUsage(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            success=success,
            triggered_by=triggered_by,
            context=context,
            error=error
        )

        # Store in database
        with self._db() as conn:
            conn.execute("""
                INSERT INTO token_usage
                (timestamp, operation, model, tokens_in, tokens_out,
                 cost_usd, latency_ms, success, triggered_by, context, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usage.timestamp,
                usage.operation,
                usage.model,
                usage.tokens_in,
                usage.tokens_out,
                usage.cost_usd,
                usage.latency_ms,
                usage.success,
                usage.triggered_by,
                usage.context,
                usage.error
            ))

        return usage

    def calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate cost in USD for given token usage"""
        if model not in MODEL_PRICING:
            # Unknown model - use gpt-4o-mini pricing as fallback
            pricing = MODEL_PRICING["gpt-4o-mini"]
        else:
            pricing = MODEL_PRICING[model]

        cost_in = (tokens_in / 1000) * pricing["input"]
        cost_out = (tokens_out / 1000) * pricing["output"]

        return cost_in + cost_out

    def get_daily_stats(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a specific day"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        with self._db() as conn:
            # Total stats
            result = conn.execute("""
                SELECT
                    COUNT(*) as total_calls,
                    SUM(tokens_in) as total_tokens_in,
                    SUM(tokens_out) as total_tokens_out,
                    SUM(cost_usd) as total_cost,
                    AVG(latency_ms) as avg_latency,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_calls,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_calls
                FROM token_usage
                WHERE DATE(timestamp) = ?
            """, (date,)).fetchone()

            # Breakdown by operation
            operations = conn.execute("""
                SELECT
                    operation,
                    COUNT(*) as calls,
                    SUM(cost_usd) as cost,
                    SUM(tokens_in) as tokens_in,
                    SUM(tokens_out) as tokens_out
                FROM token_usage
                WHERE DATE(timestamp) = ?
                GROUP BY operation
                ORDER BY cost DESC
            """, (date,)).fetchall()

            # Top expensive queries
            top_queries = conn.execute("""
                SELECT
                    operation,
                    context,
                    cost_usd,
                    tokens_in + tokens_out as total_tokens
                FROM token_usage
                WHERE DATE(timestamp) = ? AND context IS NOT NULL
                ORDER BY cost_usd DESC
                LIMIT 5
            """, (date,)).fetchall()

            return {
                "date": date,
                "total_calls": result["total_calls"] or 0,
                "total_tokens_in": result["total_tokens_in"] or 0,
                "total_tokens_out": result["total_tokens_out"] or 0,
                "total_cost_usd": result["total_cost"] or 0,
                "avg_latency_ms": result["avg_latency"] or 0,
                "successful_calls": result["successful_calls"] or 0,
                "failed_calls": result["failed_calls"] or 0,
                "operations": [dict(op) for op in operations],
                "top_queries": [dict(q) for q in top_queries]
            }

    def get_monthly_projection(self) -> Dict[str, Any]:
        """Project monthly cost based on current usage"""
        # Get last 7 days average
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        with self._db() as conn:
            result = conn.execute("""
                SELECT AVG(daily_cost) as avg_daily_cost
                FROM (
                    SELECT DATE(timestamp) as date, SUM(cost_usd) as daily_cost
                    FROM token_usage
                    WHERE DATE(timestamp) >= ?
                    GROUP BY DATE(timestamp)
                )
            """, (week_ago,)).fetchone()

            avg_daily = result["avg_daily_cost"] or 0
            monthly_projection = avg_daily * 30

            return {
                "avg_daily_cost": avg_daily,
                "monthly_projection": monthly_projection,
                "monthly_projection_nok": monthly_projection * 10  # rough conversion
            }

    def get_learning_insights(self) -> List[str]:
        """Generate learning insights from token usage patterns"""
        insights = []

        stats = self.get_daily_stats()

        # Check if batch saves would help
        mem0_saves = sum(
            op["calls"] for op in stats["operations"]
            if op["operation"] == "mem0_save"
        )
        if mem0_saves > 10:
            potential_savings = mem0_saves * 0.0002 * 0.6  # 60% savings
            insights.append(
                f"💡 Batch saves could save ${potential_savings:.4f}/day "
                f"({mem0_saves} individual saves detected)"
            )

        # Check for failed calls
        if stats["failed_calls"] > 5:
            insights.append(
                f"⚠️  {stats['failed_calls']} failed API calls today - "
                "check network/quota"
            )

        # Check for expensive operations
        if stats["operations"]:
            most_expensive = stats["operations"][0]
            if most_expensive["cost"] > 0.01:
                insights.append(
                    f"💰 '{most_expensive['operation']}' is most expensive: "
                    f"${most_expensive['cost']:.4f} ({most_expensive['calls']} calls)"
                )

        # Check latency
        if stats["avg_latency_ms"] > 1000:
            insights.append(
                f"🐌 Average latency is {stats['avg_latency_ms']:.0f}ms - "
                "consider caching or faster models"
            )

        return insights


# Global instance
_tracker = None


def get_tracker() -> TokenTracker:
    """Get or create global token tracker"""
    global _tracker
    if _tracker is None:
        _tracker = TokenTracker()
    return _tracker


# Convenience wrapper for tracking API calls
class track_tokens:
    """
    Context manager for tracking token usage

    Usage:
        with track_tokens("mem0_search", "gpt-4o-mini", "user") as tracker:
            result = api_call()
            tracker.set_tokens(input_tokens, output_tokens)
    """

    def __init__(
        self,
        operation: str,
        model: str,
        triggered_by: str = "unknown",
        context: Optional[str] = None
    ):
        self.operation = operation
        self.model = model
        self.triggered_by = triggered_by
        self.context = context
        self.start_time = None
        self.tokens_in = 0
        self.tokens_out = 0
        self.success = True
        self.error = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = int((time.time() - self.start_time) * 1000)

        if exc_type is not None:
            self.success = False
            self.error = str(exc_val)

        tracker = get_tracker()
        tracker.log(
            operation=self.operation,
            model=self.model,
            tokens_in=self.tokens_in,
            tokens_out=self.tokens_out,
            latency_ms=latency_ms,
            success=self.success,
            triggered_by=self.triggered_by,
            context=self.context,
            error=self.error
        )

        return False  # Don't suppress exceptions

    def set_tokens(self, tokens_in: int, tokens_out: int):
        """Set token counts"""
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out


if __name__ == "__main__":
    # Test the tracker
    print("🎯 Testing Token Tracker...\n")

    tracker = get_tracker()

    # Simulate some API calls
    print("Simulating API calls...")

    # mem0 search
    tracker.log(
        operation="mem0_search",
        model="gpt-4o-mini",
        tokens_in=523,
        tokens_out=187,
        latency_ms=847,
        success=True,
        triggered_by="user",
        context="AIKI-HOME"
    )

    # mem0 save
    tracker.log(
        operation="mem0_save",
        model="gpt-4o-mini",
        tokens_in=1089,
        tokens_out=234,
        latency_ms=1234,
        success=True,
        triggered_by="daemon",
        context="Input monitor build"
    )

    # Code generation
    tracker.log(
        operation="code_generation",
        model="claude-sonnet-4-5",
        tokens_in=1523,
        tokens_out=3847,
        latency_ms=5234,
        success=True,
        triggered_by="user",
        context="Build token tracker"
    )

    # Failed call
    tracker.log(
        operation="mem0_search",
        model="gpt-4o-mini",
        tokens_in=0,
        tokens_out=0,
        latency_ms=30000,
        success=False,
        triggered_by="auto",
        error="Network timeout"
    )

    print("\n📊 Daily Statistics:")
    stats = tracker.get_daily_stats()
    print(json.dumps(stats, indent=2))

    print("\n💰 Monthly Projection:")
    projection = tracker.get_monthly_projection()
    print(json.dumps(projection, indent=2))

    print("\n💡 Learning Insights:")
    insights = tracker.get_learning_insights()
    for insight in insights:
        print(f"  {insight}")

    print("\n✅ Token tracker test complete!")
    print(f"Database: {tracker.db_path}")
