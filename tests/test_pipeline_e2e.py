from src.connectors.base import Item
from src.pipeline.graph import process_items
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.language_models.fake import FakeListLLM
import yaml
import os

def test_pipeline_e2e(tmpdir):
    # Setup dummy profile
    profile_path = os.path.join(tmpdir, "profile.yaml")
    with open(profile_path, 'w') as f:
        yaml.dump({"keywords": ["ai", "agents"]}, f)

    item1 = Item(title="AI Agent", url="http://1", source="Src", published_date="date", raw_summary="sum")

    llm = FakeListLLM(responses=["architecture-pattern", "This is a summary."])
    embedder = FakeEmbeddings(size=2)

    processed = process_items(
        raw_items=[item1],
        recent_items=[],
        llm=llm,
        embedder=embedder,
        profile_path=profile_path
    )

    assert len(processed) == 1
    assert processed[0].category == "architecture-pattern"
    assert processed[0].summary == "This is a summary."
    assert processed[0].score is not None
