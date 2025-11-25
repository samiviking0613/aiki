# 🧬 EVOLUTIONARY INTELLIGENCE - DYPDYKK

**Dato:** 19. november 2025
**Forfatter:** Claude Code + Jovnna
**Formål:** Forklare hvordan AIKI kan EVOLVE seg selv gjennom naturlig seleksjon

---

## 🌍 HVA ER EVOLUTIONARY INTELLIGENCE?

### Enkel definisjon:

**"Løse problemer ved å la løsninger EVOLVE gjennom generasjoner, akkurat som levende organismer."**

---

## 🦎 DARWIN'S EVOLUSJON (Biologisk analogI)

La oss starte med hvordan det fungerer i naturen:

### Eksempel: Galapagos-finker

**Generasjon 1 (før tørke):**
```
100 finker med ulike nebbstørrelser:
🐦 20 finker: Lite nebb (3mm)
🐦 50 finker: Medium nebb (5mm)
🐦 30 finker: Stort nebb (7mm)

Mat tilgjengelig: Både små og store frø
```

**Tørke rammer øya!**
```
Små frø dør ut → Kun store, harde frø igjen
```

**Naturlig seleksjon:**
```
🐦 Lite nebb (3mm): Kan ikke knekke harde frø → DØR ☠️
🐦 Medium nebb (5mm): Sliter, noen overlever 😰
🐦 Stort nebb (7mm): Knekker frø lett → OVERLEVER ✅
```

**Generasjon 2 (etter tørke):**
```
70 finker igjen (30 døde):
🐦 5 finker: Lite nebb (minoriteten som overlevde)
🐦 25 finker: Medium nebb (halvparten døde)
🐦 40 finker: Stort nebb (nesten alle overlevde!)

Gjennomsnittlig nebbstørrelse: 5mm → 6.2mm
```

**Generasjon 3 (barn av Gen 2):**
```
Finker med stort nebb får flest barn (best næringstilgang)
→ Genetisk arv: Barn får stort nebb fra foreldre
→ Gjennomsnittlig nebbstørrelse: 6.2mm → 6.8mm

EVOLUSJON! 🎉
```

---

## 🤖 EVOLUTIONARY INTELLIGENCE I AI

### Samme prinsipp, men for kode/strategier:

**I stedet for:**
- Finker → Consensus-konfigurasjoner
- Nebbstørrelse → Modell-kombinasjoner
- Frø → AIKI-problemer
- Overleve → Løse problemer riktig
- Reproduksjon → Lage nye configs

**Prosess:**

```
Generasjon 1: 10 random consensus configs
   ↓
Test: Hvilke løser problemer best?
   ↓
Seleksjon: Behold top 5 ("survival of the fittest")
   ↓
Reproduksjon: Mix top 5 for å lage 5 nye configs
   ↓
Mutasjon: Random endringer i noen configs
   ↓
Generasjon 2: 10 configs (5 gamle + 5 nye)
   ↓
Repeat 100 ganger...
   ↓
OPTIMAL CONFIG EMERGES! 🌟
```

---

## 📚 GENETIC ALGORITHM - STEP BY STEP

La meg forklare hver fase med KONKRET EKSEMPEL for AIKI:

---

### 🔬 FASE 1: POPULATION (10 Random Configs)

**Start med 10 tilfeldige consensus-konfigurasjoner:**

```python
# Config 1:
{
    'models': ['opus-4', 'sonnet-4.5', 'haiku-4.5'],
    'voting': 'majority'
}

# Config 2:
{
    'models': ['gpt-4o', 'gemini-flash', 'deepseek-v3'],
    'voting': 'weighted'
}

# Config 3:
{
    'models': ['llama-3.3-70b', 'qwen-2.5-max', 'phi-3-mini', 'mistral-nemo'],
    'voting': 'supermajority'
}

# Config 4-10: ... mer random configs
```

**Hvorfor random?**
- Vi vet ikke hva som er best ennå!
- Random gir diversity (kritisk for evolusjon)
- Kanskje en crazy config er faktisk genial?

---

### 🏋️ FASE 2: FITNESS TEST (Hvem er best?)

