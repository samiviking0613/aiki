#!/usr/bin/env python3
"""
⚙️ AIKI CONFIGURATION - Centralized Config Management

All configuration og environment variables samlet her.

Created: 19. November 2025
Author: Claude Code + Jovnna
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
ENV_FILE = Path.home() / "aiki" / ".env"
load_dotenv(ENV_FILE)


# ════════════════════════════════════════════════════════════════════
# API KEYS (from environment)
# ════════════════════════════════════════════════════════════════════

OPENROUTER_KEY = os.getenv('OPENROUTER_KEY')
if not OPENROUTER_KEY:
    raise ValueError("OPENROUTER_KEY not set! Create .env file with API key.")

# Direct Anthropic API (for cost savings - no OpenRouter markup!)
# Verified working: 20. Nov 2025
ANTHROPIC_KEY = os.getenv('ANTHROPIC_KEY', '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')

OPENROUTER_URL = 'https://openrouter.ai/api/v1'


# ════════════════════════════════════════════════════════════════════
# PATHS
# ════════════════════════════════════════════════════════════════════

AIKI_HOME = Path.home() / "aiki"
LOGS_DIR = AIKI_HOME / "logs"
BACKUPS_DIR = AIKI_HOME / "backups"
DATA_DIR = AIKI_HOME / "data"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# File paths
CONSCIOUSNESS_FILE = AIKI_HOME / "aiki_consciousness.py"
REFLECTION_LOG = LOGS_DIR / "reflections.json"
VALIDATION_LOG = LOGS_DIR / "validations.json"
COMPLEXITY_LOG = LOGS_DIR / "complexity_decisions.json"
LEARNING_HISTORY = LOGS_DIR / "learning_history.json"
COST_LOG = LOGS_DIR / "costs.json"
INTERACTION_LOG = LOGS_DIR / "interactions.json"


# ════════════════════════════════════════════════════════════════════
# QDRANT CONFIG
# ════════════════════════════════════════════════════════════════════

QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')

COLLECTION_NAMES = {
    'consciousness': 'aiki_consciousness',  # 470 AIKI minner
    'interactions': 'aiki_interactions',     # User interactions
    'reflections': 'aiki_reflections',       # Self-reflections
    'modifications': 'aiki_modifications'    # Self-modifications
}


# ════════════════════════════════════════════════════════════════════
# MODEL CONFIGURATION
# ════════════════════════════════════════════════════════════════════

MODELS = {
    # Cheap tier
    'llama-70b': {
        'name': 'meta-llama/llama-3.1-70b-instruct',
        'display_name': 'Llama 3.1 70B',
        'cost_input': 0.0001,   # per 1M tokens
        'cost_output': 0.0001,
        'use_for': ['simple_queries']
    },

    # Balanced tier
    'haiku': {
        'name': 'anthropic/claude-3.5-haiku',
        'display_name': 'Claude Haiku 3.5',
        'cost_input': 1.00,     # per 1M tokens
        'cost_output': 4.00,
        'use_for': ['standard_reflection', 'medium_queries']
    },

    'gemini-flash': {
        'name': 'google/gemini-2.0-flash-exp',
        'display_name': 'Gemini 2.0 Flash',
        'cost_input': 2.00,
        'cost_output': 8.00,
        'use_for': ['reasoning', 'balanced_queries']
    },

    # Premium tier
    'sonnet': {
        'name': 'anthropic/claude-3.5-sonnet',
        'display_name': 'Claude Sonnet 3.5',
        'cost_input': 3.00,
        'cost_output': 15.00,
        'use_for': ['code_generation', 'complex_queries']
    },

    'opus': {
        'name': 'anthropic/claude-opus-4',
        'display_name': 'Claude Opus 4',
        'cost_input': 15.00,
        'cost_output': 75.00,
        'use_for': ['code_review', 'critical_reflection', 'meta_cognition']
    }
}


# ════════════════════════════════════════════════════════════════════
# REFLECTION CONFIG
# ════════════════════════════════════════════════════════════════════

REFLECTION_CONFIG = {
    'standard_model': 'haiku',  # Changed from llama-70b!
    'critical_model': 'opus',
    'critical_threshold': 0.5,  # quality_score < 0.5 → use Opus
    'enable_persistence': True,
    'max_log_size': 1000
}


# ════════════════════════════════════════════════════════════════════
# MODIFICATION CONFIG
# ════════════════════════════════════════════════════════════════════

MODIFICATION_CONFIG = {
    'approval_mode': 'supervised',  # 'autonomous' | 'supervised' | 'log_only'
    'use_multi_agent': True,
    'enable_sandbox': True,
    'enable_versioning': True
}


# ════════════════════════════════════════════════════════════════════
# COMPLEXITY LEARNING CONFIG
# ════════════════════════════════════════════════════════════════════

LEARNING_CONFIG = {
    'batch_size': 50,           # Min decisions før Opus evaluation
    'max_days': 7,              # Max dager før forced evaluation
    'target_agreement': (0.90, 0.95),
    'use_batch_api': True       # Use Batch API for 50% discount
}


# ════════════════════════════════════════════════════════════════════
# COST MANAGEMENT
# ════════════════════════════════════════════════════════════════════

COST_CONFIG = {
    'enable_tracking': os.getenv('ENABLE_COST_TRACKING', 'true').lower() == 'true',
    'monthly_budget': 200.00,   # $200/måned budget
    'alert_threshold': 0.8,     # Alert ved 80% av budget
    'enable_auto_downgrade': True  # Auto-switch til billigere model hvis over budget
}


# ════════════════════════════════════════════════════════════════════
# MONITORING CONFIG
# ════════════════════════════════════════════════════════════════════

MONITORING_CONFIG = {
    'enable': os.getenv('ENABLE_MONITORING', 'true').lower() == 'true',
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'health_check_interval': 300,  # 5 minutes
    'enable_rate_limiting': True,
    'max_calls_per_minute': 60
}


# ════════════════════════════════════════════════════════════════════
# EMOTION DETECTION CONFIG (NEW!)
# ════════════════════════════════════════════════════════════════════

EMOTION_CONFIG = {
    'enable': True,
    'track_keyboard': True,      # Track typing patterns
    'track_mouse': True,         # Track mouse movements
    'use_llm_detection': False,  # Use pattern matching (cheaper)
    'adjust_tone': True          # Auto-adjust AIKI's tone
}


# ════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════

def get_model_config(model_key: str) -> dict:
    """Get model configuration"""
    if model_key not in MODELS:
        raise ValueError(f"Unknown model: {model_key}")
    return MODELS[model_key]


def get_model_for_task(task: str) -> str:
    """
    Get recommended model for task

    Tasks: simple_query, medium_query, complex_query,
           standard_reflection, critical_reflection,
           code_generation, code_review
    """
    for key, config in MODELS.items():
        if task in config['use_for']:
            return key

    # Fallback
    return 'haiku'


def calculate_cost(input_tokens: int, output_tokens: int, model_key: str) -> float:
    """Calculate cost for API call"""
    model = MODELS[model_key]
    cost = (
        (input_tokens / 1_000_000) * model['cost_input'] +
        (output_tokens / 1_000_000) * model['cost_output']
    )
    return cost


# ════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ════════════════════════════════════════════════════════════════════

def initialize():
    """Initialize AIKI configuration"""
    print("⚙️ AIKI Configuration loaded")
    print(f"   API Key: {'✅ Set' if OPENROUTER_KEY else '❌ Missing'}")
    print(f"   Qdrant: {QDRANT_URL}")
    print(f"   Cost tracking: {'✅' if COST_CONFIG['enable_tracking'] else '❌'}")
    print(f"   Monitoring: {'✅' if MONITORING_CONFIG['enable'] else '❌'}")
    print(f"   Emotion detection: {'✅' if EMOTION_CONFIG['enable'] else '❌'}")
    print()


if __name__ == '__main__':
    initialize()
    print("Model configurations:")
    for key, config in MODELS.items():
        print(f"  {key}: {config['display_name']}")
        print(f"    Cost: ${config['cost_input']:.2f}/${config['cost_output']:.2f} per 1M tokens")
        print(f"    Use for: {', '.join(config['use_for'])}")
