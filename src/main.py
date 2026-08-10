import os
import yaml
from typing import List
from dotenv import load_dotenv

from langchain_core.embeddings import FakeEmbeddings
from langchain_core.language_models.fake import FakeListLLM

try:
    from langchain_google_vertexai import VertexAI, VertexAIEmbeddings
except ImportError:
    pass

from src.connectors.arxiv import ArxivConnector
from src.connectors.rss import RSSConnector
from src.connectors.github_trending import GitHubTrendingConnector
from src.storage.sqlite_store import SQLiteStore
from src.pipeline.graph import process_items
from src.delivery.digest_html import generate_digest

def load_config(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_llm_and_embedder():
    # Attempt to use Vertex AI, fallback to a fake one for testing if not configured
    try:
        # VertexAI looks for GOOGLE_APPLICATION_CREDENTIALS or default credentials
        llm = VertexAI(model_name="gemini-1.5-flash", temperature=0)
        embedder = VertexAIEmbeddings(model_name="textembedding-gecko@003")

        # Test initialization
        llm.invoke("test")
        return llm, embedder
    except Exception as e:
        print(f"Vertex AI not configured or error initializing: {e}")
        print("Falling back to Fake LLM and Embedder for demonstration.")
        llm = FakeListLLM(responses=["Fake classification/summary response."] * 100)
        embedder = FakeEmbeddings(size=768)
        return llm, embedder

def main():
    print("Starting AI Trend Radar Pipeline...")

    # Load env vars
    load_dotenv()

    # 1. Load Configurations
    sources_config = load_config("config/sources.yaml")

    # 2. Initialize Components
    store = SQLiteStore("items.db")
    llm, embedder = get_llm_and_embedder()

    # 3. Fetch from Connectors
    connectors = []
    if "arxiv" in sources_config:
        connectors.append(ArxivConnector(sources_config["arxiv"]))
    if "rss" in sources_config:
        connectors.append(RSSConnector(sources_config["rss"]))
    if "github_trending" in sources_config:
        connectors.append(GitHubTrendingConnector(sources_config["github_trending"]))

    raw_items = []
    for connector in connectors:
        print(f"Fetching from {connector.__class__.__name__}...")
        try:
            items = connector.fetch()
            raw_items.extend(items)
            print(f"Fetched {len(items)} items.")
        except Exception as e:
            print(f"Error fetching from {connector.__class__.__name__}: {e}")

    print(f"Total raw items fetched: {len(raw_items)}")

    if not raw_items:
        print("No items fetched. Exiting.")
        return

    # 4. Get recent items for deduplication context
    recent_items = store.get_recent_items(limit=200)

    # 5. Run Processing Pipeline (LangGraph)
    print("Starting processing pipeline...")
    processed_items = process_items(
        raw_items=raw_items,
        recent_items=recent_items,
        llm=llm,
        embedder=embedder,
        profile_path="config/profile.yaml"
    )
    print(f"Pipeline finished. Items remaining after deduplication: {len(processed_items)}")

    if not processed_items:
        print("No new items after deduplication. Exiting.")
        return

    # 6. Save Processed Items
    print("Saving items to database...")
    store.save_items(processed_items)

    # 7. Generate Digest
    print("Generating HTML digest...")
    digest_path = generate_digest(processed_items, "output")
    print(f"Digest successfully generated at: {digest_path}")

if __name__ == "__main__":
    main()