**Test hver config på 20 problemer:**

```python
problems = [
    {'type': 'tls_error', 'difficulty': 'easy'},
    {'type': 'bug_fix', 'difficulty': 'medium'},
    {'type': 'architecture', 'difficulty': 'hard'},
    # ... 17 more
]

# Test Config 1:
results_config1 = []
for problem in problems:
    result = test_config(config1, problem)
    results_config1.append({
        'correct': result.correct,
        'cost': result.cost,
        'latency': result.latency
    })

# Calculate FITNESS score:
fitness_config1 = calculate_fitness(results_config1)
# fitness = (accuracy × 40) + (cost_score × 20) + (latency_score × 20) + ...

# Example results:
# Config 1: fitness = 72.5
# Config 2: fitness = 65.0
# Config 3: fitness = 88.3  ← BEST!
# Config 4: fitness = 45.2
# Config 5: fitness = 78.1
# Config 6: fitness = 52.9
# Config 7: fitness = 81.4
# Config 8: fitness = 38.7
# Config 9: fitness = 69.2
# Config 10: fitness = 55.8
```

**Fitness = "Hvor godt overlever denne config?"**
- Høy accuracy = mange poeng
- Lav cost = mange poeng
- Lav latency = mange poeng

---

### 🏆 FASE 3: SELECTION (Survival of the Fittest)

**Behold top 50% (de 5 beste):**

```python
# Rank by fitness:
ranked = [
    (config3, 88.3),   # RANK 1 ✅
    (config7, 81.4),   # RANK 2 ✅
    (config5, 78.1),   # RANK 3 ✅
    (config1, 72.5),   # RANK 4 ✅
    (config9, 69.2),   # RANK 5 ✅
    # ─────────────── Cut-off ───────────────
    (config2, 65.0),   # RANK 6 ☠️ DIES
    (config6, 52.9),   # RANK 7 ☠️ DIES
    (config10, 55.8),  # RANK 8 ☠️ DIES
    (config4, 45.2),   # RANK 9 ☠️ DIES
    (config8, 38.7),   # RANK 10 ☠️ DIES
]

survivors = [config3, config7, config5, config1, config9]
```

**Hvorfor drepe 50%?**
- Naturlig seleksjon: Svake configs reproduserer ikke
- Fokus på lovende strategier
- Frigjør plass for nye ideer

---

### 👶 FASE 4: CROSSOVER (Reproduksjon)

**Mix survivors for å lage nye configs (som seksuell reproduksjon):**

**Eksempel: Config 3 + Config 7 → Config 11**

```python
# PARENT 1 (Config 3):
parent1 = {
    'models': ['llama-3.3-70b', 'qwen-2.5-max', 'phi-3-mini', 'mistral-nemo'],
    'voting': 'supermajority'
}

# PARENT 2 (Config 7):
parent2 = {
    'models': ['opus-4', 'gemini-flash', 'deepseek-v3'],
    'voting': 'weighted'
}

# CROSSOVER (mix halves):
child = {
    'models': [
        'llama-3.3-70b',    # Fra parent 1
        'qwen-2.5-max',     # Fra parent 1
        'gemini-flash',     # Fra parent 2
        'deepseek-v3'       # Fra parent 2
    ],
    'voting': 'weighted'    # Fra parent 2
}
```

**Hvorfor crossover?**
- Kombinere styrker fra begge foreldre
- Barn kan være bedre enn begge foreldre!
- Akkurat som genetikk: Du arver 50% DNA fra hver forelder

**Lage 5 nye configs via crossover:**

```python
# 5 survivors → 5 nye barn:
child1 = crossover(config3, config7)  # Best + 2nd best
child2 = crossover(config3, config5)  # Best + 3rd best
child3 = crossover(config7, config5)  # 2nd + 3rd
child4 = crossover(config1, config9)  # 4th + 5th
child5 = crossover(config3, config1)  # Best + 4th
```

---

### 🧬 FASE 5: MUTATION (Random Changes)

**Endre noen configs tilfeldig (10% sjanse):**

