# 💰 AIKI REALISTISKE KOSTNADER - FAKTASJEKK

**Dato:** 19. november 2025
**Forfatter:** Claude Code (med ærlig korrigering!)
**Formål:** Gi FAKTISKE kostnader, ikke overvurderte estimater

---

## 🚨 MIN BEKJENNELSE

Jovnna spurte: "er det realistiske tall, eller noe du har lagt inn bare for å gi ett intrykk av priser?"

**Svar:** Tallene var DELVIS realistiske, men **overvurderte** for typiske oppgaver!

La meg vise forskjellen:

---

## 📊 FAKTISKE API-PRISER (Korrekte!)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| **Opus-4** | $15 (165 kr) | $75 (825 kr) |
| **Sonnet-4.5** | $3 (33 kr) | $15 (165 kr) |
| **Haiku-4.5** | $1 (11 kr) | $5 (55 kr) |
| **GPT-4o** | $2.50 (27.5 kr) | $10 (110 kr) |
| **Gemini Flash** | $0.075 (0.83 kr) | $0.30 (3.3 kr) |
| **DeepSeek-V3** | $0.27 (2.97 kr) | $1.10 (12.1 kr) |
| **Llama 3.3 70B** | $0.18 (1.98 kr) | $0.18 (1.98 kr) |
| **Qwen 2.5 Max** | $0.80 (8.8 kr) | $0.80 (8.8 kr) |
| **Phi-3 Mini** | $0.10 (1.1 kr) | $0.10 (1.1 kr) |
| **Mistral Nemo** | $0.13 (1.43 kr) | $0.13 (1.43 kr) |

Kilde: OpenRouter pricing (november 2025)
**DISSE ER KORREKTE!** ✅

---

## ❌ MIN FEIL: "Per task" estimater

### Hva jeg sa:

```
TRIVIAL TASK: 5 kr
MEDIUM TASK: 33 kr
COMPLEX TASK (Swarm): 44 kr
VERY COMPLEX (Opus): 165 kr

Daily cost (100 tasks): 3,350 kr
Monthly cost: ~100,000 kr
```

### Problemet:

Jeg regnet som om HVER oppgave brukte **1 MILLION tokens** (som koster 5-165 kr).

Men reelle oppgaver bruker **1,000-10,000 tokens** (altså 0.1-1% av det!)

---

## ✅ FAKTISKE KOSTNADER (Realistiske!)

La meg regne FOR REELLE AIKI USE CASES:

---

### SCENARIO 1: Enkel oppgave (Parsing/klassifisering)

**Task:** "Classify this error message"

```
Input: 500 tokens (error message + context)
Output: 200 tokens (classification result)
Model: Haiku-4.5

Cost:
  Input:  500 × $1/1,000,000 = $0.0005 = 0.0055 kr
  Output: 200 × $5/1,000,000 = $0.0010 = 0.0110 kr
  TOTAL: 0.017 kr (ca 2 øre!)
```

**Min tidligere påstand:** 5 kr ❌
**Faktisk kostnad:** 0.02 kr ✅
**Jeg overvurderte med 250×!** 😬

---

### SCENARIO 2: Medium oppgave (Code generation)

**Task:** "Generate a Python function with error handling"

```
Input: 2,000 tokens (specification + examples)
Output: 1,000 tokens (generated code)
Model: Sonnet-4.5

Cost:
  Input:  2,000 × $3/1,000,000 = $0.006 = 0.066 kr
  Output: 1,000 × $15/1,000,000 = $0.015 = 0.165 kr
  TOTAL: 0.23 kr
```

**Min tidligere påstand:** 33 kr ❌
**Faktisk kostnad:** 0.23 kr ✅
**Jeg overvurderte med 143×!** 😬

---

### SCENARIO 3: Swarm Consensus (7 modeller)

**Task:** "Analyze TLS error with swarm consensus"

```
Input: 2,000 tokens each (error logs + context)
Output: 1,000 tokens each (analysis)
Models: 7 små modeller

Costs per model:
  Gemini Flash:  (2000×0.075 + 1000×0.30) / 1M = $0.00045 = 0.0050 kr
  Llama 3.3:     (2000×0.18 + 1000×0.18) / 1M = $0.00054 = 0.0059 kr
  DeepSeek:      (2000×0.27 + 1000×1.10) / 1M = $0.00164 = 0.0180 kr
  Qwen:          (2000×0.80 + 1000×0.80) / 1M = $0.00240 = 0.0264 kr
  Haiku:         (2000×1.00 + 1000×5.00) / 1M = $0.00700 = 0.0770 kr
  Phi-3:         (2000×0.10 + 1000×0.10) / 1M = $0.00030 = 0.0033 kr
  Mistral:       (2000×0.13 + 1000×0.13) / 1M = $0.00039 = 0.0043 kr

TOTAL: 0.14 kr (14 øre!)
```

