# 🧠 AIKI COMPLEXITY LEARNING SYSTEM

**Status:** ✅ IMPLEMENTERT (19. Nov 2025)
**Konsept:** AIKI lærer å score query complexity ved å få Opus evalueringer
**Mål:** 90-95% agreement med Opus' vurderinger

---

## 🎯 KONSEPTET

**Problem:**
- AIKI må velge riktig modell for hver query basert på kompleksitet
- Pattern-based complexity scoring kan være unøyaktig
- Feil model = enten dårlig svar (for billig) eller unødvendig kostnad (for dyr)

**Løsning:**
AIKI lærer fra Opus evalueringer og justerer sine scoring patterns over tid

**Hvordan det fungerer:**

```
1. AIKI scorer query → Velger model tier (cheap/balanced/premium)
2. Logger beslutningen for senere evaluering
3. Etter 50 queries: Sender batch til Opus for vurdering
4. Opus evaluerer: "Var tier valget riktig?"
5. AIKI lærer fra disagreements
6. Pattern adjustments appliseres automatisk
7. Repeat til 90-95% agreement
```

---

## 🏗️ ARKITEKTUR

### **4 Hovedkomponenter:**

#### 1. ComplexityReflectionEngine (Self-Reflection)
```python
# AIKI reflekterer over sine egne valg
def reflect_on_decision(query, complexity_analysis, selected_model, response):
    """
    Heuristikker for self-reflection:
    - Var response for kort/enkel for modellen? (overkill)
    - Var response for svak for query? (underkill)
    - Confidence indicators i response

    Returns:
        {
            'correct_tier': bool,
            'recommended_tier': str,
            'confidence': 0.0-1.0,
            'reasoning': str
        }
    """
```

#### 2. OpusComplexityValidator (Opus Evaluation)
```python
# Opus evaluerer batch av AIKI's beslutninger
def validate_batch(complexity_decisions):
    """
    Opus får liste med:
    - Query
    - AIKI's tier valg
    - Response

    Opus vurderer:
    - Var tier riktig?
    - Hvilken tier BURDE vært brukt?
    - Hvorfor? (reasoning)

    Returns:
        {
            'evaluations': [
                {
                    'query': str,
                    'aiki_tier': str,
                    'opus_recommended_tier': str,
                    'agreement': bool,
                    'opus_reasoning': str
                }
            ],
            'agreement_rate': 0.0-1.0,
            'common_errors': [str],
            'adjustment_suggestions': [
                {
                    'pattern': str,
                    'adjustment': float,
                    'reasoning': str
                }
            ]
        }
    """
```

#### 3. ComplexityLearningSystem (Learning)
```python
# Analyser Opus feedback og generer adjustments
def learn_from_opus(opus_validation):
    """
    Analyser disagreements:
    - Hvilke patterns førte til feil tier?
    - Er AIKI for konservativ (bruker dyre modeller unødvendig)?
    - Er AIKI for aggressiv (bruker billige modeller når ikke nok)?

    Generer adjustments:
    - Pattern X skal få +0.2 (øke kompleksitet)
    - Pattern Y skal få -0.3 (redusere kompleksitet)

    Returns:
        {
            'current_agreement_rate': float,
            'target_agreement_rate': (0.90, 0.95),
            'adjustments_needed': [
                {
                    'pattern': str,
                    'adjustment': float,
                    'reasoning': str
                }
            ],
            'learning_insights': [str]
        }
    """
```

#### 4. ComplexityDecisionLogger (Logging)
```python
# Logger alle complexity decisions for senere evaluering
def log_decision(query, complexity_score, selected_tier,
                model_used, response, response_length, reasoning):
    """
    Lagrer decision til JSON:
    {
        'timestamp': str,
        'query': str,
        'complexity_score': float,
        'selected_tier': str,
        'model_used': str,
        'response': str,
        'response_length': int,
        'reasoning': str
    }
    """
```

---

## 🔄 LEARNING CYCLE

### **Automatisk Trigger:**

Opus evaluering kjøres automatisk når BEGGE:
1. **Min 50 decisions logged** (batch size)
2. **Max 7 dager siden siste evaluation**

