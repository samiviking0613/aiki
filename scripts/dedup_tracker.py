#!/usr/bin/env python3
"""
Dedupliserings-Tracker for AIKI Memory System

Sikrer at viktig kontekst ikke går tapt ved deduplisering.
Logger alle dedupliserings-beslutninger for manuell gjennomgang.

Bruk:
    python scripts/dedup_tracker.py analyze    # Analyser potensielle duplikater
    python scripts/dedup_tracker.py review     # Vis pending for review
    python scripts/dedup_tracker.py approve    # Godkjenn og slett duplikater
    python scripts/dedup_tracker.py restore ID # Gjenopprett et slettet minne
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

# Setup
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault('OPENAI_API_KEY', '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')
os.environ.setdefault('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Paths
DATA_DIR = Path(__file__).parent.parent / "data" / "dedup_tracking"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PENDING_FILE = DATA_DIR / "pending_deletions.json"
DELETED_FILE = DATA_DIR / "deleted_memories.json"  # Backup før sletting
APPROVED_FILE = DATA_DIR / "approved_deletions.json"
LOG_FILE = DATA_DIR / "dedup_log.json"


@dataclass
class DuplicateCandidate:
    """Et potensielt duplikat som må vurderes"""
    original_id: str
    original_text: str
    original_collection: str
    duplicate_id: str
    duplicate_text: str
    duplicate_collection: str
    similarity_score: float
    reason: str  # Hvorfor vi tror det er duplikat
    detected_at: str
    status: str = "pending"  # pending, approved, rejected, restored
    risk_level: str = "low"  # low, medium, high - for varsling
    auto_delete: bool = True  # False = krever manuell godkjenning


# Nøkkelord som indikerer viktig kontekst - ALDRI auto-slett
IMPORTANT_KEYWORDS = [
    'aiki', 'ultimate', 'vision', 'roadmap', 'arkitektur', 'design',
    'beslutning', 'strategi', 'mål', 'plan', 'kritisk', 'viktig',
    'adhd', 'jovnna', 'personlig', 'familie', 'barn', 'kids',
    'api-key', 'passord', 'hemmelighet', 'secret', 'credential',
    'økonomi', 'bank', 'lån', 'innovasjon', 'støtte',
    'genesis', 'circle', 'prime', 'consciousness'
]

# Mønstre som er trygge å slette automatisk
SAFE_DELETE_PATTERNS = [
    'auto-healing is enabled',
    'thread explosion',
    'check interval',
    'memory daemon',
    'health check',
    'heartbeat',
]


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host='localhost', port=6333)


def classify_risk(text: str) -> Tuple[str, bool]:
    """
    Klassifiser risiko for sletting av et minne.

    Returns:
        (risk_level, auto_delete)
        - "high" + False = ALDRI auto-slett, krever manuell review
        - "medium" + False = Vis varsel, men kan godkjennes
        - "low" + True = Trygt å auto-slette
    """
    text_lower = text.lower()

    # Sjekk for viktige nøkkelord → HØY RISIKO
    for keyword in IMPORTANT_KEYWORDS:
        if keyword in text_lower:
            return ("high", False)

    # Sjekk for trygge mønstre → LAV RISIKO
    for pattern in SAFE_DELETE_PATTERNS:
        if pattern in text_lower:
            return ("low", True)

    # Lengde-basert heuristikk
    if len(text) > 500:
        # Lange minner har ofte viktig kontekst
        return ("medium", False)

    if len(text) < 50:
        # Veldig korte minner er ofte duplikater
        return ("low", True)

    # Default: medium risiko, krever godkjenning
    return ("medium", False)


def compute_text_hash(text: str) -> str:
    """Lag hash av tekst for rask sammenligning"""
    normalized = ' '.join(text.lower().split())
    return hashlib.md5(normalized.encode()).hexdigest()


def text_similarity(text1: str, text2: str) -> float:
    """Enkel Jaccard similarity mellom to tekster"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)


