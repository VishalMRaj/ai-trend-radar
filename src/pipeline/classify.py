from typing import Dict, Any, List
from src.connectors.base import Item

def run_classify(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify items into categories: architecture-pattern, tooling, research, product-launch.
    """
    items: List[Item] = state.get("items", [])
    llm = state.get("llm")

    if not items or not llm:
        return {"items": items}

    categories = ["architecture-pattern", "tooling", "research", "product-launch"]
    prompt_template = """
    Classify the following text into exactly ONE of these categories: {categories}.
    Return ONLY the category name, nothing else.

    Title: {title}
    Summary: {summary}
    """

    for item in items:
        if item.category:
            continue

        try:
            prompt = prompt_template.format(
                categories=", ".join(categories),
                title=item.title,
                summary=item.raw_summary
            )
            response = llm.invoke(prompt)
            # Basic parsing
            if hasattr(response, 'content'):
                result = response.content.strip().lower()
            else:
                result = str(response).strip().lower()

            # Find closest match
            matched_category = None
            for cat in categories:
                if cat in result:
                    matched_category = cat
                    break

            if matched_category:
                item.category = matched_category
            else:
                item.category = "research" # default fallback

        except Exception as e:
            print(f"Error classifying item {item.url}: {e}")
            item.category = "research"

    return {"items": items}