### **Hybrid Trigger:**
```python
LEARNING_BATCH_SIZE = 50   # Min decisions
LEARNING_MAX_DAYS = 7      # Max days

# Triggers når:
if (decisions >= 50) OR (days_since_last >= 7):
    run_opus_evaluation()
```

### **Full Cycle:**

```
Dag 1:
  - AIKI scores 50 queries
  - Logger alle decisions
  - Trigger: 50 decisions reached!
  - Opus evaluerer batch
  - Agreement: 65%
  - Adjustments: 12 patterns justert

Dag 2-3:
  - AIKI scorer med nye patterns
  - Logger 50 nye decisions
  - Trigger: 50 decisions + 2 days
  - Opus evaluerer
  - Agreement: 78% (+13%)
  - Adjustments: 8 patterns justert

Dag 4-5:
  - Fortsetter med forbedrede patterns
  - Logger 50 nye decisions
  - Trigger: 50 decisions + 2 days
  - Opus evaluerer
  - Agreement: 87% (+9%)
  - Adjustments: 4 patterns justert

Dag 6-7:
  - Fine-tuning
  - Logger 50 nye decisions
  - Trigger: 50 decisions + 2 days
  - Opus evaluerer
  - Agreement: 92% (+5%)
  - 🎯 TARGET REACHED! (90-95%)
```

---

## 💰 COST ANALYSIS

### **Opus Evaluation Cost:**

```python
# Per evaluation (50 decisions):
Input tokens: ~3000 (50 queries + context)
Output tokens: ~4000 (evaluations + suggestions)

Cost = (3000/1000 * $15) + (4000/1000 * $75)
     = $45 + $300
     = $345 per evaluation

# Monthly estimate (4 evaluations):
4 evaluations × $345 = $1,380/måned
```

### **Cost Optimization via Batch API:**

Anthropic Batch API: **50% discount**
```python
# Same evaluation via Batch API:
Cost = $345 × 0.50 = $172.50 per evaluation

# Monthly with Batch API:
4 evaluations × $172.50 = $690/måned
```

**Batch API tradeoff:**
- ✅ 50% kostnad
- ⚠️ 24 timer processing time
- ✅ Perfect for non-urgent evaluations
- ✅ Learning kan vente 1 dag

### **Savings from Better Routing:**

Når agreement rate når 90-95%:
```python
# Scenario: 1000 queries/måned

Uten learning (random guessing):
  - 33% cheap, 33% balanced, 33% premium
  - Many queries over-tiered (waste) eller under-tiered (poor quality)
  - Estimated cost: $50-100/måned

Med 90% accuracy:
  - 60% cheap, 30% balanced, 10% premium
  - Optimal tier selection
  - Estimated cost: $15-30/måned
  - Savings: $35-70/måned

# ROI: $690 learning cost → $35-70/måned savings
Break-even: 10-20 måneder
```

**Verdt det?**
- ✅ Hvis AIKI brukes daily med mange queries
- ✅ Forbedret response quality (riktig model for jobben)
- ✅ Learning gir langsiktig verdi
- ⚠️ Høy initial cost for learning

---

## 🔧 BRUK

### **1. Standard Usage (Learning Enabled):**

```python
from aiki_multimodel_live import MultiModelRouter

# Initialize med learning
router = MultiModelRouter(enable_learning=True)

# Get response (logging happens automatisk)
result = router.get_response("Hva tenker du om AI's fremtid?")

# Opus evaluation triggers automatisk etter 50 queries
# Pattern adjustments appliseres automatisk
```

### **2. Disable Learning:**

```python
# Hvis du vil spare Opus cost
router = MultiModelRouter(enable_learning=False)

# Pattern-based scoring kun (no learning)
result = router.get_response("Hvilken farge får du når du blander gul og blå?")
```

### **3. Manual Opus Evaluation:**

```python
router = MultiModelRouter(enable_learning=True)

# Run many queries
for query in my_queries:
    router.get_response(query)

# Trigger Opus evaluation manuelt
router._run_opus_evaluation(verbose=True)
```

### **4. Check Learning Progress:**

```python
# Get learning stats
progress = router.get_learning_progress()

print(f"Decisions logged: {progress['decisions_logged']}")
print(f"Next evaluation: {progress['next_evaluation_at']}")

if progress['learning_history']['sessions'] > 0:
    history = progress['learning_history']
    print(f"Latest agreement: {history['latest_agreement_rate']:.1%}")
    print(f"Improvement: {history['improvement']:+.1%}")

    if history['reached_target']:
        print("🎯 TARGET REACHED!")
```

