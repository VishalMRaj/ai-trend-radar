from abc import ABC, abstractmethod
from typing import List, Optional
from src.connectors.base import Item

class ItemStore(ABC):
    @abstractmethod
    def save_items(self, items: List[Item]) -> None:
        """Save a list of items to the store."""
        pass

    @abstractmethod
    def get_recent_items(self, limit: int = 100) -> List[Item]:
        """Retrieve recent items from the store."""
        pass