def analyze_collection_duplicates(collection_name: str) -> List[DuplicateCandidate]:
    """Finn potensielle duplikater i en collection"""
    client = get_qdrant_client()

    try:
        info = client.get_collection(collection_name)
        count = info.points_count
    except Exception as e:
        print(f"Kunne ikke lese {collection_name}: {e}")
        return []

    if count == 0:
        return []

    print(f"Analyserer {collection_name} ({count} minner)...")

    # Hent alle punkter
    points = client.scroll(
        collection_name=collection_name,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )[0]

    # Grupper etter hash for eksakte duplikater
    hash_groups: Dict[str, List] = {}
    for point in points:
        payload = point.payload or {}
        text = payload.get('memory', payload.get('data', ''))
        if not text:
            continue

        h = compute_text_hash(text)
        if h not in hash_groups:
            hash_groups[h] = []
        hash_groups[h].append({
            'id': str(point.id),
            'text': text,
            'payload': payload
        })

    duplicates = []
    now = datetime.now().isoformat()

    # Finn eksakte duplikater (samme hash)
    for h, group in hash_groups.items():
        if len(group) > 1:
            original = group[0]
            for dup in group[1:]:
                duplicates.append(DuplicateCandidate(
                    original_id=original['id'],
                    original_text=original['text'][:500],
                    original_collection=collection_name,
                    duplicate_id=dup['id'],
                    duplicate_text=dup['text'][:500],
                    duplicate_collection=collection_name,
                    similarity_score=1.0,
                    reason="EKSAKT DUPLIKAT (samme hash)",
                    detected_at=now
                ))

    # Finn nære duplikater (høy tekstlikhet)
    texts = [(p.id, p.payload.get('memory', p.payload.get('data', '')))
             for p in points if p.payload]

    for i, (id1, text1) in enumerate(texts):
        if not text1 or len(text1) < 20:
            continue
        for j, (id2, text2) in enumerate(texts[i+1:], i+1):
            if not text2 or len(text2) < 20:
                continue

            # Skip hvis allerede funnet som eksakt
            if compute_text_hash(text1) == compute_text_hash(text2):
                continue

            sim = text_similarity(text1, text2)
            if sim > 0.85:  # 85%+ likhet
                duplicates.append(DuplicateCandidate(
                    original_id=str(id1),
                    original_text=text1[:500],
                    original_collection=collection_name,
                    duplicate_id=str(id2),
                    duplicate_text=text2[:500],
                    duplicate_collection=collection_name,
                    similarity_score=sim,
                    reason=f"HØY LIKHET ({sim:.1%})",
                    detected_at=now
                ))

    return duplicates


def analyze_cross_collection_duplicates() -> List[DuplicateCandidate]:
    """Finn duplikater på tvers av collections"""
    client = get_qdrant_client()
    collections = ['mem0_memories', 'mem0_memories_large', 'aiki_consciousness']

    all_memories = []
    for coll in collections:
        try:
            points = client.scroll(
                collection_name=coll,
                limit=10000,
                with_payload=True,
                with_vectors=False
            )[0]
            for p in points:
                text = p.payload.get('memory', p.payload.get('data', '')) if p.payload else ''
                if text:
                    all_memories.append({
                        'id': str(p.id),
                        'text': text,
                        'collection': coll,
                        'hash': compute_text_hash(text)
                    })
        except:
            continue

    print(f"Analyserer {len(all_memories)} minner på tvers av collections...")

    # Grupper etter hash
    hash_groups: Dict[str, List] = {}
    for mem in all_memories:
        h = mem['hash']
        if h not in hash_groups:
            hash_groups[h] = []
        hash_groups[h].append(mem)

    duplicates = []
    now = datetime.now().isoformat()

    for h, group in hash_groups.items():
        # Kun interessant hvis samme minne finnes i flere collections
        collections_in_group = set(m['collection'] for m in group)
        if len(collections_in_group) > 1:
            # Behold den i large hvis tilgjengelig, ellers første
            sorted_group = sorted(group, key=lambda x: (
                0 if x['collection'] == 'mem0_memories_large' else 1
            ))
            original = sorted_group[0]

            for dup in sorted_group[1:]:
                if dup['collection'] != original['collection']:
                    duplicates.append(DuplicateCandidate(
                        original_id=original['id'],
                        original_text=original['text'][:500],
                        original_collection=original['collection'],
                        duplicate_id=dup['id'],
                        duplicate_text=dup['text'][:500],
                        duplicate_collection=dup['collection'],
                        similarity_score=1.0,
                        reason=f"CROSS-COLLECTION DUPLIKAT",
                        detected_at=now
                    ))

    return duplicates


def save_pending(candidates: List[DuplicateCandidate]):
    """Lagre pending deletions til fil"""
    existing = load_pending()

    # Legg til nye (unngå duplikater i listen)
    existing_ids = {(c['duplicate_id'], c['duplicate_collection']) for c in existing}

    for c in candidates:
        key = (c.duplicate_id, c.duplicate_collection)
        if key not in existing_ids:
            existing.append(asdict(c))
            existing_ids.add(key)

    with open(PENDING_FILE, 'w') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"Lagret {len(existing)} pending deletions til {PENDING_FILE}")


