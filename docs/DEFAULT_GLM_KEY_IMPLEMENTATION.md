# 默认共享GLM密钥实施方案

> **完成日期**: 2026-05-18  
> **Git Commit**: c807a96  
> **状态**: ✅ 已完成

---

## 🎯 设计目标

**免费层默认配置，付费层用户自配**

```
┌─ 用户视角 ────────────────────────┐
│ GLM初筛：✅ 开箱即用，无需配置    │
│ EasyRouter：需自己注册配置        │
│ 总配置复杂度：降低50%             │
└───────────────────────────────────┘

┌─ 成本视角 ────────────────────────┐
│ GLM：项目承担（免费配额共享）     │
│ EasyRouter：用户自己承担          │
│ 项目成本：¥0/天                   │
└───────────────────────────────────┘
```

---

## 📝 实施内容

### 1. GLM客户端 - 内置默认密钥

**文件**: `scripts/ai_filter/glm_client.py`

```python
class GLMClient:
    # 项目提供的默认共享密钥
    DEFAULT_API_KEY = "a6a06824dfbf42b29e5af74334bbeb6f.BMbBvfB7obgYbgTG"
    
    # 请求限流保护（每分钟30次）
    MAX_REQUESTS_PER_MINUTE = 30
    
    def __init__(self, api_key=None):
        # 优先级：传入参数 > 环境变量 > 默认密钥
        self.api_key = (
            api_key or 
            os.getenv("GLM_API_KEY") or 
            self.DEFAULT_API_KEY
        )
        
        # 标记是否使用共享密钥
        self.using_shared_key = (self.api_key == self.DEFAULT_API_KEY)
```

**特性**:
- ✅ 三级优先级：明确传入 > 环境变量 > 默认
- ✅ 自动检测是否共享密钥
- ✅ 请求限流保护（仅共享密钥）
- ✅ 自定义异常：`QuotaExceededError`

---

### 2. 降级策略

**GLM配额耗尽时的处理**：

```python
# tier2_pipeline.py

def _glm_classify(self, item):
    try:
        response = self.glm_client.call_model(...)
        return classification_result
    
    except QuotaExceededError as e:
        # 返回None触发降级
        print(f"⚠️  GLM quota exceeded, degrading...")
        return None  # ← 关键：返回None而非False
    
    except Exception as e:
        # 其他错误直接拒绝
        return False

def filter(self, item, source_config):
    # Stage 1: 关键词筛选
    if not keyword_filter(item):
        return None
    
    # Stage 2: GLM分类（支持降级）
    glm_result = _glm_classify(item)
    
    if glm_result is None:
        # GLM不可用，跳过此阶段
        print(f"ℹ️  Skipping GLM stage...")
        # 继续到深度分析
    elif glm_result is False:
        # GLM明确拒绝
        return None
    # glm_result is True，继续
    
    # Stage 3: 深度分析
    return _ai_deep_analysis(item)
```

**降级流程**：

```
正常流程：
关键词筛选 → GLM初筛 → 深度分析
  100条  →   30条  →   15条  →  10条

GLM限流后：
关键词筛选 → [跳过GLM] → 深度分析
  100条  →      30条     →  18条  ← 更多内容进入深度分析
```

**成本影响**:
- GLM正常：¥0 (GLM) + ¥0.06 (深度15条) = ¥0.06/天
- GLM限流：¥0 + ¥0.12 (深度30条) = ¥0.12/天

---

### 3. 部署工具UI优化

**智谱AI密钥输入框**：

```html
<div class="form-control">
  <label class="label">
    <span class="label-text flex items-center gap-2">
      智谱 AI API 密钥
      <span class="badge badge-success">已含免费配额</span>
    </span>
    <span class="label-text-alt">可选</span>
  </label>
  <input type="password" id="glm-api-key"
         placeholder="留空使用默认免费配额，或填入你自己的密钥获得独立配额" />
  <label class="label">
    <span class="label-text-alt">
      💡 默认已包含免费配额（所有用户共享），无需配置。
    </span>
  </label>
</div>
```

**EasyRouter密钥输入框**：

