"""Tests for main filter orchestrator."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.ai_filter.main_filter import AIContentFilter


class TestAIContentFilter:
    """Test suite for AIContentFilter orchestrator."""

    @pytest.fixture
    def mock_components(self):
        """Mock all filter components."""
        with patch('scripts.ai_filter.main_filter.WhitelistRouter') as mock_router, \
             patch('scripts.ai_filter.main_filter.Tier0Processor') as mock_tier0, \
             patch('scripts.ai_filter.main_filter.Tier1Filter') as mock_tier1, \
             patch('scripts.ai_filter.main_filter.Tier2Pipeline') as mock_tier2:

            yield {
                'router': mock_router.return_value,
                'tier0': mock_tier0.return_value,
                'tier1': mock_tier1.return_value,
                'tier2': mock_tier2.return_value
            }

    @pytest.fixture
    def filter_instance(self, mock_components):
        """Create AIContentFilter instance with mocked components."""
        return AIContentFilter()

    def test_filter_routes_to_tier0(self, filter_instance, mock_components):
        """Test that Tier 0 items are routed to Tier0Processor."""
        # Arrange
        item = {
            'title': 'OpenAI Announcement',
            'link': 'https://openai.com/blog/news',
            'source': {'name': 'OpenAI Blog'}
        }
        source_config = {'tier': 0, 'name': 'OpenAI Blog'}

        mock_components['router'].classify_item.return_value = (0, source_config)
        mock_components['tier0'].process.return_value = {'filtered': True, 'tier': 0}

        # Act
        result = filter_instance.filter_item(item)

        # Assert
        assert result == {'filtered': True, 'tier': 0}
        mock_components['router'].classify_item.assert_called_once_with(item)
        mock_components['tier0'].process.assert_called_once_with(item, source_config)
        mock_components['tier1'].filter_item.assert_not_called()
        mock_components['tier2'].process_item.assert_not_called()

    def test_filter_routes_to_tier1(self, filter_instance, mock_components):
        """Test that Tier 1 items are routed to Tier1Filter."""
        # Arrange
        item = {
            'title': 'Machine learning advances',
            'link': 'https://techcrunch.com/ml-news',
            'source': {'name': 'TechCrunch'}
        }
        source_config = {'tier': 1, 'name': 'TechCrunch'}

        mock_components['router'].classify_item.return_value = (1, source_config)
        mock_components['tier1'].filter_item.return_value = {'filtered': True, 'tier': 1}

        # Act
        result = filter_instance.filter_item(item)

        # Assert
        assert result == {'filtered': True, 'tier': 1}
        mock_components['router'].classify_item.assert_called_once_with(item)
        mock_components['tier1'].filter_item.assert_called_once_with(item, source_config)
        mock_components['tier0'].process.assert_not_called()
        mock_components['tier2'].process_item.assert_not_called()

    def test_filter_routes_to_tier2(self, filter_instance, mock_components):
        """Test that Tier 2 items are routed to Tier2Pipeline."""
        # Arrange
        item = {
            'title': 'General tech news',
            'link': 'https://news.ycombinator.com/item',
            'source': {'name': 'Hacker News'}
        }
        source_config = {'tier': 2, 'name': 'Hacker News'}

        mock_components['router'].classify_item.return_value = (2, source_config)
        mock_components['tier2'].process_item.return_value = {'filtered': True, 'tier': 2}

        # Act
        result = filter_instance.filter_item(item)

        # Assert
        assert result == {'filtered': True, 'tier': 2}
        mock_components['router'].classify_item.assert_called_once_with(item)
        mock_components['tier2'].process_item.assert_called_once_with(item, source_config)
        mock_components['tier0'].process.assert_not_called()
        mock_components['tier1'].filter_item.assert_not_called()

    def test_filter_rejects_blacklist(self, filter_instance, mock_components):
        """Test that blacklisted items (-1) return None."""
        # Arrange
        item = {
            'title': 'Crypto scam news',
            'link': 'https://spam.example.com/scam',
            'source': {'name': 'Spam Site'}
        }

        mock_components['router'].classify_item.return_value = (-1, None)

        # Act
        result = filter_instance.filter_item(item)

        # Assert
        assert result is None
        mock_components['router'].classify_item.assert_called_once_with(item)
        mock_components['tier0'].process.assert_not_called()
        mock_components['tier1'].filter_item.assert_not_called()
        mock_components['tier2'].process_item.assert_not_called()

    def test_filter_batch_combines_all_tiers(self, filter_instance, mock_components):
        """Test that batch processing handles mixed tier items correctly."""
        # Arrange
        items = [
            {'title': 'OpenAI News', 'source': {'name': 'OpenAI'}},
            {'title': 'Tech Article', 'source': {'name': 'TechCrunch'}},
            {'title': 'HN Post', 'source': {'name': 'HN'}},
            {'title': 'Spam', 'source': {'name': 'Spam'}},
        ]

        # Mock router responses
        mock_components['router'].classify_item.side_effect = [
            (0, {'tier': 0}),
            (1, {'tier': 1}),
            (2, {'tier': 2}),
            (-1, None),
        ]

        # Mock processor responses
        mock_components['tier0'].process.return_value = {'result': 'tier0'}
        mock_components['tier1'].filter_item.return_value = {'result': 'tier1'}
        mock_components['tier2'].process_item.return_value = {'result': 'tier2'}

        # Act
        results = filter_instance.filter_batch(items)

        # Assert
        assert len(results) == 3  # 4 items, 1 filtered out
        assert results[0] == {'result': 'tier0'}
        assert results[1] == {'result': 'tier1'}
        assert results[2] == {'result': 'tier2'}

        assert mock_components['router'].classify_item.call_count == 4
        assert mock_components['tier0'].process.call_count == 1
        assert mock_components['tier1'].filter_item.call_count == 1
        assert mock_components['tier2'].process_item.call_count == 1

    def test_filter_disabled_returns_original_items(self, mock_components):
        """Test that when filter is disabled, original items are returned."""
        # Arrange
        with patch('os.getenv', return_value="0"):
            filter_instance = AIContentFilter()

        item = {'title': 'Test', 'source': {'name': 'Test'}}

        # Act
        result = filter_instance.filter_item(item)

        # Assert
        assert result == item
        mock_components['router'].classify_item.assert_not_called()

    def test_get_statistics(self, filter_instance, mock_components):
        """Test statistics generation for processed items."""
        # Arrange
        items = [
            {'title': 'OpenAI News', 'source': {'name': 'OpenAI'}},
            {'title': 'Tech Article', 'source': {'name': 'TechCrunch'}},
            {'title': 'HN Post', 'source': {'name': 'HN'}},
            {'title': 'Spam', 'source': {'name': 'Spam'}},
        ]

        mock_components['router'].classify_item.side_effect = [
            (0, {'tier': 0}),
            (1, {'tier': 1}),
            (2, {'tier': 2}),
            (-1, None),
        ]

        # Act
        stats = filter_instance.get_statistics(items)

        # Assert
        assert stats['total'] == 4
        assert stats['tier_0'] == 1
        assert stats['tier_1'] == 1
        assert stats['tier_2'] == 1
        assert stats['blacklisted'] == 1
