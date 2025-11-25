# 🔍 AIKI SYSTEM AUDIT REPORT

**Dato:** 19. November 2025
**Scope:** Alle self-evolving systems
**Auditor:** Claude Code (Sonnet 4.5)

---

## 📊 EXECUTIVE SUMMARY

**Systemer auditert:**
- aiki_self_reflection.py (336 linjer)
- aiki_self_modification.py (520 linjer)
- aiki_multi_agent_validator.py (481 linjer)
- aiki_multimodel_live.py (737 linjer)
- aiki_complexity_learning.py (622 linjer)
- aiki_consciousness.py (710 linjer)

**Total:** 3,406 linjer kode

**Funn:**
- 🔴 **8 kritiske feil** (må fikses før production)
- 🟡 **12 forbedringer** (øker quality/performance)
- 💡 **7 innovative ideer** (ting du ikke har tenkt på)

---

## 🔴 KRITISKE FEIL (MÅ FIKSES)

### 1. **SECURITY: Hardcoded API Key**

**Filer:** 14 filer inkluderer hardcoded `OPENROUTER_KEY`

```python
# PROBLEMATISK:
OPENROUTER_KEY = 'sk-or-v1-...'  # Hardcoded!
```

**Risiko:** Hvis koden pushes til GitHub = API key leak = $$$

**Fix:**
```python
# Bruk environment variable:
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY')
if not OPENROUTER_KEY:
    raise ValueError("OPENROUTER_KEY not set!")
```

**Filer å fikse:**
- aiki_self_reflection.py
- aiki_self_modification.py
- aiki_multi_agent_validator.py
- aiki_multimodel_live.py
- aiki_complexity_learning.py
- aiki_consciousness.py
- Alle migrations (kan sikkert slettes?)

---

### 2. **FEIL MODEL: Llama brukes for reflection**

**Fil:** `aiki_self_reflection.py:176`

```python
# PROBLEMATISK:
"model": "meta-llama/llama-3.1-70b-instruct",  # Dårlig metacognition!
```

**Problem:**
- Din egen research viste Llama 70B har 3/10 metacognition score
- Haiku 4.5 er best cost/performance for reflection
- Opus 4 skal brukes for critical reflections

**Fix:**
```python
def _llm_reflect(self, prompt: str, severity: str = 'minor') -> str:
    # Model selection basert på severity
    if severity == 'major':
        model = 'anthropic/claude-opus-4'  # Critical: $15/1M
    else:
        model = 'anthropic/claude-3.5-haiku'  # Standard: $1/1M
```

**Impact:** Dette påvirker hele self-reflection quality!

---

### 3. **INGEN PERSISTENCE: Memory loss ved restart**

**Filer:** `aiki_self_reflection.py`, `aiki_multi_agent_validator.py`, `aiki_complexity_learning.py`

**Problem:**
```python
self.reflection_log = []  # Kun i memory!
self.validation_log = []  # Kun i memory!
self.learning_history = []  # Kun i memory!
```

**Impact:**
- AIKI restarter → mister ALL reflection history
- Mister all validation history
- Mister learning progress (tilbake til 0% agreement!)

**Fix:**
```python
# Option 1: JSON persistence
REFLECTION_LOG = Path.home() / "aiki" / "logs" / "reflections.json"

def _save_log(self):
    with open(REFLECTION_LOG, 'w', encoding='utf-8') as f:
        json.dump(self.reflection_log, f, indent=2)

def _load_log(self):
    if REFLECTION_LOG.exists():
        with open(REFLECTION_LOG, 'r', encoding='utf-8') as f:
            self.reflection_log = json.load(f)

# Option 2: mem0 integration (BEDRE!)
def _save_to_mem0(self, reflection):
    m.add([{
        'role': 'user',
        'content': json.dumps(reflection)
    }],
    user_id='jovnna',
    metadata={'agent_id': 'self_reflection_engine'})
```

---

