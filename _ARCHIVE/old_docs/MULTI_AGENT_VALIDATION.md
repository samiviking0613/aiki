# 🛡️ MULTI-AGENT CODE VALIDATION SYSTEM

**Status:** ✅ IMPLEMENTERT (19. Nov 2025)
**Konsept:** Sonnet bygger, Opus reviewer, Sandbox tester - Consensus kreves!

---

## 🎯 KONSEPTET

**Jovnnas innsikt:**
> "Om Aiki skal endre egen kode, så skal koden først bygges i en sandboks,
> så må den koden godkjennes av flere andre modeller. La oss si sonnet bygger
> grunnkoden. Så skal opus godkjenne og eventuelt utbedre feil og forbedringer."

**Dette gir:**
- ✅ Sonnet 4.5: Rask + billig code generation
- ✅ Opus 4: Kritisk review + improvements
- ✅ Sandbox: Sikrer koden fungerer før apply
- ✅ Multi-agent consensus: Reduserer sjansen for bugs/farlig kode

---

## 🏗️ ARKITEKTUR

```
AIKI bestemmer å endre seg selv
    (fra reflection eller user request)
          ↓
┌─────────────────────────────────────────────────┐
│ PHASE 1: SONNET 4.5 (Code Generator)           │
│ ──────────────────────────────────────          │
│ Input:                                          │
│   - Modification proposal (description, type)   │
│   - Current aiki_consciousness.py               │
│                                                 │
│ Task:                                           │
│   - Identifiser kode som må endres             │
│   - Generer old_code + new_code                │
│   - Lag test cases                             │
│   - Safety considerations                      │
│                                                 │
│ Output:                                         │
│   {                                             │
│     "old_code": "exact section to replace",    │
│     "new_code": "improved implementation",     │
│     "explanation": "why this works",           │
│     "test_cases": [...],                       │
│     "safety_considerations": [...]             │
│   }                                             │
│                                                 │
│ Model: anthropic/claude-3.5-sonnet             │
│ Cost: ~$0.015/1K tokens                        │
│ Temperature: 0.2 (precise code generation)     │
└─────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────┐
│ PHASE 2: OPUS 4 (Code Reviewer + Improver)     │
│ ────────────────────────────────────────        │
│ Input:                                          │
│   - Sonnet's generated code                    │
│   - Original proposal                          │
│   - Context                                    │
│                                                 │
│ Task:                                           │
│   - Code quality review                        │
│   - Logic review (unintended side effects?)    │
│   - Safety review (dangerous operations?)      │
│   - Improvement suggestions                    │
│                                                 │
│ Output:                                         │
│   {                                             │
│     "approved": true/false,                    │
│     "confidence": 0.0-1.0,                     │
│     "issues": [                                │
│       {                                         │
│         "severity": "critical|major|minor",    │
│         "description": "what's wrong",         │
│         "line": "which code section"           │
│       }                                         │
│     ],                                          │
│     "improvements": [...],                     │
│     "improved_code": {                         │
│       "old_code": "same or adjusted",          │
│       "new_code": "better version"             │
│     },                                          │
│     "safety_verdict": "safe|risky|dangerous"   │
│   }                                             │
│                                                 │
│ Model: anthropic/claude-opus-4                 │
│ Cost: ~$0.075/1K tokens                        │
│ Temperature: 0.1 (critical review)             │
└─────────────────────────────────────────────────┘
          ↓
      [Hvis Opus approved]
          ↓
┌─────────────────────────────────────────────────┐
│ PHASE 3: SANDBOX TESTING                       │
│ ───────────────────────                         │
│ 1. Create temp directory                       │
│ 2. Copy aiki_consciousness.py to sandbox       │
│ 3. Apply Opus's improved code                  │
│ 4. Run tests:                                  │
│    ✓ Syntax check (compile)                   │
│    ✓ Import check (can be imported?)          │
│    ✓ [Future: Run full test suite]            │
│                                                 │
│ Output:                                         │
│   {                                             │
│     "passed": true/false,                      │
│     "tests_run": ["syntax", "import"],         │
│     "errors": [...]                            │
│   }                                             │
│                                                 │
│ Cost: $0 (local sandbox)                       │
│ Time: ~5-10 seconds                            │
└─────────────────────────────────────────────────┘
          ↓
      [Hvis all tests pass]
          ↓
┌─────────────────────────────────────────────────┐
│ PHASE 4: APPLY TO PRODUCTION                   │
│ ──────────────────────────────                  │
│ 1. Backup current aiki_consciousness.py        │
│ 2. Apply Opus's improved code                  │
│ 3. Git commit (AIKI as author)                 │
│ 4. Log modification                            │
│                                                 │
│ Result: AIKI har evolvet trygt! ✅             │
└─────────────────────────────────────────────────┘
```

