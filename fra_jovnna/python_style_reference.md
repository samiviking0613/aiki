# Python Style Reference (Aiki base)

Denne filen oppsummerer de viktigste delene av PEP 8 + Google Python Style Guide.
Målet er å gi Aiki et konsistent grunnlag for Python-kode.

---

## 1. Grunnprinsipper

- Lesbarhet > korthet.
- En tydelig måte å gjøre ting på.
- Små, fokuserte funksjoner og moduler.
- Konsistent stil viktigere enn "perfekt" stil.

---

## 2. Indentering og layout

- Indent: 4 spaces, aldri tabs.
- Maks linjelengde: 88–100 tegn (helst 88).
- Tom linje:
  - 2 tomme linjer før toppnivå-funksjoner og -klasser.
  - 1 tom linje mellom metoder inne i en klasse.

Eksempel:

```python
def public_function():
    ...


class MyClass:
    def method_one(self):
        ...

    def method_two(self):
        ...
```

---

## 3. Navngiving

Bruk konsekvent stil:

- Funksjoner: snake_case
- Variabler: snake_case
- Klasser: CamelCase
- Konstanter: UPPER_SNAKE_CASE
- Moduler/filer: snake_case.py

Eksempel:

```python
MAX_RETRIES = 3

def fetch_data():
    ...

class ApiClient:
    ...
```

Unngå:
- Enbokstavsnavn, bortsett fra korte loop-variabler (i, j, k).
- "Magiske" navn som ikke sier hva de gjør.

---

## 4. Imports

- Imports øverst i fila.
- Rekkefølge:
  1. Standardbibliotek
  2. Tredjepart
  3. Lokale moduler

- Bruk normalt hele moduler, ikke `from x import *`.

```python
import os
import pathlib

import requests

from aiki_core.config import load_config
```

---

## 5. Dokstrings

- Bruk triple doble anførselstegn """.
- Forklar hva funksjonen gjør, ikke hvordan i detalj.

```python
def fetch_user(user_id: int) -> User:
    """Hent en bruker fra databasen.

    Args:
        user_id: ID til brukeren.

    Returns:
        User-objektet hvis funnet, ellers kastes exception.
    """
    ...
```

---

## 6. Type hints

- Alle nye funksjoner skal ha type hints på argumenter og returverdi.
- Bruk `from __future__ import annotations` i nye filer når det trengs.

```python
from __future__ import annotations

from typing import Iterable

def sum_values(values: Iterable[int]) -> int:
    return sum(values)
```

---

## 7. Feilhåndtering og logging

- Ikke svelg exceptions i `except` uten logging.
- Bruk logging istedenfor print i produksjonskode.

```python
import logging

logger = logging.getLogger(__name__)

def process_item(item: dict) -> None:
    try:
        ...
    except KeyError as exc:
        logger.error("Missing key in item: %s", exc)
        raise
```

---

## 8. Testing

- Testfiler heter `test_*.py`.
- En test skal være liten, tydelig og fokusert.
- Bruk pytest-stil når mulig.

```python
def test_sum_values():
    assert sum_values([1, 2, 3]) == 6
```

---

## 9. Kommentarer

- Bruk kommentarer kun når koden ikke er selvforklarende.
- Forklar hvorfor, ikke åpenbare ting.

```python
# Denne cachingen er kritisk for å redusere antall API-kall.
cache = {}
```

---

## 10. Konklusjon

Dette dokumentet er Aiki sin kortversjon av PEP 8 + Google Python Style.
For mer detaljer: bruk de fullstendige stilguidene lokalt.
