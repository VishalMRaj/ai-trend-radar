import numpy as np
from typing import List, Dict, Any
from src.connectors.base import Item

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def run_dedup(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deduplicate items based on embedding similarity.
    Since we are avoiding complex external vector DBs for v1, we do this in-memory.
    """
    items: List[Item] = state.get("raw_items", [])
    recent_items: List[Item] = state.get("recent_items", [])
    embeddings_store: Dict[str, np.ndarray] = state.get("embeddings_store", {})
    embedder = state.get("embedder")

    if not items or not embedder:
        return {"items": items}

    similarity_threshold = 0.85
    deduped_items = []

    # We will combine recent_items and deduped_items for comparison
    seen_items = list(recent_items)

    for item in items:
        # Generate embedding for the new item
        text_to_embed = f"{item.title} {item.raw_summary}"

        try:
            item_embedding = embedder.embed_query(text_to_embed)
            embeddings_store[item.url] = np.array(item_embedding)

            is_duplicate = False

            for seen_item in seen_items:
                seen_emb = embeddings_store.get(seen_item.url)
                if seen_emb is None:
                    # Try to embed on the fly if not in store (e.g. from previous runs)
                    try:
                        seen_text = f"{seen_item.title} {seen_item.raw_summary}"
                        seen_emb = np.array(embedder.embed_query(seen_text))
                        embeddings_store[seen_item.url] = seen_emb
                    except Exception:
                        continue

                if seen_emb is not None:
                    sim = cosine_similarity(np.array(item_embedding), seen_emb)
                    if sim > similarity_threshold:
                        is_duplicate = True
                        # Merge source links if it's a new duplicate
                        if item.url not in seen_item.source_links:
                            seen_item.source_links.append(item.url)
                            # Ensure the updated seen_item is returned so it gets saved
                            if seen_item not in deduped_items:
                                deduped_items.append(seen_item)
                        break

            if not is_duplicate:
                deduped_items.append(item)
                seen_items.append(item)

        except Exception as e:
            print(f"Error embedding item {item.url}: {e}")
            # Fallback: keep the item if embedding fails
            deduped_items.append(item)

    return {"items": deduped_items, "embeddings_store": embeddings_store}
