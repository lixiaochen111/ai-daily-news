# AI筛选系统完整逻辑文档

> **最后更新**: 2026-05-17  
> **版本**: v1.0  
> **目的**: 记录AI筛选系统的完整架构，避免逻辑混乱

---

## 📋 设计原则

1. **白名单优先**: 根据来源特点分层处理，避免一刀切
2. **成本优化**: 免费模型初筛 → 付费模型精筛
3. **语言感知**: 中文/英文内容路由到不同模型
4. **质量优先**: 宁可多花钱，不漏好内容

---

## 🎯 完整筛选流程

```
┌────────────────────────────────────────────────────────────────┐
│ 步骤1: RSS抓取                                                  │
│ - 从OPML/配置读取所有RSS源                                      │
│ - 并行抓取，获取原始数据                                        │
│ - 输出: latest_items_all (所有原始内容)                        │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ 步骤2: 基础预处理                                               │
│ - 标准化字段格式                                                │
│ - 时间过滤（24小时内）                                          │
│ - 去除明显无效内容                                              │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ 步骤3: 白名单路由 ⚡ 关键步骤                                   │
│ WhitelistRouter.classify_item()                                │
│ - 读取 config/source-whitelist.yaml                            │
│ - 根据 source/url/title 匹配 patterns                          │
│ - 分类为 Tier -1/0/1/2                                         │
│ - 优先级: 黑名单 > Tier 0 > Tier 1 > Tier 2 > 默认Tier 2      │
└──────────────────────┬─────────────────────────────────────────┘
                       │
          ┌────────────┼────────────┬──────────────┐
          ▼            ▼            ▼              ▼
     [黑名单]     [Tier 0]     [Tier 1]       [Tier 2]
      删除        编辑精选      高质量源        广域源
          │            │            │              │
          │            │            │              │
          X            │            │              ▼
                       │            │         ┌─────────────┐
                       │            │         │ 3.1 关键词筛选│
                       │            │         │ - 本地匹配    │
                       │            │         │ - BASE_KEYWORDS│
                       │            │         │ - filter_focus│
                       │            │         │ - exclude_topics│
                       │            │         │ 100条 → 30条  │
                       │            │         └──────┬────────┘
                       │            │                │
                       │            │                ▼
                       │            │         ┌─────────────┐
                       │            │         │ 3.2 GLM初筛  │
                       │            │         │ - GLM-4-Flash│
                       │            │         │ - 免费模型    │
                       │            │         │ - 快速分类    │
                       │            │         │ 30条 → 15条  │
                       │            │         └──────┬────────┘
                       │            │                │
                       ▼            ▼                ▼
                  ┌────────────────────────────────────┐
                  │ 步骤4: 深度AI分析（付费）            │
                  │ ✅ Tier 0: 跳过（直接输出）         │
                  │ ✅ Tier 1: 直接深度分析（10条）     │
                  │ ✅ Tier 2: 通过初筛后分析（15条）   │
                  │                                     │
                  │ 语言检测:                           │
                  │  - detect_language()               │
                  │  - 基于 whitelist + 字符比例        │
                  │                                     │
                  │ 模型路由:                           │
                  │  - 中文 → DeepSeek (¥1/M tokens)  │
                  │  - 英文 → GPT-4o Mini ($0.15/M)   │
                  │                                     │
                  │ 分析输出:                           │
                  │  - design_relevance (0-10)         │
                  │  - quality_score (0-10)            │
                  │  - tags (数组)                      │
                  │  - reasoning (文本)                 │
                  │                                     │
                  │ 过滤阈值:                           │
                  │  - Tier 1: relevance >= 0.6       │
                  │  - Tier 2: relevance >= 0.7       │
                  └──────────────┬──────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│ 步骤5: 合并结果                                                 │
│ - Tier 0 内容直接添加（含 _tier=0 元数据）                     │
│ - Tier 1 通过深度分析的内容（含 _tier=1 元数据）               │
│ - Tier 2 通过三阶段筛选的内容（含 _tier=2 元数据）             │
│ - 输出: filtered_items                                         │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ 步骤6: AI相关性打标签 ⚠️ 注意：仅打标签，不过滤                │
│ add_ai_relevance_fields()                                      │
│ - 基于AI_KEYWORDS关键词匹配                                    │
│ - 添加 ai_is_related (布尔值)                                  │
│ - 添加 ai_score (0-1分数)                                      │
│ - ❌ 不删除任何内容！                                           │
│ - ✅ 仅用于前端显示"AI强相关"徽章                              │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ 步骤7: 后续处理                                                 │
│ - 双语翻译（标题翻译）                                          │
│ - 去重处理                                                      │
│ - 生成 data/news.json                                          │
│ - Git commit & push                                            │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎨 三个层级的详细设计

### Tier 0: 编辑精选源

**特点**:
- 编辑团队已经人工筛选
- 内容密度高，质量有保障
- 无需AI判断

**示例源**:
- UX Collective (Medium编辑精选)
- Codrops (创意前端案例)
- Awwwards (设计奖项获奖作品)

**处理流程**:
```
输入 → 添加元数据 → 输出
```

**成本**: ¥0 (无AI调用)

**预计量**: 40条/天

---

### Tier 1: 高质量源

**特点**:
- 内容质量高，但主题范围广
- 不是所有内容都相关AI/设计
- 需要AI判断相关性
- **内容量少（10-20条/天）**

**示例源**:
- 优设网（部分设计教程）
- 少数派（科技+生活方式）
- UX Collective Weekly (精选newsletter)

**处理流程**:
```
输入 → 深度AI分析 → 过滤 → 输出
```

**为什么不需要GLM初筛？**
1. 内容量少（10-20条），直接深度分析成本可控
2. 质量高，误删成本高
3. 一次深度分析比"GLM初筛+深度分析"更可靠

**成本**: ¥0.02/天 (10条 × ¥0.002/条)

**预计量**: 10条/天（输入） → 6条/天（输出，60%通过率）

---

### Tier 2: 广域官方源

**特点**:
- 内容广泛（产品公告、技术博客、招聘等）
- 需要多阶段筛选
- **内容量大（100条+/天）**

**示例源**:
- Figma Blog (产品更新+设计教程)
- OpenAI Blog (AI研究+产品)
- Google AI Blog (技术论文+应用)

**处理流程**:
```
输入 (100条)
  ↓ 关键词筛选 (免费，本地)
