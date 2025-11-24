#!/usr/bin/env python3
"""
Finner potensielt utdaterte filer som bør vurderes for arkivering/sletting.

Kriterier:
- Ikke endret på >30 dager
- Ligger i rot-mappe (ikke organisert)
- Dupliserte navn
- Tomme filer
- Test-filer utenfor tests/
"""

from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import os

AIKI_DIR = Path.home() / "aiki"
IGNORE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', 'shared_qdrant', 'mcp-mem0', '_ARCHIVE', 'data', 'logs'}
IGNORE_FILES = {'.gitignore', '.env', 'README.md', 'CLAUDE.md'}

def get_all_files():
    """Hent alle filer"""
    files = []
    for f in AIKI_DIR.rglob('*'):
        if f.is_file():
            # Skip ignored directories
            if any(ignored in f.parts for ignored in IGNORE_DIRS):
                continue
            if f.name in IGNORE_FILES:
                continue
            files.append(f)
    return files

def find_stale_files(days=30):
    """Filer ikke endret på X dager"""
    cutoff = datetime.now() - timedelta(days=days)
    stale = []
    for f in get_all_files():
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime < cutoff:
            stale.append((f, mtime))
    return sorted(stale, key=lambda x: x[1])

def find_root_files():
    """Filer i rot-mappen (bør organiseres)"""
    root_files = []
    for f in AIKI_DIR.iterdir():
        if f.is_file() and f.name not in IGNORE_FILES:
            if not f.name.startswith('.'):
                root_files.append(f)
    return root_files

def find_duplicate_names():
    """Filer med samme navn i ulike mapper"""
    name_to_paths = defaultdict(list)
    for f in get_all_files():
        name_to_paths[f.name].append(f)
    return {name: paths for name, paths in name_to_paths.items() if len(paths) > 1}

def find_empty_files():
    """Tomme filer"""
    return [f for f in get_all_files() if f.stat().st_size == 0]

def find_misplaced_tests():
    """Test-filer utenfor tests/"""
    misplaced = []
    for f in get_all_files():
        if f.name.startswith('test_') or f.name.endswith('_test.py'):
            if 'tests' not in f.parts:
                misplaced.append(f)
    return misplaced

def main():
    print("=" * 60)
    print("AIKI FILE HEALTH CHECK")
    print(f"Dato: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Stale files
    stale = find_stale_files(30)
    if stale:
        print(f"\n📦 IKKE ENDRET PÅ 30+ DAGER ({len(stale)} filer):")
        for f, mtime in stale[:15]:
            rel = f.relative_to(AIKI_DIR)
            days_ago = (datetime.now() - mtime).days
            print(f"  {rel} ({days_ago}d)")
        if len(stale) > 15:
            print(f"  ... og {len(stale) - 15} til")

    # Root files
    root = find_root_files()
    if root:
        print(f"\n📁 FILER I ROT-MAPPE ({len(root)} filer):")
        for f in root:
            print(f"  {f.name}")

    # Duplicates
    dupes = find_duplicate_names()
    if dupes:
        print(f"\n🔄 DUPLISERTE FILNAVN ({len(dupes)} navn):")
        for name, paths in list(dupes.items())[:5]:
            print(f"  {name}:")
            for p in paths:
                print(f"    - {p.relative_to(AIKI_DIR)}")

    # Empty files
    empty = find_empty_files()
    if empty:
        print(f"\n⚠️ TOMME FILER ({len(empty)} filer):")
        for f in empty[:10]:
            print(f"  {f.relative_to(AIKI_DIR)}")

    # Misplaced tests
    misplaced = find_misplaced_tests()
    if misplaced:
        print(f"\n🧪 TEST-FILER UTENFOR tests/ ({len(misplaced)} filer):")
        for f in misplaced:
            print(f"  {f.relative_to(AIKI_DIR)}")

    print("\n" + "=" * 60)
    total_issues = len(stale) + len(root) + len(dupes) + len(empty) + len(misplaced)
    if total_issues == 0:
        print("✅ Ingen problemer funnet!")
    else:
        print(f"📋 Totalt {total_issues} potensielle issues å se på")
    print("=" * 60)

if __name__ == "__main__":
    main()
