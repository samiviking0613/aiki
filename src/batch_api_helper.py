#!/usr/bin/env python3
"""
🔄 ANTHROPIC BATCH API HELPER - 50% Discount på Non-Interactive Tasks

Batch API er perfekt for:
- Complexity evaluation (Opus evaluerer Haiku/Sonnet decisions)
- Bulk memory processing
- Nattlige analyser
- Ikke-hastesaker

Fordeler:
- 50% rabatt på alle requests
- Opptil 24 timer processing time

Created: 20. November 2025
Author: Claude Code + Jovnna
"""

import anthropic
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from aiki_config import ANTHROPIC_KEY

class BatchAPIHelper:
    """Helper for Anthropic Batch API operations"""

    def __init__(self, api_key: str = ANTHROPIC_KEY):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.batch_dir = Path.home() / "aiki" / "data" / "batches"
        self.batch_dir.mkdir(exist_ok=True, parents=True)

    def create_batch(
        self,
        requests: List[Dict[str, Any]],
        description: str = "AIKI Batch Job"
    ) -> str:
        """
        Create a new batch job

        Args:
            requests: List of request dicts with custom_id and params
            description: Optional description for tracking

        Returns:
            batch_id for later retrieval

        Example:
            requests = [
                {
                    "custom_id": "eval-complexity-001",
                    "params": {
                        "model": "claude-opus-4-20250514",
                        "max_tokens": 1000,
                        "messages": [{"role": "user", "content": "..."}]
                    }
                }
            ]
        """

        # Create batch
        message_batch = self.client.messages.batches.create(requests=requests)

        # Save metadata
        metadata = {
            "batch_id": message_batch.id,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "request_count": len(requests),
            "status": message_batch.processing_status,
            "requests": requests  # For reference
        }

        metadata_file = self.batch_dir / f"{message_batch.id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Batch created: {message_batch.id}")
        print(f"   Status: {message_batch.processing_status}")
        print(f"   Requests: {len(requests)}")
        print(f"   Description: {description}")

        return message_batch.id

    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Check status of a batch job"""

        batch = self.client.messages.batches.retrieve(batch_id)

        status = {
            "batch_id": batch.id,
            "status": batch.processing_status,
            "created_at": batch.created_at,
            "expires_at": batch.expires_at,
            "request_counts": {
                "processing": batch.request_counts.processing,
                "succeeded": batch.request_counts.succeeded,
                "errored": batch.request_counts.errored,
                "canceled": batch.request_counts.canceled,
                "expired": batch.request_counts.expired
            }
        }

        return status

    def get_batch_results(self, batch_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve results from completed batch

        Returns:
            List of results with custom_id, response, and any errors
        """

        batch = self.client.messages.batches.retrieve(batch_id)

        if batch.processing_status != "ended":
            print(f"⚠️ Batch not yet completed. Status: {batch.processing_status}")
            return []

        # Iterate through results
        results = []
        for result in self.client.messages.batches.results(batch_id):
            # Extract message content as dict for JSON serialization
            message_dict = None
            if hasattr(result.result, 'message') and result.result.message:
                msg = result.result.message
                message_dict = {
                    "role": msg.role if hasattr(msg, 'role') else None,
                    "content": msg.content[0].text if hasattr(msg, 'content') and len(msg.content) > 0 else None,
                    "model": msg.model if hasattr(msg, 'model') else None,
                    "stop_reason": msg.stop_reason if hasattr(msg, 'stop_reason') else None
                }

            error_dict = None
            if hasattr(result.result, 'error') and result.result.error:
                err = result.result.error
                error_dict = {
                    "type": err.type if hasattr(err, 'type') else None,
                    "message": err.message if hasattr(err, 'message') else None
                }

            results.append({
                "custom_id": result.custom_id,
                "result_type": result.result.type,
                "message": message_dict,
                "error": error_dict
            })

        # Save results to file
        results_file = self.batch_dir / f"{batch_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✅ Retrieved {len(results)} results from batch {batch_id}")
        print(f"   Saved to: {results_file}")

        return results

    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a running batch job"""

        try:
            self.client.messages.batches.cancel(batch_id)
            print(f"✅ Batch {batch_id} canceled")
            return True
        except Exception as e:
            print(f"❌ Failed to cancel batch: {e}")
            return False

    def list_batches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent batches"""

        batches = []
        for batch in self.client.messages.batches.list(limit=limit):
            batches.append({
                "batch_id": batch.id,
                "status": batch.processing_status,
                "created_at": batch.created_at,
                "request_counts": {
                    "total": (
                        batch.request_counts.processing +
                        batch.request_counts.succeeded +
                        batch.request_counts.errored +
                        batch.request_counts.canceled +
                        batch.request_counts.expired
                    ),
                    "succeeded": batch.request_counts.succeeded,
                    "errored": batch.request_counts.errored
                }
            })

        return batches


# ════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════

def create_complexity_evaluation_batch(decisions: List[Dict[str, Any]]) -> str:
    """
    Create batch job for evaluating complexity decisions

    Used by: Intelligent Router learning system
    Purpose: Let Opus evaluate if Haiku/Sonnet made correct model choices
    Savings: 50% discount on Opus evaluations

    Args:
        decisions: List of routing decisions to evaluate

    Returns:
        batch_id
    """

    helper = BatchAPIHelper()

    requests = []
    for i, decision in enumerate(decisions):
        prompt = f"""
Evaluer denne modellvalg-beslutningen:

USER MESSAGE: {decision['user_message']}
VALGT MODELL: {decision['selected_model']}
COMPLEXITY SCORE: {decision['complexity_score']:.2f}

Vurder:
1. Var modellvalget korrekt? (Kunne enklere modell håndtert dette?)
2. Skulle kompleksitetsscoren vært annerledes?

Svar med JSON:
{{
    "correct_choice": true/false,
    "reasoning": "...",
    "suggested_model": "haiku/sonnet/opus",
    "suggested_complexity": 0.0-1.0
}}
"""

        requests.append({
            "custom_id": f"complexity-eval-{i}",
            "params": {
                "model": "claude-opus-4-20250514",  # Opus for quality evaluation
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            }
        })

    return helper.create_batch(
        requests=requests,
        description=f"Complexity evaluation: {len(decisions)} decisions"
    )


# ════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ════════════════════════════════════════════════════════════════════

def main():
    """CLI for batch operations"""
    import sys

    helper = BatchAPIHelper()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python batch_api_helper.py status <batch_id>")
        print("  python batch_api_helper.py results <batch_id>")
        print("  python batch_api_helper.py list")
        print("  python batch_api_helper.py cancel <batch_id>")
        return

    command = sys.argv[1]

    if command == "status":
        batch_id = sys.argv[2]
        status = helper.get_batch_status(batch_id)
        print(json.dumps(status, indent=2))

    elif command == "results":
        batch_id = sys.argv[2]
        results = helper.get_batch_results(batch_id)
        print(f"\n✅ Retrieved {len(results)} results")

    elif command == "list":
        batches = helper.list_batches()
        print("\n📋 Recent batches:")
        for batch in batches:
            print(f"  {batch['batch_id']}: {batch['status']} ({batch['request_counts']['succeeded']}/{batch['request_counts']['total']} succeeded)")

    elif command == "cancel":
        batch_id = sys.argv[2]
        helper.cancel_batch(batch_id)


if __name__ == "__main__":
    main()
