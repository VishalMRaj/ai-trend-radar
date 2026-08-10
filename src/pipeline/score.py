import numpy as np
from typing import Dict, Any, List
import yaml
from src.connectors.base import Item
from src.pipeline.dedup import cosine_similarity

def run_score(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score items based on relevance to the owner profile keywords using embeddings.
    """
    items: List[Item] = state.get("items", [])
    embedder = state.get("embedder")
    embeddings_store = state.get("embeddings_store", {})
    profile_path = state.get("profile_path", "config/profile.yaml")

    if not items or not embedder:
        return {"items": items}

    try:
        with open(profile_path, 'r') as f:
            profile = yaml.safe_load(f)
            keywords = profile.get("keywords", [])
    except Exception as e:
        print(f"Error loading profile from {profile_path}: {e}")
        keywords = []

    if not keywords:
        # Give a default score if no profile
        for item in items:
            item.score = 0.5
        return {"items": items}

    # Create an embedding for the profile
    profile_text = " ".join(keywords)
    try:
        profile_embedding = np.array(embedder.embed_query(profile_text))
    except Exception as e:
        print(f"Error embedding profile: {e}")
        for item in items:
            item.score = 0.5
        return {"items": items}

    for item in items:
        item_embedding = embeddings_store.get(item.url)
        if item_embedding is None:
            try:
                text_to_embed = f"{item.title} {item.raw_summary}"
                item_embedding = np.array(embedder.embed_query(text_to_embed))
                embeddings_store[item.url] = item_embedding
            except Exception:
                pass

        if item_embedding is not None:
            score = cosine_similarity(profile_embedding, item_embedding)
            # Normalize score slightly to look better (0-1)
            item.score = max(0.0, min(1.0, score))
        else:
            item.score = 0.5

    return {"items": items}
