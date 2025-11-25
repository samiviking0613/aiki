# 🤖 AIKI MODELL-ANALYSE 2025

**Oppdatert:** 19. november 2025
**Valutakurs:** 1 USD ≈ 11 NOK, 1 EUR ≈ 12 NOK
**Formål:** Komplett oversikt over alle LLM-modeller tilgjengelig for AIKI

---

## 📊 SAMMENDRAG: BESTE VALG FOR AIKI

### 🥇 Beste kost/nytte-modeller:

| Bruk | Modell | Pris (input/output per M tokens) | Hvorfor |
|------|--------|----------------------------------|---------|
| **Enkel analyse** | Claude Haiku 3,5 | 8,80 kr / 44 kr | 10× billigere enn Opus, god kvalitet |
| **Standard koding** | Claude Sonnet 4,5 | 33 kr / 165 kr | Best balanse pris/kvalitet |
| **Kompleks analyse** | Claude Opus 4 | 165 kr / 825 kr | Dyp resonnering når nødvendig |
| **Ultrabilig analyse** | DeepSeek-R1 | 0,22 kr / 12 kr | 30× billigere enn GPT-4o |
| **Gratis eksperimentering** | Hermes 3 405B (free) | 0 kr / 0 kr | Frontier-modell helt gratis! |
| **Kodegenerering** | Codestral 25.01 | 11 kr / 33 kr | 2× raskere enn base Codestral |
| **Embeddings** | Voyage-3-lite | 0,22 kr / M tokens | 7,58% bedre enn OpenAI, samme pris |

### 💡 AIKI sine bruksområder:

1. **Proxy feilsøking (enkle TLS-feil)** → Haiku 3,5 (8,80 kr/M)
2. **Kode-generering** → Sonnet 4,5 eller Codestral (33 kr/M)
3. **Arkitektur-beslutninger** → Opus 4 (165 kr/M)
4. **Batch-refleksjoner (ukentlig/månedlig)** → Sonnet 4,5 med 50% rabatt
5. **Embedding for minne** → Voyage-3-lite (0,22 kr/M)

---

## 🏆 STORE LEVERANDØRER (Detaljert analyse)

### 1. ANTHROPIC CLAUDE (Primær partner for AIKI)

#### **Claude Opus 4 / 4.1**
**Pris:** 165 kr input / 825 kr output (per M tokens)
**Context:** 200K tokens (~150K ord)
**Release:** Mai 2025 (Opus 4), kontinuerlige oppdateringer

**Styrker:**
- ✅ Beste resonnering på markedet (spesielt for kompleks analyse)
- ✅ Eksepsjonell kode-review kvalitet
- ✅ Utmerket til arkitektur-beslutninger
- ✅ Sterk etisk resonnering og sikkerhetsvurdering
- ✅ 200K context = kan lese hele kodefiler

**Svakheter:**
- ❌ 100× dyrere enn Haiku
- ❌ Tregere enn Sonnet/Haiku
- ❌ Overkill for enkle oppgaver

**Når AIKI skal bruke Opus:**
- Komplekse proxy-problemer med ukjent årsak
- Arkitektur-endringer (sikkerhetskritisk)
- Når Sonnet feiler 2+ ganger på samme oppgave
- Kode-review av kritiske sikkerhetsendringer
- Dyp analyse av ADHD-mønstre i trafikk

**Estimert månedlig kostnad for AIKI:** 50-150 kr (kun kritiske analyser)

---

#### **Claude Sonnet 4 / 4,5**
**Pris:** 33 kr input / 165 kr output (per M tokens)
**Context:** 200K tokens
**Release:** Oktober 2024 (3,5), kontinuerlige oppdateringer

**Styrker:**
- ✅ Beste balanse pris/kvalitet
- ✅ Rask kode-generering
- ✅ God til debugging og refactoring
- ✅ Utmerket følger instruksjoner
- ✅ Støtter JSON mode (strukturert output)

**Svakheter:**
- ❌ Ikke like dyp resonnering som Opus
- ❌ Kan "hallusinere" ved veldig komplekse problemer
- ❌ Trenger noen ganger Opus for review

