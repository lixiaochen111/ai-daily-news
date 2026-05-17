"""
测试白名单路由器
验证三级白名单分类逻辑
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.ai_filter.whitelist_router import WhitelistRouter


class TestWhitelistRouter:
    """测试WhitelistRouter类"""

    @pytest.fixture
    def router(self):
        """创建路由器实例"""
        config_path = project_root / "config" / "source-whitelist.yaml"
        return WhitelistRouter(str(config_path))

    def test_tier_0_source(self, router):
        """测试Tier 0源（编辑精选源）- UX Collective"""
        item = {
            'source': 'UX Collective',
            'url': 'https://uxdesign.cc/some-article',
            'title': 'Great UX Design Article'
        }

        tier, source_config = router.classify_item(item)

        assert tier == 0, "UX Collective应该被分类为Tier 0"
        assert source_config is not None
        assert source_config['id'] == 'ux_collective'
        assert source_config['name'] == 'UX Collective'
        assert 'uxdesign.cc' in source_config['patterns']

    def test_tier_1_source(self, router):
        """测试Tier 1源（高质量源）- 优设网"""
        item = {
            'source': '优设网',
            'url': 'https://www.uisdc.com/ai-design-tutorial',
            'title': 'AI设计教程：Midjourney实战'
        }

        tier, source_config = router.classify_item(item)

        assert tier == 1, "优设网应该被分类为Tier 1"
        assert source_config is not None
        assert source_config['id'] == 'uisdc'
        assert source_config['name'] == '优设网'
        assert 'uisdc.com' in source_config['patterns']

    def test_tier_2_source(self, router):
        """测试Tier 2源（广域官方源）- Figma"""
        item = {
            'source': 'Figma Blog',
            'url': 'https://www.figma.com/blog/new-ai-feature',
            'title': 'Announcing Figma AI'
        }

        tier, source_config = router.classify_item(item)

        assert tier == 2, "Figma应该被分类为Tier 2"
        assert source_config is not None
        assert source_config['id'] == 'figma_official'
        assert source_config['name'] == 'Figma Blog'
        assert 'figma.com/blog' in source_config['patterns']

    def test_blacklist_source(self, router):
        """测试黑名单源 - 娱乐内容"""
        item = {
            'source': '娱乐八卦网',
            'url': 'https://example.com/entertainment',
            'title': '震惊！明星爆料'
        }

        tier, source_config = router.classify_item(item)

        assert tier == -1, "娱乐内容应该被分类为黑名单（-1）"
        assert source_config is not None
        assert source_config['reason'] is not None

    def test_blacklist_title_spam(self, router):
        """测试黑名单 - 标题党"""
        item = {
            'source': 'Some News Site',
            'url': 'https://example.com/news',
            'title': '震惊！你绝对想不到的秘密'
        }

        tier, source_config = router.classify_item(item)

        assert tier == -1, "标题党应该被分类为黑名单（-1）"
        assert source_config is not None

    def test_unknown_source_defaults_to_tier_2(self, router):
        """测试未知源默认分类为Tier 2"""
        item = {
            'source': 'Unknown Tech Blog',
            'url': 'https://unknown-blog.com/article',
            'title': 'Some Tech Article'
        }

        tier, source_config = router.classify_item(item)

        assert tier == 2, "未知源应该默认分类为Tier 2"
        assert source_config is None, "未知源不应该有source_config"

    def test_case_insensitive_matching(self, router):
        """测试不区分大小写的匹配"""
        # 测试大小写变化
        item1 = {
            'source': 'ux collective',  # 全小写
            'url': 'https://UXDESIGN.CC/article',  # 全大写
            'title': 'Test Article'
        }

        tier1, config1 = router.classify_item(item1)
        assert tier1 == 0, "不区分大小写匹配应该正常工作"

        item2 = {
            'source': 'UX COLLECTIVE',  # 全大写
            'url': 'https://uxdesign.cc/article',
            'title': 'Test Article'
        }

        tier2, config2 = router.classify_item(item2)
        assert tier2 == 0, "不区分大小写匹配应该正常工作"

    def test_url_pattern_matching(self, router):
        """测试URL模式匹配"""
        # 测试通过URL匹配（即使source名称不同）
        item = {
            'source': 'Different Name',
            'url': 'https://muz.li/some-article',
            'title': 'Design Inspiration'
        }

        tier, source_config = router.classify_item(item)

        assert tier == 0, "应该通过URL匹配到Muzli（Tier 0）"
        assert source_config['id'] == 'muzli'

    def test_blacklist_priority(self, router):
        """测试黑名单优先级最高"""
        # 即使URL匹配Tier 0源，但标题包含黑名单关键词
        item = {
            'source': 'UX Collective',
            'url': 'https://uxdesign.cc/article',
            'title': '震惊！不看后悔的设计秘密'  # 包含黑名单词
        }

        tier, source_config = router.classify_item(item)

        assert tier == -1, "黑名单应该有最高优先级"
