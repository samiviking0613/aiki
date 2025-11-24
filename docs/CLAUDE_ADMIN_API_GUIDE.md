# 🔑 Claude Admin API - Komplett Guide

**Sist oppdatert:** 20. november 2025
**Organisasjon:** J-E.T.T AS (ID: eef69736-fb31-4fd3-8c9e-22028be3a156)
**Admin Key:** `Anthropic_admin_key1` (lagret i Api-nøkler/)

---

## 📋 Oversikt

Admin API gir **full programmatisk kontroll** over organisasjonen din. Vi har testet alle endepunkter og bekreftet tilgang.

**Base URL:** `https://api.anthropic.com/v1/organizations/`

**Autentisering:**
```bash
x-api-key: sk-ant-admin-...
anthropic-version: 2023-06-01
```

---

## ✅ VERIFISERTE ENDEPUNKTER (Testet 20. Nov 2025)

### 1. Organisasjonsinformasjon

**GET** `/v1/organizations/me`

**Response:**
```json
{
  "id": "eef69736-fb31-4fd3-8c9e-22028be3a156",
  "type": "organization",
  "name": "J-E.T.T AS"
}
```

**Bruk:** Finn organization ID programmatisk.

---

### 2. API Keys Management

**GET** `/v1/organizations/api_keys`

**Response:**
```json
{
  "data": [
    {
      "id": "apikey_01TKo74N45WDgHEApxbX27WM",
      "type": "api_key",
      "name": "Aiki Ultimate bach",
      "workspace_id": "wrkspc_01FKErGVedytav1p7nbB9Hmt",
      "created_at": "2025-11-20T..."
    }
  ]
}
```

**Hva vi har:**
- 11 API keys totalt
- Fordelt på 3 workspaces
- Kan filtrere, oppdatere navn, disable keys

**POST** `/v1/organizations/api_keys/{api_key_id}`
→ Oppdater key (rename, enable/disable)

---

### 3. Workspaces

**GET** `/v1/organizations/workspaces`

**Response:**
```json
{
  "data": [
    {
      "id": "wrkspc_01VJaVQBdyxE5SYyBPjmRwkX",
      "type": "workspace",
      "name": "Claude Code",
      "created_at": "2025-11-13T12:34:10.870368Z",
      "archived_at": null
    }
  ]
}
```

**Våre workspaces:**
1. **Claude Code** - For Claude Code-bruk
2. **Default** - Standard workspace
3. **[Tredje workspace]**

**Andre operasjoner:**
- `POST /workspaces` - Opprett nytt workspace
- `POST /workspaces/{id}/archive` - Arkiver workspace

---

### 4. Organization Members

**GET** `/v1/organizations/users`

**Response:**
```json
{
  "data": [
    {
      "id": "user_01HQHEcfanHgHrFRLNSRcmDR",
      "type": "user",
      "email": "jeballovara@outlook.com",
      "name": "Jovnna-Edvar Ballovara",
      "role": "admin",
      "added_at": "2025-06..."
    }
  ]
}
```

**Roller:**
- `admin` - Full tilgang
- `developer` - API key management
- `billing` - Cost og billing
- `user` - Read-only

**Andre operasjoner:**
- `POST /users/{id}` - Oppdater rolle
- `DELETE /users/{id}` - Fjern medlem

---

### 5. Invites

**GET** `/v1/organizations/invites`

**Response:**
```json
{
  "data": []  // Ingen aktive invitasjoner
}
```

**Andre operasjoner:**
- `POST /invites` - Send invitasjon
- `DELETE /invites/{id}` - Kanseller invitasjon

---

### 6. Cost Report 💰

**GET** `/v1/organizations/cost_report`

**Parametere:**
- `starting_at` (required) - ISO 8601 timestamp
- `ending_at` (optional) - Default: now
- `bucket_width` (optional) - `1h`, `1d`, `1w` (default: `1d`)
- `limit` (optional) - Max 31 (dager)

**Response:**
```json
{
  "data": [
    {
      "starting_at": "2025-11-13T00:00:00Z",
      "ending_at": "2025-11-14T00:00:00Z",
      "results": [
        {
          "currency": "USD",
          "amount": "497.30"
        }
      ]
    }
  ],
  "has_more": false
}
```

**Våre tall (siste 7 dager):**
- 13. Nov: $497.30 (setup day!)
- 16. Nov: $40.52
- 17. Nov: $12.49
- 18. Nov: $15.36
- **Total:** $565.67
- **Gjennomsnitt:** $80.81/dag

**Bruk:**
- Weekly usage tracking (for statusline)
- Kostnadsovervåking
- Budget alerts

---

### 7. Usage Report 📊

**GET** `/v1/organizations/usage_report/messages`