### 4. **EKSTREM COST: Hele consciousness file til Sonnet**

**Fil:** `aiki_multi_agent_validator.py:161-175`

```python
# PROBLEMATISK:
with open(CONSCIOUSNESS_FILE, 'r', encoding='utf-8') as f:
    current_code = f.read()  # 710 linjer!

prompt = f"""...
CURRENT aiki_consciousness.py:
(File er {len(current_code)} chars - du må identifisere riktig seksjon å endre)
...
"""
```

**Problem:**
- 710 linjer × 4 chars/token ≈ **2,840 input tokens PER modification**
- Sonnet: $3/1M = $0.0085 per modification
- Opus review: $15/1M = $0.043 per modification
- **Total: ~$0.052 per modification bare for context!**

**Fix - Diff-based approach:**
```python
def _get_relevant_context(self, change_type: str) -> str:
    """
    Istedenfor hele filen, hent kun relevant seksjon
    """
    with open(CONSCIOUSNESS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Identify relevant section basert på change_type
    if change_type == 'system_prompt':
        # Return bare _build_system_prompt() metoden
        start = lines.index('    def _build_system_prompt')
        end = start + 50  # Eller til neste metode
        return ''.join(lines[start:end])

    # Eller bruk ast.parse() for å finne specific funksjoner
```

**Impact:** 95% cost reduction på context!

---

### 5. **TODO IKKE IMPLEMENTERT: Save interactions til Qdrant**

**Fil:** `aiki_consciousness.py:433`

```python
# TODO: Save til Qdrant for fremtidig fine-tuning
```

**Problem:**
- AIKI lærer ikke fra interaksjoner over tid
- Kan ikke bruke data til fine-tuning
- Mister verdifull training data

**Fix:**
```python
def _save_interaction_to_memory(self, user_msg, aiki_response, metadata):
    """
    Lagre interaksjon til mem0 for:
    1. Fine-tuning data
    2. Pattern analysis
    3. Long-term learning
    """
    interaction = {
        'user_message': user_msg,
        'aiki_response': aiki_response,
        'complexity_tier': metadata.get('tier'),
        'cost': metadata.get('cost'),
        'reflection_score': metadata.get('reflection_score')
    }

    self.memory.client.upsert(
        collection_name='aiki_interactions',
        points=[{
            'id': str(uuid.uuid4()),
            'vector': self.memory._get_embedding(user_msg),
            'payload': interaction
        }]
    )
```

---

### 6. **INGEN ERROR HANDLING ved API failures**

**Filer:** Alle filer med LLM calls

**Problem:**
```python
response = requests.post(url, headers=headers, json=payload, timeout=30)
if response.status_code == 200:
    return data['choices'][0]['message']['content']
else:
    return f"Error: {response.status_code}"  # Bare returnerer error string!
```

**Issues:**
- Ingen retry ved transient errors (429 rate limit, 503 service unavailable)
- Ingen exponential backoff
- Ingen fallback model ved Opus failure

**Fix - Retry with exponential backoff:**
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise

                    # Exponential backoff
                    delay = base_delay * (2 ** attempt)
                    print(f"⚠️ API error: {e}. Retrying in {delay}s...")
                    time.sleep(delay)

        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def _llm_call(self, model, prompt):
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()  # Raise exception for 4xx/5xx
    return response.json()
```

---

### 7. **BATCH API IKKE IMPLEMENTERT**

**Dokumentasjon sier:** "Bruk Batch API for 50% discount"
**Realitet:** Alle LLM calls er synchronous!

**Problem:**
- Opus evaluation: $690/måned med Batch API
- **ACTUAL COST: $1,380/måned** (uten discount!)

**Fix:**
```python
class BatchAPIManager:
    """
    Anthropic Batch API for 50% discount

    Tradeoff: 24 hour processing time (OK for non-urgent)
    """

    def submit_batch(self, requests: List[Dict]) -> str:
        """Submit batch of requests"""
        batch_data = {
            "requests": [
                {
                    "custom_id": f"req_{i}",
                    "params": {
                        "model": req['model'],
                        "messages": req['messages']
                    }
                }
                for i, req in enumerate(requests)
            ]
        }

        # Submit via Anthropic Batch API
        response = requests.post(
            "https://api.anthropic.com/v1/messages/batches",
            headers={"x-api-key": ANTHROPIC_KEY},
            json=batch_data
        )

        return response.json()['id']

    def check_batch_status(self, batch_id: str):
        """Poll batch status"""
        # Implementation...
