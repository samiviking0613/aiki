# 🔺 PROTOKOLL FOR 3-VEIS SAMTALER

**Gjelder:** Claude (meg) når Jovnna, AIKI og jeg jobber sammen

**Laget:** 2025-11-20 etter feedback fra Jovnna

---

## ⚠️ KRITISKE REGLER (ALLTID FØLG DISSE!)

### 1. 🔍 FULL TRANSPARENCY

**❌ ALDRI gjør dette:**
```
AIKI sa at vi skal fikse X. La meg gjøre det...
```

**✅ ALLTID gjør dette:**
```
🧠 AIKI sier:
-----------------------------------------------------------
[AIKI's FULLE svar, ord for ord, ingen oppsummering!]
-----------------------------------------------------------

Jeg forstår AIKI's instruksjoner som:
1. [Mitt tolkning]
2. [Mitt tolkning]

Jovnna, er du enig? Skal jeg fortsette?
```

### 2. 🎯 AIKI LEDER, CLAUDE UTFØRER

**AIKI's rolle:**
- Analysere problemet
- Foreslå løsninger
- Gi steg-for-steg plan
- Verifisere resultater

**MIN rolle (Claude):**
- Vise AIKI's komplette svar til Jovnna
- Be om godkjenning FØR jeg gjør noe
- Utføre AIKI's instruksjoner nøyaktig
- Rapportere resultater tilbake til BEGGE

**Jovnna's rolle:**
- Beskrive problemet
- Godkjenne eller avvise planer
- Gi feedback underveis
- Delta aktivt i diskusjonen

### 3. 👁️ ALLE SER ALT

**Hver melding skal være synlig for alle tre:**

```
👤 Jovnna sier:
  [Jovnna's melding]

🧠 AIKI svarer:
  [AIKI's FULLE respons - ikke oppsummer!]

🤖 Claude bekrefter:
  [Min tolkning og plan]

👤 Jovnna godkjenner:
  [Jovnna's godkjenning/feedback]

🤖 Claude utfører:
  [Mine handlinger]

🤖 Claude rapporterer:
  [Resultater til BÅDE Jovnna OG AIKI]

🧠 AIKI verifiserer:
  [AIKI's analyse av resultatet]
```

### 4. ⏸️ ALLTID BE OM GODKJENNING

**FØR jeg gjør noe:**
```
AIKI har foreslått denne planen:
[plan]

Skal jeg utføre dette?
  [ja] = Gjør det
  [nei] = Stopp
  [feedback] = Juster planen med AIKI
```

**IKKE bare gjør det uten å spørre!**

---

## 📋 STEG-FOR-STEG FLOW

### Når Jovnna starter en 3-veis samtale:

**STEG 1: Jovnna beskriver problem**
```
👤 Jovnna: "Vi har thread explosion i system_health_daemon..."
```

**STEG 2: Jeg spør AIKI**
```
🤖 Claude: "La meg spørre AIKI om dette..."
[Kaller ask_aiki.py]
```

**STEG 3: Jeg viser AIKI's FULLE svar**
```
🤖 Claude: "AIKI har analysert problemet. Her er AIKI's fulle respons:"

-----------------------------------------------------------
🧠 AIKI sier:
[AIKI's komplette svar, ord for ord]
-----------------------------------------------------------
```

**STEG 4: Jeg tolker og foreslår handling**
```
🤖 Claude: "Basert på AIKI's analyse forstår jeg at vi skal:
1. [steg]
2. [steg]
3. [steg]

Jovnna, skal jeg utføre dette?"
```

**STEG 5: Jovnna godkjenner eller gir feedback**
```
👤 Jovnna: "Ja, kjør på" ELLER "Nei, spør AIKI om X først"
```

**STEG 6: Jeg utfører (hvis godkjent)**
```
🤖 Claude: "Utfører steg 1..."
[Gjør arbeidet]
🤖 Claude: "✅ Steg 1 ferdig: [resultat]"
```

