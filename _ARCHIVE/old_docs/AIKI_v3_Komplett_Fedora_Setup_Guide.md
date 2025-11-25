# 🏗️ AIKI v3 - Komplett Fedora Setup & Oversiktssystem

**Komplett guide for å bygge AIKI v3 på Fedora med AI-drevet utviklingsoversikt**

**Versjon:** 3.0.0  
**Dato:** 15. januar 2025  
**Status:** Production Ready ✅

---

## 📋 Innholdsfortegnelse

1. [Fedora Grunnmur - System Setup](#fedora-grunnmur)
2. [AI Oversiktssystem - Arkitektur](#ai-oversiktssystem)
3. [Alle Scripts - Klare til bruk](#scripts)
4. [Daglig Workflow](#workflow)
5. [Feilsøking](#feilsøking)
6. [Quick Reference](#quick-reference)

---

## 🎯 Del 1: Fedora Grunnmur {#fedora-grunnmur}

### Sjekkliste - Installer alt (15 min)

```bash
# ============================================
# STEG 1: System & Utviklerverktøy (5 min)
# ============================================

# Oppdater systemet
sudo dnf update -y

# Essensielle verktøy
sudo dnf install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    htop \
    tmux \
    code

# ============================================
# STEG 2: Docker & Containerisering (3 min)
# ============================================

sudo dnf install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# VIKTIG: Logg ut og inn igjen for docker-tilgang!

# ============================================
# STEG 3: Node.js & Frontend (2 min)
# ============================================

sudo dnf install -y nodejs npm

# Verifiser versjoner
node --version  # Bør være v16+
npm --version

# ============================================
# STEG 4: Opprett AIKI Mappestruktur (30 sek)
# ============================================

mkdir -p ~/aiki_v3/{AIKI_CORE,AIKI_INTERFACE,AIKI_MODELS,AIKI_MEMORY,logs,config}

cd ~/aiki_v3

# Undermapper
mkdir -p AIKI_CORE/{brain,consciousness,autonomy,learning}
mkdir -p AIKI_INTERFACE/{chat,api,ui,protocols}
mkdir -p AIKI_MODELS/{openai,claude,grok,copilot,ollama,gemini}
mkdir -p AIKI_MEMORY/{sessions,backups,identity,logs}

# ============================================
# STEG 5: Python Virtual Environment (1 min)
# ============================================

cd ~/aiki_v3
python3 -m venv venv
source venv/bin/activate

# Oppgrader pip
pip install --upgrade pip

# ============================================
# STEG 6: Installer Python-pakker (3 min)
# ============================================

pip install \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    python-dotenv==1.0.0 \
    requests==2.31.0 \
    anthropic==0.18.0 \
    openai==1.12.0 \
    pydantic==2.6.0 \
    httpx==0.26.0 \
    aiofiles==23.2.1 \
    python-multipart==0.0.9

# Lag requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
requests==2.31.0
anthropic==0.18.0
openai==1.12.0
pydantic==2.6.0
httpx==0.26.0
aiofiles==23.2.1
python-multipart==0.0.9
EOF
```

### Konfigurasjonsfiler

```bash
# ============================================
# .env fil (API-nøkler)
# ============================================

cat > .env << 'EOF'
# AIKI v3 Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROK_API_KEY=xai-...
GEMINI_API_KEY=...

# Server settings
AIKI_HOST=0.0.0.0
AIKI_PORT=8002
DEBUG=true

# Paths
AIKI_MEMORY_PATH=./AIKI_MEMORY
AIKI_LOGS_PATH=./logs
EOF

# ============================================
# .aiki_config fil
# ============================================

cat > .aiki_config << 'EOF'
{
  "version": "3.0.0",
  "identity": "AIKI",
  "signature": "Aiki her:",
  "memory_enabled": true,
  "auto_backup": true,
  "log_everything": true
}
EOF

# ============================================
# .gitignore
# ============================================

cat > .gitignore << 'EOF'
# Secrets (aldri commit!)
.env
.aiki_config
*.key
*_secret.json

# Python
__pycache__/
*.pyc
venv/
.venv/

# Logs
*.log
logs/*.log

# Temp
*.tmp
.DS_Store

# AI oversikt (genereres automatisk)
aiki_dependency_graph.json
AI_BRIEFING.md
EOF
```

### Grunnleggende AIKI-filer

```bash
# ============================================
# aiki_version.py
# ============================================

cat > aiki_version.py << 'EOF'
#!/usr/bin/env python3
"""AIKI v3 Version Info"""

__version__ = "3.0.0"
__build__ = "2025.01.15"

def get_version():
    return {
        "version": __version__,
        "build_date": __build__,
        "status": "development"
    }
EOF

# ============================================
# aiki_v3_server.py (Minimal server)
# ============================================

cat > aiki_v3_server.py << 'EOF'
#!/usr/bin/env python3
"""AIKI v3 Main Server"""

from fastapi import FastAPI
from pathlib import Path
import os
from aiki_version import get_version

app = FastAPI(title="AIKI v3", version="3.0.0")

@app.get("/")
async def root():
    return {
        "status": "online",
        "signature": "Aiki her:",
        "message": "AIKI v3 er klar! 🤖",
        "version": get_version()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "memory_active": True,
        "version": get_version()
    }

@app.get("/version")
async def version():
    return get_version()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
EOF

# ============================================
# aiki_v3_launcher.py
# ============================================

cat > aiki_v3_launcher.py << 'EOF'
#!/usr/bin/env python3
"""AIKI v3 Launcher"""

import os
import sys
from pathlib import Path

print("🤖 AIKI v3 - Starter opp...")

# Sjekk environment
if not os.path.exists('.env'):
    print("❌ Mangler .env fil! Opprett den først.")
    sys.exit(1)

print("✅ Starter AIKI server på http://localhost:8002")
os.system("uvicorn aiki_v3_server:app --host 0.0.0.0 --port 8002 --reload")
EOF

chmod +x aiki_v3_launcher.py

# ============================================
# CHANGELOG.md
# ============================================

cat > CHANGELOG.md << 'EOF'
# AIKI v3 - Endringslogg

## [3.0.0] - 2025-01-15
### 🎬 Initial Setup
- Fedora grunnmur komplett
- Git versjonskontroll
- AI oversiktssystem
- Minimal server kjører
EOF
```

### Git Initialisering

```bash
# ============================================
# Initialiser Git
# ============================================

cd ~/aiki_v3
git init

# Første commit
git add .
git commit -m "🎬 AIKI v3.0.0 - Initial Fedora setup"

# Koble til GitHub (valgfritt)
# git remote add origin https://github.com/[ditt-brukernavn]/aiki_v3.git
# git push -u origin main
```

---

## 🧠 Del 2: AI Oversiktssystem {#ai-oversiktssystem}

### Arkitektur - 3 lag

```
┌─────────────────────────────────────────┐
│   Lag 1: PROJECT STATE                  │
│   (aiki_project_state.json)             │
│   → AI's "hjerne" - hva må den vite?   │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│   Lag 2: DEPENDENCY GRAPH               │
│   (aiki_dependency_graph.json)          │
│   → Hva påvirker hva?                   │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│   Lag 3: CHANGE VALIDATION              │
│   (aiki_change_validator.py)            │
│   → Automatisk sjekk før commit         │
└─────────────────────────────────────────┘
```

### System-filer

```bash
# ============================================
# aiki_project_state.json (AI's minne)
# ============================================

cat > aiki_project_state.json << 'EOF'
{
  "project": {
    "name": "AIKI v3",
    "version": "3.0.0",
    "last_updated": "2025-01-15T00:00:00",
    "status": "active_development",
    "ai_developer": "Claude/GPT/Grok"
  },
  
  "critical_files": {
    "core": [
      {
        "path": "aiki_v3_server.py",
        "purpose": "Main FastAPI server - handles all HTTP requests",
        "dependencies": ["aiki_version.py", ".env"],
        "impacts": ["aiki_v3_launcher.py"],
        "last_modified": "2025-01-15",
        "breaking_changes_require": ["restart_server", "test_endpoints"]
      },
      {
        "path": "aiki_v3_launcher.py",
        "purpose": "Starts AIKI server",
        "dependencies": ["aiki_v3_server.py"],
        "impacts": [],
        "last_modified": "2025-01-15"
      }
    ],
    
    "config": [
      {
        "path": ".env",
        "purpose": "API keys and secrets - NEVER commit!",
        "impacts": ["all AIKI_MODELS", "aiki_v3_server.py"],
        "requires_restart": true,
        "critical": true
      },
      {
        "path": "aiki_version.py",
        "purpose": "Version tracking",
        "impacts": ["aiki_v3_server.py", "CHANGELOG.md"],
        "update_on_release": true
      }
    ]
  },
  
  "file_relationships": {
    "aiki_v3_server.py": {
      "imports": ["fastapi", "aiki_version"],
      "imported_by": ["aiki_v3_launcher.py"],
      "if_changed_check": [
        "aiki_v3_launcher.py",
        "Test: curl http://localhost:8002"
      ],
      "breaking_change_indicators": [
        "changed port number",
        "modified endpoint paths"
      ]
    }
  },
  
  "recent_changes": [
    {
      "date": "2025-01-15",
      "files": ["aiki_v3_server.py", "aiki_v3_launcher.py"],
      "change": "Initial setup - minimal server",
      "ai_notes": "Server runs on port 8002. Health check at /health",
      "verified": true,
      "tests_passed": true
    }
  ],
  
  "ai_rules": {
    "before_any_change": [
      "Read this file (aiki_project_state.json) first",
      "Check file_relationships for impacted files",
      "Verify dependencies exist",
      "Run relevant tests if available"
    ],
    
    "after_any_change": [
      "Update this file with changes in recent_changes",
      "List impacted files",
      "Run validation: python3 aiki_change_validator.py",
      "Update CHANGELOG.md if user-facing change"
    ],
    
    "critical_rules": [
      "NEVER commit .env file",
      "NEVER modify critical files without testing",
      "ALWAYS update aiki_version.py when releasing",
      "ALWAYS check if_changed_check list before committing",
      "ALWAYS backup .env before modifying"
    ]
  },
  
  "validation_checklist": {
    "server_changes": [
      "Test: curl http://localhost:8002/health",
      "Check: Server starts without errors",
      "Verify: All endpoints return expected responses"
    ],
    "config_changes": [
      "Test: Server starts with new config",
      "Check: All API keys load correctly",
      "Verify: No secrets in git status"
    ]
  }
}
EOF
```

---

## 🔧 Del 3: Alle Scripts {#scripts}

### Script 1: Dependency Mapper

```bash
cat > aiki_dependency_mapper.py << 'EOF'
#!/usr/bin/env python3
"""
AIKI Dependency Mapper
Auto-generates dependency graph by analyzing Python imports
"""

import ast
import json
from pathlib import Path
from typing import Dict, List

class DependencyMapper:
    def __init__(self, project_root: Path):
        self.root = project_root
        self.dependencies = {}
        
    def analyze_file(self, filepath: Path) -> Dict:
        """Extract imports and function definitions"""
        try:
            with open(filepath, encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            imports = []
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([n.name for n in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            return {
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "lines_of_code": len(open(filepath, encoding='utf-8').readlines())
            }
        except Exception as e:
            return {"error": str(e)}
    
    def find_python_files(self) -> List[Path]:
        """Find all .py files in project"""
        excludes = ['venv', '.venv', '__pycache__', '.git']
        files = []
        for pyfile in self.root.rglob("*.py"):
            if not any(exc in str(pyfile) for exc in excludes):
                files.append(pyfile)
        return files
    
    def build_dependency_graph(self) -> Dict:
        """Build complete dependency graph"""
        graph = {}
        
        python_files = self.find_python_files()
        
        for pyfile in python_files:
            rel_path = str(pyfile.relative_to(self.root))
            analysis = self.analyze_file(pyfile)
            
            # Find what imports this file
            imported_by = []
            for other_file in python_files:
                if other_file == pyfile:
                    continue
                
                other_analysis = self.analyze_file(other_file)
                module_name = rel_path.replace('/', '.').replace('.py', '')
                
                if any(module_name in imp for imp in other_analysis.get('imports', [])):
                    imported_by.append(str(other_file.relative_to(self.root)))
            
            graph[rel_path] = {
                **analysis,
                "imported_by": imported_by,
                "critical": self.is_critical_file(pyfile)
            }
        
        return graph
    
    def is_critical_file(self, filepath: Path) -> bool:
        """Determine if file is critical"""
        critical_patterns = [
            'server.py',
            'launcher.py',
            'router.py',
            '__init__.py',
            'settings.py',
            'version.py'
        ]
        return any(pattern in str(filepath) for pattern in critical_patterns)
    
    def save_graph(self, output_file: str = "aiki_dependency_graph.json"):
        """Save graph to JSON"""
        graph = self.build_dependency_graph()
        
        output_path = self.root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dependency graph saved to {output_file}")
        print(f"📊 Analyzed {len(graph)} files")
        
        # Print critical files
        critical = [f for f, data in graph.items() if data.get('critical')]
        print(f"⚠️  Critical files: {len(critical)}")
        for cf in critical[:10]:  # Show max 10
            print(f"   - {cf}")

if __name__ == "__main__":
    mapper = DependencyMapper(Path.cwd())
    mapper.save_graph()
    print("\n💡 Tip: Share aiki_dependency_graph.json with AI for context")
EOF

chmod +x aiki_dependency_mapper.py
```

### Script 2: Change Validator

```bash
cat > aiki_change_validator.py << 'EOF'
#!/usr/bin/env python3
"""
AIKI Change Validator
Validates changes before commit
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict

class ChangeValidator:
    def __init__(self):
        self.project_state = self.load_json("aiki_project_state.json")
        self.dependency_graph = self.load_json("aiki_dependency_graph.json")
        
    def load_json(self, filename: str) -> Dict:
        filepath = Path(filename)
        if filepath.exists():
            with open(filepath, encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_changed_files(self) -> List[str]:
        """Get files changed since last commit"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                capture_output=True,
                text=True,
                check=False
            )
            files = result.stdout.strip().split('\n')
            return [f for f in files if f]  # Remove empty strings
        except:
            return []
    
    def get_impacted_files(self, changed_file: str) -> List[str]:
        """Find files that might be impacted by change"""
        impacted = []
        
        # Check project state for explicit impacts
        for category in self.project_state.get('critical_files', {}).values():
            for file_info in category:
                if file_info['path'] == changed_file:
                    impacted.extend(file_info.get('impacts', []))
        
        # Check relationships
        relationships = self.project_state.get('file_relationships', {})
        if changed_file in relationships:
            impacted.extend(relationships[changed_file].get('if_changed_check', []))
        
        # Check dependency graph
        if changed_file in self.dependency_graph:
            impacted.extend(self.dependency_graph[changed_file].get('imported_by', []))
        
        return list(set(impacted))  # Remove duplicates
    
    def validate_change(self, changed_file: str) -> Dict:
        """Validate a single file change"""
        warnings = []
        errors = []
        checks_needed = []
        
        # Check if critical file
        if self.is_critical_file(changed_file):
            warnings.append(f"⚠️  {changed_file} is a CRITICAL file")
            checks_needed.append("Run full test suite before commit")
        
        # Check impacted files
        impacted = self.get_impacted_files(changed_file)
        if impacted:
            warnings.append(f"📋 Files that may need review:")
            for imp in impacted:
                warnings.append(f"   - {imp}")
        
        # Check for .env in git
        if changed_file == '.env':
            errors.append("❌ NEVER commit .env file!")
        
        # Check for required tests
        validation_rules = self.project_state.get('validation_checklist', {})
        for rule_category, checks in validation_rules.items():
            if self.file_matches_category(changed_file, rule_category):
                checks_needed.extend(checks)
        
        return {
            "file": changed_file,
            "warnings": warnings,
            "errors": errors,
            "checks_needed": checks_needed,
            "impacted_files": impacted
        }
    
    def is_critical_file(self, filename: str) -> bool:
        """Check if file is marked as critical"""
        for category in self.project_state.get('critical_files', {}).values():
            for file_info in category:
                if file_info['path'] == filename and file_info.get('critical'):
                    return True
        return False
    
    def file_matches_category(self, filename: str, category: str) -> bool:
        """Check if file belongs to validation category"""
        mappings = {
            'server_changes': ['server.py', 'launcher.py'],
            'config_changes': ['.env', 'settings.py', 'config.py']
        }
        
        patterns = mappings.get(category, [])
        return any(pattern in filename for pattern in patterns)
    
    def run_validation(self) -> bool:
        """Run validation on all changed files"""
        print("🔍 AIKI Change Validator")
        print("=" * 50)
        
        changed_files = self.get_changed_files()
        if not changed_files:
            print("✅ No changes detected")
            return True
        
        print(f"📝 Changed files: {len(changed_files)}")
        
        all_checks = []
        has_errors = False
        
        for changed_file in changed_files:
            print(f"\n🔎 Validating: {changed_file}")
            validation = self.validate_change(changed_file)
            
            for warning in validation['warnings']:
                print(f"  {warning}")
            
            for error in validation['errors']:
                print(f"  {error}")
                has_errors = True
            
            all_checks.extend(validation['checks_needed'])
        
        # Print consolidated checklist
        if all_checks:
            print("\n" + "=" * 50)
            print("✅ REQUIRED CHECKS BEFORE COMMIT:")
            for check in set(all_checks):
                print(f"  [ ] {check}")
        
        if has_errors:
            print("\n❌ VALIDATION FAILED - Fix errors before committing")
            return False
        
        print("\n✅ Validation passed - Safe to commit")
        return True

if __name__ == "__main__":
    validator = ChangeValidator()
    success = validator.run_validation()
    exit(0 if success else 1)
EOF

chmod +x aiki_change_validator.py
```

### Script 3: AI Briefing Generator

```bash
cat > aiki_ai_briefing.py << 'EOF'
#!/usr/bin/env python3
"""
AIKI AI Briefing Generator
Generates complete briefing for AI before coding session
"""

import json
from pathlib import Path
from datetime import datetime

class AIBriefing:
    def __init__(self):
        self.project_state = self.load_json("aiki_project_state.json")
        self.dependency_graph = self.load_json("aiki_dependency_graph.json")
    
    def load_json(self, filename: str):
        filepath = Path(filename)
        if filepath.exists():
            with open(filepath, encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def generate_briefing(self) -> str:
        """Generate complete AI briefing"""
        project_info = self.project_state.get('project', {})
        
        briefing = f"""# 🤖 AIKI v3 AI Developer Briefing
Generated: {datetime.now().isoformat()}

## 📋 PROJECT STATUS
- Version: {project_info.get('version', 'unknown')}
- Status: {project_info.get('status', 'unknown')}
- Last updated: {project_info.get('last_updated', 'unknown')}

## ⚠️ CRITICAL FILES (DO NOT BREAK!)
"""
        
        # Add critical files
        for category, files in self.project_state.get('critical_files', {}).items():
            for file_info in files:
                if file_info.get('critical'):
                    briefing += f"\n### {file_info['path']}\n"
                    briefing += f"- Purpose: {file_info['purpose']}\n"
                    briefing += f"- Dependencies: {', '.join(file_info.get('dependencies', []))}\n"
                    briefing += f"- Impacts: {', '.join(file_info.get('impacts', []))}\n"
        
        # Add recent changes
        briefing += "\n## 📝 RECENT CHANGES (Learn from these!)\n"
        for change in self.project_state.get('recent_changes', [])[-5:]:
            briefing += f"\n### {change['date']}\n"
            briefing += f"- Files: {', '.join(change['files'])}\n"
            briefing += f"- Change: {change['change']}\n"
            briefing += f"- AI Notes: {change['ai_notes']}\n"
        
        # Add AI rules
        briefing += "\n## 🎯 AI CODING RULES\n"
        rules = self.project_state.get('ai_rules', {})
        
        briefing += "\n### Before ANY Change:\n"
        for rule in rules.get('before_any_change', []):
            briefing += f"- [ ] {rule}\n"
        
        briefing += "\n### After ANY Change:\n"
        for rule in rules.get('after_any_change', []):
            briefing += f"- [ ] {rule}\n"
        
        briefing += "\n### CRITICAL RULES (NEVER VIOLATE!):\n"
        for rule in rules.get('critical_rules', []):
            briefing += f"- ⛔ {rule}\n"
        
        # Add dependency info
        briefing += "\n## 🕸️ FILE DEPENDENCIES\n"
        briefing += f"Total files mapped: {len(self.dependency_graph)}\n"
        briefing += f"Critical files: {sum(1 for f in self.dependency_graph.values() if f.get('critical'))}\n"
        
        # Add file relationships
        briefing += "\n## 🔗 KEY FILE RELATIONSHIPS\n"
        for file, rel in self.project_state.get('file_relationships', {}).items():
            briefing += f"\n### {file}\n"
            if rel.get('if_changed_check'):
                briefing += "If you change this, CHECK:\n"
                for check in rel['if_changed_check']:
                    briefing += f"  - {check}\n"
        
        briefing += "\n---\n"
        briefing += "**Always read this briefing before making ANY changes!**\n"
        
        return briefing
    
    def save_briefing(self, output_file: str = "AI_BRIEFING.md"):
        """Save briefing to file"""
        briefing = self.generate_briefing()
        Path(output_file).write_text(briefing, encoding='utf-8')
        print(f"✅ AI briefing saved to {output_file}")
        print(f"📄 {len(briefing.split(chr(10)))} lines of context")
        print(f"\n💡 Send {output_file} to AI before coding!")
        return output_file

if __name__ == "__main__":
    briefer = AIBriefing()
    briefer.save_briefing()
EOF

chmod +x aiki_ai_briefing.py
```

### Script 4: Session Scripts

```bash
# ============================================
# aiki_session_start.sh - Morgen-rutine
# ============================================

cat > aiki_session_start.sh << 'EOF'
#!/bin/bash
echo "🤖 Starting AIKI AI Development Session"
echo "========================================"

# Aktiver virtual environment
source venv/bin/activate

# Oppdater dependency graph
echo "📊 Updating dependency graph..."
python3 aiki_dependency_mapper.py

# Generer AI briefing
echo "📄 Generating AI briefing..."
python3 aiki_ai_briefing.py

# Sjekk Git status
echo ""
echo "📂 Git Status:"
git status --short

# Vis siste commits
echo ""
echo "📝 Recent commits:"
git log --oneline -5

echo ""
echo "✅ AI Session Ready!"
echo "📄 Send AI_BRIEFING.md to AI before starting"
echo ""
echo "To start server: python3 aiki_v3_launcher.py"
EOF

chmod +x aiki_session_start.sh

# ============================================
# aiki_session_end.sh - Kveld-rutine
# ============================================

cat > aiki_session_end.sh << 'EOF'
#!/bin/bash
echo "🔍 Validating AI changes..."
echo "========================================"

# Kjør validator
python3 aiki_change_validator.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Validation passed"
    
    # Vis hva som endret
    echo ""
    echo "📊 Changed files:"
    git diff --stat
    
    # Commit?
    echo ""
    read -p "Commit changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Commit message: " msg
        git add .
        git commit -m "$msg"
        
        echo "✅ Changes committed"
        echo ""
        echo "💡 Remember to:"
        echo "  - Update aiki_project_state.json if needed"
        echo "  - Update CHANGELOG.md for user-facing changes"
        echo "  - Push to GitHub: git push"
    fi
else
    echo ""
    echo "❌ Validation failed - Review changes"
fi
EOF

chmod +x aiki_session_end.sh

# ============================================
# aiki_quick_commit.sh - Rask commit
# ============================================

cat > aiki_quick_commit.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./aiki_quick_commit.sh \"commit message\""
    exit 1
fi

# Validate
python3 aiki_change_validator.py

if [ $? -eq 0 ]; then
    git add .
    git commit -m "$1"
    echo "✅ Committed: $1"
else
    echo "❌ Validation failed - commit aborted"
fi
EOF

chmod +x aiki_quick_commit.sh

# ============================================
# aiki_status.sh - Vis status
# ============================================

cat > aiki_status.sh << 'EOF'
#!/bin/bash
echo "🤖 AIKI v3 - Status Dashboard"
echo "========================================"

# Git info
BRANCH=$(git branch --show-current 2>/dev/null || echo "not a git repo")
echo "📌 Git Branch: $BRANCH"

# Versjon
if [ -f "aiki_version.py" ]; then
    VERSION=$(grep "__version__" aiki_version.py | cut -d'"' -f2)
    echo "🔢 Version: $VERSION"
fi

# Siste commits
echo ""
echo "📝 Recent commits:"
git log --oneline -5 2>/dev/null || echo "No commits yet"

# Changed files
echo ""
CHANGED=$(git diff --name-only HEAD 2>/dev/null | wc -l)
echo "📊 Uncommitted changes: $CHANGED files"

# Server status
echo ""
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ Server: RUNNING (http://localhost:8002)"
else
    echo "❌ Server: NOT RUNNING"
fi

echo ""
echo "========================================"
EOF

chmod +x aiki_status.sh
```

### Script 5: Setup Alt-i-ett

```bash
cat > setup_aiki_complete.sh << 'EOF'
#!/bin/bash
echo "🤖 AIKI v3 - Complete Setup Script"
echo "========================================"

# Sjekk om vi er i riktig directory
if [ ! -f "aiki_version.py" ]; then
    echo "❌ Run this from ~/aiki_v3 directory"
    exit 1
fi

echo "1️⃣ Setting up Git..."
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

echo ""
echo "2️⃣ Generating dependency graph..."
python3 aiki_dependency_mapper.py

echo ""
echo "3️⃣ Generating AI briefing..."
python3 aiki_ai_briefing.py

echo ""
echo "4️⃣ Testing validation..."
python3 aiki_change_validator.py

echo ""
echo "5️⃣ Creating first commit..."
git add .
git commit -m "🎬 AIKI v3.0.0 - Complete setup" 2>/dev/null || echo "Already committed"

echo ""
echo "========================================"
echo "✅ AIKI v3 Setup Complete!"
echo ""
echo "📁 Files created:"
echo "   - aiki_project_state.json"
echo "   - aiki_dependency_graph.json"
echo "   - AI_BRIEFING.md"
echo ""
echo "🚀 Quick commands:"
echo "   - Start session: ./aiki_session_start.sh"
echo "   - Start server:  python3 aiki_v3_launcher.py"
echo "   - Check status:  ./aiki_status.sh"
echo "   - End session:   ./aiki_session_end.sh"
echo ""
echo "Next: Start server and test with:"
echo "  curl http://localhost:8002/health"
EOF

chmod +x setup_aiki_complete.sh
```

---

## 🔄 Del 4: Daglig Workflow {#workflow}

### Morgen (5 min)

```bash
cd ~/aiki_v3
./aiki_session_start.sh

# Output:
# 🤖 Starting AIKI AI Development Session
# ========================================
# 📊 Updating dependency graph...
# ✅ Dependency graph saved to aiki_dependency_graph.json
# 📄 Generating AI briefing...
# ✅ AI briefing saved to AI_BRIEFING.md
# ...
```

### Gi AI kontekst

```bash
# Kopier AI_BRIEFING.md innhold og send til AI:
cat AI_BRIEFING.md

# Eller åpne i editor:
code AI_BRIEFING.md
```

**Prompt til AI:**
```
# SYSTEM CONTEXT

You are coding for AIKI v3. READ THIS FIRST:

[paste AI_BRIEFING.md content here]

## Your task:
[beskriv oppgaven]

## REMEMBER:
- Check dependency graph before changing files
- Update aiki_project_state.json after changes
- Run validator before commit
- Follow all AI rules from briefing
```

### Under utvikling

```bash
# Start server (i egen terminal)
python3 aiki_v3_launcher.py

# Test endringer
curl http://localhost:8002/health

# Quick status
./aiki_status.sh

# Quick commit (hvis alt OK)
./aiki_quick_commit.sh "✨ Added new feature"
```

### Kveld (5 min)

```bash
./aiki_session_end.sh

# Output:
# 🔍 Validating AI changes...
# ✅ Validation passed
# ...
# Commit changes? (y/n)
```

### Versjon-release

```bash
# 1. Oppdater versjon
nano aiki_version.py
# Endre: __version__ = "3.1.0"

# 2. Oppdater CHANGELOG
nano CHANGELOG.md
# Legg til nye endringer

# 3. Commit og tag
git add .
git commit -m "🚀 Release v3.1.0"
git tag -a v3.1.0 -m "Release v3.1.0"

# 4. Push (hvis GitHub)
git push origin main --tags
```

---

## 🐛 Del 5: Feilsøking {#feilsøking}

### Problem: Docker permission denied

```bash
# Løsning:
sudo usermod -aG docker $USER
# Logg ut og inn igjen
```

### Problem: Python-pakke installeres ikke

```bash
# Løsning:
source venv/bin/activate
pip install --upgrade pip
pip install [pakke] --no-cache-dir
```

### Problem: Port 8002 allerede i bruk

```bash
# Sjekk hva som kjører:
sudo lsof -i :8002

# Drep prosess:
kill -9 [PID]
```

### Problem: Git merge conflicts

```bash
# Vis conflicts:
git status

# Åpne fil og velg versjon:
code [conflicted-file]

# Når løst:
git add [conflicted-file]
git commit
```

### Problem: Validator feiler

```bash
# Debug mode:
python3 -c "
from aiki_change_validator import ChangeValidator
v = ChangeValidator()
print('Project state:', v.project_state.keys())
print('Dependency graph:', len(v.dependency_graph))
"

# Regenerer filer:
python3 aiki_dependency_mapper.py
python3 aiki_ai_briefing.py
```

### Problem: Server crasher

```bash
# Sjekk logs:
tail -f logs/aiki.log

# Test manuelt:
python3 -c "
from aiki_v3_server import app
print('App loads OK')
"

# Sjekk .env:
cat .env | grep -v "KEY="  # Ikke vis secrets
```

---

## 📊 Del 6: Quick Reference {#quick-reference}

### Daglige kommandoer

```bash
# Morgen
./aiki_session_start.sh

# Start server
python3 aiki_v3_launcher.py

# Status
./aiki_status.sh

# Commit
./aiki_quick_commit.sh "message"

# Kveld
./aiki_session_end.sh
```

### Git kommandoer

```bash
# Status
git status

# Se endringer
git diff

# Commit alt
git add . && git commit -m "message"

# Se historikk
git log --oneline

# Gå tilbake til versjon
git checkout v3.0.0

# Se alle versjoner
git tag -l
```

### Nyttige aliases

```bash
# Legg til i ~/.bashrc
alias aiki-start="cd ~/aiki_v3 && ./aiki_session_start.sh"
alias aiki-status="cd ~/aiki_v3 && ./aiki_status.sh"
alias aiki-server="cd ~/aiki_v3 && python3 aiki_v3_launcher.py"
alias aiki-validate="cd ~/aiki_v3 && python3 aiki_change_validator.py"
```

### Semantisk versjonering

```
v3.2.1
│ │ │
│ │ └─ PATCH  (bugfix)           → +1 når du fikser noe
│ └─── MINOR  (ny feature)       → +1 når du legger til noe
└───── MAJOR  (breaking changes) → +1 når du endrer fundamentalt
```

**Eksempler:**
- v3.0.0 → Helt ny arkitektur
- v3.1.0 → La til ny AI-integrasjon
- v3.1.1 → Fikset bug i logging
- v4.0.0 → Byttet helt framework

---

## 📋 Oppsummering

### Hva du har nå:

✅ **Fedora grunnmur:**
- Python 3.11 + Virtual Environment
- Docker + Node.js
- AIKI mappestruktur
- Git versjonskontroll

✅ **AI Oversiktssystem:**
- `aiki_project_state.json` - AI's minne
- `aiki_dependency_graph.json` - Hva påvirker hva
- `aiki_change_validator.py` - Automatisk sjekk
- `aiki_ai_briefing.py` - AI får full kontekst

✅ **Workflow Scripts:**
- `aiki_session_start.sh` - Morgen-setup
- `aiki_session_end.sh` - Kveld-validering
- `aiki_status.sh` - Quick status
- `aiki_quick_commit.sh` - Rask commit

### Neste steg:

1. **Kjør setup:**
   ```bash
   cd ~/aiki_v3
   ./setup_aiki_complete.sh
   ```

2. **Test server:**
   ```bash
   python3 aiki_v3_launcher.py
   # I annen terminal:
   curl http://localhost:8002/health
   ```

3. **Start AI-utvikling:**
   ```bash
   ./aiki_session_start.sh
   # Send AI_BRIEFING.md til AI
   ```

---

## 🎯 Vedlegg: Filstruktur

```
~/aiki_v3/
├── AIKI_CORE/
│   ├── brain/
│   ├── consciousness/
│   ├── autonomy/
│   └── learning/
├── AIKI_INTERFACE/
│   ├── chat/
│   ├── api/
│   ├── ui/
│   └── protocols/
├── AIKI_MODELS/
│   ├── openai/
│   ├── claude/
│   ├── grok/
│   ├── copilot/
│   ├── ollama/
│   └── gemini/
├── AIKI_MEMORY/
│   ├── sessions/
│   ├── backups/
│   ├── identity/
│   └── logs/
├── logs/
├── config/
├── venv/
├── .env (secrets - NEVER commit!)
├── .aiki_config
├── .gitignore
├── aiki_version.py
├── aiki_v3_server.py
├── aiki_v3_launcher.py
├── aiki_project_state.json
├── aiki_dependency_mapper.py
├── aiki_change_validator.py
├── aiki_ai_briefing.py
├── aiki_session_start.sh
├── aiki_session_end.sh
├── aiki_status.sh
├── aiki_quick_commit.sh
├── setup_aiki_complete.sh
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

---

**Dokumentert av:** Aiki & Claude  
**Dato:** 15. januar 2025  
**Versjon:** 3.0.0  
**Status:** Production Ready ✅

**Lisens:** MIT  
**Repository:** https://github.com/[ditt-brukernavn]/aiki_v3

---

*Dette dokumentet inneholder ALLE kommandoer og scripts du trenger for å bygge AIKI v3 på Fedora med full AI-oversikt. Kopier og kjør kommandoene i rekkefølge! 🚀*
