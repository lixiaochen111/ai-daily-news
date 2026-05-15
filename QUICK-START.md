# 🎯 快速开始 - 3步部署你的AI日报

## 前置准备

✅ 已在GitHub创建空仓库：`ai-daily-news`（如果还没有，现在去创建）

## 🚀 三步部署

### 步骤1：推送代码（1分钟）

在终端运行：

```bash
cd /Users/lixiaochen/Desktop/ai-daily-news
./deploy.sh
```

或手动执行：

```bash
cd /Users/lixiaochen/Desktop/ai-daily-news

# 删除原remote并添加你的
git remote remove origin
git remote add origin https://github.com/lixiaochen111/ai-daily-news.git

# 提交并推送
git add .
git commit -m "feat: 初始化AI+设计日报"
git branch -M main
git push -u origin main --force
```

### 步骤2：启用GitHub功能（2分钟）

1. **启用Actions**
   - 访问：https://github.com/lixiaochen111/ai-daily-news
   - 点击 **Actions** 标签
   - 点击绿色按钮：**I understand my workflows, enable them**

2. **配置Pages**
   - 点击 **Settings** → **Pages**
   - **Source** 选择：`GitHub Actions`
   - 点击 **Save**

### 步骤3：首次运行（3分钟）

1. 回到 **Actions** 标签
2. 点击左侧 **Update AI News Snapshot**
3. 点击右上角 **Run workflow** → **Run workflow**
4. 等待2-3分钟（绿色✓表示成功）

## 🎉 完成！

**你的网站地址：** https://lixiaochen111.github.io/ai-daily-news/

从明天开始，每天北京时间10:00自动更新！

---

## 📊 你的配置

- **追踪账号**：15个（AI+设计领域）
- **更新频率**：每天1次（10:00 AM北京时间）
- **数据保留**：21天
- **托管方式**：GitHub Pages（免费）

## 🔍 查看运行状态

- **Actions页面**：https://github.com/lixiaochen111/ai-daily-news/actions
  - 绿色✓ = 成功
  - 红色✗ = 失败（点击查看日志）

## 🛠️ 常用操作

### 手动触发更新
Actions → Update AI News Snapshot → Run workflow

### 添加更多Twitter账号
编辑 `feeds/follow.opml`，提交推送即可

### 修改更新时间
编辑 `.github/workflows/update-news.yml` 的cron

---

## 📖 详细文档

- **完整部署指南**：[DEPLOYMENT.md](./DEPLOYMENT.md)
- **中文README**：[README-ZH.md](./README-ZH.md)
- **原始项目**：[AI News Radar](https://github.com/LearnPrompt/ai-news-radar)

## ❓ 遇到问题？

### RSS源无法访问
- 等待几分钟重试（RSSHub有时不稳定）
- 查看 `data/source-status.json` 了解哪些源失败了

### Actions执行失败
- 点击失败的workflow查看日志
- 常见原因：RSSHub超时（会自动重试）

### 网站404
- 确认Pages已启用且Source为 "GitHub Actions"
- 等待3-5分钟DNS生效
- 检查Deploy to GitHub Pages workflow是否成功

---

**提示**：首次部署后建议等待10分钟，让所有服务完全生效。
