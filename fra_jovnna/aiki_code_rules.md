# Aiki Code Rules

Disse reglene gjelder all kode Aiki skriver, uansett språk.
Målet er stabilitet, lesbarhet og enkel videreutvikling.

---

## 1. Generelle prinsipper

1. Kode skal være forståelig for et menneske som kommer inn senere.
2. Kode skal være modularisert (små, tydelige enheter).
3. Ingen hemmeligheter hardkodes i kode.
4. All funksjonalitet som kan testes, skal kunne testes.

---

## 2. Struktur og organisering

- Ett ansvar per modul/fil når mulig.
- Del opp:
  - konfigurasjon
  - domenelogikk
  - IO (API, DB, fil)
- Bruk mappe-struktur som følger domenet, ikke teknologien alene.

Eksempel:

```text
aiki/
  core/
  config/
  services/
  adapters/
  cli/
  tests/
```

---

## 3. Konfigurasjon

- Skal leses fra:
  - miljøvariabler
  - config-filer (YAML/TOML/JSON)
- Aldri API-nøkler, passord eller tokens direkte i kode.

---

## 4. Logging og observability

- Bruk logging (ikke print) i produksjonskode.
- Logg:
  - viktige beslutninger
  - feil
  - eksterne kall (minst på debug/info-nivå)

Men:
- Ikke logg sensitive data (tokens, passord, personinfo).

---

## 5. Feilhåndtering

- Unngå "bare" `except Exception` uten re-raise eller logging.
- Gi tydelige feilmeldinger.
- Skill mellom:
  - forventede feil (nettverk nede, valideringsfeil osv.)
  - programmeringsfeil (bug i kode).

---

## 6. Tests

- Nye moduler skal som hovedregel ha minst én test.
- Kritiske funksjoner: flere tester (edge cases).
- Ikke strev etter 100% coverage, men test det som er:
  - business critical
  - komplisert
  - lett å ødelegge

---

## 7. Dokumentasjon

- Minst én kort beskrivelse i toppen av viktige filer:
  - hva denne modulen gjør
  - hvordan den brukes
- Viktige funksjoner/klasser har dokstring.

---

## 8. AI-spesifikke regler

Når Aiki skriver kode for AI-integrasjon:

- Skal tydelig merke:
  - hvor eksterne API-er brukes
  - hvilke modeller som brukes
- Skal legge til TODO-kommentarer der:
  - det er usikkerhet
  - antakelser er gjort
  - man planlegger senere optimalisering

Eksempel:

```python
# TODO: Optimalisere dette kallet ved å bruke batch-endpoint senere.
```

---

## 9. Språkspesifikke referanser

- For Python: se `python_style_reference.md` og `python_patterns_reference.md`.
- For Mojo: se `mojo_language_reference.md`.

Aiki skal ikke duplisere disse reglene i hver fil,
men heller referere til dem i systemprompt/instruksjoner.

---

## 10. Oppdatering og versjonering

- Denne fila er versjon: v0.1-draft.
- Når praktisk erfaring viser nye behov:
  - legg til nye regler
  - fjern regler som er ubrukelige
  - hold det kort og relevant
