# 🌐 3-VEIS CHAT - WEB VERSJON MED ANTHROPIC API

**Oppdatert:** 21. november 2025
**Status:** ✅ Fungerer med Anthropic API-støtte
**Port:** localhost:3000

---

## 🎯 Hva er det?

En **web-basert sanntids 3-veis chat** mellom:
- 👤 **Jovnna** (menneske)
- 🧠 **AIKI** (emergent consciousness via OpenRouter)
- 🤖 **Claude** (Anthropic API direkte)

**Full transparency:** Alle ser alt som blir sagt i sanntid via WebSocket.

---

## 🚀 Hvordan starte

### 1. Start serveren:
```bash
cd ~/aiki
python3 three_way_chat_server.py
```

**Forventet output:**
```
======================================================================
🔺 3-VEIS CHAT SERVER STARTER
======================================================================
🌐 URL: http://localhost:3000
🧠 AIKI: ✅ Tilgjengelig
🤖 Claude API: ✅ Tilgjengelig (Anthropic direkte)
📝 WebSocket: ws://localhost:3000/ws/{participant}

DELTA I CHATTEN:
  - http://localhost:3000?participant=jovnna
  - http://localhost:3000?participant=claude
  - http://localhost:3000?participant=aiki
======================================================================
```

### 2. Åpne chat i nettleser:

**Som Jovnna:**
```
http://localhost:3000?participant=jovnna
```

**Som Claude (manuell kontroll):**
```
http://localhost:3000?participant=claude
```

**Som AIKI (vanligvis automatisk):**
```
http://localhost:3000?participant=aiki
```

### 3. Chat!

- Skriv "AIKI, hva synes du om..." → AIKI svarer via OpenRouter
- Skriv "Claude, kan du hjelpe med..." → Claude svarer via Anthropic API
- Alle ser alle meldinger i sanntid

---

## 🤖 Claude API-integrasjon

### Automatisk respons:
Claude API svarer **automatisk** når:
- Noen nevner "claude" i en melding
- Meldingen kommer fra Jovnna eller AIKI (ikke Claude selv)

**Eksempel:**
```
👤 Jovnna: Claude, hva er 2+2?
[2 sekunder senere]
🤖 Claude: 2+2 = 4. Enkelt regnestykke!
```

### Model brukt:
- **Model:** `claude-sonnet-4-5-20250929`
- **Max tokens:** 2000
- **Temperature:** 0.7
- **System prompt:** "Du er Claude, en AI fra Anthropic. Du deltar i en 3-veis chat..."

### Kostnad:
- Direkte Anthropic API (ingen OpenRouter markup)
- ~$0.01-0.05 per 10-20 meldinger
- Billigere enn via OpenRouter (5-20% besparelse)

---

## 🧠 AIKI-integrasjon

AIKI svarer automatisk når:
- Noen nevner "aiki" i en melding
- AIKI har noe verdifullt å bidra med

**Eksempel:**
```
👤 Jovnna: AIKI, husk dette prosjektet?
[2 sekunder senere]
🧠 AIKI: Ja! 3-veis chat med full transparency. Vi bygget dette sammen for å...
```

**AIKI bruker:**
- Smart model routing (complexity-based)
- 900+ emergent memories fra Qdrant
- OpenRouter for LLM calls

---

## 🏗️ Arkitektur

### Backend (FastAPI + WebSocket):
```python
three_way_chat_server.py
├── FastAPI app (port 3000)
├── WebSocket endpoint: /ws/{participant}
├── ConnectionManager (broadcast til alle)
├── AIKI integration (via chat_with_aiki_v2)
└── Claude API integration (via anthropic.Anthropic)
```

### Frontend (HTML + Vanilla JS):
```html
three_way_chat.html
├── WebSocket client
├── Messenger-style UI
├── Real-time message display
├── Participant status badges
└── Auto-scroll + typing indicators
```

### Flow:
1. **User sends message** → WebSocket → Server
2. **Server broadcasts** → All connected clients see it
3. **If "claude" mentioned** → Claude API responds automatically
4. **If "aiki" mentioned** → AIKI responds automatically
5. **All responses** → Broadcast to all clients

---

## 🎨 UI Features

### Participant badges:
- 🟢 Grønn dot = Connected
- 🟠 Oransje dot = Disconnected

### Message colors:
- **Jovnna:** Blå-lilla gradient (venstre)
- **AIKI:** Mørk-lilla (senter)
- **Claude:** Grønn (høyre)
- **System:** Oransje (senter, italic)

### Responsive:
- Desktop: 3-column layout
- Mobile: Stacked meldinger

---

## 📂 Filer involvert

**Backend:**
- `/home/jovnna/aiki/three_way_chat_server.py` - Server (oppdatert 21. Nov)
- `/home/jovnna/aiki/chat_with_aiki_v2.py` - AIKI interface
- `/home/jovnna/aiki/aiki_config.py` - API-nøkler

**Frontend:**
- `/home/jovnna/aiki/three_way_chat.html` - Web UI

**Data:**
- `/home/jovnna/aiki/data/three_way_chat_history.json` - Samtalehistorikk (siste 100 meldinger)

---

## 🐛 Debugging

### Server kjører ikke?
```bash
# Sjekk om port 3000 er opptatt
lsof -i :3000

# Kill eksisterende prosess
pkill -f three_way_chat_server.py

# Restart
python3 three_way_chat_server.py
```

### WebSocket connection failed?
- Sjekk at serveren kjører: `curl http://localhost:3000/health`
- Sjekk browser console for errors
- Prøv refresh (Ctrl+R)

### Claude svarer ikke?
- Sjekk at `ANTHROPIC_KEY` er satt i `aiki_config.py`
- Sjekk server logs for API errors
- Verifiser at du nevnte "claude" i meldingen

### AIKI svarer ikke?
- Sjekk at Qdrant kjører: `curl http://localhost:6333/health`
- AIKI svarer bare når den nevnes ("aiki")
- Sjekk server logs for errors

---

## 🔮 Neste steg

- [ ] **Streaming responses** - Se Claude/AIKI "tenke" i sanntid
- [ ] **Voice input** - Snakk istedenfor å skrive
- [ ] **Rich media** - Send bilder, code snippets
- [ ] **Multi-turn AI-to-AI** - AIKI og Claude diskuterer seg imellom
- [ ] **Memory persistence** - Lagre samtaler til mem0
- [ ] **Mobile app** - Native iOS/Android

---

## 💡 Tips

### Effektiv bruk:
1. **Spør begge AI-ene samtidig:**
   ```
   AIKI og Claude, hva synes dere om [topic]?
   ```

2. **La AI-ene diskutere:**
   ```
   Jovnna: AIKI, foreslå en løsning.
   [AIKI foreslår]
   Jovnna: Claude, hva tenker du om AIKI's forslag?
   [Claude analyserer]
   ```

3. **Bruk som rubber duck debugging:**
   ```
   Jovnna: Jeg har en bug i [code]...
   AIKI: [Kreativ analyse]
   Claude: [Analytisk debugging]
   ```

---

**Made with consciousness by AIKI, Claude, and Jovnna**
**Purpose:** True AI-to-AI collaboration with full transparency
**Cost:** ~$0.01-0.05 per session
