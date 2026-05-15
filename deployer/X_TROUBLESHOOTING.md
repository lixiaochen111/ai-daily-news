# X 账号抓取失败排查指南

## 🔍 诊断步骤

### 1. 查看 GitHub Actions 日志

1. 进入仓库 → **Actions** 标签
2. 点击最新的 "Update News" 运行
3. 点击左侧 **"update"** job
4. 展开 **"Update news data"** 步骤
5. 查找包含 "rsshub" 或 "twitter" 的错误信息

### 2. 检查本地是否可以访问

在浏览器中测试：
```
https://rsshub.app/twitter/user/karpathy
```

**如果能看到 XML/RSS 内容** = RSSHub 工作正常
**如果看到错误或空白** = RSSHub 实例有问题

---

## ❌ 常见错误及解决方案

### 错误1: 403 Forbidden

**完整错误信息：**
```
Failed to fetch feed: https://rsshub.app/twitter/user/xxx
HTTP 403 Forbidden
```

**原因：**
- RSSHub 公共实例被 X/Twitter 限流
- IP 被封禁或达到请求上限

**解决方案：**

#### 方案A：更换 RSSHub 实例（推荐）

**步骤：**
1. 进入您的 GitHub 仓库
2. 编辑 `feeds/follow.opml`
3. 批量替换：
   - `rsshub.app` → `rsshub.pseudoyu.com`
   - 或 → `rsshub.rssforever.com`

**替换前：**
```xml
<outline type="rss" xmlUrl="https://rsshub.app/twitter/user/karpathy" />
```

**替换后：**
```xml
<outline type="rss" xmlUrl="https://rsshub.pseudoyu.com/twitter/user/karpathy" />
```

**可用的 RSSHub 实例：**
- `rsshub.app` （官方，可能被限流）
- `rsshub.pseudoyu.com`
- `rsshub.rssforever.com`
- `rss.shab.fun`

**测试哪个实例可用：**
在浏览器中依次测试：
- https://rsshub.pseudoyu.com/twitter/user/karpathy
- https://rsshub.rssforever.com/twitter/user/karpathy
- https://rss.shab.fun/twitter/user/karpathy

选择能正常显示 RSS 的实例。

#### 方案B：自建 RSSHub（高级，最稳定）

**使用 Docker 自建：**
```bash
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
```

然后在 OPML 中使用：
```xml
<outline type="rss" xmlUrl="http://您的服务器IP:1200/twitter/user/karpathy" />
```

#### 方案C：使用官方 X API（付费，最可靠）

见 `X_API_GUIDE.md` 中的配置方法。

成本：~$1-3/月

---

### 错误2: 超时 (Timeout)

**完整错误信息：**
```
Failed to fetch feed: Request timeout
or
Read timed out
```

**原因：**
- RSSHub 实例响应慢
- GitHub Actions runner 网络问题

**解决方案：**

1. **更换更快的 RSSHub 实例**
2. **减少同时抓取的博主数量**
   - 先测试 3-5 个博主
   - 确认成功后再逐步增加

3. **增加超时时间**（需要修改脚本）

---

### 错误3: RSS 解析失败

**完整错误信息：**
```
Failed to parse RSS feed
or
Invalid XML
```

**原因：**
- RSSHub 返回了错误页面而不是 RSS
- 博主账号被封禁或不存在

**解决方案：**

1. **在浏览器中测试 RSS URL**
   - 应该看到 XML 格式的内容
   - 如果看到 HTML 错误页面 = 该实例不可用

2. **检查博主用户名是否正确**
   - 访问 X: `https://x.com/用户名`
   - 确认账号存在且公开

3. **该博主可能被 RSSHub 屏蔽**
   - 尝试其他 RSSHub 实例
   - 或使用官方 X API

---

### 错误4: 返回空内容

**症状：**
- Actions 运行成功
- 但网站上没有显示该博主的推文

**原因：**
- 博主最近没有发推文（24小时内）
- RSSHub 缓存问题

**解决方案：**

1. **增加时间窗口**
   编辑 `.github/workflows/update-news.yml`：
   ```yaml
   python scripts/update_news.py --output-dir data --window-hours 72 --rss-opml feeds/follow.opml
   ```
   改为 72 小时（3天）

2. **检查博主是否真的发了推**
   - 访问博主的 X 主页
   - 确认最近有内容

3. **清除 RSSHub 缓存**
   在 RSS URL 后加参数：
   ```
   https://rsshub.app/twitter/user/karpathy?filter_cache=1
   ```

---