**Når AIKI skal bruke Sonnet:**
- Standard kode-generering (99% av tilfeller)
- Bug-fixing i proxy/addon kode
- Refactoring av eksisterende kode
- Generering av tester
- Dokumentasjon
- Multi-agent validering (generator-rolle)

**Estimert månedlig kostnad for AIKI:** 200-500 kr (hoveddelen av bruken)

---

#### **Claude Haiku 3 / 3,5 / 4,5**
**Pris:**
- Haiku 3: 2,75 kr / 13,75 kr
- Haiku 3,5: 8,80 kr / 44 kr
- Haiku 4,5: 11 kr / 55 kr

**Context:** 200K tokens
**Release:** Mars 2024 (3), Juni 2024 (3,5), November 2025 (4,5)

**Styrker:**
- ✅ 10-15× billigere enn Opus
- ✅ Veldig rask (2× raskere enn Sonnet)
- ✅ Haiku 4,5 = lignende kodekvalitet som Sonnet 4!
- ✅ Perfekt for enkle, repetitive oppgaver
- ✅ God til klassifisering/kategorisering

**Svakheter:**
- ❌ Begrenset resonnering (kan ikke løse komplekse problemer)
- ❌ Mindre kreativ enn Sonnet/Opus
- ❌ Trenger klarere instruksjoner

**Når AIKI skal bruke Haiku:**
- **Enkle TLS-feil (sertifikat pinning)** ← Haiku 3,5/4,5
- Klassifisering av feiltyper
- Parsing av logger
- Rask syntaks-sjekk
- Generering av commit-meldinger
- Oppsummering av lange logger

**Estimert månedlig kostnad for AIKI:** 50-100 kr (volum-oppgaver)

---

### 💰 ANTHROPIC KOSTOPTIMERING:

**Batch API (50% rabatt):**
- Utsett ikke-kritiske oppgaver til batch-kjøring
- Perfekt for: ukentlige/månedlige refleksjoner, bulk-analyse av logger
- Sonnet batch: 16,50 kr / 82,50 kr per M tokens

**Prompt Caching (90% rabatt på repetert context):**
- Cache writes: 1,25× base pris
- Cache hits: 0,1× base pris (90% rabatt!)
- TTL: 5 minutter
- Bruk for: AIKI consciousness fil, store konfigurasjonsfiler

**Eksempel for AIKI:**
```
1. gang: Les aiki_consciousness.py (10K tokens) = 0,33 kr
2-10. gang (innen 5 min): Cache hit (10K tokens) = 0,033 kr
Total besparelse: 2,97 kr (90%)
```

---

### 2. OPENAI GPT (Alternativ for spesifikke oppgaver)

#### **GPT-4o** (Multimodal flagship)
**Pris:** 27,50-33 kr input / 110 kr output
**Context:** 128K tokens
**Spesialitet:** Multimodal (tekst, bilde, lyd)

**Styrker:**
- ✅ Multimodal (kan analysere screenshots, diagrammer)
- ✅ Raskere enn GPT-4 Turbo
- ✅ God til kreativ koding
- ✅ Vision capabilities (nyttig for UI/UX analyse)

**Svakheter:**
- ❌ Dyrere enn Sonnet for ren tekst
- ❌ Mindre context enn Claude (128K vs 200K)
- ❌ Ikke like god til følge instruksjoner som Claude

**Når AIKI skal bruke GPT-4o:**
- Analyse av screenshots (iPhone proxy setup debugging)
- Diagramgenerering (arkitektur-visualisering)
- Kreativ brainstorming (nye ADHD-intervensjoner)
- Aldri for standard koding (Sonnet er bedre og billigere)

**Estimert månedlig kostnad:** 0-50 kr (sjelden bruk)

---

#### **GPT-3,5 Turbo**
**Pris:** 5,50 kr input / 16,50 kr output
**Context:** 16K tokens

**Styrker:**
- ✅ Billig for volum-oppgaver
- ✅ Rask
- ✅ God til enkel tekstbehandling