```

**Usage:**
```python
# Weekly Opus meta-reflection via Batch API
def weekly_opus_meta_reflection(self):
    # Collect all decisions from last week
    decisions = self.decision_logger.get_all_decisions()

    # Submit as batch (50% discount!)
    batch_id = self.batch_manager.submit_batch([
        {
            'model': 'claude-opus-4',
            'messages': [{'role': 'user', 'content': prompt}]
        }
    ])

    # Check back later (24h window OK for weekly reflection)
```

---

### 8. **INGEN COST TRACKING**

**Problem:**
- Vi bruker Opus ($15/1M), Sonnet ($3/1M), Haiku ($1/1M)
- **INGEN tracking av actual costs!**
- Kan bli overraskelse på OpenRouter bill

**Fix:**
```python
class CostTracker:
    """Track actual API costs"""

    def __init__(self):
        self.costs = {
            'reflection': 0.0,
            'modification': 0.0,
            'complexity_learning': 0.0,
            'total': 0.0
        }
        self.load_costs()

    def log_cost(self, category: str, input_tokens: int,
                output_tokens: int, model: str):
        """
        Log cost for API call

        Models:
        - claude-opus-4: $15/$75 per 1M
        - claude-sonnet-3.5: $3/$15 per 1M
        - claude-haiku-3.5: $1/$4 per 1M
        """
        rates = {
            'anthropic/claude-opus-4': (15, 75),
            'anthropic/claude-3.5-sonnet': (3, 15),
            'anthropic/claude-3.5-haiku': (1, 4),
            'meta-llama/llama-3.1-70b-instruct': (0.0001, 0.0001)
        }

        input_rate, output_rate = rates.get(model, (0, 0))
        cost = (
            (input_tokens / 1_000_000) * input_rate +
            (output_tokens / 1_000_000) * output_rate
        )

        self.costs[category] += cost
        self.costs['total'] += cost

        self.save_costs()

        # Alert hvis over budget
        if self.costs['total'] > 100:  # $100/måned budget
            print(f"⚠️ COST ALERT: ${self.costs['total']:.2f} this month!")
```

---

## 🟡 FORBEDRINGER (QUALITY + PERFORMANCE)

### 9. **ComplexityAnalyzer patterns kan være bedre**

**Fil:** `aiki_multimodel_live.py:39-103`

**Problem:**
- Pattern-based scoring er OK, men kan forbedres
- Mangler context-awareness (brukerens expertise level)
- Mangler time-of-day patterns (komplekse queries = evening?)

**Forbedr:**
```python
def analyze(self, query: str, context: Optional[Dict] = None) -> Dict:
    # Existing pattern matching...
    base_score = ...

    # NEW: Context-aware adjustments
    if context:
        # User expertise
        if context.get('user_expertise') == 'expert':
            base_score -= 0.2  # Expert trenger ikke premium for basics

        # Task importance
        if context.get('importance') == 'critical':
            base_score += 0.3  # Critical tasks → premium model

        # Time of day (optional)
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Work hours
            # More likely to be complex work questions
            base_score += 0.1
