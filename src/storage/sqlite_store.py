import sqlite3
import json
from typing import List
from src.connectors.base import Item
from src.storage.store import ItemStore


class SQLiteStore(ItemStore):
    def __init__(self, db_path: str = "items.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    source TEXT NOT NULL,
                    published_date TEXT,
                    raw_summary TEXT,
                    category TEXT,
                    score REAL,
                    summary TEXT,
                    source_links TEXT
                )
            ''')
            conn.commit()

    def save_items(self, items: List[Item]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for item in items:
                source_links_json = json.dumps(item.source_links) if item.source_links else json.dumps([item.url])
                cursor.execute('''
                    INSERT INTO items (title, url, source, published_date, raw_summary, category, score, summary, source_links)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        title=excluded.title,
                        source=excluded.source,
                        published_date=excluded.published_date,
                        raw_summary=excluded.raw_summary,
                        category=excluded.category,
                        score=excluded.score,
                        summary=excluded.summary,
                        source_links=excluded.source_links
                ''', (
                    item.title,
                    item.url,
                    item.source,
                    item.published_date,
                    item.raw_summary,
                    item.category,
                    item.score,
                    item.summary,
                    source_links_json
                ))
            conn.commit()

    def get_recent_items(self, limit: int = 100) -> List[Item]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, url, source, published_date, raw_summary, category, score, summary, source_links
                FROM items
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,))

            rows = cursor.fetchall()
            items = []
            for row in rows:
                source_links = json.loads(row[9]) if row[9] else []
                item = Item(
                    id=row[0],
                    title=row[1],
                    url=row[2],
                    source=row[3],
                    published_date=row[4],
                    raw_summary=row[5],
                    category=row[6],
                    score=row[7],
                    summary=row[8],
                    source_links=source_links
                )
                items.append(item)
            return items