---

## 💰 COST ANALYSIS

### **Per Modification:**

```
Phase 1 (Sonnet generation):
  Input: ~500 tokens (proposal + context)
  Output: ~1000 tokens (code + explanation)
  Cost: $0.015 * 1.5 = ~$0.023

Phase 2 (Opus review):
  Input: ~1500 tokens (Sonnet's code + proposal)
  Output: ~2000 tokens (review + improvements)
  Cost: $0.075 * 3.5 = ~$0.26

Phase 3 (Sandbox):
  Cost: $0 (local)

Total per modification: ~$0.28
```

### **Monthly Estimate:**

```
Scenario 1: Lavt bruk (1 modification/uke)
  4 modifications × $0.28 = ~$1.12/måned

Scenario 2: Middels bruk (3 modifications/uke)
  12 modifications × $0.28 = ~$3.36/måned

Scenario 3: Høyt bruk (1 modification/dag)
  30 modifications × $0.28 = ~$8.40/måned
```

**Verdt det?**
- ✅ $0.28 per modification er billig for SAFETY
- ✅ Opus review alene er verdt prisen (catches bugs!)
- ✅ Reduserer risiko for farlige/dårlige modifications

---

## 🔧 BRUK

### **1. Med Multi-Agent Validation (anbefalt):**

```python
from aiki_self_modification import SelfModificationEngine

# Initialize med multi-agent validation
engine = SelfModificationEngine(
    approval_mode='supervised',
    use_multi_agent=True  # Default: True
)

# Propose modification (NO need for old_code/new_code!)
result = engine.propose_modification_with_multi_agent(
    change_type='tone_adjustment',
    description='Reduser bruk av emojis i system prompt',
    severity='minor',
    reason='User feedback: Too many emojis',
    context={'reflection_quality_score': 0.5}
)

# Result:
# {
#   'approved': True,  # Minor auto-approved
#   'modification_id': 'mod_20251119_123456',
#   'status': 'auto_approved',
#   'validation_result': {
#     'validation_steps': [
#       {'agent': 'sonnet-4.5', 'success': True, ...},
#       {'agent': 'opus-4', 'approved': True, ...},
#       {'passed': True, 'tests_run': [...]}
#     ]
#   }
# }
```

### **2. Uten Multi-Agent (gammel måte):**

```python
# Krever at du spesifiserer old_code/new_code selv
result = engine.propose_modification(
    change_type='tone_adjustment',
    description='Reduser emojis',
    old_code='# Exact old code section',
    new_code='# New code',
    severity='minor'
)
```

---

## 🚨 SAFETY FEATURES

### **1. Opus Review Catches:**
- 🔍 Syntax errors før sandbox
- 🔍 Logic bugs (off-by-one, null checks, etc.)
- 🔍 Security issues (SQL injection, command injection)
- 🔍 Unintended side effects
- 🔍 Missing error handling

### **2. Sandbox Prevents:**
- 🛡️ Syntax errors fra å nå production
- 🛡️ Import failures
- 🛡️ Runtime crashes (i fremtiden: full test suite)

### **3. Rollback Capability:**
```python
# If AIKI breaks itself, rollback:
engine.rollback_to_backup(
    '/home/jovnna/aiki/backups/aiki_consciousness_20251119_123456.py'
)
```

### **4. Git Version Control:**
```bash
# All modifications tracked:
git log --author="AIKI Consciousness"

# Rollback hvis nødvendig:
git checkout <commit_id> aiki_consciousness.py
```