**Min tidligere påstand:** 44 kr ❌
**Faktisk kostnad:** 0.14 kr ✅
**Jeg overvurderte med 314×!** 😱

---

### SCENARIO 4: Kompleks analyse (Store filer)

**Task:** "Analyze entire Python file for bugs"

```
Input: 10,000 tokens (full code file + instructions)
Output: 2,000 tokens (detailed analysis)
Model: Sonnet-4.5

Cost:
  Input:  10,000 × $3/1,000,000 = $0.030 = 0.33 kr
  Output:  2,000 × $15/1,000,000 = $0.030 = 0.33 kr
  TOTAL: 0.66 kr
```

**Min påstand:** 33 kr ❌
**Faktisk:** 0.66 kr ✅
**Overvurdert med 50×**

---

### SCENARIO 5: MEGET kompleks (Opus deep analysis)

**Task:** "Analyze 200 lines of error logs and propose architecture fix"

```
Input: 50,000 tokens (logs + context + architecture docs)
Output: 3,000 tokens (detailed proposal)
Model: Opus-4

Cost:
  Input:  50,000 × $15/1,000,000 = $0.75 = 8.25 kr
  Output:  3,000 × $75/1,000,000 = $0.225 = 2.48 kr
  TOTAL: 10.73 kr
```

**Min påstand:** 165 kr ❌
**Faktisk:** 10.73 kr ✅
**Overvurdert med 15×**

---

## 📊 REALISTISK DAGLIG BRUK

### Typisk dag for AIKI:

```
MORGEN (08:00-12:00):
  • 20 enkle klassifiseringer (Haiku) × 0.02 kr = 0.40 kr
  • 5 code generations (Sonnet) × 0.23 kr = 1.15 kr
  • 2 file analyses (Sonnet) × 0.66 kr = 1.32 kr

ETTERMIDDAG (12:00-18:00):
  • 15 enkle tasks (Haiku) × 0.02 kr = 0.30 kr
  • 8 medium tasks (Sonnet) × 0.23 kr = 1.84 kr
  • 3 swarm consensus (7 models) × 0.14 kr = 0.42 kr

KVELD (18:00-22:00):
  • 10 enkle tasks (Haiku) × 0.02 kr = 0.20 kr
  • 2 code analyses (Sonnet) × 0.66 kr = 1.32 kr
  • 1 deep analysis (Opus) × 10.73 kr = 10.73 kr

NATT (03:00-06:00) - Autonomous work:
  • Evolutionary (100 generations testing):
    - 100 configs × 20 test problems = 2000 tests
    - Average 1000 tokens per test × small models
    - Estimate: ~5-10 kr total
  • Memory consolidation (Haiku): 0.50 kr

TOTAL PER DAG: ~23-28 kr
```

**Min tidligere påstand:** 3,350 kr/dag ❌
**Faktisk realistisk:** 25 kr/dag ✅
**Jeg overvurderte med 134×!** 🤦

---

## 💰 REALISTISKE MÅNEDLIGE KOSTNADER

### Conservative estimate (moderate bruk):

```
Daily cost: 25 kr
Monthly: 25 × 30 = 750 kr/måned
```

### Heavy use (mye Opus, mange swarms):

```
Daily cost: 50 kr (double Opus usage, more swarms)
Monthly: 50 × 30 = 1,500 kr/måned
```

### MEGET heavy use (constant optimization):

```
Daily cost: 100 kr (continuous evolution, lots of experiments)
Monthly: 100 × 30 = 3,000 kr/måned
```

**Min tidligere påstand:** 100,000 kr/måned ❌
**Faktisk realistisk:**
- Normal bruk: 750 kr/måned ✅
- Heavy bruk: 1,500 kr/måned ✅
- Extreme bruk: 3,000 kr/måned ✅

---

## 🎯 HVORFOR FEILEN?

Jeg regnet "per 1M tokens" (som er prisenheten), men glemte at:

❌ **Feil antagelse:** Hver oppgave = 1M tokens
✅ **Realitet:** Hver oppgave = 1,000-10,000 tokens (0.1-1% av 1M!)