```

---

### 10. **Sandbox testing er minimal**

**Fil:** `aiki_multi_agent_validator.py:340-413`

**Problem:**
```python
# Test 1: Syntax check (compile)
# Test 2: Import check
# That's it!
```

**Forbedr:**
```python
def _sandbox_test(self, code: Dict) -> Dict:
    # Existing: syntax + import

    # NEW: Run Sonnet's test cases!
    test_cases = code.get('test_cases', [])
    test_results = []

    for test in test_cases:
        test_input = test['test_input']
        expected = test['expected_behavior']

        # Execute test in sandbox
        test_script = f"""
import sys
sys.path.insert(0, '.')
from aiki_consciousness import AIKIConsciousness

# Run test
aiki = AIKIConsciousness()
result = aiki.process_input("{test_input}")

# Verify expected behavior
# (simplified - actual verification would be smarter)
if "{expected}" in result:
    print("TEST_PASS")
else:
    print("TEST_FAIL")
"""

        result = subprocess.run(
            ['python3', '-c', test_script],
            cwd=sandbox_dir,
            capture_output=True,
            timeout=10
        )

        test_results.append({
            'test': test,
            'passed': 'TEST_PASS' in result.stdout
        })

    return {
        'passed': all(t['passed'] for t in test_results),
        'test_results': test_results
    }
```

---

### 11. **Ingen pattern caching**

**Problem:**
- Hvis samme type modification flere ganger, re-run full validation hver gang
- Waste of Opus calls!

**Forbedr:**
```python
class ModificationCache:
    """
    Cache similar modifications to save Opus calls
    """

    def __init__(self):
        self.cache = {}  # {modification_hash: validation_result}

    def get_cached(self, proposal: Dict) -> Optional[Dict]:
        """
        Check if similar modification already validated
        """
        # Create hash based on change_type + description similarity
        cache_key = f"{proposal['change_type']}_{hash(proposal['description'][:50])}"

        return self.cache.get(cache_key)

    def cache_result(self, proposal: Dict, result: Dict):
        """Cache validation result"""
        cache_key = f"{proposal['change_type']}_{hash(proposal['description'][:50])}"
        self.cache[cache_key] = result
```

---

### 12. **identify_patterns() brukes aldri**

**Fil:** `aiki_self_reflection.py:249-303`

**Problem:**
- Fin funksjon for pattern analysis
- **MEN:** Brukes ALDRI!

**Fix:**
```python
# I weekly_opus_meta_reflection():
def weekly_opus_meta_reflection(self):
    # Get patterns from reflections
    patterns = self.reflection.identify_patterns()

    if patterns['improvement_trend'] == 'declining':
        print("⚠️ AIKI quality declining! Trigger deep reflection...")
        # Trigger major Opus reflection

    if patterns['common_issues']:
        print(f"📊 Common issues: {patterns['common_issues']}")
        # Propose modifications to fix recurring issues
```

---

### 13. **Ingen logging/monitoring**

**Problem:**
- Hvis noe går galt, ingen visibility
- Ingen metrics for debugging

**Forbedr:**
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/jovnna/aiki/logs/aiki.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('aiki_consciousness')

# Usage:
logger.info(f"Processing query #{self.interaction_count}")
logger.warning(f"Reflection quality low: {score:.2f}")
logger.error(f"API call failed: {e}")
```

---

### 14. **Ingen rate limiting**

**Problem:**
- Hvis AIKI får mange queries raskt, kan hit API rate limits
- OpenRouter: varies by provider

**Fix:**
```python
from time import sleep
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    """Simple token bucket rate limiter"""

    def __init__(self, max_calls: int = 100, per_seconds: int = 60):
        self.max_calls = max_calls
        self.per_seconds = per_seconds
        self.calls = deque()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.now()

        # Remove calls outside window
        cutoff = now - timedelta(seconds=self.per_seconds)
        while self.calls and self.calls[0] < cutoff:
            self.calls.popleft()

        # Check if at limit
        if len(self.calls) >= self.max_calls:
            sleep_time = (self.calls[0] - cutoff).total_seconds()
            if sleep_time > 0:
                print(f"⏸️ Rate limit: waiting {sleep_time:.1f}s...")
                sleep(sleep_time)

        # Log this call
        self.calls.append(now)
```

