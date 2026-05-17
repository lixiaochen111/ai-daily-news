#!/bin/bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   AI筛选系统配置检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查 .env 文件
if [ -f ".env" ]; then
    echo "✅ .env 文件存在"
    
    # 检查API密钥
    if grep -q "EASYROUTER_API_KEY=your_api_key_here" .env; then
        echo "⚠️  API密钥未配置（仍是默认值）"
        echo ""
        echo "📝 配置步骤："
        echo "   1. 编辑文件: open .env"
        echo "   2. 修改这行: EASYROUTER_API_KEY=你的真实密钥"
        echo "   3. 保存文件"
    elif grep -q "EASYROUTER_API_KEY=.*[a-zA-Z0-9]" .env; then
        echo "✅ API密钥已配置"
    else
        echo "⚠️  API密钥为空"
    fi
    
    # 检查AI筛选开关
    if grep -q "AI_FILTER_ENABLED=1" .env; then
        echo "✅ AI筛选已启用"
    else
        echo "⚠️  AI筛选未启用（设为0或未设置）"
    fi
else
    echo "❌ .env 文件不存在"
    echo ""
    echo "📝 创建步骤："
    echo "   cp .env.example .env"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   配置文件位置: $(pwd)/.env"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
