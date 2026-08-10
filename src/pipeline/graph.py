import os
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

from src.connectors.base import Item
from src.pipeline.dedup import run_dedup
from src.pipeline.classify import run_classify
from src.pipeline.score import run_score
from src.pipeline.summarize import run_summarize

class GraphState(TypedDict):
    raw_items: List[Item]
    recent_items: List[Item]
    items: List[Item]
    embeddings_store: Dict[str, Any]
    llm: Any
    embedder: Any
    profile_path: str


def create_pipeline() -> StateGraph:
    workflow = StateGraph(GraphState)

    workflow.add_node("dedup", run_dedup)
    workflow.add_node("classify", run_classify)
    workflow.add_node("score", run_score)
    workflow.add_node("summarize", run_summarize)

    workflow.add_edge(START, "dedup")
    workflow.add_edge("dedup", "classify")
    workflow.add_edge("classify", "score")
    workflow.add_edge("score", "summarize")
    workflow.add_edge("summarize", END)

    return workflow.compile()

def process_items(
    raw_items: List[Item],
    recent_items: List[Item],
    llm: Any,
    embedder: Any,
    profile_path: str = "config/profile.yaml"
) -> List[Item]:
    app = create_pipeline()

    initial_state = {
        "raw_items": raw_items,
        "recent_items": recent_items,
        "items": [],
        "embeddings_store": {},
        "llm": llm,
        "embedder": embedder,
        "profile_path": profile_path
    }

    result = app.invoke(initial_state)
    return result.get("items", [])