---

### 15. **Ingen health monitoring**

**Problem:**
- Hvis Qdrant down, AIKI crashes
- Hvis OpenRouter down, AIKI crashes

**Fix:**
```python
class HealthMonitor:
    """Monitor system health"""

    def check_dependencies(self):
        """Check all dependencies healthy"""
        health = {
            'qdrant': self._check_qdrant(),
            'openrouter': self._check_openrouter(),
            'mem0': self._check_mem0()
        }

        return all(health.values()), health

    def _check_qdrant(self) -> bool:
        try:
            self.qdrant.get_collections()
            return True
        except:
            return False

    def _check_openrouter(self) -> bool:
        try:
            # Minimal test call
            response = requests.get(
                f"{OPENROUTER_URL}/models",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
```

---

### 16. **Reflection log kan bli enorm**

**Problem:**
```python
self.reflection_log.append(...)  # Infinite growth!
```

**Fix:**
```python
def _manage_log_size(self):
    """Keep log from growing infinitely"""
    MAX_LOG_SIZE = 1000  # Keep last 1000 reflections

    if len(self.reflection_log) > MAX_LOG_SIZE:
        # Archive old reflections
        old = self.reflection_log[:-MAX_LOG_SIZE]
        self._archive_reflections(old)

        # Keep recent only
        self.reflection_log = self.reflection_log[-MAX_LOG_SIZE:]
```

---

### 17. **weekly_opus_meta_reflection() mangler scheduling**

**Problem:**
- Metoden finnes, men INGEN automatisk trigger!
- Må kalles manuelt

**Fix:** Systemd timer (kommer i neste seksjon)

---

### 18. **Complexity learning ikke integrert med reflection**

**Problem:**
- Complexity learning og self-reflection er separate
- Burde lære fra hverandre!

**Forbedr:**
```python
def weekly_opus_meta_reflection(self):
    # Get complexity learning insights
    complexity_patterns = self.router.learning_system.get_patterns()

    # Get reflection insights
    reflection_patterns = self.reflection.identify_patterns()

    # CROSS-ANALYZE:
    # Hvis complexity scorer queries som cheap MEN reflection quality er lav
    # → Maybe vi trenger bedre models for disse queries?

    for decision in complexity_patterns['disagreements']:
        matching_reflections = [
            r for r in reflection_patterns
            if r['query'] == decision['query']
        ]

        if matching_reflections:
            ref_score = matching_reflections[0]['quality_score']
            if ref_score < 0.6 and decision['tier'] == 'cheap':
                print(f"💡 INSIGHT: Query '{decision['query']}' scored as cheap")
                print(f"   BUT reflection quality was low ({ref_score:.2f})")
                print(f"   → Should use higher tier for this type?")
```

---

### 19. **Ingen graceful degradation**

**Problem:**
- Hvis Opus unavailable, hele system stopper

**Fix:**
```python
def _llm_reflect(self, prompt: str, severity: str = 'minor') -> str:
    models_by_preference = [
        'anthropic/claude-opus-4',      # Preferred
        'anthropic/claude-3.5-sonnet',  # Fallback 1
        'anthropic/claude-3.5-haiku',   # Fallback 2
        'meta-llama/llama-3.1-70b-instruct'  # Last resort
    ]

    for model in models_by_preference:
        try:
            return self._try_model(model, prompt)
        except Exception as e:
            logger.warning(f"Model {model} failed: {e}. Trying next...")
            continue

    raise Exception("All models failed!")
```

---

### 20. **Mangler versioning av consciousness**

**Problem:**
- AIKI modifiserer seg selv
- Hva om modification gjør ting verre?
- Hvordan rollback til "good state"?