30条通过
  ↓ GLM-4-Flash分类 (免费)
15条通过
  ↓ 深度AI分析 (付费)
10条通过
```

**为什么需要GLM初筛？**
1. 内容量大，关键词筛选后仍有30条
2. 直接深度分析成本高（30条 × ¥0.002 = ¥0.06）
3. GLM免费，可以快速筛掉明显无关内容
4. 最终深度分析只需15条（¥0.03），省50%成本

**成本**: ¥0.23/天
- GLM初筛: ¥0 (免费)
- 深度分析: 60条 × ¥0.004 = ¥0.24

**预计量**: 100条/天（输入） → 60条/天（输出，10%通过率）

---

## 💰 成本估算（每日）

| Tier | AI调用 | 数量 | 单价 | 成本 |
|------|--------|------|------|------|
| Tier 0 | - | - | - | ¥0 |
| Tier 1 | 深度分析 | 10条 | ¥0.002 | ¥0.02 |
| Tier 2-GLM | GLM-4-Flash | 30条 | ¥0 (免费?) | ¥0 |
| Tier 2-深度 | DeepSeek/GPT | 15条 | ¥0.004 | ¥0.06 |
| **总计** | - | - | - | **¥0.08/天** |

⚠️ **注意**: 需要确认GLM-4-Flash是否真的免费！

---

## 🔧 关键技术点

### 1. 白名单匹配逻辑

```python
# WhitelistRouter.classify_item()
def classify_item(item):
    source = item.get("source", "").lower()
    url = item.get("url", "").lower()
    title = item.get("title", "").lower()
    combined = f"{source} {url} {title}"
    
    # 优先级顺序
    # 1. 黑名单（最高优先级）
    for blacklist_source in blacklist_sources:
        for pattern in blacklist_source["patterns"]:
            if pattern.lower() in combined:
                return (-1, None)
    
    # 2. Tier 0
    for tier0_source in tier_0_sources:
        for pattern in tier0_source["patterns"]:
            if pattern.lower() in combined:
                return (0, tier0_source)
    
    # 3. Tier 1
    for tier1_source in tier_1_sources:
        for pattern in tier1_source["patterns"]:
            if pattern.lower() in combined:
                return (1, tier1_source)
    
    # 4. Tier 2
    for tier2_source in tier_2_sources:
        for pattern in tier2_source["patterns"]:
            if pattern.lower() in combined:
                return (2, tier2_source)
    
    # 5. 默认 Tier 2
    return (2, None)