**Parametere:**
- `starting_at` (required) - ISO 8601 timestamp
- `ending_at` (required) - ISO 8601 timestamp
- `bucket_width` (optional) - `1h`, `1d`, `1w`
- `group_by` (optional) - `workspace_id`, `api_key_id`, `model`, etc.

**Response Structure:**
```json
{
  "data": [
    {
      "starting_at": "2025-11-13T00:00:00Z",
      "ending_at": "2025-11-14T00:00:00Z",
      "results": [
        {
          "uncached_input_tokens": 259276,
          "cache_creation": {
            "ephemeral_1h_input_tokens": 0,
            "ephemeral_5m_input_tokens": 567413
          },
          "cache_read_input_tokens": 5680224,
          "output_tokens": 60360,
          "server_tool_use": {
            "web_search_requests": 2
          },
          "api_key_id": null,
          "workspace_id": null,
          "model": null,
          "service_tier": null,
          "context_window": null
        }
      ]
    }
  ]
}
```

**Viktig oppdagelse:**
- `cache_creation` er et **objekt**, ikke en enkelt verdi!
- `ephemeral_5m_input_tokens` - Cache som varer 5 min
- `ephemeral_1h_input_tokens` - Cache som varer 1 time

**13. Nov (setup day) tall:**
- Uncached input: 259K tokens
- Cache creation: 567K tokens
- **Cache read: 5.68M tokens** (gratis!)
- Output: 60K tokens
- Web search: 2 requests

**Beregninger:**
```python
# Total tokens inkludert cache
total = uncached + cache_creation + cache_read + output
total = 259K + 567K + 5680K + 60K = 6,566K tokens

# Tokens som teller mot limits (ekskl cache_read)
limit_tokens = uncached + cache_creation + output
limit_tokens = 259K + 567K + 60K = 886K tokens

# Cache efficiency
efficiency = (cache_read / total) * 100
efficiency = (5680K / 6566K) * 100 = 86.5% 🚀
```

**Bruk:**
- Måle faktisk token usage
- Beregne cache efficiency
- Splitte usage per workspace/API key/model

---

## 🎯 PRAKTISKE BRUKSOMRÅDER

### 1. Real-Time Usage Dashboard

**Mulig:**
- Daglig cost breakdown (siste 7/30 dager)
- Cache efficiency tracking
- Token usage per workspace
- Cost per model
- Sammenligne Claude Code vs API usage

**Implementert:**
- ✅ `scripts/aiki_cost_dashboard.py` (trenger fix for cache_creation)
- ✅ `scripts/fetch_claude_weekly_usage.py` (for statusline)

### 2. Budget Alerts

**Mulig:**
- Alert når daglig cost > threshold
- Alert når weekly % > 80%
- Slack/Discord webhooks
- Email notifications

**Ikke implementert ennå.**

### 3. Workspace Analytics

**Mulig med `group_by`:**
```bash
# Usage per workspace
/usage_report/messages?group_by=workspace_id

# Usage per API key
/usage_report/messages?group_by=api_key_id

# Usage per model
/usage_report/messages?group_by=model
```

**Eksempel bruk:**
- Måle hvor mye AIKI-HOME proxy koster vs Claude Code
- Finne mest kostbare API keys
- Sammenligne Sonnet 4 vs Opus 4 usage

### 4. API Key Rotation

**Mulig:**
- List alle keys med `created_at`
- Automatisk disable keys > 90 dager gamle
- Varsle før keys expires (hvis de har expiry)

### 5. Team Management

**Mulig:**
- Programmatisk invitere nye medlemmer
- Oppdatere roller basert på GitHub teams
- Sync med LDAP/AD

**Ikke relevant for enkeltmannsorg.**

---

## 🚀 NYE MULIGHETER VI KAN UTFORSKE

### 1. Learned Limits System (v2)

**Nåværende:**
- Estimerer session limit (88K) med 50% confidence
- Bruker cost som proxy for weekly limit

**Forbedring:**
- Bruk `usage_report` til å **måle faktiske tokens brukt per time**
- Beregn personlig cost-per-hour ratio
- Track når rate limits nås (HTTP 429)
- Juster estimates basert på faktiske hits

**Implementasjon:**
```python
# Hent usage_report med 1h buckets
/usage_report/messages?bucket_width=1h

# For hver time: beregn tokens/hour
tokens_per_hour = uncached + cache_creation + output

# Hvis HTTP 429: logg timestamp + tokens
# Lær faktisk session limit (88K?)
```

### 2. Multi-Workspace Cost Tracking

**Mulig:**
- Opprett separate workspaces for:
  - `Claude Code` - Personal coding
  - `AIKI-HOME` - Proxy AI processing
  - `AIKI_v3` - Consciousness system
  - `Testing` - Experiments

- Track cost per workspace
- Alert hvis AIKI-HOME koster for mye

