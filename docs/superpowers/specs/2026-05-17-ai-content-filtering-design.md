# AI内容筛选系统设计规范

> 设计日期：2026-05-17  
> 目标：为AI设计情报站建立智能内容筛选系统  
> 用户定位：UI/UX设计师、AI设计工具关注者

---

## 一、系统目标

构建三级内容筛选系统，实现：
1. **精准筛选**：从500条原始内容中筛选出15-23条高质量内容
2. **成本可控**：每日AI调用成本控制在¥0.25以内
3. **个性化推荐**：基于用户反馈动态调整推荐权重
4. **稳定可靠**：使用国产模型，避免网络问题

---

## 二、核心架构

### 2.1 三级白名单系统

```
原始内容（500条）
    ↓
┌─────────────────────────────────────┐
│  三级白名单路由                       │
│  - Tier 0: 编辑精选源（8个）          │
│  - Tier 1: 高质量源（2个）            │
│  - Tier 2: 广域官方源（6个）          │
└─────────────────────────────────────┘
    ↓          ↓           ↓
  Tier 0     Tier 1      Tier 2
 (直接发布)  (AI分析)  (完整筛选)
```

**Tier 0：编辑精选源（8个）**
- UX Collective, Codrops, Web Designer Depot
- Awwwards, Muzli, Sidebar, Webdesigner News
- 秋芝2046
- **处理：** 内容整理 → 直接发布
- **预期：** 8-12条/天

**Tier 1：高质量源（2个）**
- 优设网, UX Collective Weekly
- **处理：** 跳过关键词 → AI深度分析 → 发布
- **预期：** 2-3条/天

**Tier 2：广域官方源（6个）**
- Figma, OpenAI, Anthropic（只要新产品发布）
- 少数派, 掘金（只要AI coding）
- AI HOT（综合关注）
- **处理：** 关键词初筛 → AI深度分析 → 发布
- **预期：** 5-8条/天

---

### 2.2 AI模型配置

**EasyRouter统一接入：**
- 阶段2（分类）：GLM-4-Flash（免费）
- 阶段3（深度分析）：
  - 中文内容 → DeepSeek-V4 Pro
  - 英文内容 → GPT-4o Mini

**语言检测规则：**
```python
# 中文字符占比 > 40% → 中文
# 英文字符占比 > 60% → 英文
# 白名单源优先级：少数派、优设网 → 中文
```

---

### 2.3 处理流程

```
[Tier 0] 编辑精选源
→ 内容整理（摘要/翻译）
→ 标记为必发布
→ 输出

[Tier 1] 高质量源
→ AI深度分析（DeepSeek/GPT-4o）
→ 筛选（design_relevance >= 0.6 或 quality >= 7）
→ 输出

[Tier 2] 广域官方源
→ 关键词初筛（ai_relevance.py）
→ GLM-4-Flash快速分类
→ AI深度分析（按语言路由）
→ 筛选（design_relevance >= 0.7）
→ 输出

最终合并 → latest-24h-ai-filtered.json
```

---

## 三、数据结构

### 3.1 AI分析输出

```json
{
  "title": "原始标题",
  "url": "https://...",
  "published_at": "2026-05-17T10:00:00Z",
  "source": "来源名称",
  
  "_tier": 0,
  "_source_config": {...},
  
  "ai_design_relevance": 0.85,
  "ai_quality_score": 8,
  "ai_categories": ["design_tool", "tutorial"],
  "ai_recommendation": "Figma新增AI生成UI组件功能",
  "ai_reasoning": "设计师核心工具重大更新",
  "ai_topic_potential": 0.7,
  "ai_model_used": "deepseek-v4-pro",
  "ai_language": "zh",
  "ai_tier": 0,
  "ai_must_publish": true
}
```

### 3.2 用户偏好存储

```javascript
// localStorage
{
  "version": 1,
  "category_weights": {
    "design_tool": 1.2,
    "tutorial": 1.5,
    "inspiration": 0.6,
    "ai_drawing": 1.0,
    "model_release": 0.8,
    "industry_news": 0.3
  },
  "quality_preference": 0.8,
  "interaction_stats": {
    "total_clicks": 45,
    "interested_clicks": 30,
    "not_interested_clicks": 15
  }
}
```

---

## 四、前端个性化引擎

