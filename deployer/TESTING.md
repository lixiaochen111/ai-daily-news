# Deployer 测试指南

## 🧪 测试前准备

### 1. 准备 GitHub Token

1. 访问 https://github.com/settings/tokens/new
2. 创建一个 classic token，名称如 "AI Daily News Deployer Testing"
3. 选择权限：
   - ✅ `repo` (完整仓库权限)
   - ✅ `workflow` (GitHub Actions权限)
4. 点击生成并复制 token（只显示一次！）

### 2. 安装依赖

```bash
cd deployer
npm install
```

## 🚀 运行测试

### 开发模式运行

```bash
npm run dev
```

这会：
- 启动Electron应用
- 打开开发者工具（DevTools）
- 可以在控制台查看详细日志

### 生产模式测试

```bash
npm start
```

## ✅ 测试流程

### 第 1 步：基本信息
- [x] 输入 GitHub 用户名
- [x] 输入邮箱地址
- [x] 输入仓库名称（必须是唯一的）
- [x] 检查网站 URL 预览是否正确

### 第 2 步：GitHub 认证
- [x] 粘贴 GitHub token
- [x] 点击"验证令牌"按钮
- [x] 确认显示：✅ 令牌验证成功！用户：xxx
- [x] 如果权限不足，应显示警告

### 第 3 步：RSS 订阅源
- [x] 输入至少一个RSS源URL
- [x] 测试推荐的AI新闻源
- [x] 确认能删除已添加的源
- [x] 尝试添加重复的源（应提示错误）

### 第 4 步：高级配置
- [x] 选择更新计划
- [x] 测试自定义cron表达式
- [x] 选择时区
- [x] 修改每页文章数
- [x] 切换评论和分析开关

### 第 5 步：审查和部署
- [x] 确认所有配置摘要正确
- [x] 点击"立即部署"
- [x] 观察部署进度：
  - 正在创建仓库... ✓
  - 正在上传文件... ✓
  - 正在配置 GitHub Actions... ✓
  - 正在启用 GitHub Pages... ✓
  - 正在完成部署... ✓
- [x] 部署成功后：
  - 点击"打开站点"（可能需要等待1-2分钟）
  - 点击"打开仓库"确认文件已上传
  - 检查 Actions 标签页的 workflow

## 🐛 常见问题

### Token验证失败
- 确认token包含 `repo` 和 `workflow` 权限
- 检查token是否过期
- 确保网络连接正常

### 仓库创建失败
- 检查仓库名是否已存在
- 确认仓库名只包含字母、数字、连字符、下划线
- 检查GitHub账号是否有权限创建仓库

### 文件上传失败
- 检查 deployer 的父目录是否包含完整项目文件
- 确认 index.html、assets/ 等文件存在
- 查看控制台错误日志

### Pages 无法访问
- **这是正常的！** GitHub Pages 首次构建需要 1-2 分钟
- 在仓库的 Actions 标签页检查构建进度
- 等待构建完成后刷新页面

### API 速率限制
- GitHub API 有调用频率限制
- 如果部署失败提示速率限制，等待一段时间后重试
- 认证用户：5000 请求/小时
- 未认证：60 请求/小时

## 📊 查看部署结果

### 1. 检查仓库
访问：`https://github.com/你的用户名/仓库名`

应包含文件：
- index.html
- assets/styles.css
- assets/app.js
- README.md
- feeds/follow.opml
- .github/workflows/update-news.yml

### 2. 检查 GitHub Actions
1. 进入仓库的 "Actions" 标签
2. 应该看到 "Update News" workflow
3. 可以手动点击 "Run workflow" 触发更新

### 3. 检查 GitHub Pages
1. 进入仓库 "Settings" → "Pages"
2. 应该显示：Your site is published at https://用户名.github.io/仓库名/
3. 首次部署需要等待 1-2 分钟构建

### 4. 访问网站
打开：`https://你的用户名.github.io/仓库名`

应该看到：
- AI Daily News 标题
- RSS 订阅源列表
- 24小时内的新闻（如果有）

## 🔍 调试技巧

### 查看详细日志
开发模式下（`npm run dev`），DevTools 会自动打开：

**主进程日志**（main.js）：
- Electron 控制台显示
- 包含 GitHub API 调用详情

**渲染进程日志**（app.js）：
- 浏览器 DevTools 控制台
- 包含前端状态和事件

### 测试单个步骤

可以在 main.js 中注释掉某些步骤来测试特定功能：

```javascript
// Step 1: Create repository
sendProgress('progress-repo', '正在创建仓库...', 'in-progress');
// const repo = await createRepository(octokit, config);  // 注释掉跳过

// Step 2: Upload files (测试这一步)
sendProgress('progress-files', '正在上传文件...', 'in-progress');
await uploadProjectFiles(octokit, config, repo);
```

## 📝 测试清单

完成以下测试场景：

- [ ] 成功部署（正常流程）
- [ ] Token验证失败（错误token）
- [ ] 仓库名重复（已存在的仓库）
- [ ] 网络中断（断网测试）
- [ ] 权限不足（token缺少必需权限）
- [ ] 大量RSS源（10+个源）
- [ ] 特殊字符处理（仓库名、邮箱等）
- [ ] 部署后再次访问（检查状态保存）

## 🎯 性能指标

正常部署预期时间：
- Token验证：< 2秒
- 创建仓库：2-3秒
- 上传文件：5-10秒（取决于文件数量）
- 配置Actions：1-2秒
- 启用Pages：1-2秒
- **总计：约10-20秒**

首次访问网站：
- GitHub Pages 构建：1-2分钟
- 后续访问：即时加载
