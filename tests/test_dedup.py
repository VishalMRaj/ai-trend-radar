import numpy as np
from src.pipeline.dedup import cosine_similarity, run_dedup
from src.connectors.base import Item
from langchain_core.embeddings import FakeEmbeddings

def test_cosine_similarity():
    v1 = np.array([1, 0])
    v2 = np.array([1, 0])
    v3 = np.array([0, 1])

    assert np.isclose(cosine_similarity(v1, v2), 1.0)
    assert np.isclose(cosine_similarity(v1, v3), 0.0)

def test_run_dedup():
    item1 = Item(title="Test", url="http://1", source="Src", published_date="date", raw_summary="sum1")
    item2 = Item(title="Test", url="http://2", source="Src", published_date="date", raw_summary="sum1")

    embedder = FakeEmbeddings(size=2)
    state = {
        "raw_items": [item1, item2],
        "recent_items": [],
        "embeddings_store": {},
        "embedder": embedder
    }

    result = run_dedup(state)

    # Check if duplicate is removed - FakeEmbedder sometimes returns slightly different items based on state,
    # so we mock a specific deterministic embedding behavior if needed, or we just test the similarity logic.
    # We can also mock embedder.embed_query to be purely deterministic based on text

    # Actually, langchain FakeEmbeddings might give random numbers. Let's make a truly deterministic one
    class DeterministicEmbeddings:
        def embed_query(self, text):
            # Same text = same float list
            import hashlib
            h = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
            np.random.seed(h % (2**32))
            return np.random.rand(2).tolist()

    state["embedder"] = DeterministicEmbeddings()
    result = run_dedup(state)

    # The deterministic embedder returns the exact same embedding for the same text
    # Since title and summary are identical, it should dedup item2
    assert len(result["items"]) == 1
    assert result["items"][0].url == "http://1"
    # item2 URL should be added to source links
    assert "http://2" in result["items"][0].source_links
