"""
Tests for Tier 1 Filter (AI-only analysis)

Tier 1 sources (优设网, UX Collective Weekly) are high-quality but need AI to judge relevance.
Skip keyword filtering, go directly to deep AI analysis.

Filter criteria:
- design_relevance >= 0.6 OR quality_score >= 7
- Language detection: Chinese → DeepSeek, English → GPT-4o Mini
"""
import json
from unittest.mock import Mock, patch
import pytest

from scripts.ai_filter.tier1_filter import Tier1Filter


class TestTier1Filter:
    """Test Tier 1 Filter AI-only analysis"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock EasyRouterClient"""
        with patch('scripts.ai_filter.tier1_filter.EasyRouterClient') as MockClient:
            mock_instance = Mock()
            MockClient.return_value = mock_instance
            yield mock_instance

    def test_filter_calls_ai_with_chinese_model(self, mock_client):
        """Chinese content should use deepseek-chat model"""
        filter_instance = Tier1Filter()

        # Mock Chinese content
        item = {
            "title": "AI设计工具实战教程",
            "url": "https://www.uisdc.com/ai-tutorial",
            "source": "优设网",
            "site_name": "uisdc.com"
        }

        source_config = {
            "id": "uisdc",
            "name": "优设网",
            "patterns": ["uisdc.com"]
        }

        # Mock AI response - high design relevance
        mock_client.call_model.return_value = {
            "content": json.dumps({
                "design_relevance": 8,
                "quality_score": 7,
                "categories": ["AI工具", "设计教程"],
                "target_audience": "UI/UX设计师",
                "key_insights": "详细的AI设计工具使用教程"
            }),
            "tokens": 300
        }

        result = filter_instance.filter_item(item, source_config)

        # Verify DeepSeek model was used for Chinese content
        mock_client.call_model.assert_called_once()
        call_args = mock_client.call_model.call_args
        assert call_args[1]["model"] == "deepseek-chat"

        # Verify item was accepted
        assert result is not None
        assert result["title"] == item["title"]

    def test_filter_calls_ai_with_english_model(self, mock_client):
        """English content should use gpt-4o-mini model"""
        filter_instance = Tier1Filter()

        # Mock English content
        item = {
            "title": "Design Systems Best Practices",
            "url": "https://uxdesign.cc/design-systems",
            "source": "UX Collective",
            "site_name": "uxdesign.cc"
        }

        source_config = {
            "id": "ux_collective",
            "name": "UX Collective",
            "patterns": ["uxdesign.cc"]
        }

        # Mock AI response - high quality
        mock_client.call_model.return_value = {
            "content": json.dumps({
                "design_relevance": 7,
                "quality_score": 9,
                "categories": ["Design Systems", "Best Practices"],
                "target_audience": "Product designers",
                "key_insights": "Comprehensive guide to design systems"
            }),
            "tokens": 250
        }

        result = filter_instance.filter_item(item, source_config)

        # Verify GPT-4o-mini model was used for English content
        mock_client.call_model.assert_called_once()
        call_args = mock_client.call_model.call_args
        assert call_args[1]["model"] == "gpt-4o-mini"

        # Verify item was accepted
        assert result is not None
        assert result["title"] == item["title"]

    def test_filter_rejects_low_relevance(self, mock_client):
        """Items with design_relevance < 0.6 AND quality_score < 7 should be rejected"""
        filter_instance = Tier1Filter()

        item = {
            "title": "General Tech News Article",
            "url": "https://example.com/tech-news",
            "source": "Some Source",
            "site_name": "example.com"
        }

        source_config = {
            "id": "some_source",
            "name": "Some Source"
        }

        # Mock AI response - low relevance and quality
        mock_client.call_model.return_value = {
            "content": json.dumps({
                "design_relevance": 3,  # < 6 (normalized to 0.3)
                "quality_score": 5,      # < 7
                "categories": ["Tech News"],
                "target_audience": "General audience",
                "key_insights": "Generic tech news"
            }),
            "tokens": 200
        }

        result = filter_instance.filter_item(item, source_config)

        # Verify item was rejected
        assert result is None

    def test_filter_accepts_high_quality(self, mock_client):
        """Items with quality_score >= 7 should pass even if design_relevance is low"""
        filter_instance = Tier1Filter()

        item = {
            "title": "Important Industry Announcement",
            "url": "https://example.com/announcement",
            "source": "Tech Source",
            "site_name": "example.com"
        }

        source_config = {
            "id": "tech_source",
            "name": "Tech Source"
        }

        # Mock AI response - low design relevance but high quality
        mock_client.call_model.return_value = {
            "content": json.dumps({
                "design_relevance": 4,  # < 6 (low)
                "quality_score": 8,      # >= 7 (high quality)
                "categories": ["Industry News"],
                "target_audience": "Tech professionals",
                "key_insights": "Major industry development"
            }),
            "tokens": 220
        }

        result = filter_instance.filter_item(item, source_config)

        # Verify item was accepted due to high quality
        assert result is not None
        assert result["title"] == item["title"]
        assert result["ai_quality_score"] == 8

    def test_filter_returns_enriched_item(self, mock_client):
        """Filter should return item enriched with AI metadata"""
        filter_instance = Tier1Filter()

        item = {
            "title": "UI Design Trends 2026",
            "url": "https://www.uisdc.com/ui-trends-2026",
            "source": "优设网",
            "site_name": "uisdc.com",
            "published_at": "2026-05-17T10:00:00Z"
        }

        source_config = {
            "id": "uisdc",
            "name": "优设网"
        }

        # Mock AI response
        ai_response = {
            "design_relevance": 9,
            "quality_score": 8,
            "categories": ["UI设计", "设计趋势"],
            "target_audience": "UI设计师",
            "key_insights": "2026年UI设计趋势分析"
        }

        mock_client.call_model.return_value = {
            "content": json.dumps(ai_response),
            "tokens": 280
        }

        result = filter_instance.filter_item(item, source_config)

        # Verify original fields are preserved
        assert result["title"] == item["title"]
        assert result["url"] == item["url"]
        assert result["source"] == item["source"]
        assert result["published_at"] == item["published_at"]

        # Verify AI metadata is added
        assert result["_tier"] == 1
        assert result["ai_tier"] == 1
        assert result["ai_design_relevance"] == 0.9  # Normalized to 0-1
        assert result["ai_quality_score"] == 8
        assert result["ai_categories"] == ["UI设计", "设计趋势"]
        assert result["ai_target_audience"] == "UI设计师"
        assert result["ai_key_insights"] == "2026年UI设计趋势分析"
        assert result["_source_config"] == source_config