def load_pending() -> List[dict]:
    """Les pending deletions"""
    if not PENDING_FILE.exists():
        return []
    with open(PENDING_FILE, 'r') as f:
        return json.load(f)


def load_deleted() -> List[dict]:
    """Les slettede minner (backup)"""
    if not DELETED_FILE.exists():
        return []
    with open(DELETED_FILE, 'r') as f:
        return json.load(f)


def save_deleted(memories: List[dict]):
    """Lagre backup av slettede minner"""
    with open(DELETED_FILE, 'w') as f:
        json.dump(memories, f, indent=2, ensure_ascii=False)


def review_pending():
    """Vis pending deletions for review"""
    pending = load_pending()

    if not pending:
        print("Ingen pending deletions!")
        return

    print(f"\n{'='*80}")
    print(f"PENDING DELETIONS: {len(pending)} kandidater")
    print(f"{'='*80}\n")

    # Grupper etter reason
    by_reason = {}
    for p in pending:
        reason = p.get('reason', 'ukjent')
        if reason not in by_reason:
            by_reason[reason] = []
        by_reason[reason].append(p)

    for reason, items in by_reason.items():
        print(f"\n--- {reason} ({len(items)} stk) ---\n")

        for i, item in enumerate(items[:5], 1):  # Vis maks 5 per kategori
            print(f"{i}. [{item['duplicate_collection']}] ID: {item['duplicate_id'][:8]}...")
            print(f"   Original: {item['original_text'][:80]}...")
            print(f"   Duplikat: {item['duplicate_text'][:80]}...")
            print(f"   Likhet: {item['similarity_score']:.1%}")
            print()

        if len(items) > 5:
            print(f"   ... og {len(items) - 5} flere\n")

    print(f"\nFor å godkjenne: python scripts/dedup_tracker.py approve")
    print(f"For å avvise alle: python scripts/dedup_tracker.py reject")


def approve_deletions(dry_run: bool = True, smart_mode: bool = False):
    """Godkjenn og utfør sletting av duplikater"""
    pending = load_pending()

    if not pending:
        print("Ingen pending deletions!")
        return

    # Klassifiser alle pending items
    for item in pending:
        risk, auto = classify_risk(item['duplicate_text'])
        item['risk_level'] = risk
        item['auto_delete'] = auto

    # I smart mode, bare slett auto_delete=True
    if smart_mode:
        auto_items = [p for p in pending if p.get('auto_delete', False)]
        manual_items = [p for p in pending if not p.get('auto_delete', False)]

        print(f"\n{'='*80}")
        print(f"SMART SLETTING - Kun trygge duplikater")
        print(f"{'='*80}")
        print(f"\n✅ Auto-slett: {len(auto_items)} (lav risiko)")
        print(f"⚠️  Krever review: {len(manual_items)} (medium/høy risiko)\n")

        if manual_items:
            print("--- KREVER MANUELL REVIEW ---")
            high_risk = [m for m in manual_items if m.get('risk_level') == 'high']
            med_risk = [m for m in manual_items if m.get('risk_level') == 'medium']

            if high_risk:
                print(f"\n🚨 HØY RISIKO ({len(high_risk)} stk) - Inneholder viktige nøkkelord:")
                for item in high_risk[:5]:
                    print(f"   • {item['duplicate_text'][:60]}...")

            if med_risk:
                print(f"\n⚠️  MEDIUM RISIKO ({len(med_risk)} stk) - Lange eller ukjente minner:")
                for item in med_risk[:3]:
                    print(f"   • {item['duplicate_text'][:60]}...")

        to_delete = auto_items
    else:
        to_delete = pending

    print(f"\n{'='*80}")
    print(f"{'DRY RUN - ' if dry_run else ''}SLETTER {len(to_delete)} DUPLIKATER")
    print(f"{'='*80}\n")

    client = get_qdrant_client()
    deleted_backup = load_deleted()

    success = 0
    failed = 0

    for item in to_delete:
        coll = item['duplicate_collection']
        point_id = item['duplicate_id']

        # Backup først
        backup_entry = {
            **item,
            'deleted_at': datetime.now().isoformat(),
            'full_text': item['duplicate_text']  # Full tekst for restore
        }

        if dry_run:
            risk_emoji = {"high": "🚨", "medium": "⚠️", "low": "✅"}.get(item.get('risk_level', 'low'), "❓")
            print(f"[DRY] {risk_emoji} Ville slettet {point_id[:8]}... fra {coll}")
            success += 1
        else:
            try:
                # Hent full payload før sletting
                points = client.retrieve(
                    collection_name=coll,
                    ids=[point_id],
                    with_payload=True
                )
                if points:
                    backup_entry['full_payload'] = points[0].payload

                # Slett
                client.delete(
                    collection_name=coll,
                    points_selector=[point_id]
                )

                deleted_backup.append(backup_entry)
                success += 1
                print(f"✅ Slettet {point_id[:8]}... fra {coll}")

            except Exception as e:
                failed += 1
                print(f"❌ Feilet {point_id[:8]}...: {e}")

    if not dry_run:
        # Lagre backup
        save_deleted(deleted_backup)

        # Oppdater pending - fjern slettede, behold de som krever review
        if smart_mode:
            remaining = [p for p in pending if not p.get('auto_delete', False)]
            with open(PENDING_FILE, 'w') as f:
                json.dump(remaining, f, indent=2, ensure_ascii=False)
            if remaining:
                print(f"\n⚠️  {len(remaining)} minner krever fortsatt manuell review")
        else:
            with open(PENDING_FILE, 'w') as f:
                json.dump([], f)

        # Logg
        log_entry = {
            'action': 'smart_delete' if smart_mode else 'approve_deletions',
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'failed': failed,
            'remaining_for_review': len([p for p in pending if not p.get('auto_delete', False)]) if smart_mode else 0
        }
        log_action(log_entry)

    print(f"\n{'DRY RUN - ' if dry_run else ''}Resultat: {success} slettet, {failed} feilet")

    if dry_run:
        if smart_mode:
            print("\nKjør med --execute for å faktisk slette de trygge:")
            print("  python scripts/dedup_tracker.py smart --execute")
        else:
            print("\nKjør med --execute for å faktisk slette:")
            print("  python scripts/dedup_tracker.py approve --execute")


