# AI + 设计日报 🚀

自动追踪15个AI和设计领域顶尖Twitter账号的每日动态。

## ✨ 特色

- 🤖 **AI领域**：OpenAI、Karpathy、归藏等
- 🎨 **设计领域**：Adobe设计师、Vercel工程师、Cursor.ai等
- 🔄 **自动更新**：每天北京时间10:00自动抓取
- 🆓 **完全免费**：GitHub Actions + GitHub Pages，无需服务器
- 🌏 **双语支持**：中英文内容智能识别

## 🎯 追踪的15个账号

### AI研究与产品
- OpenAI官方 | Andrej Karpathy | 归藏
- Thariq (Claude Code) | Tatiana (Perplexity)
- Gavin Nelson (OpenAI设计师)

### 设计与开发
- Jakub Antalik | Wojciech Zieliński (Adobe)
- Gustav Ekerot | Rauno Freiberg (Vercel)
- Ryo Lu (Cursor.ai)

### 创新者
- Enzo Mangano | Berryxia | Zara Zhang

## 🚀 5分钟部署

### 第一步：推送到你的GitHub

```bash
cd /Users/lixiaochen/Desktop/ai-daily-news

# 删除原有remote
git remote remove origin

# 添加你的仓库（先在GitHub创建ai-daily-news仓库）
git remote add origin https://github.com/lixiaochen111/ai-daily-news.git

# 提交并推送
git add .
git commit -m "feat: customize for lixiaochen111 - 15 Twitter accounts"
git branch -M main
git push -u origin main
```

### 第二步：启用GitHub Actions

1. 访问：https://github.com/lixiaochen111/ai-daily-news
2. 点击 **Actions** → **I understand my workflows, enable them**

### 第三步：配置GitHub Pages

1. 仓库 **Settings** → **Pages**
2. Source选择：**GitHub Actions**
3. 保存

### 第四步：手动触发首次更新

1. **Actions** → **Update AI News Snapshot** → **Run workflow**
2. 等待2-3分钟执行完成

### 第五步：访问你的网站

🎉 网站地址：`https://lixiaochen111.github.io/ai-daily-news/`

## 📖 完整文档

查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解：
- 自定义RSS源
- 修改更新频率
- 集成Claude API
- 故障排查

## 🛠️ 本地测试

```bash
# 安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 运行更新脚本
python scripts/update_news.py --output-dir data --window-hours 24 --rss-opml feeds/follow.opml

# 启动本地服务器
python -m http.server 8080
# 访问：http://localhost:8080
```

## 📊 项目结构

```
ai-daily-news/
├── feeds/
│   └── follow.opml          # 15个Twitter账号RSS配置
├── .github/workflows/
│   ├── update-news.yml      # 每日自动更新
│   └── deploy-pages.yml     # 自动部署到GitHub Pages
├── data/                    # 自动生成的数据文件
├── index.html               # 网站首页
└── scripts/                 # Python更新脚本
```

## 🔧 常见问题

**Q: RSS源抓取失败？**
A: RSSHub公共实例可能不稳定，可替换为备用实例或自建。

**Q: 想添加更多账号？**
A: 编辑 `feeds/follow.opml`，参考现有格式添加。

**Q: 修改更新时间？**
A: 编辑 `.github/workflows/update-news.yml` 的cron表达式。

## 📝 下一步

- [ ] 测试RSSHub实例稳定性
- [ ] 考虑集成Claude API做内容智能过滤
- [ ] 添加更多信息源（RSS博客、Newsletter）
- [ ] 自定义网站样式

## 🙏 致谢

- [AI News Radar](https://github.com/LearnPrompt/ai-news-radar) - 原始项目
- [RSSHub](https://github.com/DIYgod/RSSHub) - RSS聚合服务
- GitHub Actions & Pages - 免费托管

---

**Made with ❤️ by Claude Code**