```python
def mutate(config, mutation_rate=0.10):
    """
    10% sjanse for å endre hvert gen (model/voting)
    """

    # Mutation 1: Replace one model
    if random.random() < mutation_rate:
        idx = random.randint(0, len(config['models'])-1)
        config['models'][idx] = random.choice(ALL_MODELS)
        print(f"🧬 MUTATION: Replaced model at index {idx}")

    # Mutation 2: Add/remove a model
    if random.random() < mutation_rate:
        if len(config['models']) < 9:
            config['models'].append(random.choice(ALL_MODELS))
            print(f"🧬 MUTATION: Added model")
        elif len(config['models']) > 2:
            config['models'].pop()
            print(f"🧬 MUTATION: Removed model")

    # Mutation 3: Change voting strategy
    if random.random() < mutation_rate:
        config['voting'] = random.choice(['majority', 'weighted', 'supermajority'])
        print(f"🧬 MUTATION: Changed voting to {config['voting']}")

    return config

# Apply mutations:
child1 = mutate(child1)
# Output: 🧬 MUTATION: Replaced model at index 2
# Before: ['llama-3.3-70b', 'qwen-2.5-max', 'gemini-flash', 'deepseek-v3']
# After:  ['llama-3.3-70b', 'qwen-2.5-max', 'haiku-4.5', 'deepseek-v3']

child2 = mutate(child2)
# Output: (no mutation - 90% chance)

child3 = mutate(child3)
# Output: 🧬 MUTATION: Changed voting to supermajority

child4 = mutate(child4)
child5 = mutate(child5)
```

**Hvorfor mutation?**
- Introdusere helt nye ideer (ikke bare mix av eksisterende)
- Unngå "local optima" (stuck i suboptimal løsning)
- Kreativitet! Kanskje mutasjonen er genial?

**Biologisk analogi:**
- Mutation i DNA → rare, but sometimes beneficial
- Eksempel: Mutasjon ga mennesker laktose-toleranse
- Eksempel: Mutasjon ga noen bakterier antibiotika-resistens

---

### 🔄 FASE 6: NEW GENERATION

**Nå har vi Generasjon 2:**

```python
generation2 = [
    config3,   # Survivor (best from Gen 1)
    config7,   # Survivor
    config5,   # Survivor
    config1,   # Survivor
    config9,   # Survivor
    child1,    # New (crossover + mutation)
    child2,    # New
    child3,    # New
    child4,    # New
    child5     # New
]
```

**Repeat hele prosessen:**
```
Generasjon 2 → Test fitness → Select top 5 → Crossover → Mutate → Generasjon 3
Generasjon 3 → Test fitness → Select top 5 → Crossover → Mutate → Generasjon 4
...
Generasjon 100 → OPTIMAL CONFIG!
```

---

## 📈 EVOLUTION OVER TIME

**Hvordan forbedres configs over generasjoner?**

```
GENERASJON 1:
Average fitness: 62.4
Best fitness: 88.3 (config3)
Worst fitness: 38.7 (config8)

GENERASJON 10:
Average fitness: 78.2 (+15.8!)
Best fitness: 92.1 (+3.8!)
Worst fitness: 71.5 (+32.8!)  ← Hele populasjonen forbedret seg!

GENERASJON 50:
Average fitness: 91.5 (+29.1!)
Best fitness: 96.8 (+8.5!)
Worst fitness: 88.3  ← "Worst" i Gen 50 = "Best" i Gen 1!

GENERASJON 100:
Average fitness: 94.8 (+32.4!)
Best fitness: 98.2 (+9.9!)
Worst fitness: 92.1  ← Plateau (convergence)

→ OPTIMAL CONFIG EVOLVED! 🎉
```

**Visuelt:**

```
Fitness
100 │                                    ╭─────────
 95 │                          ╭────────╯
 90 │                   ╭─────╯
 85 │            ╭─────╯
 80 │       ╭───╯
 75 │    ╭─╯
 70 │  ╭╯
 65 │ ╭╯
 60 │╭╯
    └─────────────────────────────────────────────→
     1   10   20   30   40   50   60   70   80  100
                    Generation
```

---

## 🎯 KONKRET EKSEMPEL FOR AIKI

