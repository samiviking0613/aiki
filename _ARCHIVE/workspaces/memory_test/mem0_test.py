
from mem0 import Memory
from mem0.configs.base import MemoryConfig, LlmConfig, EmbedderConfig
import os

print("mem0 versjon OK. Lager klient med OpenRouter ...")

# Sett opp OpenRouter via miljøvariabler
openrouter_key = "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"
os.environ["OPENAI_API_KEY"] = openrouter_key
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

config = MemoryConfig(
    llm=LlmConfig(
        provider="openai",
        config={
            "model": "openai/gpt-4o-mini"
        }
    ),
    embedder=EmbedderConfig(
        provider="openai",
        config={
            "model": "text-embedding-3-small"
        }
    )
)

m = Memory(config=config)

user_id = "test-user-1"

print("Legger inn minner ...")
m.add([{"role":"user","content":"Jovnna liker å automatisere alt papirarbeid."}], user_id=user_id, metadata={"tags":["prefs","aiki"]})
m.add([{"role":"user","content":"Aiki skal bruke Vipps og PowerOffice senere."}], user_id=user_id, metadata={"tags":["aiki","økonomi"]})

print("Søker etter 'Vipps' ...")
result = m.search("Vipps integrasjon", user_id=user_id, limit=5)

print("Treff:")
if result and 'results' in result:
    for i, h in enumerate(result['results'], 1):
        memory_text = h.get('memory', '')
        score = h.get('score', 0)
        print(f"{i}. score={score:.4f} memory={memory_text!r}")
else:
    print("Ingen treff funnet")
