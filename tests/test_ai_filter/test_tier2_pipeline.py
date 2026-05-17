"""
Tests for Tier 2 Pipeline (Keyword + AI Full Flow)

Tier 2 sources (Figma, OpenAI, etc.) have broad content that needs three-stage filtering:
1. Keyword initial filtering
2. GLM-4-Flash classification
3. AI deep analysis

Filter criteria:
- design_relevance >= 0.7 (stricter than Tier 1's 0.6)
- Respects filter_focus and exclude_topics from source config
"""
import json
from unittest.mock import Mock, patch
import pytest

from scripts.ai_filter.tier2_pipeline import Tier2Pipeline


class TestTier2Pipeline:
    """Test Tier 2 Pipeline three-stage filtering"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock EasyRouterClient"""
        with patch('scripts.ai_filter.tier2_pipeline.EasyRouterClient') as MockClient:
            mock_instance = Mock()
            MockClient.return_value = mock_instance
            yield mock_instance

    # ============================================================
    # Keyword Filtering Tests
    # ============================================================

    def test_keyword_filter_passes_relevant_content(self, mock_client):
        """Keywords matching BASE_KEYWORDS should pass Stage 1"""
        pipeline = Tier2Pipeline()

        # Content with AI+design keywords
        item = {
            "title": "New AI design tool for Figma",
            "url": "https://figma.com/ai-design-tool",
            "source": "Figma Blog",
            "site_name": "figma.com"
        }

        source_config = {
            "id": "figma",
            "name": "Figma Blog",
            "patterns": ["figma.com"]
        }

        # Should pass keyword filter (contains "ai", "design", "figma")
        assert pipeline._keyword_filter(item, source_config) is True

    def test_keyword_filter_respects_filter_focus(self, mock_client):
        """Keywords matching filter_focus should pass Stage 1"""
        pipeline = Tier2Pipeline()

        # Content about prototyping (not in BASE_KEYWORDS)
        item = {
            "title": "Advanced prototyping techniques",
            "url": "https://figma.com/prototyping",
            "source": "Figma Blog",
            "site_name": "figma.com"
        }

        source_config = {
            "id": "figma",
            "name": "Figma Blog",
            "patterns": ["figma.com"],
            "filter_focus": ["prototyping", "collaboration"]
        }

        # Should pass because "prototyping" is in filter_focus
        assert pipeline._keyword_filter(item, source_config) is True

    def test_keyword_filter_respects_exclude_topics(self, mock_client):
        """Keywords matching exclude_topics should fail Stage 1"""
        pipeline = Tier2Pipeline()

        # Content about pricing (excluded topic)
        item = {
            "title": "Figma pricing update for 2026",
            "url": "https://figma.com/pricing",
            "source": "Figma Blog",
            "site_name": "figma.com"
        }

        source_config = {
            "id": "figma",
            "name": "Figma Blog",
            "patterns": ["figma.com"],
            "exclude_topics": ["pricing", "billing", "subscription"]
        }

        # Should fail because "pricing" is in exclude_topics
        assert pipeline._keyword_filter(item, source_config) is False

    # ============================================================
    # GLM Classification Tests
    # ============================================================

    def test_glm_classify_passes_relevant(self, mock_client):
        """GLM classifying as relevant should pass Stage 2"""
        pipeline = Tier2Pipeline()

        item = {
            "title": "AI-powered design system updates",
            "url": "https://figma.com/ai-updates",
            "source": "Figma Blog",
            "site_name": "figma.com"
        }

        # Mock GLM response - relevant
        mock_client.call_model.return_value = {
            "content": json.dumps({
                "is_relevant": True,
                "confidence": 0.85,
                "reason": "AI设计工具更新，与AI+设计直接相关"
            }),
            "tokens": 50
        }

        # Should pass GLM classification
        assert pipeline._glm_classify(item) is True

        # Verify GLM-4-Flash was used
        mock_client.call_model.assert_called_once()
        call_args = mock_client.call_model.call_args
        assert call_args[1]["model"] == "glm-4-flash"

    def test_glm_classify_rejects_irrelevant(self, mock_client):
        """GLM classifying as irrelevant should fail Stage 2"""
        pipeline = Tier2Pipeline()

        item = {
            "title": "Company hiring updates",
            "url": "https://figma.com/careers",
            "source": "Figma Blog",
            "site_name": "figma.com"
        }

        # Mock GLM response - not relevant
        mock_client.call_model.return_value = {
            "content": json.dumps({
                "is_relevant": False,
                "confidence": 0.9,
                "reason": "招聘信息，与AI+设计无关"
            }),
            "tokens": 45
        }

        # Should fail GLM classification
        assert pipeline._glm_classify(item) is False

    # ============================================================
    # Full Pipeline Integration Tests
    # ============================================================

    def test_full_pipeline_rejects_at_keyword_stage(self, mock_client):
        """Content failing keyword filter should be rejected at Stage 1"""
        pipeline = Tier2Pipeline()

        # Content with no AI/design keywords
        item = {
            "title": "Company financial report Q4 2026",
            "url": "https://example.com/finance",
            "source": "Example Blog",
            "site_name": "example.com"
        }

        source_config = {
            "id": "example",
            "name": "Example Blog",
            "patterns": ["example.com"]
        }

        result = pipeline.process_item(item, source_config)

        # Should be rejected at keyword stage
        assert result is None

        # GLM should NOT be called (early rejection)
        mock_client.call_model.assert_not_called()

    def test_full_pipeline_rejects_at_glm_stage(self, mock_client):
        """Content passing keywords but failing GLM should be rejected at Stage 2"""
        pipeline = Tier2Pipeline()

        # Content with keywords but not actually relevant
        item = {
            "title": "AI is mentioned but this is about finance",
            "url": "https://example.com/ai-finance",
            "source": "Example Blog",
            "site_name": "example.com"
        }

        source_config = {
            "id": "example",
            "name": "Example Blog",
            "patterns": ["example.com"]
        }

        # Mock GLM response - not relevant
        mock_client.call_model.return_value = {
            "content": json.dumps({
                "is_relevant": False,
                "confidence": 0.8,
                "reason": "虽然提到AI，但内容是金融，不相关"
            }),
            "tokens": 50
        }

        result = pipeline.process_item(item, source_config)

        # Should be rejected at GLM stage
        assert result is None

        # GLM should be called once, deep analysis should NOT be called
        assert mock_client.call_model.call_count == 1

    def test_full_pipeline_passes_all_stages(self, mock_client):
        """Content passing all stages should be enriched and returned"""
        pipeline = Tier2Pipeline()

        item = {
            "title": "New AI design features in Figma",
            "url": "https://figma.com/ai-features",
            "source": "Figma Blog",
            "site_name": "figma.com",
            "published_at": "2026-05-17T10:00:00Z"
        }

        source_config = {
            "id": "figma",
            "name": "Figma Blog",
            "patterns": ["figma.com"]
        }

        # Mock GLM response - relevant
        mock_client.call_model.side_effect = [
            # First call: GLM classification
            {
                "content": json.dumps({
                    "is_relevant": True,
                    "confidence": 0.9,
                    "reason": "AI设计功能，直接相关"
                }),
                "tokens": 50
            },
            # Second call: Deep analysis (English content)
            {
                "content": json.dumps({
                    "design_relevance": 9,
                    "quality_score": 8,
                    "categories": ["AI Tools", "Design Features"],
                    "target_audience": "Product designers",
                    "key_insights": "New AI features for design workflows"
                }),
                "tokens": 300
            }
        ]

        result = pipeline.process_item(item, source_config)

        # Should pass all stages
        assert result is not None

        # Verify original fields preserved
        assert result["title"] == item["title"]
        assert result["url"] == item["url"]
        assert result["published_at"] == item["published_at"]

        # Verify tier metadata
        assert result["_tier"] == 2
        assert result["ai_tier"] == 2
        assert result["_source_config"] == source_config

        # Verify AI metadata
        assert result["ai_design_relevance"] == 0.9
        assert result["ai_quality_score"] == 8
        assert result["ai_categories"] == ["AI Tools", "Design Features"]
        assert result["ai_target_audience"] == "Product designers"
        assert result["ai_key_insights"] == "New AI features for design workflows"

        # Verify both AI calls were made (GLM + Deep Analysis)
        assert mock_client.call_model.call_count == 2

    def test_full_pipeline_respects_tier2_threshold(self, mock_client):
        """Tier 2 should reject items with design_relevance < 0.7 (stricter than Tier 1)"""
        pipeline = Tier2Pipeline()

        item = {
            "title": "Design tool update",
            "url": "https://figma.com/update",
            "source": "Figma Blog",
            "site_name": "figma.com"
        }

        source_config = {
            "id": "figma",
            "name": "Figma Blog",
            "patterns": ["figma.com"]
        }

        # Mock responses
        mock_client.call_model.side_effect = [
            # GLM classification - relevant
            {
                "content": json.dumps({
                    "is_relevant": True,
                    "confidence": 0.8,
                    "reason": "设计工具更新"
                }),
                "tokens": 45
            },
            # Deep analysis - design_relevance = 6/10 (0.6)
            # This would pass Tier 1 (threshold 0.6) but should fail Tier 2 (threshold 0.7)
            {
                "content": json.dumps({
                    "design_relevance": 6,  # 0.6 < 0.7 threshold
                    "quality_score": 6,      # < 7, doesn't bypass threshold
                    "categories": ["Design Tools"],
                    "target_audience": "Designers",
                    "key_insights": "Tool update"
                }),
                "tokens": 250
            }
        ]

        result = pipeline.process_item(item, source_config)

        # Should be rejected due to stricter Tier 2 threshold
        assert result is None

        # Verify both stages were called
        assert mock_client.call_model.call_count == 2