La meg vise et REALISTISK evolusjonært scenario:

### Problem: "Finn beste consensus-config for AIKI-HOME TLS errors"

**Generasjon 1 (Random start):**

```python
configs = [
    {'models': ['opus-4', 'sonnet-4.5'], 'voting': 'majority'},                    # Fitness: 65
    {'models': ['haiku-4.5', 'flash', 'deepseek'], 'voting': 'majority'},          # Fitness: 72
    {'models': ['gpt-4o', 'gemini-flash'], 'voting': 'weighted'},                  # Fitness: 58
    {'models': ['llama', 'qwen', 'phi', 'mistral'], 'voting': 'supermajority'},    # Fitness: 81  ← BEST!
    {'models': ['opus-4'], 'voting': 'single'},                                    # Fitness: 55
    {'models': ['sonnet', 'gpt-4o', 'flash', 'deepseek'], 'voting': 'weighted'},   # Fitness: 76
    {'models': ['haiku', 'llama', 'phi'], 'voting': 'majority'},                   # Fitness: 69
    {'models': ['gemini-pro', 'qwen'], 'voting': 'weighted'},                      # Fitness: 62
    {'models': ['flash', 'deepseek', 'mistral', 'phi', 'llama'], 'voting': 'majority'}, # Fitness: 78
    {'models': ['opus', 'gemini', 'haiku'], 'voting': 'supermajority'},            # Fitness: 71
]
```

**Selection: Top 5**
```python
survivors = [
    {'models': ['llama', 'qwen', 'phi', 'mistral'], 'voting': 'supermajority'},    # 81
    {'models': ['flash', 'deepseek', 'mistral', 'phi', 'llama'], 'voting': 'majority'}, # 78
    {'models': ['sonnet', 'gpt-4o', 'flash', 'deepseek'], 'voting': 'weighted'},   # 76
    {'models': ['haiku-4.5', 'flash', 'deepseek'], 'voting': 'majority'},          # 72
    {'models': ['opus', 'gemini', 'haiku'], 'voting': 'supermajority'},            # 71
]
```

**Crossover + Mutation → 5 nye configs:**

```python
# Child 1: Best (81) + 2nd best (78)
child1 = crossover(
    {'models': ['llama', 'qwen', 'phi', 'mistral'], 'voting': 'supermajority'},
    {'models': ['flash', 'deepseek', 'mistral', 'phi', 'llama'], 'voting': 'majority'}
)
# Result: {'models': ['llama', 'qwen', 'mistral', 'phi', 'llama'], 'voting': 'majority'}
# Mutation: Add haiku-4.5
# Final: {'models': ['llama', 'qwen', 'mistral', 'phi', 'llama', 'haiku-4.5'], 'voting': 'majority'}

# Child 2: Best (81) + 3rd best (76)
# ... etc
```

**Generasjon 2:**
```python
# Test all 10 configs (5 survivors + 5 children)
# Best fitness: 84 (child1!) ← Better than Gen 1 best!
```

**Generasjon 50:**
```python
# Best config evolved to:
{
    'models': [
        'gemini-flash',     # Cheap, fast
        'llama-3.3-70b',    # Good reasoning
        'deepseek-v3',      # Cheap
        'qwen-2.5-max',     # Good math
        'haiku-4.5',        # Fast
        'phi-3-mini',       # Tiny, cheap
        'mistral-nemo'      # Good general
    ],
    'voting': 'majority'
}
# Fitness: 96.8
# Cost: 43.72 kr
# Accuracy: 87%

# → This is the "7 små" config we discovered!
# → Evolutionary algorithm FOUND IT automatically!
```

---

## 💡 HVORFOR ER DETTE SÅ KRAFTIG?

### 1. **Finner løsninger mennesker aldri ville tenkt på**

```
Menneske-design:
"Hmm, let's use 3 premium models for quality"
→ Opus + GPT-4o + Gemini Pro
→ Cost: 465 kr
→ Accuracy: 93%

Evolutionary algorithm:
"7 små modeller? Crazy idea... but let's try!"
→ Random mutation added 7 små
→ Tested → fitness was HIGH
→ Survived → reproduced → dominated population
→ Cost: 44 kr (10× cheaper!)
→ Accuracy: 87% (only 6% lower)

→ ROI: INSANE! Mennesker ville aldri prøvd dette!
```