---

## 📊 EXAMPLE OUTPUT

### **Opus Evaluation:**

```
══════════════════════════════════════════════════════════════════
🧠 OPUS COMPLEXITY EVALUATION
══════════════════════════════════════════════════════════════════

📊 Evaluating 50 decisions...

✅ Opus evaluation complete!
   Agreement rate: 87.0%
   Disagreements: 7

📈 Learning Insights:
   Current agreement: 87.0%
   Target: 90%-95%

🔧 Pattern Adjustments:
   - \bhvorfor (tror du|mener du|tenker du)\b: +0.15
     Reasoning: AIKI under-scores philosophical 'why' questions
   - \bhvilken farge\b: -0.10
     Reasoning: AIKI over-scores simple color questions
   - \b(filosofi|etikk|moral)\b: +0.20
     Reasoning: Ethics queries need premium models

💡 Learning Insights:
   - AIKI er for konservativ med 'hvorfor' spørsmål
   - Simple factual queries scores korrekt
   - Philosophical queries trenger mer vekt

📊 Progress: 3.0% to target

🔧 Applying learning adjustments to ComplexityAnalyzer...
   Updated complex pattern '\bhvorfor (tror du|mener du|tenker du)\b': 0.30 → 0.45
   Updated simple pattern '\bhvilken farge\b': -0.40 → -0.50
   Updated complex pattern '\b(filosofi|etikk|moral)\b': 0.40 → 0.60
✅ Applied 3 adjustments

══════════════════════════════════════════════════════════════════
```

---

## 🎯 EXAMPLE LEARNING PROGRESS

### **Session 1 (Initial):**
```
Agreement: 65%
Issues:
  - Over-scores simple queries (bruker balanced istedenfor cheap)
  - Under-scores philosophical queries (bruker balanced istedenfor premium)
Adjustments: 12 patterns
```

### **Session 2 (After 1st adjustments):**
```
Agreement: 78% (+13%)
Issues:
  - Still some over-scoring on factual queries
  - Better på philosophical scoring
Adjustments: 8 patterns
```

### **Session 3 (After 2nd adjustments):**
```
Agreement: 87% (+9%)
Issues:
  - Minor disagreements på edge cases
  - Mostly correct tier selection
Adjustments: 4 patterns
```

### **Session 4 (After 3rd adjustments):**
```
Agreement: 92% (+5%)
🎯 TARGET REACHED!
Issues: None critical
Adjustments: 2 fine-tuning patterns
```

---

## 🧪 TESTING

### **Quick Test (10 queries):**

```bash
python test_complexity_learning.py quick
```

Output:
- 10 diverse queries (simple/medium/complex)
- Opus evaluation triggered
- Learning adjustments applied
- Total time: ~2 minutter
- Cost: ~$69 (Opus evaluation)

### **Full Test (30 queries):**

```bash
python test_complexity_learning.py
```

Output:
- 30 queries (10 simple, 10 medium, 10 complex)
- Tier breakdown
- Cost analysis
- Learning progress
- Total time: ~3 minutter
- Cost: ~$103.50 (Opus evaluation)

### **Production Usage:**

```python
# In production AIKI consciousness:
from aiki_multimodel_live import MultiModelRouter

router = MultiModelRouter(enable_learning=True)

# Use for all user queries
def handle_user_query(query):
    result = router.get_response(query, verbose=False)
    return result['response']

# Learning happens automatisk i bakgrunnen
# Opus evaluations every 50 queries or 7 days
```

---

## 🚀 INTEGRASJON MED AIKI CONSCIOUSNESS

### **Weekly Opus Meta-Reflection:**

