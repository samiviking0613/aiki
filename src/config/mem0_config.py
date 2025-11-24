"""
Sentral mem0-konfigurasjon for AIKI.

ALLE filer skal importere config herfra for konsistens.
Endret 23.11.2025: Oppgradert til text-embedding-3-large (3072 dims)
"""

import os

# API-nøkler
OPENROUTER_API_KEY = os.environ.get(
    'OPENAI_API_KEY',
    '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'
)
OPENROUTER_BASE_URL = os.environ.get(
    'OPENAI_BASE_URL',
    'https://openrouter.ai/api/v1'
)

# Embedding-konfigurasjon
# Oppgradert fra small (1536) til large (3072) for bedre assosiativ hukommelse
EMBEDDING_MODEL = 'text-embedding-3-large'
EMBEDDING_DIMS = 3072

# Qdrant-konfigurasjon
QDRANT_HOST = 'localhost'
QDRANT_PORT = 6333
QDRANT_COLLECTION = 'mem0_memories_large'  # Ny collection for large embeddings

# LLM-konfigurasjon
LLM_MODEL = 'openai/gpt-4o-mini'
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 2000


def get_mem0_config() -> dict:
    """Returner komplett mem0-konfigurasjon."""
    return {
        'llm': {
            'provider': 'openai',
            'config': {
                'model': LLM_MODEL,
                'temperature': LLM_TEMPERATURE,
                'max_tokens': LLM_MAX_TOKENS
            }
        },
        'embedder': {
            'provider': 'openai',
            'config': {
                'model': EMBEDDING_MODEL,
                'embedding_dims': EMBEDDING_DIMS
            }
        },
        'vector_store': {
            'provider': 'qdrant',
            'config': {
                'collection_name': QDRANT_COLLECTION,
                'host': QDRANT_HOST,
                'port': QDRANT_PORT,
                'embedding_model_dims': EMBEDDING_DIMS
            }
        }
    }


def setup_environment():
    """Sett opp miljøvariabler for OpenRouter."""
    os.environ['OPENAI_API_KEY'] = OPENROUTER_API_KEY
    os.environ['OPENAI_BASE_URL'] = OPENROUTER_BASE_URL
