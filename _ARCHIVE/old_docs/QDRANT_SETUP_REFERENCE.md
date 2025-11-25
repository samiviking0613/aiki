# 🎯 AIKI QDRANT SETUP - QUICK REFERENCE

**Last Updated:** 18. November 2025
**Status:** PRODUCTION (Server Mode)

---

## ✅ CURRENT SETUP (USE THIS)

### Qdrant Server (Multi-Writer)
```
URL:        http://localhost:6333
Container:  aiki_qdrant (Docker)
Data:       /var/lib/docker/volumes/aiki_v3_docker_qdrant_storage/_data
UI:         http://localhost:6333/dashboard
Status:     docker ps | grep qdrant
```

### Collections:
- `mem0_memories` - **690 points** (all AIKI memories)
- `mem0migrations` - 2 points (migration tracking)

### Why Server Mode?
**Problem:** Multiple processes writing to embedded Qdrant = "readonly database" errors
- health_daemon
- memory_daemon
- MCP mem0 server
- Claude Code

**Solution:** Qdrant server handles concurrent writes natively (MVCC)

---

## 📝 CONFIGURATION (Copy-Paste Ready)

### Python Config:
```python
config = {
    'llm': {
        'provider': 'openai',
        'config': {'model': 'openai/gpt-4o-mini'}
    },
    'embedder': {
        'provider': 'openai',
        'config': {
            'model': 'text-embedding-3-small',
            'embedding_dims': 1536
        }
    },
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'url': 'http://localhost:6333',  # ✅ SERVER MODE
            'collection_name': 'mem0_memories',
            'embedding_model_dims': 1536
        }
    }
}
```

### MCP Server (.mcp.json):
```json
{
  "mcpServers": {
    "mem0": {
      "env": {
        "QDRANT_URL": "http://localhost:6333"
      }
    }
  }
}
```

---

## 🗂️ FILES UPDATED (2025-11-18)

### ✅ Configured for Server Mode:
1. `/home/jovnna/aiki/natural_logger.py` (line 57)
2. `/home/jovnna/aiki/memory_daemon.py` (line 219)
3. `/home/jovnna/aiki/system_health_daemon.py` (line 328)
4. `/home/jovnna/aiki/mcp-mem0/src/utils.py` (uses QDRANT_URL env var)

**Check:** All use `'url': 'http://localhost:6333'` NOT `'path': ...`

---

## ❌ DEPRECATED (DO NOT USE)

### Embedded Qdrant (Path-Based)
```
Directory:  /home/jovnna/aiki/shared_qdrant_DEPRECATED_USE_SERVER_6333/
Status:     DEPRECATED (renamed 2025-11-18)
Data:       0 points (empty - all migrated to server)
Reason:     Single-writer limitation = readonly errors
```

### Old Config (DON'T USE):
```python
# ❌ WRONG - Causes readonly errors!
config = {
    'vector_store': {
        'config': {
            'path': '/home/jovnna/aiki/shared_qdrant'  # DEPRECATED
        }
    }
}
```

---

## 🔧 TROUBLESHOOTING

### Check if Qdrant Server is Running:
```bash
docker ps | grep qdrant
# Should show: aiki_qdrant (Up X hours)

curl http://localhost:6333/health
# Should return: {"title":"qdrant - vector search engine","version":"..."}
```

### Check Collections:
```bash
curl http://localhost:6333/collections
# Should show: mem0_memories, mem0migrations
```

### View Data:
```python
from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")

# Check collection info
info = client.get_collection("mem0_memories")
print(f"Points: {info.points_count}")

# Search memories
results = client.scroll("mem0_memories", limit=5)
print(results)
```

### Restart Qdrant Container:
```bash
docker restart aiki_qdrant
# Wait 5 seconds for startup
sleep 5
curl http://localhost:6333/health
```

### Check Daemon Logs for Errors:
```bash
journalctl --user -u aiki-health-daemon -u aiki-memory-daemon --since "5 min ago" | grep -i error
```

---

## 🧠 IF CONTEXT IS LOST

**Signs of wrong config:**
- Error: "attempt to write a readonly database"
- Error: "Database is locked"
- Multiple processes trying to write

**Fix:**
1. Check file headers - should mention server mode (line 7-12)
2. Check config uses `'url'` not `'path'`
3. Verify Qdrant container is running: `docker ps | grep qdrant`
4. Restart daemons: `systemctl --user restart aiki-{memory,health}-daemon`

**Data Location:**
- ✅ Primary: Qdrant server (http://localhost:6333)
- ❌ NOT in: shared_qdrant_DEPRECATED_...

---

## 📊 MONITORING

### Dashboard:
```
http://localhost:6333/dashboard
```

### Check Point Count:
```bash
curl -s http://localhost:6333/collections/mem0_memories | python3 -m json.tool | grep points_count
```

### Watch Live Logs:
```bash
# Health daemon
journalctl --user -u aiki-health-daemon -f

# Memory daemon
journalctl --user -u aiki-memory-daemon -f

# Docker logs
docker logs -f aiki_qdrant
```

---

## 🎯 SUMMARY

**DO:**
✅ Use `'url': 'http://localhost:6333'`
✅ Keep aiki_qdrant Docker container running
✅ Check http://localhost:6333/dashboard to verify data

**DON'T:**
❌ Use `'path': ...` (embedded mode)
❌ Try to access shared_qdrant_DEPRECATED_...
❌ Assume embedded mode works with multiple processes

---

**Questions? Check file headers - they have inline warnings pointing to this guide.**