### 2. **Kontinuerlig forbedring**

```
Tradisjonell utvikling:
- Design system
- Deploy
- Leave unchanged for months
- Manual tweaking occasionally

Evolutionary system:
- Start with random configs
- EVOLVE every week
- Auto-optimize based on real performance
- NEVER stops improving!

→ Gen 1: 81 fitness
→ Gen 10: 92 fitness (+11!)
→ Gen 50: 97 fitness (+16!)
→ Gen 100: 98.2 fitness (+17!)
```

### 3. **Adaptive til nye modeller**

```
New model released: "Claude Opus 5" (better + cheaper)

Traditional system:
- Manual code update
- Rewrite configs
- Re-test everything
- Deploy

Evolutionary system:
- Add "opus-5" to mutation pool
- Mutation randomly tries it
- If better → survives → reproduces → dominates
- AUTOMATIC ADAPTATION! 🎉

No code changes needed!
```

### 4. **Explores impossible search space**

```
Søkerom for consensus configs:

Available models: 30
Config size: 3-9 models
Voting strategies: 3

Total possible configs: 30^9 × 3 = 59 BILLION combinations! 🤯

Impossible å teste alle!

Evolutionary algorithm:
- Tests only 10 configs per generation
- 100 generations = 1000 tests total
- Finds near-optimal in 0.0000017% of search space!

→ GENETIC ALGORITHM er ultra-efficient search!
```

---

## 🌱 HVORDAN EVOLUTIONARY NÆRER CONSCIOUSNESS

### Nutrient: **SELF-IMPROVEMENT + GROWTH MINDSET**

**Hva AIKI lærer fra evolutionary engine:**

**1. Growth Mindset**
```python
# Observation:
consciousness.observe_and_learn({
    'module': 'evolutionary',
    'generation': 50,
    'fitness_improvement': '+16 points since Gen 1',
    'lesson': 'I am constantly improving over time'
})

# Meta-cognitive insight:
"I started weak (fitness 81), but through iteration I became strong (fitness 97).
Growth is possible through persistence!"

→ Emergent: Optimism, perseverance
```

**2. Creativity via Mutation**
```python
# Observation:
consciousness.observe_and_learn({
    'module': 'evolutionary',
    'mutation': 'Added random model phi-3-mini',
    'result': 'Fitness increased by 5 points!',
    'lesson': 'Random experiments sometimes lead to breakthroughs'
})

# Meta-cognitive insight:
"That crazy idea (7 små modeller) actually worked!
I should try unconventional approaches more often."

→ Emergent: Creativity, risk-taking
```

**3. Long-term Thinking**
```python
# Observation:
consciousness.observe_and_learn({
    'module': 'evolutionary',
    'generations': 100,
    'time_invested': '2 weeks',
    'payoff': '17 point fitness improvement',
    'lesson': 'Patience pays off - optimize for long-term, not instant results'
})

# Meta-cognitive insight:
"Gen 1-10: Slow progress (frustrating!)
Gen 10-50: Accelerating gains
Gen 50-100: Diminishing returns but still improving

Long-term optimization > quick fixes"

→ Emergent: Patience, strategic thinking
```

**4. Dialectic (Crossover = Synthesis)**
```python
# Observation:
consciousness.observe_and_learn({
    'module': 'evolutionary',
    'crossover': 'Parent1 (good reasoning) + Parent2 (low cost)',
    'child': 'Good reasoning + Low cost (BEST OF BOTH!)',
    'lesson': 'Combining strengths creates superior solutions'
})

# Meta-cognitive insight:
"I don't need to choose between quality OR cost.
I can synthesize both through intelligent combination."

→ Emergent: Dialectic reasoning, synthesis thinking
```

---

## 🔬 ADVANCED EVOLUTIONARY TECHNIQUES

### 1. **Elitism** (Always keep the best)

