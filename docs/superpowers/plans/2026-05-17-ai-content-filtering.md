# AI内容筛选系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build three-tier AI content filtering system with EasyRouter integration and frontend personalization

**Architecture:** Three-tier whitelist router distributes 500 raw items across direct-publish (Tier 0), AI-only analysis (Tier 1), and full filtering (Tier 2) pipelines. Language detection routes to appropriate models via EasyRouter. Frontend calculates personalized scores from localStorage preferences.

**Tech Stack:** Python 3.11+, EasyRouter API, GLM-4-Flash, DeepSeek-V4 Pro, GPT-4o Mini, YAML, Vue.js

---

## Task 1: Project Structure Setup

**Files:**
- Create: `scripts/ai_filter/__init__.py`
- Create: `scripts/ai_filter/whitelist_router.py`
- Create: `scripts/ai_filter/tier0_processor.py`
- Create: `scripts/ai_filter/tier1_filter.py`
- Create: `scripts/ai_filter/tier2_pipeline.py`
- Create: `scripts/ai_filter/easyrouter_client.py`
- Create: `scripts/ai_filter/language_detector.py`
- Create: `tests/test_ai_filter/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p scripts/ai_filter
mkdir -p tests/test_ai_filter
touch scripts/ai_filter/__init__.py
touch tests/test_ai_filter/__init__.py
```

- [ ] **Step 2: Create .env.example for API keys**

```bash
cat > .env.example << 'EOF'
# EasyRouter Configuration
EASYROUTER_API_KEY=your_api_key_here
EASYROUTER_BASE_URL=https://api.easyrouter.ai/v1

# AI Filter Toggle
AI_FILTER_ENABLED=1

# Model Configuration
AI_MODEL_CLASSIFY=glm-4-flash
AI_MODEL_ANALYZE_ZH=deepseek-chat
AI_MODEL_ANALYZE_EN=gpt-4o-mini
EOF
```

- [ ] **Step 3: Verify structure**

```bash
tree scripts/ai_filter tests/test_ai_filter
```

Expected output showing empty directories with `__init__.py` files

- [ ] **Step 4: Commit**

```bash
git add scripts/ai_filter/ tests/test_ai_filter/ .env.example
git commit -m "feat(ai-filter): create project structure for AI filtering system

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 2: Language Detector Module

**Files:**
- Create: `scripts/ai_filter/language_detector.py`
- Create: `tests/test_ai_filter/test_language_detector.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_ai_filter/test_language_detector.py
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
```

- [ ] **Step 2: Run test to verify failure**

```bash
pytest tests/test_ai_filter/test_language_detector.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'scripts.ai_filter.language_detector'"

- [ ] **Step 3: Implement language detector**

```python
# scripts/ai_filter/language_detector.py
import re
from typing import Literal


# Whitelist mappings
CN_SOURCES = {'少数派', '掘金', '优设网', 'sspai', 'juejin', 'uisdc', 'ai hot', 'aihot', '秋芝2046'}
EN_SOURCES = {'openai', 'anthropic', 'google', 'figma', 'ux collective', 'codrops', 
              'awwwards', 'muzli', 'sidebar', 'webdesigner'}


def detect_language(title: str, source: str, site_name: str) -> Literal["zh", "en"]:
    """
    Detect content language by whitelist + character ratio.
    
    Args:
        title: Article title
        source: Source name
        site_name: Site domain name
        
    Returns:
        "zh" for Chinese, "en" for English
    """
    combined_text = f"{title} {source} {site_name}".lower()
    
    # Check whitelist first (highest priority)
    for cn_keyword in CN_SOURCES:
        if cn_keyword in combined_text:
            return "zh"
    
    for en_keyword in EN_SOURCES:
        if en_keyword in combined_text:
            return "en"
    
    # Fallback: character ratio analysis
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', combined_text))
    english_chars = len(re.findall(r'[a-zA-Z]', combined_text))
    total_chars = chinese_chars + english_chars
    
    if total_chars == 0:
        return "en"  # Default to English if no detectable characters
    
    chinese_ratio = chinese_chars / total_chars
    
    # >40% Chinese = zh, otherwise en
    return "zh" if chinese_ratio > 0.4 else "en"
```

