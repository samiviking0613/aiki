#!/bin/bash
# AIKI - Open Interpreter Starter med API keys

# Last inn environment variabler fra .env
export $(grep -v '^#' /home/jovnna/aiki/.env | xargs)

# Konfigurer for Anthropic API (direct - best for interpreter)
export ANTHROPIC_API_KEY=$ANTHROPIC_KEY

# Alternativt: bruk OpenRouter som fallback
export OPENAI_API_KEY=$OPENROUTER_KEY
export OPENAI_API_BASE=https://openrouter.ai/api/v1

# Start interpreter med -y flagg som standard, pluss eventuelle andre flagg
/home/jovnna/.local/bin/interpreter -y "$@"
