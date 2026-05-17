import pytest
from scripts.ai_filter.language_detector import detect_language


def test_detect_chinese_by_whitelist():
    """少数派 source should always return zh"""
    result = detect_language(
        title="这是一篇文章",
        source="少数派",
        site_name="sspai.com"
    )
    assert result == "zh"


def test_detect_english_by_whitelist():
    """OpenAI source should always return en"""
    result = detect_language(
        title="Introducing GPT-5",
        source="OpenAI Blog",
        site_name="openai.com"
    )
    assert result == "en"


def test_detect_chinese_by_ratio():
    """High Chinese character ratio should return zh"""
    result = detect_language(
        title="设计工具使用指南 with some English",
        source="Unknown Source",
        site_name="example.com"
    )
    assert result == "zh"


def test_detect_english_by_ratio():
    """High English character ratio should return en"""
    result = detect_language(
        title="A complete guide to design with 少量中文",
        source="Unknown Source",
        site_name="example.com"
    )
    assert result == "en"
