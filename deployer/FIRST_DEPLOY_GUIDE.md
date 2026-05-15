# 首次部署指南

## 🎉 恭喜！您已成功部署站点

部署完成后，您需要等待 **3-5 分钟**让 GitHub Actions 生成数据文件。

---

## ⏱️ 等待流程（首次部署）

### 1️⃣ **立即可见**（0分钟）
✅ 网站可以访问
✅ 页面布局正常
⚠️ 可能显示"暂无数据"或加载警告

### 2️⃣ **Actions 运行中**（1-3分钟）
🟡 GitHub Actions 正在：
- 安装 Python 依赖
- 抓取 RSS 订阅源
- 生成数据文件
- 部署到 GitHub Pages

**如何查看进度：**
1. 进入您的 GitHub 仓库
2. 点击 **Actions** 标签
3. 查看 "Update News" workflow
4. 应该看到两个 jobs：
   - ✓ update（生成数据）
   - ✓ deploy（部署到 Pages）

### 3️⃣ **完成**（3-5分钟后）
✅ Actions 显示绿色 ✓
✅ 刷新网站
✅ 应该看到新闻列表！

---

## 🔍 验证部署成功

### 检查 Actions 状态

进入仓库 → Actions 标签：

**成功的标志：**
```
✓ Update News
  ✓ update (1m 30s)
  ✓ deploy (45s)
```

**如果看到红色 ✗：**
- 点击失败的 job
- 查看错误日志
- 常见原因：
  - RSS 源无法访问（正常，会跳过）
  - Python 依赖安装失败
  - 权限问题

### 检查数据文件

在仓库中应该看到 `data/` 目录包含：
- ✅ `latest-24h.json` - 24小时新闻
- ✅ `latest-24h-all.json` - 全量数据
- ✅ `source-status.json` - 源状态
- ✅ `waytoagi-7d.json` - WaytoAGI 更新（如果启用）

### 访问网站

打开：`https://您的用户名.github.io/仓库名`

**应该看到：**
- 📰 新闻列表（来自您的 RSS 订阅源）
- 🔍 搜索框
- 🏷️ 站点筛选
- 📊 统计信息

**如果看到"暂无数据"：**
1. 等待 3-5 分钟
2. 刷新页面（Ctrl/Cmd + Shift + R 强制刷新）
3. 检查 Actions 是否完成

---

## 🐛 常见问题

### Q: 网站显示 404 错误

**A: 两种情况：**

1. **整个站点 404：**
   - GitHub Pages 还在构建（等待 1-2 分钟）
   - 检查仓库 Settings → Pages 是否启用

2. **数据文件 404（控制台警告）：**
   - 正常！首次部署时数据还未生成
   - 等待 Actions 完成即可
   - 现在前端会优雅降级，不会显示错误

### Q: Actions 运行失败

**A: 查看错误类型：**

**常见且无害的错误：**
- "某个 RSS 源返回 403/404" - 正常，会跳过该源
- "RSSHub 超时" - 正常，第三方服务不稳定

**需要修复的错误：**
- "Permission denied" - 检查 GitHub token 权限
- "Python module not found" - 检查 requirements.txt
- "File not found" - 检查仓库文件是否完整

### Q: 网站有数据但很少

**A: 可能原因：**

1. **RSS 源没有最近更新：**
   - 某些博主可能几天没发推文
   - RSSHub 实例可能暂时不可用

2. **时间窗口太小：**
   - 默认只显示 24 小时内的内容
   - 可以修改 workflow 中的 `--window-hours 24` 为更大值

3. **RSS 源配置问题：**
   - 检查 `feeds/follow.opml` 是否正确
   - 测试几个源是否可以访问

### Q: 某些博主的推文不显示

**A: RSSHub 限制：**

1. **RSSHub 实例不稳定：**
   - 尝试更换实例：
     - `rsshub.app` → `rsshub.pseudoyu.com`
   
2. **博主最近没发推：**
   - 正常情况，等待他们发布新内容

3. **X API 限制：**
   - RSSHub 可能被 X 限流
   - 考虑使用付费 X API（更稳定）

---

## 🔄 后续更新

### 自动更新

默认情况下，站点会**自动更新**：
- 频率：根据您在第4步设置的计划
- 默认：每天午夜更新一次
- 可以在 `.github/workflows/update-news.yml` 中修改

### 手动更新

随时可以手动触发更新：
1. 进入仓库 → Actions
2. 选择 "Update News"
3. 点击 **Run workflow**
4. 等待 1-2 分钟
5. 刷新网站

### 添加更多 RSS 源

**方法1：通过 GitHub 网页：**
1. 编辑 `feeds/follow.opml`
2. 添加新的 `<outline>` 标签：
   ```xml
   <outline type="rss" xmlUrl="https://新的RSS源URL" />
   ```
3. 提交更改
4. 自动触发更新

**方法2：重新部署：**
- 使用 deployer 部署到同名仓库
- 会覆盖 OPML 文件

---

## 📊 优化建议

### 1. 调整更新频率

编辑 `.github/workflows/update-news.yml`：

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时
    # - cron: '0 0 * * *'  # 每天一次
```

### 2. 增加时间窗口

如果想看更多历史内容：

```yaml
- name: Update news data
  run: |
    python scripts/update_news.py --output-dir data --window-hours 48 --rss-opml feeds/follow.opml
```

### 3. 过滤低质量源

一周后检查 `data/source-status.json`：
- 看哪些源经常失败
- 删除不活跃的源
- 保留高质量源

---

## 🎯 下一步

现在您的 AI 新闻站点已经运行！

**建议操作：**
1. ⭐ Star 原项目：https://github.com/LearnPrompt/ai-news-radar
2. 📱 收藏您的站点到书签
3. 📧 （可选）订阅自己的 RSS：`您的站点/data/latest-24h.json`
4. 🔄 一周后优化 RSS 源列表

**分享您的站点：**
- Twitter/X
- 朋友圈
- 技术社区

---

## 📞 获取帮助

**遇到问题？**
1. 查看 GitHub Actions 日志
2. 检查浏览器控制台（F12）
3. 查阅项目文档
4. 提交 Issue

**相关文档：**
- 项目 README: `README.md`
- X API 配置: `deployer/X_API_GUIDE.md`
- 快速开始: `deployer/X_QUICK_START.md`
- 测试指南: `deployer/TESTING.md`

---

## ✨ 享受您的 AI 新闻中心！

祝您使用愉快！🎉
