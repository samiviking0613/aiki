# ⚠️ DEPRECATED - DO NOT USE

**Date:** 18. November 2025
**Status:** DEPRECATED

## This directory is NO LONGER USED

**WHY:**
This was embedded Qdrant mode (path-based), which has **single-writer limitation**.

With multiple processes (health_daemon, memory_daemon, MCP server, Claude Code),
we got "readonly database" errors.

## ✅ CURRENT SETUP:

**USE THIS INSTEAD:**
- Qdrant Server: `http://localhost:6333`
- Docker container: `aiki_qdrant`
- Data location: `/var/lib/docker/volumes/aiki_v3_docker_qdrant_storage/_data`

**All data has been migrated to server.**

## Configuration:

```python
# ✅ CORRECT (server mode):
config = {
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'url': 'http://localhost:6333',
            'collection_name': 'mem0_memories'
        }
    }
}

# ❌ OLD (embedded mode - DO NOT USE):
config = {
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'path': '/home/jovnna/aiki/shared_qdrant',  # DEPRECATED!
        }
    }
}
```

## Files Updated:
- `/home/jovnna/aiki/natural_logger.py` ✅
- `/home/jovnna/aiki/memory_daemon.py` ✅
- `/home/jovnna/aiki/system_health_daemon.py` ✅
- `/home/jovnna/aiki/mcp-mem0/src/utils.py` ✅

## If Context Loss Happens:

**Where is the data?**
1. Qdrant Server (primary): `http://localhost:6333`
2. Check running: `docker ps | grep qdrant`
3. Access UI: http://localhost:6333/dashboard
4. Collections: `mem0_memories` (690 points), `mem0migrations` (2 points)

---

**This directory can be deleted after confirming server works.**
