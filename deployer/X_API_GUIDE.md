# X API 配置指南

接入 X（Twitter）博主推文有**三种方式**，推荐程度从高到低：

---

## 方式1：RSSHub（推荐 - 免费但不稳定）

### 优点
- ✅ 完全免费
- ✅ 无需 X API token
- ✅ 配置简单

### 缺点
- ⚠️ 公共 RSSHub 实例可能不稳定
- ⚠️ 可能被 X 限流或封禁
- ⚠️ 需要依赖第三方服务

### 配置方法

在 deployer 的**第3步（RSS 订阅源）**中，直接添加 RSSHub URL：

```
https://rsshub.app/twitter/user/用户名
```

**示例：**
- Andrej Karpathy: `https://rsshub.app/twitter/user/karpathy`
- Swyx: `https://rsshub.app/twitter/user/swyx`
- Sam Altman: `https://rsshub.app/twitter/user/sama`

**常用 RSSHub 实例：**
- 官方: `https://rsshub.app`
- 备用: `https://rsshub.pseudoyu.com`

**注意：** 如果某个实例失效，可以更换其他实例。

---

## 方式2：Follow Builders 公开 Feed（推荐 - 稳定免费）

### 优点
- ✅ 完全免费
- ✅ 稳定可靠（由 zarazhangrui/follow-builders 维护）
- ✅ 已经过滤和整理
- ✅ 无需配置 API

### 缺点
- ⚠️ 只能使用预设的博主列表（25个账号）
- ⚠️ 无法自定义

### 配置方法

**Follow Builders 已经内置在项目中！** 它追踪这些账号：
- karpathy, swyx, amasad, sama, garrytan 等25个 AI/Tech 建设者

**无需额外配置**，deployer 部署时会自动包含这个源。

查看完整列表：https://github.com/zarazhangrui/follow-builders

---

## 方式3：官方 X API（高级 - 付费但最可靠）

### 优点
- ✅ 最稳定可靠
- ✅ 可以自定义任何博主
- ✅ 官方支持

### 缺点
- ❌ **需要付费**（约 $0.005/推文）
- ❌ 配置复杂
- ❌ 需要 X Developer 账号

### 费用估算

根据 `docs/research/advanced-source-free-tier-budget-2026-05-10.md`：

```
10 推文/天 × $0.005/推文 = $0.05/天 ≈ $1.50/月
50 推文/天 = $0.25/天 ≈ $7.50/月
```

### 配置步骤

#### 1. 获取 X API Bearer Token

1. 访问 https://developer.x.com/
2. 创建开发者账号（需要审核）
3. 创建一个 App
4. 在 "Keys and tokens" 中生成 Bearer Token
5. **立即复制并保存**（只显示一次）

#### 2. 配置 GitHub Secrets

部署完成后，进入您的 GitHub 仓库：

1. **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下 secrets：

**必需：**
- Name: `X_BEARER_TOKEN`
- Value: `你的 Bearer Token`

#### 3. 配置 GitHub Variables

在同一页面，切换到 **Variables** 标签：

点击 **New repository variable**，添加以下变量：

**基础配置（5个账号示例）：**
```
Name: X_API_ENABLED
Value: 1

Name: X_API_QUERY
Value: (from:karpathy OR from:swyx OR from:amasad OR from:sama OR from:garrytan) -is:retweet -is:reply

Name: X_API_MAX_RESULTS
Value: 10

Name: X_API_DAILY_POST_LIMIT
Value: 10

Name: X_API_RUN_UTC_HOUR
Value: 0

Name: X_API_RUN_UTC_MINUTE_MAX
Value: 10
```

#### 4. 自定义博主列表

修改 `X_API_QUERY` 变量：

**单个博主：**
```
from:用户名 -is:retweet -is:reply
```

**多个博主：**
```
(from:用户名1 OR from:用户名2 OR from:用户名3) -is:retweet -is:reply
```

**示例 - AI 领域建设者：**
```
(from:karpathy OR from:swyx OR from:amasad OR from:sama OR from:garrytan OR from:gdb OR from:jhooks OR from:levelsio OR from:naval OR from:pmarca) -is:retweet -is:reply
```

