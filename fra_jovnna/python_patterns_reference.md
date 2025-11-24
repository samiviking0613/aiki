# Python Patterns Reference (Aiki)

Målet her er å gi Aiki konkrete mønstre å gjenbruke slik at koden blir konsistent.

---

## 1. CLI-verktøy (kommandolinje)

Standard struktur for små CLI-verktøy:

```python
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Beskrivelse av verktøyet.")
    parser.add_argument("--config", type=str, required=True, help="Path til config-fil.")
    args = parser.parse_args()

    run(config_path=args.config)


def run(config_path: str) -> None:
    # Kjernefunksjonalitet
    ...


if __name__ == "__main__":
    main()
```

Regel:
- main() = parsing og oppstart.
- run() = logikk som kan testes direkte.

---

## 2. Service + repository pattern

Bruk dette når Aiki skriver kode som snakker med database / eksterne API:

```python
class UserRepository:
    def __init__(self, db):
        self._db = db

    def get_user(self, user_id: int) -> dict | None:
        ...


class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    def get_user_profile(self, user_id: int) -> dict:
        user = self._repo.get_user(user_id)
        if user is None:
            raise ValueError("User not found")
        return {"id": user["id"], "name": user["name"]}
```

Poeng:
- Repository = tilgang til data.
- Service = forretningslogikk.

---

## 3. Config-håndtering

Aiki skal unngå hardkoding. Typisk mønster:

```python
from dataclasses import dataclass
import os
import tomllib


@dataclass
class AppConfig:
    db_url: str
    log_level: str = "INFO"


def load_config(path: str | None = None) -> AppConfig:
    path = path or os.environ.get("AIKI_CONFIG", "config.toml")
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return AppConfig(**data["app"])
```

---

## 4. Context manager for ressurser

Eksempel: kobling til database, fil, nettverk.

```python
from contextlib import contextmanager

@contextmanager
def open_db(url: str):
    conn = connect(url)
    try:
        yield conn
    finally:
        conn.close()
```

---

## 5. Async IO-mønster

Brukes for nettverkskode, API-kall, osv.

```python
import asyncio
import httpx


async def fetch_url(url: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


async def main() -> None:
    html = await fetch_url("https://example.com")
    print(html)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. Feilhåndtering rundt eksterne systemer

Standardmønster:

```python
import logging
from typing import Any

logger = logging.getLogger(__name__)


def call_external(api, payload: dict) -> dict[str, Any]:
    try:
        resp = api.send(payload)
    except TimeoutError as exc:
        logger.error("Timeout mot ekstern tjeneste: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Ukjent feil mot ekstern tjeneste")
        raise
    else:
        return resp
```

---

## 7. Konklusjon

Når Aiki skriver Python-kode, bør den:
- bruke disse mønstrene som mal
- gjenkjenne situasjoner der de er relevante
- heller kombinere eksisterende patterns enn å finne opp nye hver gang