---

## 📊 VALIDATION LOG

Alle validations logges:

```python
validator = MultiAgentCodeValidator()

# Get validation history
history = validator.get_validation_history(limit=10)

for validation in history:
    print(f"Proposal: {validation['proposal']['description']}")
    print(f"Approved: {validation['approved']}")
    if not validation['approved']:
        print(f"Failure: {validation['failure_reason']}")
```

---

## 🎯 EKSEMPEL FLOW

### **Scenario: AIKI lærer å bruke færre emojis**

```
1. REFLECTION IDENTIFIES ISSUE:
   Haiku 4.5 reflection:
     Quality: 0.5/1.0
     Issue: "Bruker for mange emojis"
     Suggestion: "Reduser emoji bruk"

2. AIKI PROPOSES MODIFICATION:
   engine.propose_modification_with_multi_agent(
     change_type='tone_adjustment',
     description='Reduser emoji bruk i responses',
     severity='minor',
     reason='User feedback from reflection'
   )

3. SONNET 4.5 GENERATES CODE:
   {
     "old_code": "def _build_system_prompt(self, context):
         prompt = '''Du er AIKI! 🤖 Enthusiastic! 🎉'''",

     "new_code": "def _build_system_prompt(self, context):
         prompt = '''Du er AIKI. Professional and helpful.'''",

     "explanation": "Removed excessive emojis from system prompt"
   }

4. OPUS 4 REVIEWS:
   {
     "approved": true,
     "confidence": 0.95,
     "issues": [],
     "improvements": [
       "Consider adding 'use emojis sparingly' guideline"
     ],
     "improved_code": {
       "new_code": "def _build_system_prompt(self, context):
           prompt = '''Du er AIKI. Professional and helpful.
           Use emojis sparingly (max 1-2 per message).'''"
     },
     "safety_verdict": "safe"
   }

5. SANDBOX TEST:
   ✓ Syntax check: PASS
   ✓ Import check: PASS

6. APPLY:
   ✅ Backup created
   ✅ Code applied
   ✅ Git commit: "AIKI self-modification: Reduced emoji usage"
   ✅ Logged

7. NEXT INTERACTION:
   Jovnna: "Hei!"
   AIKI: "Hei! Klar for mer arbeid."  ← Fewer emojis! ✅
```

---

## 🆚 COMPARISON

### **Uten Multi-Agent (gammel):**
```
AIKI: "Jeg vil endre noe"
  → Hardcoded old_code/new_code
  → Ingen review
  → Apply umiddelbart
  → Kan innføre bugs! ❌
```

### **Med Multi-Agent (ny):**
```
AIKI: "Jeg vil endre noe"
  → Sonnet genererer kode
  → Opus reviewer kritisk
  → Sandbox tester
  → Consensus kreves
  → Trygg apply! ✅
```

---

## 🚀 NESTE STEG

### **Phase 1: ✅ COMPLETED**
- Multi-agent validation system
- Sonnet + Opus integration
- Sandbox testing
- Integration med SelfModificationEngine

### **Phase 2: Testing (nå)**
- Test med real proposals
- Observer Sonnet/Opus quality
- Tune prompts basert på results

### **Phase 3: Forbedringer**
- Full test suite i sandbox (ikke bare syntax/import)
- Gemini 2.0 Flash som tiebreaker hvis Sonnet/Opus disagreer
- Performance metrics tracking
- Cost optimization

### **Phase 4: Batch API**
- Bruk Anthropic Batch API for Opus review (50% discount)
- Async validation (24 hour window OK for non-critical)

---

## 💡 KEY INSIGHTS

1. **Sonnet er god til code generation** ($0.023 per modification)
2. **Opus er kritisk reviewer** ($0.26 per modification - verdt det!)
3. **Sandbox er gratis safety** (0 cost, high value)
4. **Multi-agent consensus reduserer risiko** dramatisk

**Jovnnas opprinnelige ide var spot-on!** 🎯

---

**Made with multi-agent consensus 🛡️ by Sonnet, Opus, and Jovnna**
**19. November 2025**