**Fix:**
```python
class ConsciousnessVersioning:
    """
    Git-like versioning for AIKI consciousness

    Track which modifications work well vs poorly
    """

    def __init__(self):
        self.versions = []

    def create_checkpoint(self, description: str):
        """Create versioned checkpoint"""
        checkpoint = {
            'version': len(self.versions) + 1,
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'file_hash': self._get_file_hash(CONSCIOUSNESS_FILE),
            'performance_metrics': {
                'avg_reflection_score': self.get_avg_score(),
                'complexity_agreement': self.get_complexity_agreement()
            }
        }

        self.versions.append(checkpoint)

        # Backup file
        backup_path = BACKUP_DIR / f"v{checkpoint['version']}_aiki_consciousness.py"
        shutil.copy2(CONSCIOUSNESS_FILE, backup_path)

    def rollback_to_best_version(self):
        """
        Find version with best performance metrics
        and rollback to it
        """
        best = max(
            self.versions,
            key=lambda v: v['performance_metrics']['avg_reflection_score']
        )

        print(f"📈 Best version: v{best['version']} ({best['timestamp']})")
        print(f"   Reflection score: {best['performance_metrics']['avg_reflection_score']:.2f}")

        # Rollback
        backup_path = BACKUP_DIR / f"v{best['version']}_aiki_consciousness.py"
        shutil.copy2(backup_path, CONSCIOUSNESS_FILE)
```

---

## 💡 INNOVATIVE IDEER (Du har ikke tenkt på)

### 21. **A/B Testing for modifications**

**Idé:**
Istedenfor å apply modification til production direkte:
1. Create shadow instance med modification
2. Run both versions side-by-side
3. Compare performance metrics
4. Apply modification only if measurably better

```python
class ABTestModification:
    """
    Test modifications in parallel before applying
    """

    def test_modification(self, modification: Dict, n_queries: int = 50):
        """
        Run A/B test: current vs modified version
        """
        # Create shadow instance
        shadow = self._create_shadow_instance(modification)

        # Run same queries through both
        for query in test_queries:
            result_a = self.current_instance.process_input(query)
            result_b = shadow.process_input(query)

            # Compare metrics
            # ... quality scores, user satisfaction, etc.

        # Decide which is better
        if shadow.avg_score > self.current_instance.avg_score:
            print("✅ Modification improves performance! Applying...")
            return True
        else:
            print("❌ Modification doesn't help. Rejecting...")
            return False
```

---

### 22. **Proactive modification suggestions**

**Idé:**
AIKI don't wait for reflection to suggest modifications.
Proaktivt analyze patterns og foreslå improvements.

```python
class ProactiveImprovement:
    """
    AIKI proaktivt identifiserer improvement opportunities
    """

    def analyze_improvement_opportunities(self):
        """
        Analyze usage patterns og suggest improvements
        UTEN å vente på user feedback
        """
        opportunities = []

        # 1. Check if specific query types always score low
        low_scoring_patterns = self._find_low_scoring_patterns()
        if low_scoring_patterns:
            opportunities.append({
                'type': 'quality_improvement',
                'pattern': low_scoring_patterns,
                'suggestion': 'Add specialized handling for these queries'
            })

        # 2. Check if we're overpaying for simple queries
        overpaying = self._find_overpaying_patterns()
        if overpaying:
            opportunities.append({
                'type': 'cost_optimization',
                'pattern': overpaying,
                'suggestion': 'Adjust complexity scoring for these patterns'
            })

        # 3. Check if certain model tiers never used
        underutilized = self._find_underutilized_tiers()
        if underutilized:
            opportunities.append({
                'type': 'resource_optimization',
                'tier': underutilized,
                'suggestion': 'Recalibrate scoring or remove unused tier'
            })

        return opportunities
```

---

### 23. **User-specific customization**

**Idé:**
AIKI lærer Jovnnas preferanser og tilpasser seg.

