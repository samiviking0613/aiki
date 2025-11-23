#!/usr/bin/env python3
"""
Auto-genererer README.md for alle mapper basert på innhold.
Kjør: python tools/generate_readmes.py
"""

from pathlib import Path
from datetime import datetime

AIKI_ROOT = Path.home() / "aiki"

# Mappe-beskrivelser (oppdater ved behov)
DESCRIPTIONS = {
    "src": "Kildekode for AIKI-systemet",
    "src/aiki_prime": "AIKI Prime - Hovedbevissthet og koordinator",
    "src/circles": "Holacracy Circles - Selvorganiserende enheter",
    "src/mini_aikis": "Mini-AIKIs - Spesialiserte sub-agenter",
    "src/safety": "Safety layers - Kill switch, constraints, audit",
    "src/monitoring": "Monitoring - Emergence detection, dashboards",
    "src/memory": "Memory systems - Episodic, semantic, working",
    "src/federation": "Federation - Multi-AIKI kommunikasjon",
    "bin": "Kjørbare shell scripts",
    "tools": "Utvikler- og admin-verktøy",
    "services": "Daemons og systemd services",
    "services/daemons": "Python daemon-prosesser",
    "services/systemd": "Systemd service-filer",
    "data": "Runtime data og session state",
    "config": "Konfigurasjonsfiler",
    "docs": "Dokumentasjon",
    "tests": "Tester",
    "_ARCHIVE": "Arkiverte/utdaterte filer (kan slettes)",
}

def get_file_info(path: Path) -> dict:
    """Hent info om filer i en mappe"""
    files = []
    for f in sorted(path.iterdir()):
        if f.name.startswith('.') or f.name == 'README.md':
            continue
        if f.name == '__pycache__':
            continue

        info = {
            'name': f.name,
            'is_dir': f.is_dir(),
            'size': f.stat().st_size if f.is_file() else None,
        }

        # Hent første docstring for Python-filer
        if f.suffix == '.py' and f.is_file():
            try:
                content = f.read_text(encoding='utf-8')
                if '"""' in content:
                    start = content.find('"""') + 3
                    end = content.find('"""', start)
                    if end > start:
                        doc = content[start:end].strip().split('\n')[0]
                        info['description'] = doc[:80]
            except:
                pass

        files.append(info)

    return files

def generate_readme(path: Path, description: str = None) -> str:
    """Generer README innhold for en mappe"""
    rel_path = path.relative_to(AIKI_ROOT)

    lines = [f"# {path.name}/", ""]

    if description:
        lines.append(description)
        lines.append("")

    files = get_file_info(path)

    if not files:
        lines.append("*Tom mappe*")
        return "\n".join(lines)

    # Separate dirs and files
    dirs = [f for f in files if f['is_dir']]
    py_files = [f for f in files if f['name'].endswith('.py')]
    sh_files = [f for f in files if f['name'].endswith('.sh')]
    other = [f for f in files if not f['is_dir'] and not f['name'].endswith(('.py', '.sh'))]

    if dirs:
        lines.append("## Undermapper")
        lines.append("")
        lines.append("| Mappe | Beskrivelse |")
        lines.append("|-------|-------------|")
        for d in dirs:
            sub_desc = DESCRIPTIONS.get(f"{rel_path}/{d['name']}", "")
            lines.append(f"| [{d['name']}/]({d['name']}/) | {sub_desc} |")
        lines.append("")

    if py_files:
        lines.append("## Python-filer")
        lines.append("")
        lines.append("| Fil | Beskrivelse |")
        lines.append("|-----|-------------|")
        for f in py_files:
            desc = f.get('description', '')
            lines.append(f"| `{f['name']}` | {desc} |")
        lines.append("")

    if sh_files:
        lines.append("## Shell scripts")
        lines.append("")
        for f in sh_files:
            lines.append(f"- `{f['name']}`")
        lines.append("")

    if other:
        lines.append("## Andre filer")
        lines.append("")
        for f in other:
            lines.append(f"- `{f['name']}`")
        lines.append("")

    lines.append("---")
    lines.append(f"*Auto-generert: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)

def main():
    """Generer README for alle mapper"""
    print("Genererer README.md filer...")

    count = 0
    for rel_path, desc in DESCRIPTIONS.items():
        path = AIKI_ROOT / rel_path
        if not path.exists() or not path.is_dir():
            continue

        readme_path = path / "README.md"
        content = generate_readme(path, desc)

        readme_path.write_text(content, encoding='utf-8')
        print(f"  {rel_path}/README.md")
        count += 1

    print(f"\nGenerert {count} README-filer!")

if __name__ == "__main__":
    main()