def restore_memory(memory_id: str):
    """Gjenopprett et slettet minne"""
    deleted = load_deleted()

    # Finn minnet
    to_restore = None
    for i, item in enumerate(deleted):
        if item['duplicate_id'].startswith(memory_id):
            to_restore = item
            del deleted[i]
            break

    if not to_restore:
        print(f"Fant ikke minne med ID som starter med {memory_id}")
        return

    client = get_qdrant_client()
    coll = to_restore['duplicate_collection']

    # Gjenopprett
    # Dette er forenklet - full restore ville trenge vektoren også
    print(f"Gjenoppretter {to_restore['duplicate_id']} til {coll}...")
    print(f"Tekst: {to_restore.get('full_text', to_restore['duplicate_text'])}")

    # For full restore må vi re-embedde
    print("\n⚠️  Full restore krever re-embedding. Bruk mem0.add() manuelt:")
    print(f'   mem0.add([{{"role": "user", "content": "{to_restore["duplicate_text"][:100]}..."}}], user_id="jovnna")')

    # Oppdater backup-fil
    save_deleted(deleted)


def log_action(entry: dict):
    """Logg en handling"""
    log = []
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r') as f:
            log = json.load(f)

    log.append(entry)

    with open(LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "analyze":
        print("Analyserer duplikater...\n")

        # Innen collections
        all_dups = []
        for coll in ['mem0_memories', 'mem0_memories_large', 'aiki_consciousness']:
            dups = analyze_collection_duplicates(coll)
            all_dups.extend(dups)
            print(f"  {coll}: {len(dups)} duplikater funnet")

        # På tvers av collections
        cross_dups = analyze_cross_collection_duplicates()
        all_dups.extend(cross_dups)
        print(f"  Cross-collection: {len(cross_dups)} duplikater funnet")

        if all_dups:
            save_pending(all_dups)
            print(f"\nTotalt: {len(all_dups)} potensielle duplikater")
            print("Kjør 'review' for å se detaljert liste")
        else:
            print("\nIngen duplikater funnet!")

    elif command == "review":
        review_pending()

    elif command == "approve":
        execute = "--execute" in sys.argv
        approve_deletions(dry_run=not execute, smart_mode=False)

    elif command == "smart":
        # Smart sletting - kun trygge duplikater, varsler om resten
        execute = "--execute" in sys.argv
        approve_deletions(dry_run=not execute, smart_mode=True)

    elif command == "reject":
        # Tøm pending uten å slette
        with open(PENDING_FILE, 'w') as f:
            json.dump([], f)
        print("Alle pending deletions avvist (ingen sletting)")

    elif command == "restore":
        if len(sys.argv) < 3:
            print("Bruk: python scripts/dedup_tracker.py restore <ID>")
            return
        restore_memory(sys.argv[2])

    elif command == "status":
        pending = load_pending()
        deleted = load_deleted()
        print(f"Pending deletions: {len(pending)}")
        print(f"Deleted (backup): {len(deleted)}")

    else:
        print(f"Ukjent kommando: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
