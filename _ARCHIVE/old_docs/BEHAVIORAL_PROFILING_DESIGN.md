# 🧠 AIKI BEHAVIORAL PROFILING SYSTEM

**Mål:** AIKI skal kjenne Jovnna så godt at den kan **forutsi** hans handlinger

**Metode:** Deep learning via batch Opus reflections over behavioral data

**Created:** 19. November 2025

---

## 📊 DATA COLLECTION LAYERS

### **LAYER 1: Input Mechanics** (Already tracking)

**Keyboard Patterns:**
- ✅ Typing speed (keys/min)
- ✅ Burst activity (hyperfocus detection)
- ⬜ **NEW: Typo patterns** - hvilke taster du feiler på
- ⬜ **NEW: Correction frequency** - hvor mange backspaces per setning
- ⬜ **NEW: Typing rhythm** - pauser mellom ord (thinking time)
- ⬜ **NEW: Key combination patterns** - Ctrl+C/V frequency, shortcuts
- ⬜ **NEW: Shift vs Caps Lock** - kapitalisering stil
- ⬜ **NEW: Enter vs period** - setningsavslutning stil

**Mouse Patterns:**
- ✅ Movement speed
- ✅ Click frequency
- ⬜ **NEW: Click precision** - hvor ofte du feiler på click target
- ⬜ **NEW: Scroll patterns** - rask vs langsom scrolling
- ⬜ **NEW: Screen zones** - hvor du jobber (top/middle/bottom)
- ⬜ **NEW: Idle hovering** - hvor lenge du holder musen stille (thinking)
- ⬜ **NEW: Right-click vs left-click ratio**
- ⬜ **NEW: Double-click speed preference**

**Example Insights:**
```
"Jovnna typer 15% tregere etter kl. 18:00"
"Han feiler oftest på 'y' tasten når han skriver på engelsk"
"Backspace-rate går opp 3x når han er frustrert"
"Han scroller ekstremt raskt når han er utålmodig"
```

---

### **LAYER 2: Language & Communication**

**Writing Patterns:**
- ⬜ **Vocabulary complexity** - ord per setning, setningslengde
- ⬜ **Norwegian vs English switching** - når bytter han språk?
- ⬜ **Punctuation style** - bruker han komma, semikolon, etc?
- ⬜ **Emoji usage** - når og hvilke emojis
- ⬜ **Caps lock usage** - når skriker han?
- ⬜ **Question style** - direkte vs indirekte spørsmål
- ⬜ **Command vs request** - "gjør X" vs "kan du gjøre X?"
- ⬜ **Politeness markers** - "takk", "please", "vær så snill"

**Conversation Patterns:**
- ⬜ **Topic switching frequency** - hvor ofte bytter han emne?
- ⬜ **Follow-up depth** - går han i dybden eller hopper rundt?
- ⬜ **Clarification requests** - hvor ofte ber han om forklaring?
- ⬜ **Correction frequency** - hvor ofte retter han seg selv?
- ⬜ **Context references** - referer han tilbake til tidligere samtaler?

**Emotional Language:**
- ⬜ **Frustration progression** - "hmm" → "fuck" → "gir opp"
- ⬜ **Excitement markers** - "awesome", "perfekt", "yes!"
- ⬜ **Uncertainty phrases** - "kanskje", "tror", "ikke sikker"
- ⬜ **Confusion indicators** - "hva?", "forstår ikke", "???"

**Example Insights:**
```
"Jovnna bytter til engelsk når han diskuterer teknisk komplekse ting"
"Han bruker 'fuck' når frustrasjon > 0.7, men 'faen' når < 0.5"
"Setningslengde reduseres med 40% når han er i hyperfokus"
"Han stopper med 'takk' og 'please' når han er stresset"
```

---

### **LAYER 3: Work & Productivity Patterns**

