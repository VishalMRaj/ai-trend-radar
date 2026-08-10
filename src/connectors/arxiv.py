import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from src.connectors.base import Connector, Item

class ArxivConnector(Connector):
    def __init__(self, config: dict):
        self.categories = config.get("categories", ["cs.AI", "cs.CL"])
        self.max_results = config.get("max_results", 100)
        self.base_url = "http://export.arxiv.org/api/query"

    def fetch(self) -> list[Item]:
        items = []
        search_query = " OR ".join([f"cat:{cat}" for cat in self.categories])
        query_params = {
            "search_query": search_query,
            "start": 0,
            "max_results": self.max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        url = f"{self.base_url}?{urllib.parse.urlencode(query_params)}"

        try:
            with urllib.request.urlopen(url) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)

                # Namespaces used by arXiv API
                ns = {'atom': 'http://www.w3.org/2005/Atom'}

                for entry in root.findall('atom:entry', ns):
                    title_elem = entry.find('atom:title', ns)
                    summary_elem = entry.find('atom:summary', ns)
                    url_elem = entry.find('atom:id', ns)
                    published_elem = entry.find('atom:published', ns)

                    title = title_elem.text.replace('\n', ' ').strip() if title_elem is not None else "No Title"
                    summary = summary_elem.text.replace('\n', ' ').strip() if summary_elem is not None else "No Summary"
                    url = url_elem.text if url_elem is not None else ""
                    published = published_elem.text if published_elem is not None else ""

                    if url:
                        item = Item(
                            title=title,
                            url=url,
                            source="arXiv",
                            published_date=published,
                            raw_summary=summary
                        )
                        items.append(item)

        except Exception as e:
            print(f"Error fetching from arXiv: {e}")

        return items
