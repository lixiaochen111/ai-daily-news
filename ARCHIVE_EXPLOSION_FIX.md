# Archive爆炸问题修复

## 问题描述

**症状:**
- Archive从3条爆增到11,050条
- 处理了15个Tier 2批次(~450条)
- Token消耗339K(远超预期154K)
- 最终只3条成功筛选

**根本原因:**
所有fetcher返回的items直接加入archive,**没有限制**。

## 问题根源分析

### 代码逻辑(修复前)

```python
# Line 3045-3082: 直接循环所有raw_items加入archive
for raw in raw_items:
    # ... normalize ...
    item_id = make_item_id(...)
    
    if item_id not in archive:
        archive[item_id] = {...}  # 无限制地添加!
```

### 实际运行情况

**Fetcher数量:** 至少15个
- opmlrss (RSS feeds)
- techurls, buzzing, iris, bestblogs, tophub, zeli
- official_ai, ai_breakfast, follow_builders
- ai_hubtoday, aibase, aihot, newsnow
- agentmail, x_api_search

**每个fetcher可能返回:** 100-500+条

**总计raw_items:** 1000-5000+条

**Archive增长:**
- 旧archive: 3条
- 新增raw_items: ~5000条
- 几乎所有都是"新条目"(不在3条旧archive中)
- Archive → 11,050条 (3 + 5000 + 历史prune保留)

### 为什么AI筛选限制没起作用?

AI筛选限制在**line 3120-3140**,对`new_items_to_filter`分组限制50条/source。

但这**只限制进入AI的条目**,不限制archive增长。

```
所有fetcher → raw_items (5000+条) 
  ↓ 无限制
archive爆炸 (11,050条)
  ↓ 
latest_items_all (24h窗口内的条目,可能几千条)
  ↓ 
new_items_to_filter (不在archive中的条目)
  ↓ 按source限制50条
AI筛选 (~450条进入AI)
```

## 修复方案

在**line 3042-3045**之前,对`raw_items`按source分组限制50条:

```python
# CRITICAL: Limit raw_items to 50 per source BEFORE adding to archive
from collections import defaultdict
raw_by_source: defaultdict[str, list[RawItem]] = defaultdict(list)
for raw in raw_items:
    source_key = f"{raw.site_id}:{raw.source}"
    raw_by_source[source_key].append(raw)

# Sort each source group by published time, take latest 50
limited_raw_items: list[RawItem] = []
for source_key, items in raw_by_source.items():
    items.sort(key=lambda x: x.published_at or datetime.min.replace(tzinfo=UTC), reverse=True)
    limited_raw_items.extend(items[:50])  # Max 50 per source

raw_items = limited_raw_items
print(f"📊 Limited raw_items to {len(raw_items)} items (50 per source)")
```

## 预期效果

### 修复前

| 步骤 | 数量 |
|------|------|
| Fetcher总返回 | ~5000条 |
| Archive增长 | +5000条 |
| 进入AI筛选 | ~450条(按source限制) |
| Token消耗 | 339K |

### 修复后

| 步骤 | 数量 |
|------|------|
| Fetcher总返回 | ~5000条 |
| **Source限制** | **~750条(15源×50)** |
| Archive增长 | +750条 |
| 进入AI筛选 | ~450条(按source限制) |
| Token消耗 | ~160K(预期) |

## 其他相关限制

### RSS Fetch限制 (Line 2169)
```python
entries = parsed.entries[:50]  # ✅ 已有50条限制
```

### AI筛选限制 (Line 3120-3140)
```python
# 按source分组,取最新50条进入AI
items_by_source = defaultdict(list)
for item in new_items_to_filter:
    source_key = f"{item.get('site_id')}:{item.get('source')}"
    items_by_source[source_key].append(item)

limited_items = []
for source_key, items in items_by_source.items():
    items.sort(key=lambda x: event_time(x) or datetime.min.replace(tzinfo=UTC), reverse=True)
    limited_items.extend(items[:50])  # ✅ 已有50条限制
```

### Tier 2 GLM限制 (Line 452-458)
```python
# Limit to 100 items for free AI (GLM)
keyword_passed = []
for item in items:
    if self._keyword_filter(item, source_config):
        keyword_passed.append(item)
        if len(keyword_passed) >= 100:  # ✅ 已有100条限制
            break
```

## 测试检查

### 语法检查 ✅
```bash
python3 -m py_compile scripts/update_news.py
```

### 下次运行预期
- Archive增长: ~750条(而非5000+)
- 进入AI: ~450条
- Token消耗: ~160K(而非339K)

## 部署

```bash
git add scripts/update_news.py ARCHIVE_EXPLOSION_FIX.md
git commit -m "fix(archive): limit raw_items to 50 per source before archive insertion"
git push origin main
```

---

修复时间: 2026-05-22  
问题定位: 检查archive增长原因 → 发现15+个fetcher无限制  
修复策略: 在archive插入前统一限制50条/source  
预期节省: ~180K tokens/run
