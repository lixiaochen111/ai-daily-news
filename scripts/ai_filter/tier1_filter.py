"""
Tier 1 Filter - AI-Only Analysis

For high-quality sources (优设网, UX Collective Weekly) that need AI to judge relevance.
Skips keyword filtering and goes directly to deep AI analysis.

Filter criteria:
- design_relevance >= 0.6 OR quality_score >= 7
- Language detection: Chinese → DeepSeek, English → GPT-4o Mini
"""
import json
import os
from typing import Dict, Any, Optional

from scripts.ai_filter.easyrouter_client import EasyRouterClient
from scripts.ai_filter.glm_client import GLMClient
from scripts.ai_filter.language_detector import detect_language
from scripts.ai_filter.prompts import build_analysis_prompt


class Tier1Filter:
    """
    Tier 1 过滤器：仅AI深度分析

    用于优设网、UX Collective Weekly等高质量源。
    这些源内容质量高，但需要AI判断相关性。
    """

    def __init__(self):
        """Initialize Tier 1 filter with EasyRouter client and model configuration."""
        self.client = EasyRouterClient()
        self.glm_client = GLMClient()

        # Model configuration from environment variables
        self.model_zh = os.getenv("AI_MODEL_ANALYZE_ZH", "deepseek-v4-pro")
        self.model_en = os.getenv("AI_MODEL_ANALYZE_EN", "deepseek-v4-pro")

        # Filter thresholds
        self.design_relevance_threshold = 0.6  # 6/10 normalized to 0-1
        self.quality_score_threshold = 7       # 7/10

    def filter_item(self, item: Dict[str, Any], source_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Filter a single item using AI-only analysis.

        Args:
            item: Content item with title, url, source, site_name
            source_config: Source configuration dictionary (can be None)

        Returns:
            Enriched item with AI metadata if accepted, None if rejected
        """
        # Handle missing source_config
        if source_config is None:
            source_config = {}
        # Detect language
        language = detect_language(
            title=item.get("title", ""),
            source=item.get("source", ""),
            site_name=item.get("site_name", "")
        )

        # Select model based on language
        model = self.model_zh if language == "zh" else self.model_en

        # Build analysis prompt
        system_prompt = "You are a professional AI content analyst specializing in design and technology."
        user_prompt = build_analysis_prompt(
            title=item.get("title", ""),
            source=item.get("source", ""),
            summary=item.get("summary"),
            language=language
        )

        # Call AI for deep analysis
        try:
            response = self.client.call_model(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=500
            )

            # Parse AI response (robust JSON extraction)
            import re
            content = response["content"]
            ai_analysis = None

            # Strategy 1: Direct JSON parse
            try:
                ai_analysis = json.loads(content)
            except json.JSONDecodeError:
                pass

            # Strategy 2: Extract from first { to last }
            if not ai_analysis:
                first_brace = content.find('{')
                last_brace = content.rfind('}')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    json_candidate = content[first_brace:last_brace+1]
                    try:
                        ai_analysis = json.loads(json_candidate)
                    except json.JSONDecodeError:
                        pass

            # Strategy 3: Find JSON with design_relevance (support nested arrays)
            if not ai_analysis:
                json_match = re.search(r'\{.*?"design_relevance".*?\}', content, re.DOTALL)
                if json_match:
                    try:
                        ai_analysis = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        pass

            if not ai_analysis:
                print(f"⚠️  Tier 1 AI response unparseable: {content[:100]}...")
                return None

            # Extract scores
            design_relevance = ai_analysis.get("design_relevance", 0)  # 0-10 scale
            quality_score = ai_analysis.get("quality_score", 0)        # 0-10 scale

            # Normalize design_relevance to 0-1 scale
            design_relevance_normalized = design_relevance / 10.0

            # Apply filter criteria: design_relevance >= 0.6 OR quality_score >= 7
            if design_relevance_normalized >= self.design_relevance_threshold or quality_score >= self.quality_score_threshold:
                # Accept: enrich item with AI metadata
                enriched_item = item.copy()

                # Add tier tracking
                enriched_item["_tier"] = 1
                enriched_item["ai_tier"] = 1
                enriched_item["_source_config"] = source_config

                # Add AI analysis metadata
                enriched_item["ai_design_relevance"] = design_relevance_normalized
                enriched_item["ai_quality_score"] = quality_score
                enriched_item["ai_categories"] = ai_analysis.get("categories", [])
                enriched_item["ai_target_audience"] = ai_analysis.get("target_audience", "")
                enriched_item["ai_key_insights"] = ai_analysis.get("key_insights", "")
                enriched_item["ai_recommendation"] = ai_analysis.get("recommendation", "")

                return enriched_item
            else:
                # Reject: low relevance and low quality
                return None

        except (ValueError, Exception) as e:
            print(f"⚠️  Tier 1 EasyRouter failed: {e}, falling back to GLM")
            return self._glm_fallback_analysis(item, source_config, language)

    def _glm_fallback_analysis(self, item: Dict[str, Any], source_config: Dict[str, Any], language: str) -> Optional[Dict[str, Any]]:
        """Fallback to GLM when EasyRouter is unavailable."""
        try:
            user_prompt = build_analysis_prompt(
                title=item.get("title", ""),
                source=item.get("source", ""),
                summary=item.get("summary"),
                language=language
            )
            response = self.glm_client.call_model(
                model="glm-4-flash",
                system_prompt="You are a professional AI content analyst specializing in design and technology.",
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=500
            )

            import re
            content = response["content"]
            ai_analysis = None

            try:
                ai_analysis = json.loads(content)
            except json.JSONDecodeError:
                pass

            if not ai_analysis:
                first_brace = content.find('{')
                last_brace = content.rfind('}')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    try:
                        ai_analysis = json.loads(content[first_brace:last_brace+1])
                    except json.JSONDecodeError:
                        pass

            if not ai_analysis:
                return None

            design_relevance = ai_analysis.get("design_relevance", 0) / 10.0
            quality_score = ai_analysis.get("quality_score", 0)

            if design_relevance >= self.design_relevance_threshold or quality_score >= self.quality_score_threshold:
                enriched_item = item.copy()
                enriched_item["_tier"] = 1
                enriched_item["ai_tier"] = 1
                enriched_item["_source_config"] = source_config
                enriched_item["ai_design_relevance"] = design_relevance
                enriched_item["ai_quality_score"] = quality_score
                enriched_item["ai_categories"] = ai_analysis.get("categories", [])
                enriched_item["ai_fallback"] = "glm"
                return enriched_item

            return None
        except Exception as e2:
            print(f"⚠️  Tier 1 GLM fallback also failed: {e2}")
            return None