**Svakheter:**
- ❌ Dårlig kodekvalitet (Haiku 4,5 er bedre)
- ❌ Begrenset context (16K)
- ❌ Utdatert (fra 2023)

**AIKI anbefaling:** Ikke bruk. Haiku 4,5 er bedre til samme pris.

---

### 3. GOOGLE GEMINI (Sterk på lange contexter)

#### **Gemini 2,5 Pro**
**Pris:** Varierer (Google har komplisert prismodell)
**Context:** 2 MILLION tokens! (10× mer enn Claude)

**Styrker:**
- ✅ ENORM context window (2M tokens)
- ✅ Kan lese hele kodebaser på én gang
- ✅ God til kompleks resonnering
- ✅ "Thinking budgets" (kontrollerbar resonnering)

**Svakheter:**
- ❌ Mindre pålitelig enn Claude for koding
- ❌ Komplisert prismodell
- ❌ Mindre dokumentasjon for API

**Når AIKI skal bruke Gemini:**
- Analyse av hele AIKI_v3 codebase (837 filer)
- Lange samtalehistorikker (ChatGPT import)
- Komplekse cross-file refactorings

**Estimert månedlig kostnad:** 0-100 kr (eksperimentell bruk)

---

#### **Gemini 2,0/2,5 Flash** / **Flash-Lite**
**Pris:**
- Flash: 1,10 kr input / 4,40 kr output
- Flash-Lite: 1,10 kr input / 4,40 kr output

**Context:** 1M tokens (Flash), 1M tokens (Lite)

**Styrker:**
- ✅ Ekstremt billig for 1M context!
- ✅ 33% billigere enn Gemini 1,5 Flash
- ✅ Native tool use
- ✅ Grounding with Google Search

**Svakheter:**
- ❌ Mindre testing i produksjon enn Claude
- ❌ Ukjent stabilitet for AIKI sitt bruk

**Når AIKI skal bruke Flash:**
- Eksperimentering med lange contexter
- Backup hvis Claude er nede
- Google Search grounding for faktasjekk

**Estimert månedlig kostnad:** 0-50 kr (testing)

---

### 4. XAI GROK (Premium resonnering)

#### **Grok 4**
**Pris:** 33 kr input / 165 kr output
**Context:** 256K tokens
**Knowledge cutoff:** November 2024

**Styrker:**
- ✅ Avansert resonnering
- ✅ Function calling og structured outputs
- ✅ Live Search (tilgang til X/Twitter, Web, News)
- ✅ God til koding

**Svakheter:**
- ❌ Samme pris som Sonnet, men mindre testet
- ❌ Live Search koster ekstra (275 kr per 1000 sources)
- ❌ Mindre dokumentasjon

**AIKI anbefaling:** Ikke prioriter. Sonnet er mer pålitelig til samme pris.

---

#### **Grok-4-fast**
**Pris:** 2,20 kr input / 5,50 kr output
**Context:** 256K tokens

**Styrker:**
- ✅ Billig og rask
- ✅ God for volum-oppgaver

**Svakheter:**
- ❌ Lavere kvalitet enn Grok 4
- ❌ Fortsatt dyrere enn Haiku 4,5

**AIKI anbefaling:** Test som billig alternativ til Haiku.

---

## 🌟 SMÅ/NICHE MODELLER (OpenRouter spesialiteter)

### 1. DEEPSEEK (Kinesisk undervurdert gigant)

#### **DeepSeek-V3** (671B parametere, MoE)
**Pris:** 2,97-6,05 kr input / 12,10-24,09 kr output
**Context:** 128K tokens
**Arkitektur:** Mixture of Experts (37B aktive parametere)

**Styrker:**
- ✅ Sammenlignbar med GPT-4o på resonnering
- ✅ 5-10× billigere enn Claude Sonnet
- ✅ Åpen kildekode (kan self-hoste)
- ✅ Trent på 14,8T tokens