```

### 2. 语言检测逻辑

```python
# language_detector.py
def detect_language(title, source, site_name):
    combined = f"{title} {source} {site_name}".lower()
    
    # 1. 白名单优先（高置信度）
    if any(kw in combined for kw in CN_SOURCES):
        return "zh"
    if any(kw in combined for kw in EN_SOURCES):
        return "en"
    
    # 2. 字符比例分析（后备）
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', combined))
    english_chars = len(re.findall(r'[a-zA-Z]', combined))
    total = chinese_chars + english_chars
    
    if total == 0:
        return "en"  # 默认英文
    
    chinese_ratio = chinese_chars / total
    return "zh" if chinese_ratio > 0.12 else "en"
```

### 3. GLM-4-Flash分类Prompt

```python
system_prompt = "你是一个AI内容分类器，专注于判断内容是否与AI+设计相关。"

user_prompt = """
请判断以下内容是否与"AI+设计"主题相关。

标题: {title}
来源: {source}

返回JSON格式:
{
  "is_relevant": true/false,
  "reason": "简短理由"
}
"""

# 调用GLM-4-Flash
response = client.call_model(
    model="glm-4-flash",
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    temperature=0.1,  # 低温度，保持一致性
    max_tokens=200
)
```

### 4. 深度分析Prompt

```python
system_prompt = "You are a professional AI content analyst specializing in design and technology."

user_prompt = """
Analyze this content for AI/design relevance:

Title: {title}
Source: {source}
Summary: {summary}

Rate on 0-10 scale and return JSON:
{
  "design_relevance": 0-10,
  "quality_score": 0-10,
  "tags": ["tag1", "tag2"],
  "reasoning": "brief explanation"
}
"""

# 语言路由
model = "deepseek-chat" if language == "zh" else "gpt-4o-mini"

response = client.call_model(
    model=model,
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    temperature=0.3,
    max_tokens=500
)
```

---

## ⚠️ 常见误区

### 误区1: ai_relevance.py用于过滤

❌ **错误做法**:
```python
# update_news.py
latest_items = [item for item in latest_items_all 
                if item.get("ai_is_related")]  # ❌ 删除内容
```

✅ **正确做法**:
```python
# update_news.py
# 1. AI筛选管道处理
latest_items = ai_filter.filter_batch(latest_items_all)

# 2. ai_relevance仅打标签
for item in latest_items:
    add_ai_relevance_fields(item)  # 添加ai_is_related字段

