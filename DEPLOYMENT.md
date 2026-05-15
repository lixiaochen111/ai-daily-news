# AI + Design Daily News - 部署指南

这是你的个人AI+设计领域日报网站，自动追踪15个Twitter账号的最新动态。

## 🎯 功能特性

- ✅ 自动追踪15个AI和设计领域Twitter账号
- ✅ 每天北京时间10:00自动更新（UTC 02:00）
- ✅ GitHub Actions自动化，无需服务器
- ✅ GitHub Pages静态网站托管
- ✅ 支持中英文双语内容

## 📋 追踪的账号列表

### AI领域（5个）
- OpenAI - OpenAI官方
- Andrej Karpathy - AI研究员
- 归藏 (op7418) - AI工具关注者
- Thariq (trq212) - Claude Code团队
- Tatiana Tsiguleva - Perplexity

### 设计/产品（7个）
- Jakub Antalik - Lead Product Designer
- Wojciech Zieliński - Adobe设计师
- Matt Silva - UI工程师
- Eduard Bodak - Web设计师
- Gustav Ekerot - 设计工程师
- Rauno Freiberg - Vercel设计工程师
- Ryo Lu - Cursor.ai设计师

### AI+设计交叉（3个）
- Enzo Manuel Mangano - Base设计工程师
- Berryxia - AI工具开发者
- Zara Zhang - Builder

## 🚀 部署步骤

### 1. Fork仓库到你的GitHub

1. 访问：https://github.com/lixiaochen111/ai-daily-news
2. 点击右上角 **Fork** 按钮
3. 选择你的账号（lixiaochen111）

### 2. 启用GitHub Actions

1. 进入你fork的仓库
2. 点击 **Actions** 标签
3. 点击 **I understand my workflows, enable them**

### 3. 配置GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. Source选择：**GitHub Actions**
3. 保存配置

### 4. （可选）配置OPML Base64 Secret

如果你想保护你的订阅列表隐私：

```bash
# 在本地生成Base64编码
cat feeds/follow.opml | base64 > follow.opml.b64
```

然后在GitHub仓库设置中：
1. **Settings** → **Secrets and variables** → **Actions**
2. 新建Secret：`FOLLOW_OPML_B64`
3. 粘贴base64内容

### 5. 手动触发首次更新

1. 进入 **Actions** 标签
2. 选择 **Update AI News Snapshot**
3. 点击 **Run workflow**
4. 等待执行完成（约2-3分钟）

### 6. 访问你的网站

网站地址：`https://lixiaochen111.github.io/ai-daily-news/`

## 🔧 自定义配置

### 修改更新频率

编辑 `.github/workflows/update-news.yml`：

```yaml
schedule:
  - cron: "0 2 * * *"  # 每天UTC 02:00 (北京时间10:00)
  # - cron: "0 2,14 * * *"  # 每天两次：10:00和22:00
```

### 添加更多Twitter账号

编辑 `feeds/follow.opml`，添加新的outline：

```xml
<outline
  text="账号名称"
  title="账号描述"
  type="rss"
  xmlUrl="https://rsshub.app/twitter/user/用户名"
  htmlUrl="https://x.com/用户名"
/>
```

### RSSHub备用实例

如果 `rsshub.app` 不稳定，可以替换为备用实例：

- `https://rss.shab.chat`
- `https://rsshub.rssforever.com`
- `https://rsshub.pseudoyu.com`

## 📊 数据说明

- `data/latest-24h.json` - 最近24小时的新闻
- `data/archive.json` - 21天归档数据
- `data/source-status.json` - RSS源状态监控

## 🛠️ 故障排查

### RSS源无法访问

**问题**：某些Twitter账号无法抓取
**解决**：
1. 检查RSSHub公共实例是否可用
2. 尝试替换为备用实例
3. 考虑自建RSSHub实例（部署到Vercel/Railway）

### GitHub Actions失败

**问题**：Workflow执行失败
**解决**：
1. 检查Actions日志
2. 确认RSS_MAX_FEEDS变量（默认10，可调整）
3. 确认Python依赖是否正确安装

### 网站无法访问

**问题**：GitHub Pages未生效
**解决**：
1. 确认Settings → Pages已启用
2. 等待3-5分钟DNS传播
3. 检查Deploy to GitHub Pages workflow是否成功

## 🌟 进阶功能

### 集成Claude API进行内容过滤

在GitHub Secrets中添加：
- `ANTHROPIC_API_KEY` - 你的Claude API密钥

AI将自动：
- 过滤低质量内容
- 提取关键信息
- 生成中文摘要
- 智能分类标签

### 自建RSSHub实例

如果公共实例不稳定，推荐部署私有实例：

```bash
# 一键部署到Vercel
git clone https://github.com/DIYgod/RSSHub.git
cd RSSHub
vercel deploy
```

然后修改 `feeds/follow.opml` 中的 `rsshub.app` 为你的实例地址。

## 📝 维护

- **添加新账号**：编辑 `feeds/follow.opml` 后提交
- **调整分类**：修改OPML的outline结构
- **修改样式**：编辑 `index.html` 和相关CSS

## 📧 问题反馈

如有问题，请在GitHub Issues中提出。

---

**Powered by**：
- [AI News Radar](https://github.com/LearnPrompt/ai-news-radar)
- [RSSHub](https://github.com/DIYgod/RSSHub)
- GitHub Actions + GitHub Pages
