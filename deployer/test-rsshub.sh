#!/bin/bash

INSTANCES=(
  "rsshub.app"
  "rsshub.pseudoyu.com"
  "rsshub.rssforever.com"
  "rss.shab.fun"
)

echo "测试 RSSHub 实例可用性..."
echo ""

for instance in "${INSTANCES[@]}"; do
  echo "测试: $instance"
  status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "https://$instance/twitter/user/karpathy")
  if [ "$status" = "200" ]; then
    echo "✅ $instance 可用 (HTTP $status)"
  else
    echo "❌ $instance 不可用 (HTTP $status)"
  fi
  echo ""
done

echo "建议: 在浏览器中访问以下链接验证:"
echo "https://rsshub.pseudoyu.com/twitter/user/karpathy"
echo "https://rsshub.rssforever.com/twitter/user/karpathy"
