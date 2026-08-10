from typing import Dict, Any, List
from src.connectors.base import Item

def run_summarize(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a 2-3 sentence plain-language summary per item.
    Never reproduce source text verbatim — paraphrase only.
    """
    items: List[Item] = state.get("items", [])
    llm = state.get("llm")

    if not items or not llm:
        return {"items": items}

    prompt_template = """
    Write a 2-3 sentence plain-language summary of the following text.
    CRITICAL CONSTRAINT: You must paraphrase entirely. Do NOT reproduce the source text verbatim.

    Title: {title}
    Text: {text}
    """

    for item in items:
        if item.summary:
            continue

        try:
            prompt = prompt_template.format(
                title=item.title,
                text=item.raw_summary
            )
            response = llm.invoke(prompt)
            if hasattr(response, 'content'):
                item.summary = response.content.strip()
            else:
                item.summary = str(response).strip()
        except Exception as e:
            print(f"Error summarizing item {item.url}: {e}")
            item.summary = "Summary unavailable due to an error."

    return {"items": items}