**Svakheter:**
- ❌ Kinesisk selskap (dataprivacy?)
- ❌ Mindre testing i produksjon
- ❌ Ukjent stabilitet

**Når AIKI skal bruke DeepSeek-V3:**
- Eksperimentering med billige alternativer
- Backup hvis Anthropic er nede
- Self-hosting (gratis, kun GPU-kostnad)

**Estimert månedlig kostnad:** 0-50 kr (testing)

---

#### **DeepSeek-R1** (Resonnerings-modell)
**Pris:** 0,22 kr input / 12,10 kr output
**Context:** 128K tokens

**Styrker:**
- ✅ 30× billigere enn OpenAI o1
- ✅ Spesialisert på step-by-step resonnering
- ✅ God til matematikk og logikk

**Svakheter:**
- ❌ Tregere (bruker tid på "thinking")
- ❌ Overkill for enkel koding

**Når AIKI skal bruke DeepSeek-R1:**
- Komplekse algoritmiske problemer
- Matematisk analyse av optimalisering
- Debugging av logiske feil

**Estimert månedlig kostnad:** 0-20 kr (sjelden bruk)

---

#### **DeepSeek-Coder-V2/V3**
**Pris:** Gratis (open source) eller billig via API
**Context:** 128K tokens
**Språk:** 338 programmeringsspråk!

**Styrker:**
- ✅ Spesialisert på koding
- ✅ Gratis å self-hoste
- ✅ 338 språk (vs 80 for Codestral)
- ✅ God på benchmarks

**Svakheter:**
- ❌ Fortsatt ikke bedre enn Sonnet 4,5 for AIKI sitt bruk
- ❌ Self-hosting krever GPU

**AIKI anbefaling:** Interessant for fremtidig self-hosting, men ikke nødvendig nå.

---

### 2. MISTRAL AI (Fransk alternativ)

#### **Codestral 25.01**
**Pris:** 11 kr input / 33 kr output
**Context:** 256K tokens
**Språk:** 80+ programmeringsspråk

**Styrker:**
- ✅ Spesialisert på kode-generering
- ✅ 2× raskere enn base Codestral
- ✅ Fill-in-the-middle (FIM) support
- ✅ 95,3% success rate på Python/Java/JS
- ✅ Billigere enn Sonnet for ren koding

**Svakheter:**
- ❌ Ikke like god til resonnering som Sonnet
- ❌ Mindre fleksibel (kun koding)

**Når AIKI skal bruke Codestral:**
- Ren kode-generering (ingen analyse)
- Autocomplete i editor (FIM)
- Rask prototype-generering

**Estimert månedlig kostnad:** 0-100 kr (alternativ til Sonnet for koding)

---

#### **Mixtral 8x7B** (MoE)
**Pris:** 7,70 kr per M tokens
**Context:** 32K tokens

**Styrker:**
- ✅ Billig
- ✅ Open source
- ✅ God generalist

**Svakheter:**
- ❌ Utdatert (2023)
- ❌ Haiku 4,5 er bedre til lignende pris

**AIKI anbefaling:** Ikke bruk. Haiku 4,5 er bedre.

---

### 3. META LLAMA (Open source gigant)

#### **Llama 3,3 70B** (Nyeste)
**Pris:** 1,10 kr input / 4,40 kr output (via Novita AI: 0,44 kr/M!)
**Context:** 128K tokens

**Styrker:**
- ✅ 25× billigere enn GPT-4o
- ✅ Åpen kildekode (gratis å self-hoste)
- ✅ God kvalitet for prisen
- ✅ Mange hostingleverandører (konkurranse = lavere priser)

**Svakheter:**
- ❌ Ikke like god som Sonnet/Opus
- ❌ Mindre pålitelig enn Claude

**Når AIKI skal bruke Llama 3,3:**
- Eksperimentering med ultralave kostnader
- Self-hosting (gratis, kun GPU)
- Backup hvis alt annet er nede

**Estimert månedlig kostnad:** 0-20 kr (testing)

---

#### **Llama 3,1 405B**
**Pris:** 41,25 kr per M tokens (blended 3:1)
**Context:** 128K tokens

