import os
from datetime import datetime
from collections import defaultdict
from typing import List
import html
from src.connectors.base import Item

def generate_digest(items: List[Item], output_dir: str = "output") -> str:
    """
    Generate a static HTML digest from the top-scored items.
    Groups items by category and sorts by score descending.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Filter out items with very low score if we have lots of them, or just sort
    # We will take max top 15 total items
    sorted_items = sorted(items, key=lambda x: x.score or 0.0, reverse=True)[:15]

    # Group by category
    grouped_items = defaultdict(list)
    for item in sorted_items:
        category = item.category or "uncategorized"
        grouped_items[category].append(item)

    date_str = datetime.now().strftime("%Y-%m-%d")
    html_filename = os.path.join(output_dir, f"digest-{date_str}.html")

    html_content = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        f"<title>AI Trend Radar Digest - {date_str}</title>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }",
        "h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }",
        "h2 { color: #0056b3; margin-top: 30px; text-transform: capitalize; border-bottom: 1px solid #ccc; padding-bottom: 5px;}",
        ".item { margin-bottom: 25px; padding: 15px; border: 1px solid #eee; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }",
        ".item-title { font-size: 1.2em; font-weight: bold; margin-bottom: 5px; }",
        ".item-title a { color: #007bff; text-decoration: none; }",
        ".item-title a:hover { text-decoration: underline; }",
        ".item-meta { font-size: 0.9em; color: #666; margin-bottom: 10px; }",
        ".item-summary { margin-bottom: 10px; }",
        ".score { display: inline-block; background: #e9ecef; padding: 2px 6px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>AI Trend Radar Digest 📡 - {date_str}</h1>",
        "<p>Your weekly digest of AI architecture developments, scored against your profile.</p>"
    ]

    for category, category_items in grouped_items.items():
        html_content.append(f"<h2>{category.replace('-', ' ')}</h2>")
        for item in category_items:
            score_str = f"Score: {item.score:.2f}" if item.score is not None else ""
            summary = item.summary or "No summary available."

            # Format multiple source links if it was merged
            source_links_html = []
            if item.source_links and len(item.source_links) > 1:
                source_links_html.append("<div class='item-meta'>Additional sources: ")
                links = []
                for i, link in enumerate(item.source_links):
                    if link != item.url:
                        links.append(f"<a href='{link}' target='_blank'>[Source {i}]</a>")
                source_links_html.append(" ".join(links))
                source_links_html.append("</div>")

            safe_title = html.escape(item.title)
            safe_url = html.escape(item.url)
            safe_source = html.escape(item.source)
            safe_summary = html.escape(summary)

            html_content.append(f"""
            <div class="item">
                <div class="item-title"><a href="{safe_url}" target="_blank">{safe_title}</a></div>
                <div class="item-meta">
                    <span class="source">{safe_source}</span> |
                    <span class="date">{item.published_date[:10] if item.published_date else ''}</span>
                    {f' | <span class="score">{score_str}</span>' if score_str else ''}
                </div>
                <div class="item-summary">{safe_summary}</div>
                {''.join(source_links_html)}
            </div>
            """)

    html_content.append("</body></html>")

    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(html_content))

    return html_filename