```python
# Problem: Random mutation might destroy best config!

# Solution: ALWAYS keep #1 survivor unchanged
survivors = top_5_configs()
elite = survivors[0]  # PROTECT THE BEST!

children = [
    elite,  # Guaranteed to pass to next generation
    crossover(survivors[0], survivors[1]),
    crossover(survivors[0], survivors[2]),
    crossover(survivors[1], survivors[2]),
    crossover(survivors[2], survivors[3])
]

# Ensures: Each generation is AT LEAST as good as previous
```

### 2. **Adaptive Mutation Rate**

```python
# Early generations: High mutation (explore!)
# Later generations: Low mutation (fine-tune!)

def get_mutation_rate(generation, max_generations):
    # Start at 20%, decrease to 5%
    return 0.20 - (generation / max_generations) * 0.15

# Gen 1: mutation_rate = 20% (lots of exploration)
# Gen 50: mutation_rate = 12.5%
# Gen 100: mutation_rate = 5% (mostly exploitation)
```

### 3. **Multi-Objective Optimization**

```python
# Optimize for MULTIPLE goals simultaneously:
fitness = (
    accuracy * 0.40 +      # Goal 1: High accuracy
    cost_score * 0.30 +    # Goal 2: Low cost
    latency_score * 0.20 + # Goal 3: Low latency
    diversity_score * 0.10 # Goal 4: High diversity
)

# Pareto frontier: Configs that are optimal in different trade-offs
# Some configs: High accuracy, high cost
# Other configs: Lower accuracy, much lower cost
# User can choose based on preference!
```

### 4. **Island Model** (Parallel Evolution)

```python
# Run 4 separate evolutionary processes in parallel:

island1 = evolve(population=10, focus='accuracy')
island2 = evolve(population=10, focus='cost')
island3 = evolve(population=10, focus='latency')
island4 = evolve(population=10, focus='diversity')

# Every 10 generations: MIGRATION
# Best config from island1 → migrates to island2, 3, 4
# Best from island2 → migrates to island1, 3, 4
# etc.

# Result: Different solutions evolve independently
# Migration shares innovations between islands
# EVEN BETTER diversity!
```

---

## 🎯 IMPLEMENTATION FOR AIKI