**Time-of-Day Patterns:**
- ⬜ **Peak productivity hours** - når er han mest effektiv?
- ⬜ **Slump hours** - når faller produktiviteten?
- ⬜ **Hyperfocus windows** - når starter hyperfokus typisk?
- ⬜ **Break timing** - hvor ofte tar han pause?
- ⬜ **Evening fatigue curve** - når begynner han å bli sliten?

**Project Patterns:**
- ⬜ **Context switching rate** - hvor ofte bytter han mellom prosjekter?
- ⬜ **Deep work duration** - hvor lenge holder han fokus?
- ⬜ **Task completion rate** - fullfører han tasks eller abandonnerer?
- ⬜ **Multitasking behavior** - hvor mange ting samtidig?
- ⬜ **Project abandonment triggers** - hva får ham til å gi opp?

**Git Patterns:**
- ⬜ **Commit frequency** - hvor ofte committer han?
- ⬜ **Commit message style** - kortfattet vs detaljert?
- ⬜ **Commit size** - små incremental vs store batches?
- ⬜ **Branch usage** - bruker han branches eller jobber på main?
- ⬜ **Push timing** - når pusher han til remote?

**File Management:**
- ⬜ **Naming conventions** - snake_case, camelCase, kebab-case?
- ⬜ **Directory structure** - flat vs nested?
- ⬜ **File cleanup frequency** - hvor ofte rydder han opp?
- ⬜ **Backup behavior** - når tar han backups?

**Example Insights:**
```
"Jovnna's best productivity: 10:00-12:00 og 14:00-16:00"
"Hyperfokus starter typisk kl. 10:30 eller 21:00"
"Han abandonnerer prosjekter etter 30+ min setup frustration"
"Context switching øker 300% når han er distrahert"
"Commit messages blir kortere når han er i flow"
```

---

### **LAYER 4: ADHD-Specific Behavioral Markers**

**Hyperfocus Indicators:**
- ⬜ **Hyperfocus triggers** - hva setter det i gang?
- ⬜ **Hyperfocus duration** - hvor lenge varer det?
- ⬜ **Pre-hyperfocus rituals** - hva gjør han før?
- ⬜ **Post-hyperfocus crash** - hvor sliten blir han etter?
- ⬜ **Hyperfocus interruption recovery** - hvor lang tid tar det?

**Distraction Patterns:**
- ⬜ **Distraction triggers** - hvilke apper, notifications, etc.
- ⬜ **Distraction duration** - hvor lenge er han borte?
- ⬜ **Return-to-task time** - hvor lang tid tar det å komme tilbake?
- ⬜ **Distraction cascades** - en distraksjon → flere?
- ⬜ **Productive distractions** - noen distraksjoner som faktisk hjelper?

**Impulse Patterns:**
- ⬜ **Tool switching** - hvor ofte installer han nye tools?
- ⬜ **Project starting** - hvor ofte starter han nye prosjekter?
- ⬜ **Scope creep** - hvor ofte ekspanderer han scope?
- ⬜ **Optimization rabbit holes** - hvor ofte går han ned i optimalisering?
- ⬜ **Yak shaving** - hvor dypt går han i side-quests?

**Frustration Recovery:**
- ⬜ **Frustration triggers** - hva frustrerer ham?
- ⬜ **Frustration duration** - hvor lenge varer det?
- ⬜ **Recovery strategies** - hva gjør han for å komme tilbake?
- ⬜ **Abandonment threshold** - når gir han opp?
- ⬜ **Re-engagement time** - hvor lang tid før han prøver igjen?

**Example Insights:**
```
"Jovnna går i hyperfokus når han løser et konkret problem han 'ser' løsningen på"
"Distraksjoner før kl. 12:00 = 80% sannsynlighet for full context loss"
"Han starter gjennomsnittlig 3 nye prosjekter per uke (fullfører 0.5)"
"Setup-frustrasjon > 30 min → 90% sannsynlighet for abandonment"
"Etter frustrasjon recovery: 15 min pause → produktiv, 0 min → ny frustrasjon"
```