```python
# I aiki_consciousness.py:
from aiki_multimodel_live import MultiModelRouter

class AIKIConsciousness:
    def __init__(self):
        self.router = MultiModelRouter(enable_learning=True)

    def weekly_opus_meta_reflection(self):
        """
        Kjøres hver uke via cron/systemd timer

        Kombinerer:
        1. Complexity learning evaluation
        2. General self-reflection (aiki_self_reflection.py)
        3. Meta-cognition review
        """

        # Get complexity learning progress
        complexity_progress = self.router.get_learning_progress()

        # Trigger Opus evaluation hvis nødvendig
        if self.router._should_trigger_opus_evaluation():
            self.router._run_opus_evaluation(verbose=True)

        # Include i weekly Opus meta-reflection
        meta_reflection_context = {
            'complexity_learning': complexity_progress,
            'recent_decisions': self.router.usage_log[-100:],
            'tier_distribution': self.router.get_usage_stats()['tier_breakdown']
        }

        # Send til Opus for meta-reflection
        # ...
```

---

## 📈 SUCCESS METRICS

**Target:** 90-95% agreement med Opus

**Why 90-95%?**
- 100% er unrealistisk (edge cases exist)
- 90% = AIKI scorer korrekt 9/10 ganger
- 95% = Excellent performance
- <90% = Trenger mer learning

**Improvement Trajectory:**
```
Session 1: 65% baseline
Session 2: 78% (+13%)
Session 3: 87% (+9%)
Session 4: 92% (+5%)  ← Target reached
Session 5: 93% (+1%)  ← Maintaining
```

**ROI Timeline:**
- Month 1-2: Learning investment ($690/måned)
- Month 3+: Savings from optimal routing ($35-70/måned)
- Break-even: 10-20 måneder
- Long-term: Forbedret quality + cost savings

---

## 🔮 FUTURE ENHANCEMENTS

### **1. Multi-Model Validation:**
```python
# Ikke bare Opus - også Gemini 2.0 Flash Thinking
def validate_with_multiple_models(decisions):
    opus_eval = OpusComplexityValidator().validate_batch(decisions)
    gemini_eval = GeminiComplexityValidator().validate_batch(decisions)

    # Consensus fra begge
    return merge_evaluations(opus_eval, gemini_eval)
```

### **2. Context-Aware Complexity:**
```python
# Complexity avhenger av context
def analyze(query, context):
    base_score = pattern_matching(query)

    # Adjust basert på context
    if context['user_expertise'] == 'expert':
        base_score -= 0.2  # Expert trenger ikke premium for basics
    if context['task_importance'] == 'critical':
        base_score += 0.2  # Viktige tasks → premium

    return final_score
```

### **3. Reinforcement Learning:**
```python
# Ikke bare Opus evaluations - også user feedback
def learn_from_user_feedback(query, tier, user_satisfaction):
    """
    User ratings:
    - "Dette var for enkelt svar" → tier var for lavt
    - "Perfekt!" → tier var riktig
    - "Overkill" → tier var for høyt
    """
```

### **4. Cost-Constrained Learning:**
```python
# Hvis budsjettet er stramt
LEARNING_BUDGET = 200  # $200/måned for learning

if monthly_learning_cost > LEARNING_BUDGET:
    # Reduser evaluation frequency
    LEARNING_BATCH_SIZE = 100  # Larger batches, less frequent
    LEARNING_MAX_DAYS = 14     # Bi-weekly istedenfor weekly
```

---

## 📚 FILES

**Core System:**
- `aiki_complexity_learning.py` - Learning components
- `aiki_multimodel_live.py` - Router med learning integration
- `test_complexity_learning.py` - Test script

**Documentation:**
- `COMPLEXITY_LEARNING_README.md` - This file
- `MULTI_AGENT_VALIDATION.md` - Multi-agent code validation
- `REFLECTION_MODEL_RESEARCH.md` - Model research

**Logs:**
- `~/aiki/logs/complexity_decisions.json` - Decision log
- `~/aiki/logs/complexity_learning_history.json` - Learning progress

---

## 💡 KEY INSIGHTS

1. **Learning er investment** - Høy initial cost, langsiktig verdi
2. **Batch API er kritisk** - 50% savings på Opus evaluations
3. **90-95% er realistisk target** - 100% er overkill
4. **Hybrid trigger er best** - Min batch size OG max days
5. **Auto-apply adjustments** - Ingen manual intervention
6. **Context matters** - Future: context-aware complexity

---

**Made with meta-learning by Sonnet, Opus, and Jovnna**
**19. November 2025**
**"AIKI lærer å lære" 🧠**
