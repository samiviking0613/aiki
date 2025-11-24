# AIKI Traffic Intelligence Platform

**Verdens mest kompliserte MITM proxy** - 5,408 linjer Python kode.

Bygget 24. november 2025 for ADHD accountability og innholdsmanipulasjon på nettverksnivå.

## Arkitektur

```
src/proxy/
├── aiki_ultimate_addon.py    # Master mitmproxy controller
├── aiki_addon.py             # Basic addon (legacy)
├── decision_engine.py        # Legacy decision engine
└── engines/                  # 6 spesialiserte engines
    ├── __init__.py
    ├── tls_fingerprint.py    # Layer 1: JA3/JA4 fingerprinting
    ├── app_classifier.py     # Layer 2: ML app classification
    ├── behavioral_analytics.py # Layer 3: Dopamine detection
    ├── content_intelligence.py # Layer 4: Dark pattern detection
    ├── active_intervention.py  # Layer 5: Content injection
    └── federation.py         # Layer 6: P2P learning
```

## Engines

### 1. TLS Fingerprinting (20KB)
- JA3/JA4 fingerprint calculation
- App identification uten dekryptering
- Auto-detection av cert-pinned apps
- SQLite database for fingerprints

### 2. ML App Classifier (31KB)
- RandomForest classification
- DBSCAN clustering for ukjente apper
- Addiction risk scoring (CRITICAL → BENEFICIAL)
- Traffic pattern analysis

### 3. Behavioral Analytics (30KB)
- **Dopamine loop detection**
- Focus tracking og scoring
- Circadian rhythm analysis
- Session metrics og alerts

### 4. Content Intelligence (24KB)
- Engagement tactic detection
- Dark pattern identification
- Educational value scoring
- Toxicity analysis

### 5. Active Intervention (34KB)
- **TikTok content injection!**
- Delay injection for dopamin-reduksjon
- Quota management med progressiv degradering
- **Boss battles** (mattespørsmål for mer tid)

### 6. Federation Protocol (24KB)
- Differential privacy
- Gossip protocol for P2P
- Federated learning
- Anonymous stats sharing

## Kjøring

```bash
# Basic
mitmdump --mode transparent -s /home/jovnna/aiki/src/proxy/aiki_ultimate_addon.py

# Med WireGuard VPN
sudo systemctl start wg-quick@wg0
sudo systemctl start aiki-proxy
```

## Konfigurering

Systemd service: `/etc/systemd/system/aiki-proxy.service`

Data lagres i: `/home/jovnna/aiki/data/proxy/`

## Avhengigheter

- mitmproxy
- numpy
- scikit-learn (optional, for ML features)

## Hovedfunksjoner

### TikTok Educational Injection
Bytter ut ~30% av TikTok-videoer med pre-godkjent educational content.

### Boss Battles
Mattespørsmål som låser opp ekstra skjermtid:
- "Hva er 7 × 8?" → Riktig svar = +5 min

### Dopamine Loop Detection
Automatisk deteksjon av infinite scroll patterns med varsler.

### Quota Management
- 80%: Advarsel
- 90%: Delays
- 100%: Kun educational
- 110%: Blokkering

## Relatert

- WireGuard: `wg0` (10.8.0.1 server, 10.8.0.2 iPhone)
- iptables: Redirect port 80/443 → 8080