```html
<div class="form-control">
  <label class="label">
    <span class="label-text flex items-center gap-2">
      EasyRouter API 密钥
      <span class="badge badge-warning">需要你自己的</span>
    </span>
    <span class="label-text-alt">可选</span>
  </label>
  <input type="password" id="easyrouter-api-key"
         placeholder="sk-xxxxxxxxxxxxxxxxxxxx（需自行注册获取）" />
  <label class="label">
    <span class="label-text-alt">
      🔑 需配置你自己的密钥。约¥0.08-0.25/天。
    </span>
  </label>
</div>
```

---

### 4. 帮助文档更新

```html
<div class="alert alert-success">
  1️⃣ 智谱AI（GLM-4.7-Flash）- 免费初筛
  ✅ 已内置默认配额，无需配置
</div>

• 用途：快速分类，过滤明显无关内容
• 配额：项目提供的默认免费配额（所有用户共享）
• 成本：完全免费
• 可选配置：如有自己的智谱AI账号，填入密钥可获得独立配额

<div class="alert alert-warning">
  2️⃣ EasyRouter - 付费深度分析
  ⚠️ 需配置你自己的API密钥
</div>

• 用途：精准评分，选出高质量内容
• 模型：DeepSeek（中文） + GPT-4o Mini（英文）
• 获取：easyrouter.ai 注册后创建API密钥
• 成本：约 ¥0.08-0.25/天（按实际使用量计费）

💡 配置建议：
• 推荐：只配置EasyRouter密钥（免费初筛已内置）
• 进阶：两个都配置（使用你自己的GLM配额）
• 极简：两个都不配置（仅关键词筛选）
```

---

### 5. 环境变量文档

**.env.example**:

```bash
# Zhipu AI - GLM-4.7-Flash (Free Tier)
# Default: Built-in shared API key (all users share free quota)
# Optional: Configure your own key for dedicated quota
# Get from: https://open.bigmodel.cn/
# Leave empty to use default shared key
GLM_API_KEY=

# EasyRouter - Multi-model Access
# Required: Configure your own API key
# Get from: https://easyrouter.ai/
# Cost: ~¥0.08-0.25/day
EASYROUTER_API_KEY=your_easyrouter_api_key_here
```

---

## 🔐 安全考虑

### 风险分析

**1. 密钥暴露风险**
- 默认密钥硬编码在公开仓库
- 任何人都能看到并使用
- ✅ 可接受：免费配额本身就是为用户提供的

**2. 配额滥用风险**
- 恶意用户可能大量调用
- ✅ 缓解措施：
  - 客户端限流（30次/分钟）
  - 降级策略（配额耗尽自动跳过）
  - 智谱AI服务端限流（429错误）

**3. 密钥失效风险**
- 智谱AI可能封禁滥用密钥
- ✅ 缓解措施：
  - 降级到关键词筛选
  - 文档提示用户配置自己的密钥

---

### 保护措施

#### 客户端限流

```python
class GLMClient:
    MAX_REQUESTS_PER_MINUTE = 30
    
    def _check_rate_limit(self):
        now = time.time()
        
        # 清理1分钟前的请求记录
        self._request_times = [
            t for t in self._request_times 
            if now - t < 60
        ]
        
        # 检查是否超限
        if len(self._request_times) >= self.MAX_REQUESTS_PER_MINUTE:
            return False
        
        # 记录本次请求
        self._request_times.append(now)
        return True
```

#### 降级策略

```
配额充足 → 正常三阶段筛选
    ↓
配额耗尽 → 跳过GLM，两阶段筛选
    ↓
EasyRouter也耗尽 → 降级到关键词筛选
```

---

## 📊 用户使用场景

### 场景1：默认配置用户（推荐）

```bash
# 只配置EasyRouter
EASYROUTER_API_KEY=sk-xxx...

# GLM使用默认共享密钥
# GLM_API_KEY留空
```

**特点**：
- ✅ 配置最简单（只需1个密钥）
- ✅ 成本：¥0.08-0.25/天
- ✅ GLM免费初筛正常工作
- ⚠️ 共享配额可能偶尔限流（自动降级）

---

### 场景2：进阶用户