**查询语法说明：**
- `from:用户名` - 来自特定用户的推文
- `-is:retweet` - 排除转推
- `-is:reply` - 排除回复
- `OR` - 或关系（多个用户）

#### 5. 更新 workflow 文件

需要手动修改仓库中的 `.github/workflows/update-news.yml`：

在 `env:` 部分添加：

```yaml
env:
  X_API_ENABLED: ${{ vars.X_API_ENABLED }}
  X_BEARER_TOKEN: ${{ secrets.X_BEARER_TOKEN }}
  X_API_QUERY: ${{ vars.X_API_QUERY }}
  X_API_MAX_RESULTS: ${{ vars.X_API_MAX_RESULTS }}
  X_API_DAILY_POST_LIMIT: ${{ vars.X_API_DAILY_POST_LIMIT }}
  X_API_RUN_UTC_HOUR: ${{ vars.X_API_RUN_UTC_HOUR }}
  X_API_RUN_UTC_MINUTE_MAX: ${{ vars.X_API_RUN_UTC_MINUTE_MAX }}
```

#### 6. 触发更新

配置完成后：
1. 进入仓库的 **Actions** 标签
2. 选择 "Update News" workflow
3. 点击 **Run workflow**
4. 等待完成

#### 7. 验证

检查 `data/source-status.json`：

```json
{
  "x_api": {
    "enabled": true,
    "ok": true,
    "item_count": 8,
    "estimated_cost_usd": 0.04
  }
}
```

---

## 推荐方案

根据您的需求选择：

### 🆓 **免费方案（推荐大多数用户）**
```
方式1（RSSHub）+ 方式2（Follow Builders）
```
- 使用 Follow Builders 作为稳定基础
- 用 RSSHub 补充额外的博主
- 总成本：$0

### 💰 **高级方案（追求稳定性）**
```
方式3（官方 X API）
```
- 完全可控和稳定
- 自定义任何博主
- 成本：~$1-10/月

### 🎯 **平衡方案**
```
方式2（Follow Builders）+ 方式3（少量API调用）
```
- 用 Follow Builders 覆盖常见博主
- 用 X API 追踪特定的5-10个关键账号
- 成本：~$1-3/月

---

## 常见问题

### Q: RSSHub 显示 "Too Many Requests"？
**A:** 切换到其他 RSSHub 实例，或等待一段时间后重试。

### Q: X API 费用如何计费？
**A:** 按返回的推文数量计费（~$0.005/推文），不是按请求次数。

### Q: 可以免费使用 X API 吗？
**A:** X API v2 目前没有免费配额，需要付费使用。

### Q: Follow Builders 追踪哪些账号？
**A:** 查看 https://github.com/zarazhangrui/follow-builders/blob/main/config/sources.json

### Q: 如何添加中文博主？
**A:** 使用 RSSHub：`https://rsshub.app/twitter/user/用户名`

---

## 示例配置

### 示例1：追踪5个 AI 大佬（RSSHub - 免费）

在 deployer 第3步添加：
```
https://rsshub.app/twitter/user/karpathy
https://rsshub.app/twitter/user/sama
https://rsshub.app/twitter/user/gdb
https://rsshub.app/twitter/user/swyx
https://rsshub.app/twitter/user/amasad
```

### 示例2：追踪10个建设者（X API - 付费）

配置 `X_API_QUERY`：
```
(from:karpathy OR from:sama OR from:gdb OR from:swyx OR from:amasad OR from:levelsio OR from:naval OR from:pmarca OR from:garrytan OR from:jhooks) -is:retweet -is:reply
```

成本：~10推文/天 × $0.005 = **$0.05/天** ≈ **$1.50/月**

### 示例3：混合方案（免费+付费）

- ✅ 使用 Follow Builders（25个账号，免费）
- ✅ 用 RSSHub 追踪5个额外的中文博主（免费，可能不稳定）
- ✅ 用 X API 追踪3个最关键的账号（$0.015/天）

总成本：**~$0.45/月**

---

## 获取帮助

- RSSHub 文档: https://docs.rsshub.app/
- X API 文档: https://developer.x.com/en/docs/twitter-api
- Follow Builders: https://github.com/zarazhangrui/follow-builders
- 项目文档: `docs/guides/x-api-demo-config.md`