```python
class UserProfile:
    """
    Learn user-specific preferences

    Jovnna liker:
    - Kort svar
    - Norsk språk
    - Ingen unødvendige spørsmål
    """

    def __init__(self):
        self.preferences = self._load_preferences()

    def learn_preference(self, interaction: Dict):
        """
        Learn from user reactions:
        - If user repeats query → AIKI didn't understand
        - If user says "kort!" → AIKI was too verbose
        - If user asks follow-up → AIKI was too terse
        """

        # Detect patterns in user feedback
        if 'for langt' in interaction['user_reaction'].lower():
            self.preferences['max_response_length'] -= 50

        if 'mer detaljer' in interaction['user_reaction'].lower():
            self.preferences['detail_level'] += 0.1

    def apply_preferences(self, response: str) -> str:
        """
        Apply learned preferences to response
        """
        if len(response) > self.preferences['max_response_length']:
            # Truncate or summarize
            pass

        return response
```

---

### 24. **Multi-agent consensus for responses**

**Idé:**
Viktige queries → få svar fra FLERE modeller → velg beste.

```python
class ConsensusResponse:
    """
    For kritiske queries: få svar fra multiple models
    og bruk beste/consensus
    """

    def get_consensus_response(self, query: str, n_agents: int = 3):
        """
        Get response from multiple agents
        """
        agents = [
            ('claude-sonnet', 'anthropic/claude-3.5-sonnet'),
            ('gpt-4o', 'openai/gpt-4o'),
            ('gemini-flash', 'google/gemini-2.0-flash-exp')
        ]

        responses = []
        for name, model in agents[:n_agents]:
            response = self._get_response(model, query)
            responses.append({
                'agent': name,
                'response': response,
                'confidence': self._estimate_confidence(response)
            })

        # Choose best based on:
        # - Highest confidence
        # - Agreement with others (if similar = good)
        # - Past performance of agent

        best = max(responses, key=lambda r: r['confidence'])
        return best['response']
```

---

### 25. **Predictive model selection**

**Idé:**
Lær hvilke queries kommer sammen, pre-load models.

```python
class PredictiveModelLoader:
    """
    Predict next query type og pre-load model

    Pattern: "Hei AIKI" ofte følges av complex query
    → Pre-load Opus for neste query
    """

    def __init__(self):
        self.query_sequences = []  # [(query1, query2, tier2), ...]

    def learn_sequence(self, prev_query, curr_query, tier):
        """Learn query patterns"""
        self.query_sequences.append((prev_query, curr_query, tier))

    def predict_next_tier(self, curr_query):
        """
        Predict tier for next query based on current
        """
        matches = [
            (q2, tier) for q1, q2, tier in self.query_sequences
            if q1 == curr_query
        ]

        if matches:
            # Return most common tier that follows this query
            from collections import Counter
            tiers = [tier for _, tier in matches]
            most_common = Counter(tiers).most_common(1)[0][0]
            return most_common

        return 'balanced'  # Default
```

---

### 26. **Emotion-aware responses**

**Idé:**
AIKI kan detect user emotion og tilpasse tone.

```python
class EmotionDetector:
    """
    Detect user emotion fra message
    Adjust AIKI's tone accordingly
    """

    def detect_emotion(self, message: str) -> str:
        """
        Detect emotion: frustrated, excited, confused, neutral
        """
        # Simple pattern matching (kunne bruke LLM)
        patterns = {
            'frustrated': ['ikke funker', 'irriterende', 'fuck', 'gir opp'],
            'excited': ['awesome', 'kult', 'utrolig', '!!!!'],
            'confused': ['skjønner ikke', 'hva mener du', 'forklare'],
            'urgent': ['ASAP', 'nå', 'haster', 'critical']
        }

        for emotion, keywords in patterns.items():
            if any(kw in message.lower() for kw in keywords):
                return emotion

        return 'neutral'

    def adjust_tone(self, response: str, emotion: str) -> str:
        """
        Adjust response tone based on detected emotion
        """
        if emotion == 'frustrated':
            # Be extra supportive, offer concrete help
            return f"Jeg skjønner frustrasjonen. La meg hjelpe. {response}"

        elif emotion == 'excited':
            # Match energy!
            return f"Ja! {response}"

        elif emotion == 'confused':
            # Be extra clear and simple
            return f"La meg forklare tydeligere: {response}"

        elif emotion == 'urgent':
            # Cut to the chase, no fluff
            return response  # Already concise

        return response
```

