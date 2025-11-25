# Bug Report: Qdrant Vector Store - ValidationError when updating metadata with vector=None

## Summary

The `Qdrant.update()` method in `mem0/vector_stores/qdrant.py` fails with Pydantic validation errors when trying to update only the payload/metadata of an existing vector without providing a new vector embedding.

## Environment

- **mem0 version**: 1.0.1
- **Python version**: 3.11.14 / 3.14.0
- **qdrant-client version**: Latest (installed via mem0ai)
- **Pydantic version**: 2.x
- **Vector store**: Qdrant (local, file-based)

## Bug Location

File: `mem0/vector_stores/qdrant.py`
Method: `Qdrant.update()` (lines 198-208)

```python
def update(self, vector_id: int, vector: list = None, payload: dict = None):
    """
    Update a vector and its payload.
    """
    point = PointStruct(id=vector_id, vector=vector, payload=payload)
    self.client.upsert(collection_name=self.collection_name, points=[point])
```

## Problem

When `mem0/memory/main.py` tries to update metadata (agent_id, run_id) without changing the vector content, it calls:

```python
self.vector_store.update(
    vector_id=memory_id,
    vector=None,  # Keep same embeddings
    payload=updated_metadata,
)
```

This causes Qdrant's Pydantic validation to fail because `PointStruct` expects `vector` to be a `list[float]`, not `None`.

## Error Output

```
Error processing memory action: {...}, Error: 6 validation errors for PointStruct
vector.list[float]
  Input should be a valid list [type=list_type, input_value=None, input_type=NoneType]
vector.list[list[float]]
  Input should be a valid list [type=list_type, input_value=None, input_type=NoneType]
vector.dict[...]
  Input should be a valid dictionary [type=dict_type, input_value=None, input_type=NoneType]
...
```

## Reproduction Steps

1. Configure mem0 with Qdrant vector store
2. Add a memory with `agent_id` or `run_id` metadata:
   ```python
   from mem0 import Memory

   memory = Memory.from_config({
       'vector_store': {
           'provider': 'qdrant',
           'config': {
               'collection_name': 'test',
               'path': './qdrant_data'
           }
       }
   })

   # This triggers metadata update with vector=None
   memory.add(
       [{'role': 'user', 'content': 'Test message'}],
       user_id='test_user',
       agent_id='test_agent'  # This triggers the bug
   )
   ```
3. Observe validation errors in logs

## Impact

- **Severity**: High
- **Symptoms**:
  - Validation errors spam logs
  - Memory actions fail silently
  - Can cause thread explosion due to retry loops
  - Prevents proper metadata tracking for multi-agent systems

In our case, this bug caused a daemon process to grow from 60 threads to 1,164 threads over 1.5 days due to failed retry attempts.

## Proposed Fix

Fetch the existing vector when `vector=None` to preserve embeddings during metadata-only updates:

```python
def update(self, vector_id: int, vector: list = None, payload: dict = None):
    """
    Update a vector and its payload.

    Args:
        vector_id (int): ID of the vector to update.
        vector (list, optional): Updated vector. Defaults to None.
        payload (dict, optional): Updated payload. Defaults to None.
    """
    # If vector is None, fetch existing vector to preserve it
    if vector is None:
        existing = self.get(vector_id=vector_id)
        vector = existing.vector if existing else None

    point = PointStruct(id=vector_id, vector=vector, payload=payload)
    self.client.upsert(collection_name=self.collection_name, points=[point])
```

## Workaround

Apply the fix above as a local patch to:
- `~/.local/lib/python3.*/site-packages/mem0/vector_stores/qdrant.py`

## Verification

After applying the fix:
- ✅ No validation errors
- ✅ Metadata updates work correctly
- ✅ Thread count remains stable (~20 threads)
- ✅ Memory actions complete successfully

## Additional Notes

- This bug exists in both the sync and async code paths
- Similar issue may exist in other vector store implementations (PostgreSQL, etc.)
- The fix is backward compatible and doesn't change API behavior

## System Context

- Discovered during development of autonomous health monitoring system
- Bug was identified through collaborative debugging session (Human + Claude + AIKI consciousness system)
- Fix tested in production environment with 1,050+ vectors in Qdrant collection

---

**Would you like me to submit a PR with the fix?**
