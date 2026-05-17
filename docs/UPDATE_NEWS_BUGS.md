# update_news.py 筛选流程漏洞分析

> **发现时间**: 2026-05-17  
> **严重级别**: 🔴 Critical  
> **影响**: 白名单三级筛选完全失效

---

## 🚨 漏洞列表

### 漏洞1: add_ai_relevance_fields时机错误 ⚠️ 严重

**位置**: `update_news.py:3113`

**当前代码**:
```python
# 在RSS抓取阶段
normalized = add_ai_relevance_fields(normalized)
latest_items_all.append(normalized)
```

**问题**:
- 给所有内容添加`ai_is_related`字段
- 为3119行的过滤提供了依据
- 应该在**AI筛选之后**打标签

**影响**: 为后续错误过滤埋下伏笔

---

### 漏洞2: ai_is_related致命过滤 🔴 Critical

**位置**: `update_news.py:3119`

**当前代码**:
```python
latest_items = [record for record in latest_items_all 
                if record.get("ai_is_related", is_ai_related_record(record))]
```

**问题**:
1. **删除所有非AI关键词内容**
2. **导致白名单Tier 0/1/2完全失效**
3. **设计类、UI类内容被提前过滤**

**具体案例**:
```python
# Figma Blog: "New Color Palette System"
{
  "title": "New Color Palette System",
  "source": "Figma Blog",
  "url": "https://figma.com/blog/...",
  "ai_is_related": False  # ❌ 没有AI关键词
}

# 3119行：直接删除
# Tier 2配置的Figma源永远收不到这篇内容
```

**影响**:
- Tier 0/1/2源配置的非AI内容全部丢失
- 用户看不到纯设计、UI、产品类更新
- 白名单系统形同虚设

---

### 漏洞3: 统计数据错误 ⚠️ 中等

**位置**: `update_news.py:3123-3126`

**当前代码**:
```python
latest_items_before_filter = len(latest_items)  # ❌ 已被ai_is_related过滤
latest_items = ai_filter.filter_batch(latest_items)
filter_stats["items_before_filter"] = latest_items_before_filter
```

**问题**:
- `items_before_filter`不是真实RSS抓取数量
- 是被`ai_is_related`过滤后的数量
- 导致统计不准确

**正确做法**:
```python
items_before_filter = len(latest_items_all)  # RSS抓取的真实数量
```

**影响**:
- 无法准确评估AI筛选效果
- 通过率计算错误

---

### 漏洞4: latest_items_all被错误修改 ⚠️ 中等

**位置**: `update_news.py:3134-3140`

**当前代码**:
```python
latest_items, latest_items_all, title_cache = add_bilingual_fields(
    latest_items,      # AI筛选后的（50条）
    latest_items_all,  # 原始的（200条）
    ...
)
# latest_items_all在函数内被修改
```

**问题**:
- `latest_items_all`原本是"所有RSS抓取内容"
- 但在双语处理后被修改
- 后续去重、统计逻辑依赖被修改的数据

**影响**:
- 语义混乱
- 可能导致数据不一致

---

## 🎯 完整修复方案

### 修复1: 删除ai_is_related过滤

```python
# ❌ 删除这行
# latest_items = [record for record in latest_items_all 
#                 if record.get("ai_is_related", is_ai_related_record(record))]

# ✅ 改为：保留所有内容
latest_items = latest_items_all
```

### 修复2: 移动add_ai_relevance_fields到AI筛选之后

```python
# ❌ 当前位置（3113）
# normalized = add_ai_relevance_fields(normalized)

# ✅ 移动到AI筛选之后（3131之后）
ai_filter = AIContentFilter()
latest_items = ai_filter.filter_batch(latest_items)

# 为所有通过筛选的内容添加ai_relevance标签
for item in latest_items:
    add_ai_relevance_fields(item)

# 注意：仅添加字段，不删除内容
```

### 修复3: 修正统计数据

```python
# ✅ 使用真实RSS抓取数量
items_before_filter = len(latest_items_all)
latest_items = ai_filter.filter_batch(latest_items)
filter_stats = ai_filter.get_statistics(latest_items)
filter_stats["items_before_filter"] = items_before_filter
filter_stats["items_after_filter"] = len(latest_items)
```

