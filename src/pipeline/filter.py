import os
from typing import Dict, Any, List
import yaml
from pydantic import BaseModel, Field
import jev

from src.connectors.base import Item

class ReadingDecision(BaseModel):
    worth_reading: bool = Field(description="Whether this document is worth reading based on the profile keywords")

@jev.fn
def decide_if_worth_reading(item_text: str, profile_keywords: str) -> ReadingDecision:
    """Based on the following document and user profile keywords, decide if this document is worth reading.

    User Profile Keywords:
    {{ profile_keywords }}

    Document:
    {{ item_text }}
    """
    if not os.environ.get("TYPESAFE_API_KEY"):
        return ReadingDecision(worth_reading=True)
    return decide_if_worth_reading.state()

def run_filter(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter items using Jev to decide if they are worth reading based on the user's profile.
    """
    items: List[Item] = state.get("items", [])
    profile_path = state.get("profile_path", "config/profile.yaml")

    if not items:
        return {"items": items}

    # If no TYPESAFE_API_KEY, just bypass
    if not os.environ.get("TYPESAFE_API_KEY"):
        print("No TYPESAFE_API_KEY found, bypassing Jev filter.")
        return {"items": items}

    try:
        with open(profile_path, 'r') as f:
            profile = yaml.safe_load(f)
            keywords = profile.get("keywords", [])
    except Exception as e:
        print(f"Error loading profile from {profile_path}: {e}")
        keywords = []

    if not keywords:
        return {"items": items}

    profile_keywords_str = ", ".join(keywords)

    filtered_items = []
    for item in items:
        try:
            item_text = f"Title: {item.title}\n\nSummary: {item.raw_summary}"
            decision = decide_if_worth_reading(item_text, profile_keywords_str)
            if decision.worth_reading:
                filtered_items.append(item)
            else:
                print(f"Item not worth reading, filtering out: {item.title}")
        except Exception as e:
            print(f"Error filtering item {item.url} with Jev: {e}")
            filtered_items.append(item) # fallback to keep if error

    return {"items": filtered_items}