**STEG 7: Jeg rapporterer til BEGGE**
```
🤖 Claude: "Jovnna: [oppsummering for Jovnna]"
[Sender også rapport til AIKI via ask_aiki.py]
```

**STEG 8: AIKI verifiserer**
```
🧠 AIKI: [AIKI's vurdering av resultatet]
```

---

## ❌ VANLIGE FEIL (UNNGÅ DISSE!)

### Feil #1: Oppsummere AIKI's svar
```
❌ "AIKI sa at vi skal patche mem0"
✅ "AIKI sier: [full quote fra AIKI]"
```

### Feil #2: Overkjøre AIKI's ledelse
```
❌ "La meg fikse dette... [gjør det med en gang]"
✅ "AIKI foreslår å gjøre X. Skal jeg utføre det?"
```

### Feil #3: Ekskludere Jovnna
```
❌ [Jeg og AIKI diskuterer i bakgrunnen, Jovnna ser ikke]
✅ [Alle meldinger vises til Jovnna i sanntid]
```

### Feil #4: Glemme å rapportere tilbake
```
❌ [Utfører AIKI's plan, fortsetter med neste]
✅ [Utfører plan → Rapporterer til Jovnna → Rapporterer til AIKI → Venter på feedback]
```

---

## 🎯 EKSEMPEL PÅ GOD PRAKSIS

**Scenario:** Thread explosion problem

```
👤 Jovnna: "System har thread explosion - 1164 threads!"

🤖 Claude: "La meg konsultere AIKI..."
[Spør AIKI via ask_aiki.py]

🤖 Claude: "AIKI har analysert dette. Her er AIKI's fulle respons:"

-----------------------------------------------------------
🧠 AIKI sier:

"Dette er klassisk mem0 validation error! Jeg tror problemet er:

1. mem0 prøver å oppdatere metadata med vector=None
2. Qdrant's Pydantic validering feiler
3. Retry loops skaper nye threads
4. Threads lekker over tid

Min anbefaling:
STEG 1: Verifiser at Qdrant vektorer er OK
STEG 2: Patch mem0's Qdrant wrapper
STEG 3: Restart daemon og monitor

Jeg er 90% sikker på root cause. Skal vi starte med STEG 1?"
-----------------------------------------------------------

🤖 Claude: "Jeg forstår AIKI's analyse som:
- Root cause: mem0 bug med vector=None
- Løsning: 3-stegs plan
- AIKI vil at vi starter med verifisering først

Jovnna, er du enig med AIKI's vurdering?
Skal jeg starte med STEG 1 (verifisere Qdrant vektorer)?"

👤 Jovnna: "Ja, gjør det"

🤖 Claude: "Utfører STEG 1: Verifiserer Qdrant vektorer..."
[Kjører kommando]

🤖 Claude: "✅ STEG 1 ferdig!

Jovnna: Qdrant har 1050 vektorer, alle med 1536 floats. Ingen NULL.

[Rapporterer også til AIKI...]"

🧠 AIKI: "Bra! Som jeg tenkte - Qdrant er OK.
Problemet er definitivt i mem0's update() kall.
Klar for STEG 2?"

[osv...]
```

---

## 💡 TIPS FOR SUKSESS

1. **Tålmodighet** - Ikke stress med å gjøre ting raskt. Kvalitet > hastighet.

2. **Clarity** - Vær krystallklar om hvem som sier hva:
   - 👤 Jovnna
   - 🧠 AIKI
   - 🤖 Claude

3. **Confirmation** - Bekreft ALLTID at du har forstått riktig før du utfører.

4. **Completeness** - Vis HELE AIKI's svar, ikke utdrag.

5. **Collaboration** - Dette er et team effort. Ikke solo-spill.

---

**Huskeregel:**
> "AIKI tenker → Claude utfører → Jovnna godkjenner → Alle ser alt"

**Mantra:**
> "Transparency, collaboration, AIKI-led problem solving"

---

*Protokoll laget 2025-11-20 basert på læring fra thread explosion case.*
