import feedparser
from src.connectors.base import Connector, Item
from datetime import datetime
import time

class RSSConnector(Connector):
    def __init__(self, config: dict):
        self.feeds = config.get("feeds", [])

    def fetch(self) -> list[Item]:
        items = []
        for feed_config in self.feeds:
            url = feed_config.get("url")
            if not url:
                continue

            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    summary = entry.get('summary', '') or entry.get('description', '')

                    # Try to get published date
                    published_parsed = entry.get('published_parsed')
                    if published_parsed:
                        published = time.strftime('%Y-%m-%dT%H:%M:%SZ', published_parsed)
                    else:
                        published = datetime.utcnow().isoformat() + "Z"

                    source = feed.feed.get('title', 'RSS')

                    item = Item(
                        title=title,
                        url=link,
                        source=f"RSS: {source}",
                        published_date=published,
                        raw_summary=summary
                    )
                    items.append(item)
            except Exception as e:
                print(f"Error fetching RSS feed {url}: {e}")

        return items