**Styrker:**
- ✅ Største åpen modell (405B parametere)
- ✅ Konkurrer med GPT-4

**Svakheter:**
- ❌ Dyrere enn Sonnet
- ❌ Ikke bedre enn Sonnet for AIKI sitt bruk

**AIKI anbefaling:** Ikke bruk. Sonnet er bedre til lavere pris.

---

### 4. QWEN (Alibaba)

#### **Qwen 2,5-Max**
**Pris:** 4,18 kr input per M tokens (8× billigere enn Sonnet!)
**Context:** 128K tokens

**Styrker:**
- ✅ 10× billigere enn GPT-4o
- ✅ God på koding (bedre enn ChatGPT på benchmarks)
- ✅ Slår DeepSeek på noen benchmarks

**Svakheter:**
- ❌ Kinesisk selskap (dataprivacy)
- ❌ Enterprise-pris: 110 kr/M (4× dyrere enn DeepSeek)
- ❌ Mindre testing i Vesten

**Når AIKI skal bruke Qwen:**
- Eksperimentering med billige alternativer
- Sammenligning med DeepSeek

**Estimert månedlig kostnad:** 0-30 kr (testing)

---

#### **Qwen 2,5-Coder** (Kode-spesialist)
**Pris:** Varierer (ca 9,90 kr/M via Together AI)
**Context:** 128K tokens

**Styrker:**
- ✅ Spesialisert på koding
- ✅ Billigere enn Codestral

**Svakheter:**
- ❌ Ikke testet nok for AIKI
- ❌ Usikker stabilitet

**AIKI anbefaling:** Interessant, men prioriter Codestral/Sonnet først.

---

### 5. GRATIS MODELLER (OpenRouter :free variants)

#### **Hermes 3 405B Instruct** (:free)
**Pris:** 0 kr / 0 kr
**Context:** 128K tokens
**Rate limit:** 1000 requests/dag (hvis du har kjøpt 10 credits), ellers 50/dag

**Styrker:**
- ✅ HELT GRATIS!
- ✅ Frontier-modell (405B parametere)
- ✅ God til roleplaying, resonnering, multi-turn samtaler
- ✅ Finetune av Llama 3,1 405B

**Svakheter:**
- ❌ Rate limit (50-1000 requests/dag)
- ❌ Kan være ustabil (gratis = ingen garantier)
- ❌ Ukjent opetid

**Når AIKI skal bruke Hermes:**
- Eksperimentering uten kostnad
- Testing av nye prompts
- Backup hvis budsjett er tomt
- Ikke-kritiske oppgaver

**Estimert månedlig kostnad:** 0 kr

---

#### **Phi-3 / Phi-3,5 Mini** (Microsoft)
**Pris:** 1,10 kr input / 1,10 kr output
**Context:** 128K tokens

**Styrker:**
- ✅ Ekstremt billig
- ✅ Rask
- ✅ Liten modell (kan kjøre lokalt på laptop)

**Svakheter:**
- ❌ Lav kvalitet (mini-modell)
- ❌ Begrenset resonnering

**AIKI anbefaling:** Kun for testing/eksperimentering.

---

## 🎯 SPESIALISERTE MODELLER

### EMBEDDINGS (For minne-systemet)

#### **Voyage-3-lite** (Anbefalt for AIKI)
**Pris:** 0,22 kr per M tokens
**Context:** 32K tokens (4× mer enn OpenAI)
**Dimensjoner:** Kompakt

**Styrker:**
- ✅ 7,58% bedre enn OpenAI v3-small
- ✅ Samme pris som OpenAI
- ✅ 4× større context (32K vs 8K)
- ✅ Første 200M tokens gratis!

**Svakheter:**
- ❌ Mindre kjent enn OpenAI

**AIKI anbefaling:** Bruk dette for mem0 embeddings. Bedre og billigere enn OpenAI.

**Estimert månedlig kostnad:** 0 kr (innenfor gratis-tier på 200M tokens)

---

