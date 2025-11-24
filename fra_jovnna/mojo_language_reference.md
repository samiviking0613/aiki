# Mojo Language Reference (Aiki base)

Dette dokumentet gir Aiki en kort oversikt over Mojo som språk,
med fokus på forskjeller fra Python og hva Mojo er bra til.

---

## 1. Hva er Mojo?

- Et språk laget for høy ytelse (kompileres).
- Ligner Python i syntaks, men:
  - statiske typer
  - eksplisitt memory / performance-tankegang
  - fokus på numerikk, ML, HPC.

Bruk Mojo når:
- ytelse er kritisk
- du skal bygge "hot path"-komponenter
- du jobber med numeriske kjerner.

---

## 2. Grunnsyntaks (kort)

Mojo bruker Python-lik syntaks:

```mojo
fn add(a: Int, b: Int) -> Int:
    return a + b
```

Forskjeller vs Python:
- fn for funksjoner.
- Typer er obligatoriske i de fleste tilfeller.
- Mer fokus på struct og "value types" for ytelse.

---

## 3. Typer (enkelt nivå)

Eksempler:

```mojo
fn length(xs: List[Int]) -> Int:
    var total: Int = 0
    for _ in xs:
        total += 1
    return total
```

- var = muterbar variabel.
- let = immutable.

---

## 4. Performance-tankegang

Når Aiki skriver Mojo-kode skal den:

- Minimere allokering i tight loops.
- Foretrekke faste typer.
- Unngå unødvendige abstractions i hot paths.
- Bruke en enkel, eksplisitt stil.

---

## 5. Mojo vs Python – rollefordeling i Aiki

Forslag til arbeidsdeling:

- Python:
  - Orkestrering
  - API-kall
  - Fil- og nettverkslogikk
  - Aiki Router, RAG, DB

- Mojo:
  - Tunge beregninger (numerikk)
  - Kjerner for bildebehandling / lyd / signal
  - Spesifikke performance-kritiske moduler

---

## 6. Eksempel – enkel numerisk kjerne

```mojo
fn sum_array(xs: List[Float64]) -> Float64:
    var total: Float64 = 0.0
    for x in xs:
        total += x
    return total
```

---

## 7. Praktisk for Aiki

Når Aiki genererer Mojo-kode:

- Den skal først beskrive formålet med modulen.
- Kode skal være:
  - kort
  - eksplisitt typet
  - lett å kalle fra Python (FFI / bindings).

Mojo-kode skal ikke forsøke å erstatte hele systemet,
men optimalisere kritiske deler som identifiseres senere.