### 3. Cache Efficiency Optimization

**Måling:**
```python
efficiency = cache_read / (uncached + cache_creation + cache_read)
```

**Optimalisering:**
- Hvis efficiency < 50%: Øk cache TTL
- Hvis efficiency > 90%: Perfekt!
- Track efficiency over tid

**Goal:** 85%+ cache efficiency (gratis tokens!)

### 4. Model Cost Comparison

**Test:**
- Kjør samme task på Sonnet 4 vs Opus 4
- Måle cost diff med `group_by=model`
- Velg billigste model for hver task type

### 5. Real-Time Statusline (v2)

**Nåværende statusline:**
```
Context: X% | Session: X% | Usage: X%
```

**Forbedring:**
```
Context: X% | Session: X% | Weekly: X hours / 280h | Cache: X%
```

**Ny info:**
- **Weekly hours** (beregnet fra cost/hour ratio)
- **Cache efficiency** (live update hver 5 min)

---

## 📚 OPPSUMMERING

### ✅ Hva vi har tilgang til:

| Kategori | Endepunkt | Status |
|----------|-----------|--------|
| Org Info | `/organizations/me` | ✅ Testet |
| API Keys | `/organizations/api_keys` | ✅ 11 keys funnet |
| Workspaces | `/organizations/workspaces` | ✅ 3 workspaces |
| Members | `/organizations/users` | ✅ 1 admin |
| Invites | `/organizations/invites` | ✅ 0 invites |
| Cost Report | `/organizations/cost_report` | ✅ $565.67 siste 7d |
| Usage Report | `/organizations/usage_report/messages` | ✅ 86% cache eff! |

### 🎯 Hva vi kan bygge:

1. **Enhanced Cost Dashboard** - Real-time breakdown per workspace/model
2. **Learned Limits v2** - Faktisk timer tracking istedenfor cost proxy
3. **Cache Optimizer** - Auto-tune cache settings basert på efficiency
4. **Budget Alerts** - Slack/Discord notifications ved thresholds
5. **Multi-Workspace Analytics** - Separer AIKI-HOME vs Claude Code costs

### 🤔 Hva vi IKKE kan gjøre:

- ❌ Hente faktiske "hours used" direkte (må beregnes fra cost)
- ❌ Se per-message cost (bare aggregated)
- ❌ Real-time usage (5-10 min delay på API data)
- ❌ Compliance API (krever Enterprise plan)

---

## 🛠️ NESTE STEG

**Hva vil du fokusere på?**

1. **Fikse aiki_cost_dashboard.py** - Parse cache_creation korrekt
2. **Learned Limits v2** - Track faktiske timer
3. **Multi-Workspace Setup** - Separer AIKI-HOME costs
4. **Enhanced Statusline** - Legg til cache efficiency
5. **Noe annet?**

---

**Made with Admin API by Claude Code**
**Organization:** J-E.T.T AS
**Date:** 20. November 2025

---

## 🔄 UPDATE (20. Nov 2025) - Weekly Reset Tidspunkt

### ✅ BEKREFTET FRA CLAUDE.AI:

```
Weekly limits
Resets Sun 10:59 AM  ← Søndag 10:59 UTC
82% used
```

**Kritiske funn:**

1. **Reset-tidspunkt:** Søndag 10:59 UTC (= 11:59 CET vintertid)
2. **Admin API vs Claude.ai:**
   - Admin API (daily buckets): 80.0%
   - Claude.ai (real-time): 82%
   - Forskjell: 2% = dagens bruk (ikke synlig i daily buckets ennå)

3. **Max 5x Subscription vs Prepaid API:**
   - Admin API Total: $565.67 (setup week 13-16. Nov)
   - Prepaid API (sk-ant-api03-ZbL): $5.38
   - **Max 5x dekket:** $560.29 ✅
   - **Tolkning:** Console viser KUN prepaid, Admin API viser ALT

4. **Current Week (siden søndag 17. nov 10:59 UTC):**
   - 17. nov: $12.49
   - 18. nov: $15.36
   - 19. nov: $0.00
   - 20. nov: ~$0.70 (2% av $34.82)
   - **Total:** ~$28.55 = 82% ✅

### 🎯 IMPLEMENTERT:

✅ `fetch_claude_weekly_usage.py` - Oppdatert til søndag 10:59 UTC
✅ Statusline viser korrekt weekly % (med ~2% delay pga daily buckets)

### 💡 VIKTIG INNSIKT:

**"Console viser ikke Max 5x subscription usage!"**

- Console = KUN prepaid API credits
- Admin API = Source of truth for total usage
- Dette er derfor statusline MÅ bruke Admin API

---

**Kilde:** Jovnna's observasjon + claude.ai screenshot (20. Nov 2025)
