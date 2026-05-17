"""
Tests for Tier 0 processor (direct publish)
"""
import pytest
from scripts.ai_filter.tier0_processor import Tier0Processor


def test_process_adds_tier_metadata():
    """Tier 0 processor should add ai_tier=0 and ai_must_publish=True"""
    processor = Tier0Processor()

    item = {
        "title": "10 Design Patterns You Should Know",
        "url": "https://uxdesign.cc/patterns",
        "source": "UX Collective",
        "published_at": "2026-05-17T10:00:00Z"
    }

    source_config = {
        "name": "UX Collective",
        "patterns": ["ux collective", "uxdesign.cc"],
        "description": "Curated design articles"
    }

    result = processor.process(item, source_config)

    # Verify tier metadata is added
    assert result["_tier"] == 0
    assert result["ai_tier"] == 0
    assert result["ai_must_publish"] is True
    assert result["_source_config"] == source_config


def test_process_preserves_original_fields():
    """Tier 0 processor should preserve all original item fields"""
    processor = Tier0Processor()

    item = {
        "title": "Design System Best Practices",
        "url": "https://uxdesign.cc/design-systems",
        "source": "UX Collective",
        "published_at": "2026-05-17T10:00:00Z",
        "meta": {"author": "Jane Doe", "tags": ["design", "system"]},
        "site_id": "ux_collective",
        "site_name": "UX Collective"
    }

    source_config = {
        "name": "UX Collective",
        "patterns": ["ux collective"]
    }

    result = processor.process(item, source_config)

    # Verify original fields are preserved
    assert result["title"] == item["title"]
    assert result["url"] == item["url"]
    assert result["source"] == item["source"]
    assert result["published_at"] == item["published_at"]
    assert result["meta"] == item["meta"]
    assert result["site_id"] == item["site_id"]
    assert result["site_name"] == item["site_name"]

    # Verify new fields are added
    assert result["_tier"] == 0
    assert result["ai_tier"] == 0
    assert result["ai_must_publish"] is True


def test_process_batch():
    """Tier 0 processor should handle batch processing"""
    processor = Tier0Processor()

    items = [
        {
            "title": "Article 1",
            "url": "https://uxdesign.cc/article-1",
            "source": "UX Collective"
        },
        {
            "title": "Article 2",
            "url": "https://uxdesign.cc/article-2",
            "source": "UX Collective"
        },
        {
            "title": "Article 3",
            "url": "https://uxdesign.cc/article-3",
            "source": "UX Collective"
        }
    ]

    source_config = {
        "name": "UX Collective",
        "patterns": ["ux collective"]
    }

    results = processor.process_batch(items, source_config)

    # Verify batch processing
    assert len(results) == 3

    for result in results:
        assert result["_tier"] == 0
        assert result["ai_tier"] == 0
        assert result["ai_must_publish"] is True
        assert result["_source_config"] == source_config

    # Verify titles are preserved
    assert results[0]["title"] == "Article 1"
    assert results[1]["title"] == "Article 2"
    assert results[2]["title"] == "Article 3"