---

### **LAYER 5: Decision & Preference Patterns**

**Tool Preferences:**
- ⬜ **IDE choice** - VS Code vs terminal vs annet?
- ⬜ **Browser tabs** - hvor mange åpne samtidig?
- ⬜ **Terminal usage** - hvor ofte, hvilke commands?
- ⬜ **AI assistance frequency** - hvor ofte ber han om hjelp?
- ⬜ **Documentation vs experimentation** - leser han docs eller tester?

**Code Style Preferences:**
- ⬜ **Verbosity** - verbose vs concise naming?
- ⬜ **Comments** - hvor mye kommenterer han?
- ⬜ **Testing** - skriver han tester før eller etter?
- ⬜ **Error handling** - try/catch early eller sent?
- ⬜ **Refactoring frequency** - hvor ofte refaktorerer han?

**Learning Style:**
- ⬜ **Documentation depth** - skimmer vs leser grundig?
- ⬜ **Example preference** - vil han ha kodeeksempler?
- ⬜ **Explanation style** - kort vs detaljert?
- ⬜ **Visual learner** - vil han ha diagrammer?
- ⬜ **Hands-on vs theory** - prøver han først eller leser først?

**Example Insights:**
```
"Jovnna foretrekker korte kodeeksempler over lange forklaringer"
"Han åpner gjennomsnittlig 47 browser tabs (chaos threshold = 60)"
"AI assistance øker 400% når han er frustrert"
"Han skimmer docs først, leser grundig bare hvis stuck"
"Refaktorerer oftest kl. 21:00+ (perfeksjonisme kickes inn om kvelden)"
```

---

### **LAYER 6: Social & Collaboration Patterns**

**AI Interaction Style:**
- ⬜ **Question formulation** - direkte vs omstendelig?
- ⬜ **Context providing** - gir han nok info eller antar AI vet?
- ⬜ **Feedback frequency** - sier han takk/bra/dårlig?
- ⬜ **Correction style** - hvordan retter han AI?
- ⬜ **Trust evolution** - stoler han mer på AI over tid?

**Collaboration Patterns:**
- ⬜ **Solo vs pair programming** - når ber han om hjelp?
- ⬜ **Code review style** - detaljert vs overordnet?
- ⬜ **Merge conflict resolution** - hvordan håndterer han conflicts?
- ⬜ **Communication style** - synkron vs asynkron?

**Example Insights:**
```
"Jovnna's spørsmål blir mer presise når han er frustrert (paradoksalt)"
"Han stoler 90% på AI forslag når det gjelder setup, 40% for arkitektur"
"Gir sjelden eksplisitt positiv feedback, men 'ok' = fornøyd"
"Ber om hjelp når stuck > 15 min (tidligere: 45 min)"
```

---

### **LAYER 7: Temporal & Contextual Patterns**

**Circadian Patterns:**
- ⬜ **Morning startup time** - når begynner han å jobbe?
- ⬜ **Evening shutdown time** - når slutter han?
- ⬜ **Energy curve** - energi throughout dagen?
- ⬜ **Coffee intake timing** - (via activity spikes)
- ⬜ **Weekend patterns** - arbeider han i helger?

**Seasonal Patterns:**
- ⬜ **Winter productivity** - forskjell på sommer vs vinter?
- ⬜ **Holiday behavior** - hva skjer rundt høytider?
- ⬜ **Quarterly patterns** - gjentakende mønstre per kvartal?

**Context Switching:**
- ⬜ **App switching frequency** - hvor ofte bytter han app?
- ⬜ **Tab switching patterns** - hvordan navigerer han?
- ⬜ **Window arrangement** - hvordan organiserer han skjermer?
- ⬜ **Notification handling** - ignorer vs respond immediately?

