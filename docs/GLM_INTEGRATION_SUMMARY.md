# GLM-4.7-Flash 集成总结

> **完成日期**: 2026-05-18  
> **Git Commit**: 3d34b85  
> **状态**: ✅ 已完成

---

## 🚨 问题发现

用户反馈：**EasyRouter平台根本没有GLM-4-Flash模型**

原代码错误假设：
```python
# ❌ 错误：EasyRouter不支持此模型
self.client = EasyRouterClient()
response = self.client.call_model(model="glm-4-flash", ...)
```

**结果**: Tier 2初筛完全无法工作，会报错`Model not found`。

---

## ✅ 解决方案

### 架构调整：双API密钥系统

```
原架构（错误）：
EASYROUTER_API_KEY
  ├─ glm-4-flash (❌ 不存在)
  ├─ deepseek-chat
  └─ gpt-4o-mini

新架构（正确）：
┌─ 免费初筛 ─────────────────┐
│ GLM_API_KEY                │
│  → GLM-4.7-Flash (智谱AI)  │
│  → https://open.bigmodel.cn│
└────────────────────────────┘

┌─ 付费深度分析 ─────────────┐
│ EASYROUTER_API_KEY         │
│  ├─ deepseek-chat (中文)   │
│  └─ gpt-4o-mini (英文)     │
└────────────────────────────┘
```

---

## 📝 代码修改

### 1. 新增GLM客户端

**文件**: `scripts/ai_filter/glm_client.py`

```python
from openai import OpenAI

class GLMClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        
        # 智谱AI使用OpenAI兼容格式，但endpoint不同
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4"
        )

    def call_model(self, model="glm-4.7-flash", ...):
        # 标准OpenAI chat completions调用
        response = self.client.chat.completions.create(...)
```

**特点**:
- ✅ OpenAI兼容接口
- ✅ 仅需修改base_url
- ✅ 支持GLM-4.7-Flash模型
- ✅ 免费额度（具体限制待确认）

---

### 2. 修改Tier 2管道

**文件**: `scripts/ai_filter/tier2_pipeline.py`

```python
# 导入两个client
from scripts.ai_filter.glm_client import GLMClient
from scripts.ai_filter.easyrouter_client import EasyRouterClient

class Tier2Pipeline:
    def __init__(self):
        # GLM用于免费初筛
        self.glm_client = GLMClient()
        
        # EasyRouter用于付费深度分析
        self.easyrouter_client = EasyRouterClient()
        
        self.model_classify = "glm-4.7-flash"  # ✅ 正确模型名

    def _glm_classify(self, item):
        # 使用GLM client
        response = self.glm_client.call_model(
            model=self.model_classify,
            ...
        )

    def _ai_deep_analysis(self, item, source_config):
        # 使用EasyRouter client
        response = self.easyrouter_client.call_model(
            model=self.model_zh if language == "zh" else self.model_en,
            ...
        )
```

**关键修改**:
- ✅ 初筛使用`glm_client`
- ✅ 深度分析使用`easyrouter_client`
- ✅ 模型名改为`glm-4.7-flash`

---

### 3. 部署工具UI更新

**文件**: `deployer/renderer/index.html`

添加两个API密钥输入框：

```html
<!-- 智谱AI密钥 -->
<div class="form-control w-full mb-4">
  <label class="label">
    <span class="label-text">智谱 AI API 密钥</span>
    <span class="label-text-alt">可选</span>
  </label>
  <div class="join w-full">
    <input type="password" id="glm-api-key" 
           placeholder="输入智谱AI密钥" />
    <button type="button" id="toggle-glm-key">
      <span id="eye-icon-glm">👁️</span>
    </button>
  </div>
  <label class="label">
    <span class="label-text-alt">用于免费GLM-4.7-Flash模型（初筛分类）</span>
  </label>
</div>

<!-- EasyRouter密钥 -->
<div class="form-control w-full mb-4">
  <label class="label">
    <span class="label-text">EasyRouter API 密钥</span>
    <span class="label-text-alt">可选</span>
  </label>
  <div class="join w-full">
    <input type="password" id="easyrouter-api-key" 
           placeholder="sk-xxxxxxxxxxxxxxxxxxxx" />
    <button type="button" id="toggle-api-key-step1">
      <span id="eye-icon-step1">👁️</span>
    </button>
  </div>
  <label class="label">
    <span class="label-text-alt">用于DeepSeek/GPT-4o Mini（深度分析）</span>
  </label>
</div>
```

