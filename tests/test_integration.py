"""End-to-end integration tests for AI filter pipeline.

Tests the complete filtering flow from raw items to filtered output with statistics.
"""

import json
import os
import pytest
from unittest.mock import Mock, patch
from scripts.ai_filter.main_filter import AIContentFilter


class TestIntegrationFilters:
    """Integration tests for the complete filtering pipeline."""

    @pytest.fixture
    def test_items(self):
        """Sample test items covering all tiers and blacklist."""
        return [
            # Tier 0: High-trust source (OpenAI)
            {
                'title': 'GPT-5 Model Release',
                'link': 'https://openai.com/blog/gpt-5',
                'source': {
                    'name': 'OpenAI Blog',
                    'url': 'https://openai.com/blog'
                },
                'description': 'Announcing GPT-5 with enhanced capabilities',
                'published': '2026-05-17T10:00:00Z'
            },
            # Tier 1: Medium-trust source (TechCrunch)
            {
                'title': 'New AI Startup Raises $100M',
                'link': 'https://techcrunch.com/ai-startup',
                'source': {
                    'name': 'TechCrunch',
                    'url': 'https://techcrunch.com'
                },
                'description': 'Artificial intelligence startup secures funding',
                'published': '2026-05-17T09:00:00Z'
            },
            # Tier 2: Low-trust source (Hacker News)
            {
                'title': 'Building LLM Applications with Python',
                'link': 'https://news.ycombinator.com/item?id=12345',
                'source': {
                    'name': 'Hacker News',
                    'url': 'https://news.ycombinator.com'
                },
                'description': 'Tutorial on building LLM apps',
                'published': '2026-05-17T08:00:00Z'
            },
            # Blacklist: Should be filtered out
            {
                'title': 'Crypto Trading Bot',
                'link': 'https://spam.example.com/crypto',
                'source': {
                    'name': 'Spam Site',
                    'url': 'https://spam.example.com'
                },
                'description': 'Get rich quick with crypto',
                'published': '2026-05-17T07:00:00Z'
            },
        ]

    @pytest.fixture
    def mock_tier_processors(self):
        """Mock tier processors with realistic responses."""
        with patch('scripts.ai_filter.main_filter.WhitelistRouter') as mock_router, \
             patch('scripts.ai_filter.main_filter.Tier0Processor') as mock_tier0, \
             patch('scripts.ai_filter.main_filter.Tier1Filter') as mock_tier1, \
             patch('scripts.ai_filter.main_filter.Tier2Pipeline') as mock_tier2:

            # Configure router to classify items correctly
            def classify_side_effect(item):
                source_name = item['source']['name']
                if source_name == 'OpenAI Blog':
                    return (0, {'tier': 0, 'name': source_name})
                elif source_name == 'TechCrunch':
                    return (1, {'tier': 1, 'name': source_name})
                elif source_name == 'Hacker News':
                    return (2, {'tier': 2, 'name': source_name})
                else:
                    return (-1, None)  # Blacklist

            mock_router.return_value.classify_item.side_effect = classify_side_effect

            # Configure tier processors to enrich items
            def tier0_process(item, config):
                enriched = item.copy()
                enriched['ai_metadata'] = {
                    'tier': 0,
                    'processing': 'enrichment_only',
                    'source_trust': 'high'
                }
                return enriched

            def tier1_filter(item, config):
                # Simulate keyword filtering (passes AI-related content)
                if 'AI' in item['title'] or 'artificial intelligence' in item.get('description', '').lower():
                    enriched = item.copy()
                    enriched['ai_metadata'] = {
                        'tier': 1,
                        'processing': 'keyword_filtered',
                        'source_trust': 'medium',
                        'match_type': 'keyword'
                    }
                    return enriched
                return None

            def tier2_process(item, config):
                # Simulate semantic analysis (passes LLM-related content)
                if 'LLM' in item['title'] or 'GPT' in item['title']:
                    enriched = item.copy()
                    enriched['ai_metadata'] = {
                        'tier': 2,
                        'processing': 'semantic_analysis',
                        'source_trust': 'low',
                        'relevance_score': 0.85,
                        'analysis': {
                            'is_ai_relevant': True,
                            'confidence': 'high',
                            'reasoning': 'Discusses LLM development'
                        }
                    }
                    return enriched
                return None

            mock_tier0.return_value.process.side_effect = tier0_process
            mock_tier1.return_value.filter_item.side_effect = tier1_filter
            mock_tier2.return_value.process_item.side_effect = tier2_process

            yield {
                'router': mock_router.return_value,
                'tier0': mock_tier0.return_value,
                'tier1': mock_tier1.return_value,
                'tier2': mock_tier2.return_value
            }

    def test_integration_filters_all_tiers(self, test_items, mock_tier_processors):
        """Test that complete pipeline correctly processes all tier types."""
        # Arrange
        filter_instance = AIContentFilter()

        # Act
        filtered_items = filter_instance.filter_batch(test_items)

        # Assert - Should have 3 items (excluding blacklist)
        assert len(filtered_items) == 3

        # Check Tier 0 item
        tier0_item = next(item for item in filtered_items if item['ai_metadata']['tier'] == 0)
        assert tier0_item['title'] == 'GPT-5 Model Release'
        assert tier0_item['ai_metadata']['source_trust'] == 'high'
        assert tier0_item['ai_metadata']['processing'] == 'enrichment_only'

        # Check Tier 1 item
        tier1_item = next(item for item in filtered_items if item['ai_metadata']['tier'] == 1)
        assert tier1_item['title'] == 'New AI Startup Raises $100M'
        assert tier1_item['ai_metadata']['source_trust'] == 'medium'
        assert tier1_item['ai_metadata']['processing'] == 'keyword_filtered'

        # Check Tier 2 item
        tier2_item = next(item for item in filtered_items if item['ai_metadata']['tier'] == 2)
        assert tier2_item['title'] == 'Building LLM Applications with Python'
        assert tier2_item['ai_metadata']['source_trust'] == 'low'
        assert tier2_item['ai_metadata']['processing'] == 'semantic_analysis'
        assert 'relevance_score' in tier2_item['ai_metadata']

        # Verify blacklist item was excluded
        titles = [item['title'] for item in filtered_items]
        assert 'Crypto Trading Bot' not in titles

    def test_integration_generates_valid_output_json(self, test_items, mock_tier_processors, tmp_path):
        """Test that pipeline generates valid JSON output with proper structure."""
        # Arrange
        filter_instance = AIContentFilter()
        output_file = tmp_path / "filtered_output.json"

        # Act
        filtered_items = filter_instance.filter_batch(test_items)
        stats = filter_instance.get_statistics(test_items)

        # Write output
        output_data = {
            'metadata': {
                'total_items': len(test_items),
                'filtered_items': len(filtered_items),
                'statistics': stats,
                'timestamp': '2026-05-17T10:00:00Z'
            },
            'items': filtered_items
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        # Assert - Verify JSON is valid and readable
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert loaded_data['metadata']['total_items'] == 4
        assert loaded_data['metadata']['filtered_items'] == 3
        assert loaded_data['metadata']['statistics']['tier_0'] == 1
        assert loaded_data['metadata']['statistics']['tier_1'] == 1
        assert loaded_data['metadata']['statistics']['tier_2'] == 1
        assert loaded_data['metadata']['statistics']['blacklisted'] == 1
        assert len(loaded_data['items']) == 3

        # Verify each item has ai_metadata
        for item in loaded_data['items']:
            assert 'ai_metadata' in item
            assert 'tier' in item['ai_metadata']
            assert 'processing' in item['ai_metadata']
            assert 'source_trust' in item['ai_metadata']

    def test_integration_statistics_accuracy(self, test_items, mock_tier_processors):
        """Test that statistics accurately reflect tier distribution."""
        # Arrange
        filter_instance = AIContentFilter()

        # Act
        stats = filter_instance.get_statistics(test_items)

        # Assert
        assert stats['total'] == 4
        assert stats['tier_0'] == 1
        assert stats['tier_1'] == 1
        assert stats['tier_2'] == 1
        assert stats['blacklisted'] == 1

        # Verify percentages
        total = stats['total']
        assert stats['tier_0'] / total == 0.25  # 25%
        assert stats['tier_1'] / total == 0.25  # 25%
        assert stats['tier_2'] / total == 0.25  # 25%
        assert stats['blacklisted'] / total == 0.25  # 25%

    @pytest.mark.skip(reason="Requires real API key and network access - run manually")
    def test_integration_with_real_api(self, test_items):
        """Integration test with real EasyRouter API.

        This test is skipped by default. To run manually:
        1. Set EASYROUTER_API_KEY environment variable
        2. Run: pytest tests/test_integration.py::TestIntegrationFilters::test_integration_with_real_api -v -s
        """
        # Check for API key
        api_key = os.getenv('EASYROUTER_API_KEY')
        if not api_key:
            pytest.skip("EASYROUTER_API_KEY not set")

        # Arrange - Use real filter without mocks
        filter_instance = AIContentFilter()

        # Select only items that would trigger API calls (Tier 1 and 2)
        api_test_items = [item for item in test_items
                          if item['source']['name'] in ['TechCrunch', 'Hacker News']]

        # Act
        filtered_items = filter_instance.filter_batch(api_test_items)

        # Assert - Basic validation only (actual filtering depends on real API)
        for item in filtered_items:
            assert 'ai_metadata' in item
            assert item['ai_metadata']['tier'] in [1, 2]

        print(f"\nProcessed {len(api_test_items)} items with real API")
        print(f"Filtered results: {len(filtered_items)} items passed")


class TestIntegrationDisabled:
    """Test integration when AI filter is disabled."""

    def test_disabled_filter_returns_all_items(self):
        """Test that disabled filter passes through all items unchanged."""
        # Arrange
        with patch('os.getenv', return_value="0"):
            filter_instance = AIContentFilter()

        items = [
            {'title': 'Test 1', 'source': {'name': 'Test'}},
            {'title': 'Test 2', 'source': {'name': 'Test'}},
        ]

        # Act
        result = filter_instance.filter_batch(items)

        # Assert
        assert result == items
        assert len(result) == 2

    def test_disabled_filter_statistics(self):
        """Test that statistics reflect disabled state."""
        # Arrange
        with patch('os.getenv', return_value="0"):
            filter_instance = AIContentFilter()

        items = [
            {'title': 'Test 1', 'source': {'name': 'Test'}},
            {'title': 'Test 2', 'source': {'name': 'Test'}},
        ]

        # Act
        stats = filter_instance.get_statistics(items)

        # Assert
        assert stats['total'] == 2
        assert stats['tier_0'] == 0
        assert stats['tier_1'] == 0
        assert stats['tier_2'] == 0
        assert stats['blacklisted'] == 0
        assert stats['enabled'] is False
