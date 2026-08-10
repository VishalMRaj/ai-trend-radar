from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod


@dataclass
class Item:
    title: str
    url: str
    source: str
    published_date: str
    raw_summary: str
    id: Optional[int] = None
    category: Optional[str] = None
    score: Optional[float] = None
    summary: Optional[str] = None
    source_links: Optional[list[str]] = None

    def __post_init__(self):
        if self.source_links is None:
            self.source_links = [self.url]


class Connector(ABC):
    @abstractmethod
    def fetch(self) -> list[Item]:
        """Fetch items from the source."""
        pass