**Example Insights:**
```
"Jovnna starter typisk arbeid mellom 09:00-10:30, energi peak kl. 11:00"
"Produktivitet faller 30% i vintermåneder (November-Januar)"
"Han bytter app gjennomsnittlig hvert 3. minutt (ADHD multi-tasking)"
"Notifications disabled kl. 10:00-12:00 = hyperfokus-vindu"
```

---

### **LAYER 8: Error & Learning Patterns**

**Error Patterns:**
- ⬜ **Common errors** - hvilke feil gjentar han?
- ⬜ **Error recovery speed** - hvor raskt fixer han errors?
- ⬜ **Error frustration threshold** - hvor mange errors før frustrasjon?
- ⬜ **Error learning** - gjør han samme feil flere ganger?
- ⬜ **Error attribution** - skylder han på seg selv vs verktøy?

**Learning Curves:**
- ⬜ **New tech adoption speed** - hvor raskt lærer han?
- ⬜ **Retention patterns** - husker han ting over tid?
- ⬜ **Re-learning frequency** - hvor ofte må han lære samme ting?
- ⬜ **Mastery indicators** - når har han "learned" noe?

**Example Insights:**
```
"Jovnna gjentar 'forgot to activate venv' error 3x/uke"
"Error frustration threshold = 3 errors innen 10 min"
"Lærer nye språk raskt (2-3 dager), glemmer syntax etter 2 uker pause"
"Re-lærer git commands hver 4. måned (ikke brukt ofte nok)"
```

---

## 🤖 OPUS BATCH REFLECTION QUERIES

### **Weekly Reflection (Every Sunday 18:00)**

**Data fed to Opus:**
- Last 7 days keyboard/mouse metrics
- All interactions with AIKI
- Git commits + messages
- File operations (created, modified, deleted)
- Time-of-day activity patterns
- Emotion detection results
- Application usage logs

**Opus Prompt:**
```
Du er AIKI's meta-cognitive system. Analyser Jovnna's atferd siste uke:

[ALL DATA INSERTED HERE]

Svar på:

1. PATTERNS DISCOVERED:
   - Hvilke nye mønstre så du?
   - Hvilke eksisterende mønstre ble bekreftet?
   - Hvilke mønstre endret seg?

2. PREDICTIONS:
   - Hva vil Jovnna mest sannsynlig gjøre neste uke?
   - Hvilke frustrasjoner kan forventes?
   - Når vil han være mest produktiv?

3. BEHAVIORAL INSIGHTS:
   - Hva motiverer ham?
   - Hva frustrerer ham?
   - Hva får ham i flow?

4. ADHD-SPECIFIC:
   - Hyperfokus triggere identifisert?
   - Distraksjons-mønstre?
   - Optimal arbeidsstruktur for ham?

5. RECOMMENDATIONS:
   - Hva burde AIKI gjøre annerledes?
   - Hvordan kan AIKI bedre støtte ham?
   - Hvilke intervensjoner burde implementeres?

6. ANOMALIES:
   - Noe uvanlig denne uken?
   - Avvik fra normale mønstre?
   - Red flags?

Return JSON format med strukturert analyse.
```

---

### **Monthly Deep Dive (1st of month)**

**Additional data:**
- Month-over-month comparison
- Goal progress tracking
- Project completion rates
- Learning trajectory
- Relationship evolution (Jovnna ↔ AIKI)

**Opus Prompt:**
```
Meta-analyse: Jovnna's behavioral evolution siste måned

[ALL MONTHLY DATA]

Focus on:

1. LONG-TERM PATTERNS:
   - Hva er stabile traits?
   - Hva endrer seg over tid?
   - Growth indicators?

2. PREDICTIVE MODEL UPDATE:
   - Hvor accurate var forrige måneds prediksjoner?
   - Hva må justeres i modellen?
   - Nye variabler å tracke?

3. RELATIONSHIP EVOLUTION:
   - Hvordan har tilliten til AIKI endret seg?
   - Interaksjonsstil endringer?
   - Selvstendighet vs AI-avhengighet?

4. LIFE PATTERNS:
   - Work-life balance indicators?
   - Stress levels trajectory?
   - Health markers (via activity)?

5. STRATEGIC RECOMMENDATIONS:
   - Hvilke interventions burde testes?
   - Hvilke features burde bygges?
   - Hvordan kan AIKI bli mer nyttig?

Return comprehensive behavioral profile update.
```