# 3. 前端根据标签切换视图
```

### 误区2: Tier 1需要GLM初筛

❌ **错误逻辑**:
- Tier 1内容少（10条）
- 先GLM初筛（10条 → 5条）
- 再深度分析（5条）
- 总成本：0 + ¥0.01 = ¥0.01
- **问题**: GLM误删了有价值内容

✅ **正确逻辑**:
- Tier 1直接深度分析（10条）
- 总成本：¥0.02
- **优势**: 准确率高，不漏掉好内容
- **成本差**: 只贵¥0.01，但质量更可靠

### 误区3: 白名单在AI筛选之后

❌ **错误顺序**:
```
RSS抓取 → ai_relevance过滤 → AI筛选管道
```
**问题**: ai_relevance已经删除了非AI内容，白名单的设计类源无法生效

✅ **正确顺序**:
```
RSS抓取 → 白名单路由 → 各层级筛选 → ai_relevance打标签
```

---

## 🧪 测试验证清单

在修改代码前，确保测试：

- [ ] 白名单匹配准确率（Tier 0/1/2分类正确）
- [ ] Tier 0内容直接输出（无AI调用）
- [ ] Tier 1直接深度分析（无GLM初筛）
- [ ] Tier 2三阶段完整执行
- [ ] 语言检测准确率（中文/英文路由）
- [ ] ai_relevance不删除内容（仅打标签）
- [ ] GLM-4-Flash实际成本（是否免费？）
- [ ] 每日总成本 <= ¥0.30

---

## 📝 代码修改检查表

### 需要修改的文件

1. **update_news.py**
   - [ ] 删除 `ai_is_related` 过滤（步骤4）
   - [ ] 保留 `add_ai_relevance_fields()`（步骤6，仅打标签）
   - [ ] 在步骤3之前调用 AI筛选管道

2. **scripts/ai_filter/tier1_filter.py**
   - [ ] 确认不包含GLM初筛
   - [ ] 直接调用深度分析

3. **scripts/ai_filter/tier2_pipeline.py**
   - [ ] 确认包含三阶段：关键词→GLM→深度分析

4. **scripts/ai_filter/main_filter.py**
   - [ ] 确认白名单路由在最开始

5. **config/source-whitelist.yaml**
   - [ ] 确认所有源正确分层

---

## 🔮 未来优化方向

1. **成本监控**
   - 添加每日API调用统计
   - 记录到 `data/ai-filter-stats.json`
   - 前端展示成本趋势

2. **A/B测试**
   - Tier 1 GLM初筛 vs 直接深度分析
   - 对比准确率和成本

3. **模型优化**
   - 测试其他免费分类模型
   - 评估是否需要fine-tune

4. **白名单维护**
   - 定期审查源分层
   - 根据实际效果调整

---

## 📚 相关文档

- [AI Filter Implementation Plan](./superpowers/plans/2026-05-17-ai-content-filtering.md)
- [AI Filter Design Spec](./superpowers/specs/2026-05-17-ai-content-filtering-design.md)
- [AI Filter Usage Guide](./AI_FILTER_GUIDE.md)
- [Source Coverage Documentation](./SOURCE_COVERAGE.md)

---

## 🆘 故障排查

### 问题1: AI筛选没有生效

**症状**: 输出的内容和之前一样

**检查**:
```bash
# 1. 确认环境变量
cat .env | grep AI_FILTER

# 2. 确认配置文件存在
ls -la config/source-whitelist.yaml

# 3. 查看日志
# 应该能看到"AI filter stats"
```

### 问题2: 成本过高

**症状**: EasyRouter账单超出预算

**检查**:
```python
# 查看filter_stats
{
  "tier_0": 40,  # 无成本
  "tier_1": 10,  # 10 × ¥0.002 = ¥0.02
  "tier_2": 60,  # 15 × ¥0.004 = ¥0.06
}

# 如果tier_1或tier_2数量异常，检查白名单配置
```

### 问题3: GLM-4-Flash报错

**症状**: `Model not found: glm-4-flash`

**可能原因**:
1. EasyRouter不支持此模型
2. 模型名称拼写错误
3. 需要升级账户

**解决方案**:
```bash
# 更换为其他免费模型
export AI_MODEL_CLASSIFY="gpt-4o-mini"
```

---

**文档维护**: 每次修改筛选逻辑时，务必更新此文档！
