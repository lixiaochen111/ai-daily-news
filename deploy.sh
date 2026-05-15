#!/bin/bash

echo "🚀 AI+设计日报 - 快速部署脚本"
echo "================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "feeds/follow.opml" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查git配置
if ! git config user.name > /dev/null; then
    echo "⚙️  配置Git用户信息..."
    read -p "请输入你的GitHub用户名: " git_username
    read -p "请输入你的邮箱: " git_email
    git config user.name "$git_username"
    git config user.email "$git_email"
fi

echo "📦 准备推送到GitHub..."
echo ""

# 删除原有remote
git remote remove origin 2>/dev/null || true

# 添加新的remote
echo "🔗 设置GitHub仓库地址..."
git remote add origin https://github.com/lixiaochen111/ai-daily-news.git

# 提交更改
echo "💾 提交配置文件..."
git add .
git commit -m "feat: customize for lixiaochen111 - 15 AI+Design Twitter accounts

- 配置15个Twitter账号RSS订阅
- 设置每天北京时间10:00自动更新
- 添加GitHub Pages自动部署
- 创建中文部署文档
" || echo "没有新的更改需要提交"

# 推送到GitHub
echo "🚀 推送到GitHub..."
git branch -M main
git push -u origin main --force

echo ""
echo "✅ 部署脚本执行完成！"
echo ""
echo "📋 下一步操作："
echo "1. 访问：https://github.com/lixiaochen111/ai-daily-news"
echo "2. 点击 Actions → 启用workflows"
echo "3. Settings → Pages → Source选择 'GitHub Actions'"
echo "4. Actions → Update AI News Snapshot → Run workflow"
echo "5. 等待几分钟后访问：https://lixiaochen111.github.io/ai-daily-news/"
echo ""
echo "📖 详细文档：查看 DEPLOYMENT.md 和 README-ZH.md"
echo ""