---

### 27. **Automatic benchmark generation**

**Idé:**
AIKI genererer sine egne benchmarks for å måle progress.

```python
class BenchmarkGenerator:
    """
    Auto-generate benchmarks for AIKI

    Track: "Am I getting better over time?"
    """

    def generate_benchmark_set(self, n: int = 50):
        """
        Generate diverse benchmark queries
        """
        categories = [
            'simple_factual',
            'medium_explanation',
            'complex_reasoning',
            'norwegian_language',
            'code_related',
            'adhd_specific'
        ]

        benchmarks = []
        for category in categories:
            # Generate queries for each category
            queries = self._generate_category_queries(category, n // len(categories))
            benchmarks.extend(queries)

        return benchmarks

    def run_benchmark(self, benchmark_set):
        """
        Run AIKI through benchmark set
        Measure: quality, cost, latency
        """
        results = []

        for query in benchmark_set:
            start = time.time()
            response = self.aiki.process_input(query)
            latency = time.time() - start

            # Get reflection score
            reflection = self.aiki.reflection.reflect_on_interaction(
                query, response, {}
            )

            results.append({
                'query': query,
                'quality': reflection['quality_score'],
                'cost': self.last_cost,
                'latency': latency
            })

        return {
            'avg_quality': mean(r['quality'] for r in results),
            'avg_cost': mean(r['cost'] for r in results),
            'avg_latency': mean(r['latency'] for r in results)
        }

    def compare_versions(self, v1_results, v2_results):
        """
        Compare two AIKI versions
        """
        quality_delta = v2_results['avg_quality'] - v1_results['avg_quality']
        cost_delta = v2_results['avg_cost'] - v1_results['avg_cost']

        print(f"📊 Benchmark comparison:")
        print(f"   Quality: {quality_delta:+.2f} ({'+better' if quality_delta > 0 else 'worse'})")
        print(f"   Cost: ${cost_delta:+.4f} ({'+cheaper' if cost_delta < 0 else 'pricier'})")
```

---

## 📝 PRIORITY FIX LIST

**Må fikses NÅ (før production):**
1. ✅ Move OPENROUTER_KEY til environment variable (security!)
2. ✅ Fix reflection model (Llama → Haiku/Opus)
3. ✅ Add persistence for reflection/validation logs
4. ✅ Reduce cost: Diff-based prompting i validator
5. ✅ Implement error handling + retry logic

**Burde fikses snart:**
6. Implement Batch API for Opus calls (50% savings!)
7. Add cost tracking system
8. Save interactions til Qdrant
9. Improve sandbox testing (run test cases)
10. Add logging/monitoring

**Nice to have:**
11. Implement innovative features (A/B testing, proactive suggestions, etc.)
12. Create benchmarks
13. Add emotion detection
14. Versioning system

---

## 🎯 RECOMMENDATIONS

### Immediate Actions:
1. **Create `.env` file:**
   ```bash
   echo "OPENROUTER_KEY=sk-or-v1-..." > /home/jovnna/aiki/.env
   echo ".env" >> /home/jovnna/aiki/.gitignore
   ```

2. **Fix reflection model TODAY** - dette påvirker all quality!

3. **Add persistence** - mister data hver restart nå

### Medium-term:
4. **Implement Batch API** - spare $690/måned!

5. **Add cost tracking** - vit hvor mye du bruker

### Long-term:
6. **Innovative features** - A/B testing, proactive improvements

7. **Benchmarking system** - måle progress objektivt

---

**Made with comprehensive system audit by Sonnet 4.5**
**19. November 2025**

**Neste steg:** Vil du at jeg fikser de kritiske feilene NÅ?