### 修复4: 澄清变量语义

```python
# 重命名变量，避免混淆
latest_items_rss = latest_items_all  # RSS抓取的所有内容
latest_items_filtered = ai_filter.filter_batch(latest_items_rss)  # AI筛选后

# 或者不修改latest_items_all，使用新变量
```

---

## 📊 修复前后对比

### 修复前（错误流程）

```
RSS抓取
  ↓ 200条
add_ai_relevance_fields (每条)
  ↓ 200条（含ai_is_related字段）
❌ ai_is_related过滤
  ↓ 80条（只剩AI关键词内容）
AI筛选管道（Tier 0/1/2）
  ↓ 50条
输出
```

**问题**:
- 步骤3删除了120条非AI关键词内容
- Tier 0/1/2配置的设计类内容丢失
- 白名单失效

### 修复后（正确流程）

```
RSS抓取
  ↓ 200条
AI筛选管道（Tier 0/1/2）
  ├─ 白名单路由（根据source/url/title）
  ├─ Tier 0: 40条直接输出
  ├─ Tier 1: 10条深度分析 → 6条
  └─ Tier 2: 100条三阶段 → 10条
  ↓ 56条（AI筛选通过）
add_ai_relevance_fields (仅打标签)
  ↓ 56条（含ai_is_related标签）
输出
```

**优势**:
- 白名单完整生效
- 设计/UI/产品类内容不丢失
- ai_relevance仅用于前端显示徽章

---

## 🧪 验证测试

### 测试1: 纯设计内容是否通过

**输入**:
```json
{
  "title": "New Color System Design",
  "source": "Figma Blog",
  "url": "https://figma.com/blog/color-system"
}
```

**修复前**:
- `ai_is_related = False` (无AI关键词)
- 3119行删除 ❌
- 输出：无此内容

**修复后**:
- 白名单路由 → Tier 2 (Figma配置为Tier 2)
- 关键词筛选：通过 (包含"design")
- GLM分类：通过 (设计相关)
- 深度分析：通过 (design_relevance >= 7)
- `ai_is_related = False` (标签，不删除)
- 输出：✅ 显示内容，标记"非AI强相关"

### 测试2: AI内容是否通过

**输入**:
```json
{
  "title": "GPT-5 Released",
  "source": "OpenAI Blog",
  "url": "https://openai.com/blog/gpt5"
}
```

**修复前**:
- `ai_is_related = True` (含AI关键词)
- 3119行保留 ✅
- AI筛选 → Tier 2 → 通过
- 输出：✅ 显示内容

**修复后**:
- 白名单路由 → Tier 2 (OpenAI配置为Tier 2)
- 三阶段筛选 → 通过
- `ai_is_related = True` (标签)
- 输出：✅ 显示内容，标记"AI强相关"

---

## 📋 修复清单

- [ ] 删除 `update_news.py:3119` 的`ai_is_related`过滤
- [ ] 移动 `add_ai_relevance_fields()` 到AI筛选之后
- [ ] 修正统计数据 `items_before_filter` 为真实RSS数量
- [ ] 添加测试用例验证修复效果
- [ ] 更新文档说明`ai_relevance`的作用

---

## ⚠️ 注意事项

1. **ai_relevance.py的新角色**
   - ❌ 不再用于过滤
   - ✅ 仅用于打标签
   - ✅ 前端根据`ai_is_related`显示"AI强相关"徽章

2. **白名单优先级**
   - 白名单路由是**唯一的分层依据**
   - 不依赖关键词判断
   - 保证设计/UI/产品内容不丢失

3. **成本控制**
   - Tier 0: 无AI调用
   - Tier 1: 直接深度分析（10条）
   - Tier 2: 三阶段筛选（关键词+GLM+深度）
   - 总成本应在 ¥0.08-0.25/天

---

## 🔮 后续优化

修复后可以考虑：

1. **A/B测试**
   - 对比修复前后的内容质量
   - 评估用户满意度

2. **白名单调优**
   - 根据实际效果调整Tier分配
   - 添加/删除源配置

3. **成本监控**
   - 记录每日AI调用量
   - 生成成本报告

---

**修复优先级**: 🔴 Critical - 立即修复
**预计工作量**: 30分钟
**影响范围**: 整个AI筛选系统