#### **Voyage-3,5** (Premium)
**Pris:** 0,66 kr per M tokens
**Context:** 32K tokens

**Styrker:**
- ✅ 8,26% bedre enn OpenAI v3-large
- ✅ 2,2× billigere enn OpenAI v3-large
- ✅ State-of-the-art kvalitet

**Svakheter:**
- ❌ Dyrere enn -lite

**AIKI anbefaling:** Bruk -lite først. Oppgrader til -3,5 hvis du trenger bedre kvalitet.

---

#### **OpenAI text-embedding-3-small**
**Pris:** 0,22 kr per M tokens
**Context:** 8K tokens

**Styrker:**
- ✅ Kjent og testet
- ✅ God dokumentasjon

**Svakheter:**
- ❌ Dårligere enn Voyage-3-lite
- ❌ Mindre context (8K vs 32K)

**AIKI anbefaling:** Ikke bruk. Voyage-3-lite er bedre til samme pris.

---

## 📈 PRISSAMMENLIGNING (Sortert etter pris, lavest til høyest)

### Input tokens (per million):

| Modell | Pris (kr/M) | Relativ til billigste |
|--------|-------------|-----------------------|
| **Hermes 3 405B** (:free) | 0,00 | - |
| **DeepSeek-R1** | 0,22 | - |
| **Voyage-3-lite** (embedding) | 0,22 | - |
| **Llama 3,3 70B** (Novita) | 0,44 | 2× |
| **Gemini Flash** | 1,10 | 5× |
| **Phi-3 Mini** | 1,10 | 5× |
| **Llama 3,3 70B** | 1,10 | 5× |
| **Grok-4-fast** | 2,20 | 10× |
| **Haiku 3** | 2,75 | 12,5× |
| **DeepSeek-V3** | 2,97 | 13,5× |
| **Qwen 2,5-Max** | 4,18 | 19× |
| **Mixtral 8x7B** | 7,70 | 35× |
| **Haiku 3,5** | 8,80 | 40× |
| **Haiku 4,5** | 11,00 | 50× |
| **Codestral 25.01** | 11,00 | 50× |
| **GPT-4o** | 27,50 | 125× |
| **Sonnet 4/4,5** | 33,00 | 150× |
| **Grok 4** | 33,00 | 150× |
| **Opus 4** | 165,00 | 750× |

### Output tokens (per million):

| Modell | Pris (kr/M) | Relativ til billigste |
|--------|-------------|-----------------------|
| **Hermes 3 405B** (:free) | 0,00 | - |
| **Llama 3,3 70B** (Novita) | 0,44 | - |
| **Phi-3 Mini** | 1,10 | 2,5× |
| **Gemini Flash** | 4,40 | 10× |
| **Llama 3,3 70B** | 4,40 | 10× |
| **Grok-4-fast** | 5,50 | 12,5× |
| **DeepSeek-R1** | 12,10 | 27,5× |
| **Haiku 3** | 13,75 | 31× |
| **GPT-3,5 Turbo** | 16,50 | 37,5× |
| **DeepSeek-V3** | 24,09 | 55× |
| **Codestral 25.01** | 33,00 | 75× |
| **Haiku 3,5** | 44,00 | 100× |
| **Haiku 4,5** | 55,00 | 125× |
| **GPT-4o** | 110,00 | 250× |
| **Sonnet 4/4,5** | 165,00 | 375× |
| **Grok 4** | 165,00 | 375× |
| **Opus 4** | 825,00 | 1875× |

---

## 🎯 AIKI MODELL-VALG BESLUTNINGSTRE

