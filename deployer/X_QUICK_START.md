# X API 快速开始 - 3分钟配置

## 🚀 最简单的方式（推荐）

### 方案：RSSHub（免费，3分钟配置）

**直接在 deployer 中操作即可！**

#### 步骤：

1. **启动 deployer**
2. **填写第1-2步**（基本信息和 GitHub token）
3. **在第3步（RSS 订阅源）添加以下 URL：**

```
https://rsshub.app/twitter/user/karpathy
https://rsshub.app/twitter/user/sama
https://rsshub.app/twitter/user/swyx
https://rsshub.app/twitter/user/amasad
https://rsshub.app/twitter/user/garrytan
```

4. **继续完成部署**

**就这么简单！** 5分钟后您的网站就会显示这些博主的推文。

---

## 🎯 推荐的中文博主

在第3步添加：

```
https://rsshub.app/twitter/user/op7418
https://rsshub.app/twitter/user/dotey
https://rsshub.app/twitter/user/tuturetom
https://rsshub.app/twitter/user/shao__meng
https://rsshub.app/twitter/user/9hills
```

---

## 📝 自定义其他博主

格式：`https://rsshub.app/twitter/user/用户名`

**如何找到用户名？**
1. 访问博主的 X 主页
2. URL 格式：`https://x.com/用户名`
3. 复制用户名
4. 拼接成：`https://rsshub.app/twitter/user/用户名`

**示例：**
- Naval: https://x.com/naval → `https://rsshub.app/twitter/user/naval`
- Paul Graham: https://x.com/paulg → `https://rsshub.app/twitter/user/paulg`

---

## ⚠️ 注意事项

### RSSHub 可能不稳定
- 如果某个博主的 feed 加载失败，是正常的
- 可以尝试更换 RSSHub 实例：
  - `rsshub.app` → `rsshub.pseudoyu.com`
  - 例如：`https://rsshub.pseudoyu.com/twitter/user/karpathy`

### 推荐做法
1. **先添加3-5个最重要的博主**
2. **部署后测试是否正常**
3. **如果正常，再逐步添加更多**

---

## 💰 需要更稳定？考虑付费 X API

如果 RSSHub 经常失效，可以使用官方 X API（付费）。

**成本参考：**
- 10个博主，每天抓取10条推文：**$1.50/月**
- 25个博主，每天抓取25条推文：**$3.75/月**

详细配置见：`X_API_GUIDE.md`

---

## ✅ 完整示例配置

在 deployer 第3步中，复制粘贴以下内容（选择您感兴趣的）：

### AI/ML 领域
```
https://rsshub.app/twitter/user/karpathy
https://rsshub.app/twitter/user/sama
https://rsshub.app/twitter/user/gdb
https://rsshub.app/twitter/user/xlr8harder
```

### 创业/产品
```
https://rsshub.app/twitter/user/levelsio
https://rsshub.app/twitter/user/swyx
https://rsshub.app/twitter/user/amasad
https://rsshub.app/twitter/user/naval
```

### 投资/趋势
```
https://rsshub.app/twitter/user/garrytan
https://rsshub.app/twitter/user/pmarca
https://rsshub.app/twitter/user/elonmusk
```

### 中文 AI 社区
```
https://rsshub.app/twitter/user/op7418
https://rsshub.app/twitter/user/dotey
https://rsshub.app/twitter/user/tuturetom
```

---

## 🔍 验证配置成功

部署完成后：

1. **等待3-5分钟**（GitHub Actions 运行）
2. **访问您的网站**
3. **应该看到：**
   - 博主的推文出现在新闻列表中
   - 标题显示推文内容
   - 点击可以跳转到原推文

如果没有看到推文：
- 检查 GitHub Actions 是否成功运行
- 查看 `data/source-status.json` 中的错误信息
- 尝试更换 RSSHub 实例或减少博主数量

---

## 🆘 常见问题

**Q: 推文内容显示不完整？**
A: RSSHub 有字数限制，这是正常的。可以点击链接查看完整推文。

**Q: 某些博主的推文不显示？**
A: 可能是该博主最近没有发推文，或者 RSSHub 实例暂时无法访问。

**Q: 可以只看推文，不看其他新闻吗？**
A: 可以！在网站上使用"站点筛选"功能，选择 X/Twitter 相关的源。

**Q: 推文更新频率？**
A: 默认每6小时更新一次（可以在第4步修改）。

---

## 🎉 就是这么简单！

现在您已经知道如何添加 X 博主推文了。

**记住核心公式：**
```
https://rsshub.app/twitter/user/用户名
```

立即打开 deployer，在第3步添加您关注的博主吧！🚀
