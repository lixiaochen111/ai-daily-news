"""Tests for AI analysis prompt builders."""

import pytest
from scripts.ai_filter.prompts import (
    build_classification_prompt,
    build_analysis_prompt
)


def test_classification_prompt_includes_title():
    """Classification prompt should include title and source."""
    prompt = build_classification_prompt(
        title="New AI Design Tool Released",
        source="TechCrunch"
    )

    assert "New AI Design Tool Released" in prompt
    assert "TechCrunch" in prompt
    assert "is_relevant" in prompt
    assert "confidence" in prompt
    assert "reason" in prompt


def test_analysis_prompt_includes_filter_focus():
    """Analysis prompt should include filter_focus criteria."""
    prompt = build_analysis_prompt(
        title="New AI Tool for Designers",
        source="Design Blog",
        summary="A new tool that helps designers...",
        filter_focus=["AI tools", "design productivity"],
        exclude_topics=["crypto", "blockchain"],
        language="en"
    )

    assert "New AI Tool for Designers" in prompt
    assert "Design Blog" in prompt
    assert "AI tools" in prompt
    assert "design productivity" in prompt
    assert "crypto" in prompt
    assert "blockchain" in prompt


def test_analysis_prompt_adapts_to_language():
    """Analysis prompt should adapt to Chinese language."""
    prompt_zh = build_analysis_prompt(
        title="AI设计工具发布",
        source="少数派",
        language="zh"
    )

    prompt_en = build_analysis_prompt(
        title="AI Design Tool Release",
        source="TechCrunch",
        language="en"
    )

    # Chinese prompt should have Chinese instructions
    assert "分析" in prompt_zh or "判断" in prompt_zh

    # English prompt should have English instructions
    assert "analyze" in prompt_en.lower() or "evaluate" in prompt_en.lower()

    # Both should request JSON format
    assert "JSON" in prompt_zh or "json" in prompt_zh
    assert "JSON" in prompt_en or "json" in prompt_en