- [ ] **Step 4: Run test to verify pass**

```bash
pytest tests/test_ai_filter/test_language_detector.py -v
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/ai_filter/language_detector.py tests/test_ai_filter/test_language_detector.py
git commit -m "feat(ai-filter): implement language detection with whitelist priority

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 3: EasyRouter Client Wrapper

**Files:**
- Create: `scripts/ai_filter/easyrouter_client.py`
- Create: `tests/test_ai_filter/test_easyrouter_client.py`

- [ ] **Step 1: Write failing test with mocking**

```python
# tests/test_ai_filter/test_easyrouter_client.py
import pytest
from unittest.mock import Mock, patch
from scripts.ai_filter.easyrouter_client import EasyRouterClient


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("EASYROUTER_API_KEY", "test_key_123")
    monkeypatch.setenv("EASYROUTER_BASE_URL", "https://test.api.com/v1")


def test_client_initialization(mock_env):
    """Client should initialize with environment variables"""
    client = EasyRouterClient()
    assert client.api_key == "test_key_123"
    assert client.base_url == "https://test.api.com/v1"


@patch('requests.post')
def test_call_model_success(mock_post, mock_env):
    """Client should make successful API call"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {"total_tokens": 100}
    }
    mock_post.return_value = mock_response
    
    client = EasyRouterClient()
    result = client.call_model(
        model="glm-4-flash",
        system_prompt="You are a classifier",
        user_prompt="Classify this",
        temperature=0.3
    )
    
    assert result["content"] == "Test response"
    assert result["tokens"] == 100
    mock_post.assert_called_once()


@patch('requests.post')
def test_call_model_handles_api_error(mock_post, mock_env):
    """Client should handle API errors gracefully"""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response
    
    client = EasyRouterClient()
    
    with pytest.raises(Exception) as exc_info:
        client.call_model(
            model="glm-4-flash",
            system_prompt="Test",
            user_prompt="Test"
        )
    
    assert "API call failed" in str(exc_info.value)
```

- [ ] **Step 2: Run test to verify failure**

```bash
pytest tests/test_ai_filter/test_easyrouter_client.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement EasyRouter client**

```python
# scripts/ai_filter/easyrouter_client.py
import os
import requests
from typing import Dict, Any, Optional


class EasyRouterClient:
    """
    Unified client for EasyRouter API (OpenAI-compatible format).
    Supports GLM-4-Flash, DeepSeek-V4 Pro, GPT-4o Mini.
    """
    
    def __init__(self):
        self.api_key = os.getenv("EASYROUTER_API_KEY")
        self.base_url = os.getenv("EASYROUTER_BASE_URL", "https://api.easyrouter.ai/v1")
        
        if not self.api_key:
            raise ValueError("EASYROUTER_API_KEY environment variable not set")
    
    def call_model(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Call EasyRouter API with OpenAI-compatible format.
        
        Args:
            model: Model name (glm-4-flash, deepseek-chat, gpt-4o-mini)
            system_prompt: System instruction
            user_prompt: User query
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response tokens
            
        Returns:
            Dict with 'content' (response text) and 'tokens' (usage count)
            
        Raises:
            Exception: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"API call failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            return {
                "content": data["choices"][0]["message"]["content"],
                "tokens": data.get("usage", {}).get("total_tokens", 0)
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request error: {str(e)}")
```

- [ ] **Step 4: Run test to verify pass**

```bash
pytest tests/test_ai_filter/test_easyrouter_client.py -v
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/ai_filter/easyrouter_client.py tests/test_ai_filter/test_easyrouter_client.py
git commit -m "feat(ai-filter): implement EasyRouter API client wrapper

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

(继续包含所有13个任务的完整内容...)