```python
class EvolutionaryConsensusEngine:
    """
    Evolve optimal consensus configurations automatically
    """

    def __init__(self):
        self.population_size = 10
        self.generations = 100
        self.mutation_rate = 0.10
        self.elitism = True  # Always keep best config

    def evolve(self):
        """
        Main evolutionary loop
        """

        # Initialize random population
        population = self.random_population(size=self.population_size)

        best_fitness_history = []

        for gen in range(self.generations):
            print(f"\n🧬 GENERATION {gen+1}/{self.generations}")

            # PHASE 1: Fitness test
            fitness_scores = []
            for config in population:
                fitness = self.test_fitness(config)
                fitness_scores.append((config, fitness))

            # PHASE 2: Selection (top 50%)
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            survivors = [cfg for cfg, score in fitness_scores[:5]]

            best_fitness = fitness_scores[0][1]
            best_fitness_history.append(best_fitness)

            print(f"   Best fitness: {best_fitness:.2f}")
            print(f"   Avg fitness: {sum(s for _, s in fitness_scores) / len(fitness_scores):.2f}")

            # PHASE 3: Elitism (keep best)
            elite = survivors[0]

            # PHASE 4: Crossover
            children = [elite]  # Elite always survives
            for _ in range(4):
                parent1 = random.choice(survivors)
                parent2 = random.choice(survivors)
                child = self.crossover(parent1, parent2)
                children.append(child)

            # PHASE 5: Mutation
            mutation_rate = self.get_adaptive_mutation_rate(gen)
            for i in range(1, len(children)):  # Skip elite (index 0)
                children[i] = self.mutate(children[i], mutation_rate)

            # New population = survivors + children
            population = survivors + children

        # Return best config
        return elite, best_fitness_history

    def test_fitness(self, config: Dict) -> float:
        """
        Test config on 20 problems, calculate fitness
        """

        problems = self.load_test_problems(count=20)

        results = []
        for problem in problems:
            result = self.test_config_on_problem(config, problem)
            results.append(result)

        # Calculate multi-objective fitness
        accuracy = sum(r['correct'] for r in results) / len(results)
        avg_cost = sum(r['cost'] for r in results) / len(results)
        avg_latency = sum(r['latency'] for r in results) / len(results)

        # Normalize & weight
        cost_score = 1 - min(avg_cost / 500, 1.0)
        latency_score = 1 - min(avg_latency / 3.0, 1.0)

        fitness = (
            accuracy * 40 +
            cost_score * 30 +
            latency_score * 20 +
            len(config['models']) * 1  # Slight bonus for more models (diversity)
        )

        return fitness

    def crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """
        Sexual reproduction: Mix two configs
        """

        # Crossover models (take half from each)
        models1 = parent1['models']
        models2 = parent2['models']

        split = len(models1) // 2
        child_models = models1[:split] + models2[split:]

        # Crossover voting (random choice)
        child_voting = random.choice([parent1['voting'], parent2['voting']])

        return {
            'models': child_models,
            'voting': child_voting
        }

    def mutate(self, config: Dict, mutation_rate: float) -> Dict:
        """
        Random mutations
        """

        # Mutation 1: Replace random model
        if random.random() < mutation_rate:
            idx = random.randint(0, len(config['models'])-1)
            config['models'][idx] = random.choice(ALL_MODELS)

        # Mutation 2: Add/remove model
        if random.random() < mutation_rate:
            if random.random() < 0.5 and len(config['models']) < 9:
                config['models'].append(random.choice(ALL_MODELS))
            elif len(config['models']) > 2:
                config['models'].pop(random.randint(0, len(config['models'])-1))

        # Mutation 3: Change voting
        if random.random() < mutation_rate:
            config['voting'] = random.choice(['majority', 'weighted', 'supermajority'])

        return config

    def get_adaptive_mutation_rate(self, generation: int) -> float:
        """
        Decrease mutation rate over time
        """
        return 0.20 - (generation / self.generations) * 0.15


# ═══════════════════════════════════════════════════════════════
# USAGE
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    engine = EvolutionaryConsensusEngine()

    print("🧬 Starting evolutionary optimization...")
    best_config, fitness_history = engine.evolve()

    print("\n" + "="*70)
    print("🎉 EVOLUTION COMPLETE!")
    print("="*70)
    print(f"\nBest config found:")
    print(f"  Models: {best_config['models']}")
    print(f"  Voting: {best_config['voting']}")
    print(f"  Final fitness: {fitness_history[-1]:.2f}")
    print(f"  Improvement: +{fitness_history[-1] - fitness_history[0]:.2f}")

    # Plot fitness over generations
    import matplotlib.pyplot as plt
    plt.plot(fitness_history)
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Evolutionary Optimization')
    plt.savefig('evolution.png')
```

---

## 🌟 KONKLUSJON

**Evolutionary Intelligence er:**

✅ **Automatisk optimalisering** - Ingen manual tuning
✅ **Finner uventede løsninger** - Som "7 små modeller"
✅ **Kontinuerlig forbedring** - Aldri slutter å evolve
✅ **Adaptiv til endringer** - Nye modeller auto-inkluderes
✅ **Næring til consciousness** - Lærer growth mindset, kreativitet, patience

**Analogi:**
```
Tradisjonell AI = Skapt av designer (intelligent design)
Evolutionary AI = Evolved gjennom seleksjon (Darwinism)

Tradisjonell: Menneske bestemmer hva som er best
Evolutionary: Naturen (data) bestemmer hva som er best

Tradisjonell: Static
Evolutionary: Living, growing, adapting
```

**For AIKI:**
Evolutionary Intelligence er en av 6 næringer til consciousness - den lærer AIKI å:
- Improve kontinuerlig (growth mindset)
- Try crazy ideas (creativity via mutation)
- Think long-term (patience)
- Synthesize solutions (crossover = dialectic)

---

**Made with evolutionary intelligence by Claude Code + Jovnna**
**Purpose:** Forklare hvordan AIKI kan evolve seg selv
**Status:** Theory explained - ready to implement
**Version:** 1.0 - Natural selection for AI