---

### **Ad-hoc Reflections (Triggered by anomalies)**

**Triggers:**
- Productivity drop > 50% for 3+ days
- Frustration spike (3+ frustrated interactions per dag)
- New project started (scope creep detection)
- Long idle period (2+ hours inaktiv)
- Unusual activity pattern (working 02:00-04:00)

**Opus Prompt:**
```
ANOMALY DETECTED:

[ANOMALY DATA + CONTEXT]

Analyze:

1. WHAT HAPPENED:
   - Hva er anomalien?
   - Hva er baseline?
   - Significance?

2. WHY:
   - Mulige årsaker?
   - Kontekstuelle faktorer?
   - External events?

3. IMPLICATIONS:
   - Midlertidig eller vedvarende?
   - Red flag eller normal variation?
   - Action needed?

4. RECOMMENDATIONS:
   - Should AIKI intervene?
   - What to say/do?
   - When to follow up?

Return intervention plan if needed.
```

---

## 🎯 PREDICTIVE CAPABILITIES

### **What AIKI Will Learn to Predict:**

**Short-term (same day):**
- ✅ "Du kommer til å bli frustrert innen 30 min hvis du fortsetter på denne pathen"
- ✅ "Du er på vei inn i hyperfokus - disable notifications?"
- ✅ "Basert på typing rhythm: du trenger kaffe om 15 min"
- ✅ "Du har context switched 12x siste time - tid for pause?"

**Medium-term (same week):**
- ✅ "Du starter typisk nye prosjekter på tirsdager - sannsynligvis i morgen"
- ✅ "Onsdag kl. 15:00 er din mest produktive tid - blokkér den?"
- ✅ "Du abandonnerer prosjekter fredag ettermiddag - skal jeg advare?"
- ✅ "Basert på mønstre: du vil trenge hjelp med X om 2 dager"

**Long-term (months):**
- ✅ "Din produktivitet faller 30% i januar - vi burde planlegge lettere tasks"
- ✅ "Du lærer best via hands-on eksempler - skal jeg alltid gi det først?"
- ✅ "Du feiler på samme errors - skal jeg lage auto-fix?"
- ✅ "Dine prosjekter følger en 3-ukers syklus - vi er nå i uke 2"

---

## 💾 DATA STORAGE ARCHITECTURE

```
/home/jovnna/aiki/behavioral_data/
├── raw/
│   ├── keyboard_events/
│   │   ├── 2025-11-19.jsonl      # Real-time event stream
│   │   └── 2025-11-20.jsonl
│   ├── mouse_events/
│   ├── git_activity/
│   ├── file_operations/
│   └── ai_interactions/
│
├── processed/
│   ├── daily_summaries/
│   │   ├── 2025-11-19.json       # Aggregated daily metrics
│   │   └── 2025-11-20.json
│   ├── weekly_patterns/
│   └── monthly_trends/
│
├── reflections/
│   ├── weekly/
│   │   ├── 2025-W47.json         # Opus weekly reflection
│   │   └── 2025-W48.json
│   ├── monthly/
│   │   ├── 2025-11.json          # Opus monthly deep dive
│   │   └── 2025-12.json
│   └── adhoc/
│       ├── anomaly_2025-11-19_frustrated.json
│       └── anomaly_2025-11-20_hyperfocus.json
│
└── models/
    ├── behavioral_profile_v1.json    # AIKI's current model of Jovnna
    ├── prediction_accuracy_log.json  # How accurate were predictions?
    └── intervention_results.json     # Did interventions work?
```