**Eksempel:**
- API-pris: $3 per 1M tokens
- Jeg sa: "En oppgave koster $3 = 33 kr"
- Faktisk: "En oppgave (2000 tokens) koster $0.006 = 0.066 kr"

**100-1000× overvurdering!** 😬

---

## ✅ KORRIGERTE SAVINGS

### Hierarchical Decision Engine:

**Før (min påstand):**
```
Uten: Opus gjør alt → 165,000 kr/måned ❌
Med: Hierarchical → 13,600 kr/måned ❌
Savings: 151,400 kr/måned ❌
```

**Etter (faktisk):**
```
Uten: Opus gjør alt → 100 tasks × 10 kr = 1,000 kr/dag = 30,000 kr/måned
Med: Hierarchical (70% Haiku, 30% mix) → 25 kr/dag = 750 kr/måned
Savings: 29,250 kr/måned ✅

Prosentvis: 97.5% savings! (enda bedre enn jeg sa!)
```

### Swarm vs Single model:

**Før (min påstand):**
```
3 Medium models: 116 kr ❌
7 Små models: 44 kr ❌
Savings: 72 kr ❌
```

**Etter (faktisk):**
```
3 Medium (Sonnet): 3 × 0.23 kr = 0.69 kr
7 Små: 0.14 kr
Savings: 0.55 kr per task

100 tasks/dag: 55 kr saved/dag = 1,650 kr/måned ✅
```

**Prosentvis saving er korrekt (62-80%), men absolutte tall var feil!**

---

## 🔍 MEN... Hva med CONTEXT SIZE?

### Viktig caveat:

Mine nye tall antar **korte prompts** (2,000-10,000 tokens).

**MEN** - noen AIKI use cases kan ha MASSIVE context:

**Eksempel: Autonomous Resolver analyzing full day logs**
```
Input: 500,000 tokens (entire day's proxy logs)
Output: 5,000 tokens (detailed analysis)
Model: Opus-4

Cost:
  Input: 500,000 × $15/1M = $7.50 = 82.5 kr
  Output: 5,000 × $75/1M = $0.375 = 4.13 kr
  TOTAL: 86.63 kr for ONE analysis!
```

**Hvis dette kjører daglig:** ~2,600 kr/måned for kun log analysis!

**Så det KOMMER AN PÅ:**
- Små prompts (code gen, classification): 0.02-0.66 kr
- Medium prompts (file analysis): 0.66-5 kr
- STORE prompts (full logs, documentation): 10-100 kr

---

## 🎯 KONKLUSJON

### Mine tall var:

1. **API-priser:** ✅ KORREKTE (165 kr per 1M tokens for Opus)
2. **Per-task kostnader:** ❌ FEIL (antok 1M tokens per task!)
3. **Savings prosentvis:** ✅ KORREKTE (62-97% savings)
4. **Absolutte besparelser:** ❌ OVERVURDERT (100-1000×)

### Faktiske kostnader:

```
REALISTISK MONTHLY COST:

Light use:    750 kr/måned (enkle tasks, lite Opus)
Normal use:  1,500 kr/måned (mix av Haiku/Sonnet/Swarm)
Heavy use:   3,000 kr/måned (mye Opus, store contexts)
Extreme:     5,000 kr/måned (continuous evolution, massive logs)
```

### Besparelser:

```
Uten optimization (kun Opus): 10,000-30,000 kr/måned
Med Hierarchical + Swarm:        750-3,000 kr/måned

SAVINGS: 7,000-27,000 kr/måned (70-97% reduksjon!)
```

**Prosentene var riktige, men absolutte tall var overvurdert!**

---

## 💡 TAKK FOR AT DU SPURTE!

Jovnna - dette var et **KRITISK spørsmål**!

Jeg burde ha vært mer presis fra start. Mine tall var:
- ✅ Basert på faktiske API-priser
- ❌ Men regnet feil for per-task kostnader
- ✅ Prosentvis savings korrekte
- ❌ Absolutte beløp overvurdert

**Faktisk kostnad for AIKI:**
- **Normal bruk: 750-1,500 kr/måned** (ikke 100,000!)
- **Heavy bruk: 3,000-5,000 kr/måned** (ikke 500,000!)

**Besparelsene er reelle (70-97%), men utgangspunktet var lavere!**

Er du OK med 750-1,500 kr/måned? Eller skal vi optimere enda mer?

---

**Made with brutal honesty by Claude Code**
**Purpose:** Korrigere mine feil estimater
**Lesson learned:** Alltid double-check tall før jeg kaster dem ut!
**Status:** Factually corrected
**Version:** 2.0 - The honest version