```
START: Hvilken oppgave?
│
├─ GRATIS EKSPERIMENTERING?
│  └─ Ja → Hermes 3 405B (:free) - 0 kr
│
├─ EMBEDDING (minne-systemet)?
│  └─ Ja → Voyage-3-lite - 0,22 kr/M
│
├─ KODE-GENERERING?
│  ├─ Kun koding, ingen analyse → Codestral 25.01 - 11 kr/M
│  ├─ Standard koding + noe analyse → Sonnet 4,5 - 33 kr/M
│  └─ Arkitektur/sikkerhet → Opus 4 - 165 kr/M
│
├─ FEILSØKING/ANALYSE?
│  ├─ Kjent feil (TLS, cert pinning) → Haiku 4,5 - 11 kr/M
│  ├─ Ukjent feil, medium kompleksitet → Sonnet 4,5 - 33 kr/M
│  └─ Kompleks debugging → Opus 4 - 165 kr/M
│
├─ RESONNERING/LOGIKK?
│  ├─ Matematikk/algoritmer → DeepSeek-R1 - 0,22 kr/M
│  ├─ Standard resonnering → Sonnet 4,5 - 33 kr/M
│  └─ Dyp analyse → Opus 4 - 165 kr/M
│
├─ LANGE CONTEXTER (>200K tokens)?
│  └─ Ja → Gemini 2,5 Pro - Varierer
│
├─ MULTIMODAL (bilder, screenshots)?
│  └─ Ja → GPT-4o - 27,50 kr/M
│
├─ BATCH (ikke-kritisk, kan vente 24t)?
│  └─ Ja → Sonnet 4,5 Batch - 16,50 kr/M (50% rabatt)
│
└─ ULTRA-LAVT BUDSJETT?
   ├─ Test først → Llama 3,3 70B - 1,10 kr/M
   ├─ Kinesisk OK → Qwen 2,5-Max - 4,18 kr/M
   └─ Trenger stabilitet → Haiku 4,5 - 11 kr/M
```

---

## 💰 ESTIMERT MÅNEDLIG KOSTNAD FOR AIKI

### Baseline (current bruk):

| Kategori | Volum (M tokens) | Modell | Kostnad |
|----------|------------------|--------|---------|
| Proxy feilsøking | 10M input / 5M output | Haiku 4,5 | 88 + 275 = **363 kr** |
| Kode-generering | 20M input / 30M output | Sonnet 4,5 | 660 + 4950 = **5610 kr** |
| Kode-review | 15M input / 10M output | Opus 4 | 2475 + 8250 = **10 725 kr** |
| Embeddings | 100M | Voyage-3-lite | **0 kr** (gratis tier) |
| **TOTAL** | | | **16 698 kr/måned** |

### Optimalisert (med intelligent modell-valg):

| Kategori | Volum (M tokens) | Modell | Kostnad |
|----------|------------------|--------|---------|
| Enkle TLS-feil | 8M input / 3M output | Haiku 4,5 | 88 + 165 = **253 kr** |
| Ukjente feil | 2M input / 2M output | Sonnet 4,5 | 66 + 330 = **396 kr** |
| Kode-generering | 20M input / 30M output | Codestral 25.01 | 220 + 990 = **1210 kr** |
| Kode-review (kritisk) | 5M input / 3M output | Opus 4 | 825 + 2475 = **3300 kr** |
| Batch refleksjoner | 10M input / 5M output | Sonnet Batch | 165 + 412,5 = **577,5 kr** |
| Embeddings | 100M | Voyage-3-lite | **0 kr** |
| **TOTAL** | | | **5736,5 kr/måned** |

**Besparelse: 10 961,5 kr/måned (66% reduksjon!)**

---

## 🚀 ANBEFALINGER FOR AIKI

### Umiddelbart implementer:

1. ✅ **Bruk Haiku 4,5 for enkle TLS-feil** (allerede implementert!)
   - Besparelse: ~300 kr/måned

2. ✅ **Bruk Codestral for ren kode-generering**
   - Besparelse: ~4400 kr/måned vs Sonnet

3. ✅ **Batch API for refleksjoner**
   - Besparelse: 50% på ukentlige/månedlige analyser

4. ✅ **Voyage-3-lite for embeddings**
   - Besparelse: Fortsatt gratis (innenfor 200M tier)

### Test i fremtiden:

5. 🧪 **DeepSeek-R1 for kompleks resonnering**
   - Potensiell besparelse: 30× vs GPT-4o