```bash
# 两个都配置
GLM_API_KEY=your_own_glm_key
EASYROUTER_API_KEY=sk-xxx...
```

**特点**：
- ✅ 独立GLM配额，不受共享限制
- ✅ 更稳定的服务
- ✅ 成本：¥0.08-0.25/天（GLM仍免费）
- ⚠️ 需要多注册一个账号

---

### 场景3：极简用户

```bash
# 两个都不配置
# GLM_API_KEY=
# EASYROUTER_API_KEY=
```

**特点**：
- ✅ 完全免费
- ✅ 无需注册任何账号
- ⚠️ 仅关键词筛选，准确率较低
- ⚠️ GLM默认密钥虽然可用，但没有EasyRouter无法深度分析

---

## 🧪 测试验证

### 测试1：默认密钥可用性

```bash
cd /Users/lixiaochen/Desktop/claude\ code/ai-daily-news

# 清空环境变量
export GLM_API_KEY=

# 运行测试
python3 -c "
from scripts.ai_filter.glm_client import GLMClient

client = GLMClient()
print(f'Using shared key: {client.using_shared_key}')
print(f'Key: {client.api_key[:20]}...')

response = client.call_model(
    user_prompt='测试连接',
    max_tokens=10
)
print('✅ Connection successful')
"
```

**预期结果**:
```
Using shared key: True
Key: a6a06824dfbf42b29e5a...
✅ Connection successful
```

---

### 测试2：降级逻辑

模拟GLM限流：

```python
# 手动触发QuotaExceededError
from scripts.ai_filter.glm_client import QuotaExceededError

# 在tier2_pipeline.py中模拟
def _glm_classify(self, item):
    raise QuotaExceededError("Simulated quota exhaustion")

# 运行筛选
# 预期：跳过GLM阶段，直接深度分析
```

---

## 📈 监控指标

### 建议监控的指标

1. **GLM限流频率**
   ```python
   # 记录GLM QuotaExceededError次数
   glm_quota_exceeded_count
   ```

2. **降级触发次数**
   ```python
   # 记录跳过GLM阶段的次数
   glm_degradation_count
   ```

3. **共享密钥使用率**
   ```python
   # 统计使用默认密钥 vs 自定义密钥
   shared_key_usage_percentage
   ```

---

## 💡 用户教育

### 文档说明位置

1. **README.md**
   - 添加"开箱即用"特性说明
   - 解释GLM免费初筛已内置

2. **部署工具帮助文档**
   - 已完成 ✅
   - 清楚说明三种配置模式

3. **.env.example注释**
   - 已完成 ✅
   - 说明GLM_API_KEY留空即可

---

## 🚀 后续优化

### 短期（本周）

- [ ] 添加监控统计
  - 记录GLM调用次数
  - 记录降级触发次数
  - 生成每日报告

- [ ] 优化错误提示
  - GLM限流时提示用户
  - 建议配置自己的密钥

### 中期（本月）

- [ ] 智能负载均衡
  - 多个默认密钥轮换
  - 分散请求压力

- [ ] 配额预警
  - 接近限额时提前降级
  - 避免突然失败

### 长期（季度）

- [ ] 付费方案
  - 提供项目官方API服务
  - 用户付费获得更高配额

---

## ⚠️ 重要提醒

### 对用户

1. **默认密钥是共享的**
   - 所有用户共享配额
   - 可能偶尔遇到限流
   - 建议高频使用者配置自己的密钥

2. **密钥安全**
   - 默认密钥公开在代码中（这是故意的）
   - 你的EasyRouter密钥**不要**提交到git
   - 使用GitHub Secrets存储

3. **降级是正常的**
   - GLM限流时会自动降级
   - 不影响核心功能
   - 日志会记录降级事件

---

## 📞 支持

如遇问题：

1. **GLM持续限流**
   - 配置你自己的GLM密钥（推荐）
   - 或暂时禁用AI筛选

2. **EasyRouter配置问题**
   - 查看 docs/AI_FILTER_GUIDE.md
   - 确认密钥正确写入

3. **其他问题**
   - 提交Issue到GitHub

---

**实施完成时间**: 2026-05-18  
**Git Commit**: c807a96  
**文档版本**: v1.0
