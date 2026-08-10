from src.connectors.base import Item

def test_item_creation():
    item = Item(
        title="Test Title",
        url="http://test.com",
        source="Test Source",
        published_date="2024-01-01T00:00:00Z",
        raw_summary="This is a test."
    )
    assert item.title == "Test Title"
    assert item.source_links == ["http://test.com"]