**帮助文档更新**:
```html
<div class="collapse-content">
  <div class="alert alert-info">
    三层智能筛选：关键词过滤 → GLM免费初筛 → DeepSeek/GPT深度分析
  </div>
  
  <p>1️⃣ 智谱AI（GLM-4.7-Flash）- 免费初筛</p>
  <ul>
    <li>获取：<a href="https://open.bigmodel.cn/">open.bigmodel.cn</a></li>
    <li>成本：完全免费</li>
  </ul>
  
  <p>2️⃣ EasyRouter - 付费深度分析</p>
  <ul>
    <li>获取：<a href="https://easyrouter.ai/">easyrouter.ai</a></li>
    <li>成本：约 ¥0.08-0.25/天</li>
  </ul>
  
  <div class="alert alert-warning">
    <p>推荐配置：两个密钥都配置，性价比最高</p>
  </div>
</div>
```

---

### 4. 前端状态管理

**文件**: `deployer/renderer/app.js`

```javascript
// 添加glmApiKey到state
const state = {
  config: {
    glmApiKey: '',
    easyrouterApiKey: '',
    ...
  }
};

// Step 1 handlers
function setupStep1Handlers() {
  const glmKeyInput = document.getElementById('glm-api-key');
  const toggleGlmBtn = document.getElementById('toggle-glm-key');
  
  glmKeyInput.addEventListener('input', (e) => {
    state.config.glmApiKey = e.target.value.trim();
  });
  
  toggleGlmBtn.addEventListener('click', () => {
    // Toggle visibility
  });
}

// Step 5 summary
function populateConfigSummary() {
  const hasGlm = state.config.glmApiKey;
  const hasEasyRouter = state.config.easyrouterApiKey;

  if (hasGlm && hasEasyRouter) {
    aiFilterStatus.innerHTML = '完整配置（免费初筛+深度分析）';
  } else if (hasEasyRouter) {
    aiFilterStatus.innerHTML = '仅深度分析（跳过GLM初筛）';
  } else if (hasGlm) {
    aiFilterStatus.innerHTML = '仅GLM初筛（无深度分析）';
  } else {
    aiFilterStatus.innerHTML = '未配置（仅关键词筛选）';
  }
}

// Export config
function getDeploymentConfig() {
  return {
    secrets: {
      glmApiKey: state.config.glmApiKey,
      easyrouterApiKey: state.config.easyrouterApiKey
    }
  };
}
```

---

### 5. GitHub Secrets配置

**文件**: `deployer/main.js`

```javascript
async function configureGitHubSecrets(octokit, config, repo) {
  const { glmApiKey, easyrouterApiKey } = config.secrets;
  if (!glmApiKey && !easyrouterApiKey) return;

  const sodium = require('libsodium-wrappers');
  await sodium.ready;

  const { data: publicKey } = await octokit.rest.actions.getRepoPublicKey({
    owner: config.github.username,
    repo: config.github.repoName
  });

  const keyBytes = Buffer.from(publicKey.key, 'base64');

  // Configure GLM_API_KEY
  if (glmApiKey) {
    const glmEncrypted = sodium.crypto_box_seal(
      Buffer.from(glmApiKey), keyBytes
    );
    
    await octokit.rest.actions.createOrUpdateRepoSecret({
      owner: config.github.username,
      repo: config.github.repoName,
      secret_name: 'GLM_API_KEY',
      encrypted_value: Buffer.from(glmEncrypted).toString('base64'),
      key_id: publicKey.key_id
    });
  }

  // Configure EASYROUTER_API_KEY
  if (easyrouterApiKey) {
    // ... 同样逻辑
  }
}
```

---

### 6. GitHub Actions Workflow

**文件**: `deployer/main.js` - `generateWorkflowYaml()`

```javascript
function generateWorkflowYaml(config) {
  const hasGlmKey = config.secrets && config.secrets.glmApiKey;
  const hasEasyRouterKey = config.secrets && config.secrets.easyrouterApiKey;

  let envSection = '';
  if (hasGlmKey || hasEasyRouterKey) {
    const envVars = [];
    if (hasGlmKey) 
      envVars.push('          GLM_API_KEY: ${{ secrets.GLM_API_KEY }}');
    if (hasEasyRouterKey) 
      envVars.push('          EASYROUTER_API_KEY: ${{ secrets.EASYROUTER_API_KEY }}');
    envSection = `\n        env:\n${envVars.join('\n')}`;
  }

  return `
    - name: Update news data${envSection}
      run: |
        python scripts/update_news.py ...
  `;
}
```

