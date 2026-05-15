#!/bin/bash
# 批量中文化脚本

cd /Users/lixiaochen/Desktop/ai-daily-news/deployer/renderer

# 备份原文件
cp index.html index.html.backup
cp app.js app.js.backup

# Step 3 - RSS Feeds
sed -i '' 's/Step 3: RSS Feed Configuration/第 3 步：RSS 订阅源配置/g' index.html
sed -i '' 's/Configure your news sources/配置您的新闻来源/g' index.html
sed -i '' 's/Add RSS Feed/添加 RSS 源/g' index.html
sed -i '' 's/Feed URL/订阅源 URL/g' index.html
sed -i '' 's/Feed Title/订阅源标题/g' index.html
sed -i '' 's/Category (optional)/分类（可选）/g' index.html
sed -i '' 's/Remove/移除/g' index.html
sed -i '' 's/Suggested AI News Feeds/推荐的 AI 新闻源/g' index.html
sed -i '' 's/Add all/全部添加/g' index.html

# Step 4 - Advanced
sed -i '' 's/Step 4: Advanced Options/第 4 步：高级选项/g' index.html
sed -i '' 's/Customize your deployment/自定义您的部署/g' index.html
sed -i '' 's/Update Schedule/更新计划/g' index.html
sed -i '' 's/Every 6 hours/每 6 小时/g' index.html
sed -i '' 's/Every 12 hours/每 12 小时/g' index.html
sed -i '' 's/Daily at 2 AM/每天凌晨 2 点/g' index.html
sed -i '' 's/Weekly on Monday/每周一/g' index.html
sed -i '' 's/Custom cron expression/自定义 cron 表达式/g' index.html
sed -i '' 's/Timezone/时区/g' index.html
sed -i '' 's/Articles per page/每页文章数/g' index.html
sed -i '' 's/Enable comments/启用评论/g' index.html
sed -i '' 's/Enable analytics/启用分析/g' index.html

# Step 5 - Deploy
sed -i '' 's/Step 5: Review & Deploy/第 5 步：审查和部署/g' index.html
sed -i '' 's/Review your configuration and deploy/检查您的配置并部署/g' index.html
sed -i '' 's/Configuration Summary/配置摘要/g' index.html
sed -i '' 's/Basic Information/基本信息/g' index.html
sed -i '' 's/GitHub Token/GitHub 令牌/g' index.html
sed -i '' 's/RSS Feeds/RSS 订阅源/g' index.html
sed -i '' 's/Advanced Settings/高级设置/g' index.html
sed -i '' 's/Deploy Now/立即部署/g' index.html
sed -i '' 's/Deploying.../部署中.../g' index.html
sed -i '' 's/Deployment successful!/部署成功！/g' index.html
sed -i '' 's/Deployment failed/部署失败/g' index.html
sed -i '' 's/View Repository/查看仓库/g' index.html
sed -i '' 's/View Site/查看网站/g' index.html
sed -i '' 's/Retry/重试/g' index.html
sed -i '' 's/Start New Deployment/开始新的部署/g' index.html

# app.js 中的提示信息
sed -i '' 's/Please fill in all required fields/请填写所有必填字段/g' app.js
sed -i '' 's/Invalid email format/邮箱格式无效/g' app.js
sed -i '' 's/Token verified successfully/令牌验证成功/g' app.js
sed -i '' 's/Invalid token/令牌无效/g' app.js
sed -i '' 's/Please add at least one RSS feed/请至少添加一个 RSS 订阅源/g' app.js
sed -i '' 's/Are you sure/您确定吗/g' app.js

echo "✅ 中文化完成！"
echo "备份文件：index.html.backup 和 app.js.backup"