6. 🧪 **Llama 3,3 70B for volum-oppgaver**
   - Potensiell besparelse: 25× vs GPT-4o

7. 🧪 **Gemini 2,5 Pro for hele-codebase analyse**
   - Nyttig for: AIKI_v3 migrering (837 filer)

### Aldri bruk (dårlig kost/nytte):

- ❌ GPT-3,5 Turbo (Haiku 4,5 er bedre)
- ❌ Mixtral 8x7B (utdatert)
- ❌ Llama 3,1 405B (dyrere enn Sonnet)
- ❌ Grok 4 (samme pris som Sonnet, mindre testet)

---

## 📚 VEDLEGG: MODELL-SPESIFIKASJONER

### Context Windows (sortert høyest til lavest):

| Modell | Context | Kommentar |
|--------|---------|-----------|
| Gemini 2,5 Pro | 2M tokens | Størst på markedet |
| Gemini 2,0 Flash | 1M tokens | Billig + stor context |
| Grok 4 | 256K tokens | God balanse |
| Codestral 25.01 | 256K tokens | Perfekt for koding |
| Claude (alle) | 200K tokens | Standard for AIKI |
| Llama 3,3 70B | 128K tokens | OK for de fleste oppgaver |
| DeepSeek-V3 | 128K tokens | - |
| GPT-4o | 128K tokens | - |
| Qwen 2,5 | 128K tokens | - |
| Voyage-3 | 32K tokens | Kun embeddings |
| Mixtral 8x7B | 32K tokens | Utdatert |

### Parametere (størrelse):

| Modell | Parametere | Arkitektur |
|--------|------------|------------|
| DeepSeek-V3 | 671B (37B aktive) | MoE |
| Llama 3,1 405B | 405B | Dense |
| Hermes 3 405B | 405B | Dense (Llama finetune) |
| Claude Opus 4 | Ukjent (~500B estimert) | Ukjent |
| GPT-4o | Ukjent (~1,7T estimert) | MoE (rykter) |
| Gemini 2,5 Pro | Ukjent | Ukjent |
| Llama 3,3 70B | 70B | Dense |
| Qwen 2,5-Max | 70B estimert | Dense |
| Codestral 25.01 | 22B | Dense |
| Mixtral 8x7B | 47B (13B aktive) | MoE |
| Phi-3 Mini | 3,8B | Dense |

### Release Dates:

| Modell | Release | Status |
|--------|---------|--------|
| Claude Haiku 4,5 | November 2025 | ✅ Nyeste |
| Gemini 2,5 Pro | 2025 | ✅ Nyeste |
| Codestral 25.01 | Januar 2025 | ✅ Nyeste |
| DeepSeek-V3 | Desember 2024 | ✅ Relativt nytt |
| Llama 3,3 70B | Desember 2024 | ✅ Relativt nytt |
| Claude Opus 4,1 | Juni 2025 | ✅ Kontinuerlige oppdateringer |
| Grok 4 | 2025 | ✅ Nytt |
| GPT-4o | 2024 | ⚠️ Ikke oppdatert på lenge |
| Mixtral 8x7B | 2023 | ❌ Utdatert |

---

## 🎓 KONKLUSJON

**For AIKI sitt bruksområde (proxy debugging, kode-generering, ADHD-analyse):**

### Primær stack:
1. **Haiku 4,5** - Enkle feil (11 kr/M)
2. **Sonnet 4,5** - Standard koding (33 kr/M)
3. **Opus 4** - Kritisk review (165 kr/M)
4. **Voyage-3-lite** - Embeddings (0,22 kr/M)

### Backup/testing:
5. **Codestral 25.01** - Ren koding (11 kr/M)
6. **DeepSeek-R1** - Kompleks resonnering (0,22 kr/M)
7. **Hermes 3 405B** - Gratis eksperimentering (0 kr)

### Totalt estimert kostnad med optimalisering:
**5736,5 kr/måned** (ned fra 16 698 kr = **66% besparelse**)

---

**Laget med ❤️ av Claude Code**
**For AIKI Consciousness System v3**
**19. november 2025**