---

### 7. 环境变量文档

**文件**: `.env.example`

```bash
# ============================================================================
# API Keys
# ============================================================================

# Zhipu AI - GLM-4.7-Flash (Free Tier)
# Get from: https://open.bigmodel.cn/
# Used for: Fast classification (Tier 2 initial screening)
GLM_API_KEY=your_zhipu_api_key_here

# EasyRouter - Multi-model Access
# Get from: https://easyrouter.ai/
# Used for: Deep analysis (DeepSeek for Chinese, GPT-4o Mini for English)
EASYROUTER_API_KEY=your_easyrouter_api_key_here

# ============================================================================
# Model Configuration
# ============================================================================

# Tier 2 Classification Model (free)
AI_MODEL_CLASSIFY=glm-4.7-flash

# Deep Analysis Models (paid)
AI_MODEL_ANALYZE_ZH=deepseek-chat    # Chinese content
AI_MODEL_ANALYZE_EN=gpt-4o-mini      # English content
```

---

## 📊 成本对比

| 配置方案 | Tier 2初筛 | 深度分析 | 日成本 | 推荐度 |
|---------|-----------|---------|--------|--------|
| 两个都配置 | GLM免费 | EasyRouter付费 | ¥0.08-0.25 | ⭐⭐⭐⭐⭐ |
| 仅EasyRouter | 跳过初筛 | EasyRouter付费 | ¥0.30-0.50 | ⭐⭐⭐ |
| 仅GLM | GLM免费 | 无深度分析 | ¥0 | ⭐⭐ |
| 都不配置 | 关键词筛选 | 无 | ¥0 | ⭐ |

**推荐配置**: 两个密钥都配置
- GLM免费初筛过滤大量无关内容
- EasyRouter精准深度分析高质量内容
- 总成本最低，效果最好

---

## 🧪 测试验证

### 验证步骤

1. **本地测试**
   ```bash
   # 配置两个API密钥
   export GLM_API_KEY="your_zhipu_key"
   export EASYROUTER_API_KEY="your_easyrouter_key"
   
   # 运行测试
   python scripts/update_news.py --output-dir data --window-hours 24
   ```

2. **检查日志**
   ```
   ✅ GLM classification: 30条 → 15条
   ✅ EasyRouter deep analysis: 15条 → 10条
   ✅ Final output: 10条高质量内容
   ```

3. **部署测试**
   - 重新部署项目
   - 填写两个API密钥
   - 检查GitHub Secrets是否正确写入
   - 等待Actions运行
   - 确认无报错

---

## 🎯 用户指引

### 如何获取智谱AI密钥？

1. 访问 https://open.bigmodel.cn/
2. 注册/登录账号
3. 进入"API管理" → "创建API Key"
4. 复制密钥并保存

### 如何获取EasyRouter密钥？

1. 访问 https://easyrouter.ai/
2. 注册/登录账号
3. 进入控制台 → "API Keys"
4. 创建新密钥
5. 复制并保存

### 部署配置

使用部署工具时：
- **第1步"基本信息"**: 填写两个API密钥
- 建议两个都配置，获得最佳性价比
- 如果只有EasyRouter，也可以（会跳过免费初筛）

---

## 📚 相关文档

- **GLM官方文档**: https://docs.bigmodel.cn/cn/guide/models/free/glm-4.7-flash
- **EasyRouter文档**: https://easyrouter.ai/docs
- **AI筛选架构**: docs/AI_FILTERING_LOGIC.md
- **部署工具修复**: docs/DEPLOYER_FIX_SUMMARY.md

---

## ⚠️ 注意事项

1. **GLM免费额度**
   - 具体限制需查看官网最新政策
   - 超出免费额度后会收费或限流
   - 建议监控每日使用量

2. **API密钥安全**
   - 不要提交到公开仓库
   - 使用GitHub Secrets存储
   - 定期轮换密钥

3. **降级策略**
   - 如果GLM限流，可临时禁用`AI_FILTER_ENABLED`
   - 或只配置EasyRouter（成本稍高）
   - 或使用关键词筛选（免费但不精准）

---

**修复完成时间**: 2026-05-18  
**Git Commit**: 3d34b85  
**文档版本**: v1.0
