#!/usr/bin/env python3
"""
Test GLM-4.7-Flash with official Zhipu AI SDK

Wait 5-10 minutes after rate limit error before running this test.
"""

import os
import sys
from scripts.ai_filter.glm_client import GLMClient

# Load environment
from dotenv import load_dotenv
load_dotenv()

def test_glm_official():
    print("=" * 60)
    print("测试 GLM-4.7-Flash（官方SDK）")
    print("=" * 60)

    # Test with default key
    print("\n[Test 1] 使用默认共享密钥")
    print("-" * 60)

    try:
        client = GLMClient()  # Will use default key
        print(f"✓ 客户端初始化成功")
        print(f"  - 使用共享密钥: {client.using_shared_key}")
        print(f"  - 使用官方SDK: {client.using_official_sdk}")
        print(f"  - API Key: {client.api_key[:20]}...")

        print("\n发送测试请求...")
        response = client.call_model(
            model="glm-4.7-flash",
            system_prompt="你是一个AI内容分类器。",
            user_prompt='请用JSON格式判断：标题"ChatGPT发布新功能"是否与AI相关。返回格式：{"is_relevant": true/false, "reason": "理由"}',
            temperature=0.1,
            max_tokens=100
        )

        print("\n✅ 测试成功！")
        print(f"响应内容:\n{response['content']}")
        print(f"\nToken使用:")
        print(f"  - 输入: {response['usage']['prompt_tokens']}")
        print(f"  - 输出: {response['usage']['completion_tokens']}")
        print(f"  - 总计: {response['usage']['total_tokens']}")

        # Verify content is not empty
        if not response['content'] or response['content'].strip() == '':
            print("\n⚠️  警告：响应内容为空！")
            return False
        else:
            print("\n✓ 响应内容正常")
            return True

    except Exception as e:
        print(f"\n❌ 测试失败: {type(e).__name__}: {str(e)}")
        print("\n如果是速率限制错误，请等待5-10分钟后重试")
        return False

if __name__ == "__main__":
    success = test_glm_official()
    sys.exit(0 if success else 1)