### 4.1 个性化评分算法

```javascript
personalizedScore = 
  quality_score
  × (0.5 + design_relevance × 0.5)
  × categoryPreferenceWeight
  × freshnessMultiplier
```

### 4.2 反馈更新逻辑

**用户点击"感兴趣"：**
- 对应category权重 × 1.1（上限3.0）
- 高质量内容（>=8分）：quality_preference += 0.05

**用户点击"不感兴趣"：**
- 对应category权重 × 0.85（下限0.1）
- 高质量内容（>=8分）：quality_preference -= 0.05

---

## 五、成本预估

| 阶段 | 模型 | 调用量 | 单价 | 成本 |
|------|------|--------|------|------|
| Tier 0 | - | - | - | ¥0 |
| Tier 1 | DeepSeek/GPT-4o | 10条 | - | ¥0.02 |
| Tier 2-GLM | GLM-4-Flash | 20批 | 免费 | ¥0 |
| Tier 2-分析 | DeepSeek/GPT-4o | 60条 | - | ¥0.23 |
| **总计** | - | - | - | **¥0.25/天** |

---

## 六、技术栈

- **后端：** Python 3.11+
- **AI平台：** EasyRouter（统一API）
- **模型：** GLM-4-Flash + DeepSeek-V4 Pro + GPT-4o Mini
- **配置：** YAML
- **前端：** Vue.js + localStorage
- **数据格式：** JSON

---

## 七、文件结构

```
ai-daily-news/
├── config/
│   └── source-whitelist.yaml          # 三级白名单配置
├── scripts/
│   ├── ai_filter/
│   │   ├── __init__.py
│   │   ├── whitelist_router.py        # 白名单路由器
│   │   ├── tier0_processor.py         # Tier 0处理器
│   │   ├── tier1_filter.py            # Tier 1过滤器
│   │   ├── tier2_pipeline.py          # Tier 2完整流程
│   │   └── easyrouter_client.py       # EasyRouter客户端
│   └── update_news.py                 # 主程序（集成AI筛选）
├── assets/
│   ├── app.js                         # 前端（添加个性化引擎）
│   └── personalization.js             # 个性化模块（新建）
└── tests/
    └── test_ai_filter/                # 测试文件
```

---

## 八、环境变量

```bash
# EasyRouter配置
EASYROUTER_API_KEY=your_api_key
EASYROUTER_BASE_URL=https://api.easyrouter.ai/v1

# AI筛选开关
AI_FILTER_ENABLED=1

# 模型配置
AI_MODEL_CLASSIFY=glm-4-flash
AI_MODEL_ANALYZE_ZH=deepseek-chat
AI_MODEL_ANALYZE_EN=gpt-4o-mini
```

---

## 九、验收标准

1. **筛选效果**
   - 每日输出15-23条高质量内容
   - Tier 0内容全部发布（8-12条）
   - Tier 1+2经AI筛选后输出7-11条
   - 设计相关内容占比60%+

2. **成本控制**
   - 每日AI调用成本 <= ¥0.25
   - GLM-4-Flash使用免费额度
   - DeepSeek/GPT-4o调用量 <= 80条

3. **用户体验**
   - 个性化推荐立即生效
   - "感兴趣/不感兴趣"反馈可见变化
   - 页面加载速度不受影响

4. **系统稳定**
   - API调用失败率 < 5%
   - 有降级方案（AI失败时保留原内容）
   - 日志完整可追溯

---

## 十、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| API限流 | 筛选失败 | 降级到保留所有内容 |
| 成本超支 | 预算超标 | 设置每日调用上限 |
| 误杀高质量内容 | 用户体验差 | Tier 0白名单直接发布 |
| 语言检测错误 | 模型选择错误 | 白名单源优先级规则 |
| localStorage丢失 | 偏好重置 | 默认权重设计合理 |

---

## 十一、后续优化方向

1. **短期（1-2周）**
   - 添加详细日志和监控
   - 优化Prompt提升AI准确度
   - 完善测试覆盖

2. **中期（1-2月）**
   - 支持用户手动调整category权重
   - 添加"收藏"功能影响推荐
   - 实现A/B测试不同算法

3. **长期（3月+）**
   - 协同过滤（类似用户推荐）
   - 内容去重和聚合
   - 多语言支持优化
