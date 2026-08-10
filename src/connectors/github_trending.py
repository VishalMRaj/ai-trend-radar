import requests
from bs4 import BeautifulSoup
from src.connectors.base import Connector, Item
from datetime import datetime

class GitHubTrendingConnector(Connector):
    def __init__(self, config: dict):
        self.language = config.get("language", "")
        self.base_url = "https://github.com/trending"

    def fetch(self) -> list[Item]:
        items = []
        url = self.base_url
        if self.language:
            url = f"{self.base_url}/{self.language}"

        try:
            # GitHub requires a user agent
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all repository boxes
            repo_articles = soup.find_all('article', class_='Box-row')

            for article in repo_articles:
                h2 = article.find('h2', class_='h3 lh-condensed')
                if not h2:
                    continue

                a_tag = h2.find('a')
                if not a_tag:
                    continue

                repo_path = a_tag.get('href', '').strip('/')
                title = f"GitHub: {repo_path}"
                repo_url = f"https://github.com/{repo_path}"

                p_tag = article.find('p', class_='col-9 color-fg-muted my-1 pr-4')
                summary = p_tag.text.strip() if p_tag else "No description provided."

                # We do not have a published date, use current time
                published = datetime.utcnow().isoformat() + "Z"

                item = Item(
                    title=title,
                    url=repo_url,
                    source="GitHub Trending",
                    published_date=published,
                    raw_summary=summary
                )
                items.append(item)

        except Exception as e:
            print(f"Error fetching GitHub Trending: {e}")

        return items
