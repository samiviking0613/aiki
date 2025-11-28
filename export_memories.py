#!/usr/bin/env python3
"""
Eksporterer alle minner fra mem0/Qdrant til JSON-format for backup.
"""
import json
import os
from datetime import datetime
from qdrant_client import QdrantClient

# Koble til Qdrant direkte (read-only)
client = QdrantClient(path="/home/jovnna/aiki/shared_qdrant")

# Hent collection info
collection_name = "mem0_memories"

try:
    collection_info = client.get_collection(collection_name)
    print(f"Collection: {collection_name}")
    print(f"Vektorer: {collection_info.points_count}")
    print(f"Status: {collection_info.status}")
    print()

    # Hent alle punkter (minner)
    all_points = []
    offset = None
    batch_size = 100

    while True:
        # Scroll gjennom alle punkter
        result = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=False  # Ikke inkluder vektorer for å spare plass
        )

        points, next_offset = result

        if not points:
            break

        for point in points:
            all_points.append({
                "id": str(point.id),
                "payload": point.payload
            })

        if next_offset is None:
            break

        offset = next_offset
        print(f"Hentet {len(all_points)} minner...", end='\r')

    print(f"\nTotalt {len(all_points)} minner hentet!")

    # Lagre til JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/run/media/jovnna/CEVAULT2TB/AIKI_MINNER/mem0_memories_{timestamp}.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "exported_at": datetime.now().isoformat(),
            "collection": collection_name,
            "total_memories": len(all_points),
            "memories": all_points
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Minner eksportert til: {output_path}")
    print(f"📊 Filstørrelse: {os.path.getsize(output_path) / 1024:.1f} KB")

except Exception as e:
    print(f"❌ Feil: {e}")
    import traceback
    traceback.print_exc()