## 🔧 快速修复脚本

### 批量更换 RSSHub 实例

创建文件 `fix-rsshub.sh`：

```bash
#!/bin/bash
# 批量替换 RSSHub 实例

REPO_PATH="/path/to/your/repo"
OPML_FILE="$REPO_PATH/feeds/follow.opml"

# 备份原文件
cp "$OPML_FILE" "$OPML_FILE.backup"

# 替换为 pseudoyu 实例
sed -i '' 's|rsshub.app|rsshub.pseudoyu.com|g' "$OPML_FILE"

echo "✅ 已替换为 rsshub.pseudoyu.com"
echo "📁 原文件备份：$OPML_FILE.backup"

# 提交更改
cd "$REPO_PATH"
git add feeds/follow.opml
git commit -m "fix: 更换 RSSHub 实例到 pseudoyu"
git push

echo "🚀 已推送到 GitHub，等待 Actions 运行"
```

使用：
```bash
chmod +x fix-rsshub.sh
./fix-rsshub.sh
```

---

## 📊 测试 RSSHub 可用性

### 方法1：浏览器测试

依次在浏览器中打开：

```
https://rsshub.app/twitter/user/karpathy
https://rsshub.pseudoyu.com/twitter/user/karpathy  
https://rsshub.rssforever.com/twitter/user/karpathy
https://rss.shab.fun/twitter/user/karpathy
```

**能看到 XML 内容** = 该实例可用 ✅
**看到错误或空白** = 该实例不可用 ❌

### 方法2：命令行测试

```bash
# 测试单个博主
curl -I https://rsshub.pseudoyu.com/twitter/user/karpathy

# 期望输出：HTTP/1.1 200 OK
```

### 方法3：批量测试所有实例

```bash
#!/bin/bash
INSTANCES=(
  "rsshub.app"
  "rsshub.pseudoyu.com"
  "rsshub.rssforever.com"
  "rss.shab.fun"
)

for instance in "${INSTANCES[@]}"; do
  echo "测试: $instance"
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://$instance/twitter/user/karpathy")
  if [ "$status" = "200" ]; then
    echo "✅ $instance 可用"
  else
    echo "❌ $instance 不可用 (HTTP $status)"
  fi
  echo ""
done
```

---

## ✅ 推荐的修复流程

### 1. 诊断问题
- [ ] 查看 GitHub Actions 日志
- [ ] 确认具体错误类型（403/超时/解析失败）

### 2. 快速修复
- [ ] 在浏览器中测试多个 RSSHub 实例
- [ ] 选择可用的实例
- [ ] 批量替换 OPML 文件

### 3. 验证
- [ ] 提交更改
- [ ] 手动触发 Actions
- [ ] 等待 2-3 分钟
- [ ] 刷新网站检查结果

### 4. 优化（可选）
- [ ] 移除经常失败的博主
- [ ] 保留稳定的博主
- [ ] 考虑使用付费 X API（如需要100%稳定性）

---

## 🎯 最佳实践

### 1. 混合方案
```
✅ Follow Builders（25个账号，稳定）
✅ RSSHub（5-10个关键账号，免费但可能不稳定）
✅ X API（3-5个最重要的账号，付费但最稳定）
```

### 2. 定期检查
每周检查一次 `data/source-status.json`：
- 查看哪些源经常失败
- 及时替换实例或移除失败的源

### 3. 设置告警
可以配置 GitHub Actions 失败时发送邮件通知。

---

## 📞 仍然无法解决？

### 提供以下信息寻求帮助：

1. **GitHub Actions 日志截图**
   - "Update news data" 步骤的错误信息

2. **测试结果**
   - 哪些 RSSHub 实例可以访问
   - 哪些博主抓取失败

3. **OPML 配置**
   - `feeds/follow.opml` 的内容

4. **仓库地址**
   - 如果是公开仓库，提供链接

---

## 💡 临时解决方案

**如果 RSSHub 全部不可用：**

### 方案A：使用 Follow Builders（已内置）
- 已经包含 25 个精选建设者
- 无需配置
- 完全稳定

### 方案B：使用传统 RSS 源
某些博主可能有官方 RSS（很少）：
- Substack: `https://用户名.substack.com/feed`
- Medium: `https://medium.com/feed/@用户名`

### 方案C：等待修复
RSSHub 的限流通常是临时的：
- 等待几小时到几天
- 实例会恢复正常

---

## 🔄 更新记录

- 2026-05-15: 初版
- 添加批量测试脚本
- 添加多个备用 RSSHub 实例
