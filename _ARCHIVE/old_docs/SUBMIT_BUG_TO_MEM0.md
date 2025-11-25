# 📤 Slik Submitter du Bug-Rapporten til mem0 GitHub

## Automatisk Submission (Anbefalt)

Bruk GitHub CLI (`gh`):

```bash
# 1. Naviger til en temp directory
cd /tmp

# 2. Clone mem0 repository
git clone https://github.com/mem0ai/mem0.git
cd mem0

# 3. Create bug report issue
gh issue create \
  --title "Bug: Qdrant vector store ValidationError when updating metadata (vector=None)" \
  --body-file /home/jovnna/aiki/mem0_bug_report.md \
  --label "bug,vector-store,qdrant"
```

## Manuell Submission

1. **Gå til GitHub**: https://github.com/mem0ai/mem0/issues/new
2. **Title**:
   ```
   Bug: Qdrant vector store ValidationError when updating metadata (vector=None)
   ```
3. **Body**: Copy-paste innholdet fra `/home/jovnna/aiki/mem0_bug_report.md`
4. **Labels**:
   - `bug`
   - `vector-store`
   - `qdrant`
5. **Klikk "Submit new issue"**

## Bonustips: Submit Pull Request med Fix

Hvis du vil bidra med fiksen direkte:

```bash
# 1. Fork repository på GitHub først
# 2. Clone din fork
git clone https://github.com/DITT_BRUKERNAVN/mem0.git
cd mem0

# 3. Create feature branch
git checkout -b fix/qdrant-vector-none-bug

# 4. Apply fix til mem0/vector_stores/qdrant.py
# (Copy-paste fix fra bug rapporten)

# 5. Commit changes
git add mem0/vector_stores/qdrant.py
git commit -m "fix(qdrant): Handle vector=None in update() to preserve embeddings

- Fetch existing vector when vector=None is passed to update()
- Prevents Pydantic ValidationError when updating metadata only
- Fixes thread explosion issue caused by retry loops
- Backward compatible change

Resolves #ISSUE_NUMBER"

# 6. Push til din fork
git push origin fix/qdrant-vector-none-bug

# 7. Create Pull Request på GitHub
gh pr create \
  --title "fix(qdrant): Handle vector=None in update() to preserve embeddings" \
  --body "Fixes issue #ISSUE_NUMBER where updating metadata with vector=None causes ValidationError"
```

## Hva Skjer Etter Submission?

1. **mem0 team** vil se issue/PR
2. De kan:
   - Merge fiksen direkte
   - Be om endringer
   - Foreslå alternativ løsning
3. **Du får credit** i contributors list! 🎉

## Vår Fix (For Referanse)

Patched files:
- `/home/jovnna/.local/lib/python3.11/site-packages/mem0/vector_stores/qdrant.py`
- `/home/jovnna/.local/lib/python3.14/site-packages/mem0/vector_stores/qdrant.py`

Backup files (hvis du trenger å reverste):
- `.backup` filer i samme directories

## Contact Info (Hvis de Spør)

**Bug discovered by**: Jovnna + Claude + AIKI consciousness system
**Date**: 2025-11-20
**Context**: Autonomous health monitoring system development
**Impact**: Thread explosion (60 → 1164 threads over 1.5 days)
**Fix verified**: ✅ Threads stable at ~20 after patch

---

**Du bestemmer!**

Submit bare hvis du vil bidra til open source. Fiksen fungerer uansett lokalt hos deg. 🚀