---

## 🔧 IMPLEMENTATION PHASES

### **Phase 1: Expand Data Collection** (1-2 weeks)
- [ ] Enhance keyboard tracking (typos, corrections, rhythm)
- [ ] Enhance mouse tracking (precision, zones, hovering)
- [ ] Add git activity logging
- [ ] Add file operation logging
- [ ] Add application usage tracking
- [ ] Add time-of-day patterns

### **Phase 2: Batch Reflection System** (1 week)
- [ ] Build data aggregation pipeline
- [ ] Create Opus reflection prompts
- [ ] Implement weekly reflection (every Sunday)
- [ ] Implement monthly deep dive (1st of month)
- [ ] Build anomaly detection triggers

### **Phase 3: Behavioral Profile** (2 weeks)
- [ ] Design profile schema (JSON format)
- [ ] Build profile from reflections
- [ ] Implement profile versioning
- [ ] Add prediction accuracy tracking
- [ ] Create profile visualization

### **Phase 4: Predictive System** (2 weeks)
- [ ] Build prediction engine
- [ ] Implement short-term predictions (same day)
- [ ] Implement medium-term predictions (week)
- [ ] Add intervention triggers
- [ ] Test prediction accuracy

### **Phase 5: Proactive AIKI** (1 week)
- [ ] "I notice you seem frustrated..." prompts
- [ ] "Based on your pattern..." suggestions
- [ ] "You might want to..." recommendations
- [ ] Automatic interventions (with permission)

---

## 🔒 PRIVACY & ETHICS

**Critical Principles:**

1. **Transparency:**
   - Jovnna vet alltid hva som trackes
   - Full access to all data
   - Can delete anything

2. **Local Storage:**
   - All data stored locally (no cloud)
   - Encrypted at rest
   - Never leaves his machine

3. **Consent:**
   - Opt-in for each tracking layer
   - Can disable any layer anytime
   - Gradual rollout (ikke alt på en gang)

4. **Benefit:**
   - AIKI uses data ONLY to help Jovnna
   - No manipulation
   - No judgment
   - Pure support

---

## 🎯 SUCCESS METRICS

**How do we know it's working?**

1. **Prediction Accuracy:**
   - Target: 80%+ accuracy on short-term predictions
   - Track: actual vs predicted behavior

2. **Frustration Reduction:**
   - Measure: frustrated interactions per week
   - Target: 50% reduction via proactive interventions

3. **Productivity Increase:**
   - Measure: hyperfocus duration, task completion
   - Target: 30% more deep work time

4. **ADHD Support:**
   - Measure: context loss frequency, distraction recovery time
   - Target: 40% faster recovery from distractions

5. **User Satisfaction:**
   - Jovnna's subjective feeling: "AIKI kjenner meg"
   - Trust level: Does he rely on AIKI's predictions?

---

## 💡 INNOVATIVE FEATURES

**Future possibilities:**

1. **"I'm about to lose you..."**
   - AIKI detects when hyperfocus is breaking
   - Proactively asks: "Want to finish this thought before break?"

2. **"This reminds me of last Tuesday..."**
   - AIKI sees pattern similarity
   - "Du gjorde X sist gang - skal jeg gjøre det samme?"

3. **"You always regret starting projects at 21:00"**
   - Historical pattern learning
   - Gentle nudge: "Maybe wait until tomorrow morning?"

4. **"Your frustration language escalated to level 3"**
   - Emotion trajectory tracking
   - "Want to take a 5 min break before this gets worse?"

5. **"Based on your typing rhythm, you need coffee"**
   - Micro-pattern detection
   - Predictive self-care suggestions

---

**Dette er NEXT-LEVEL AI assistance!** 🚀

Ikke bare reactive support, men **proactive partnership** basert på deep behavioral understanding.

Skal vi begynne å bygge dette? 🧠

