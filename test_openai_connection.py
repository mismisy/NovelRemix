
from openai import OpenAI
import traceback

# API密钥
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# 第三方URL
BASE_URL = "https://your-third-party-url.com/v1"
# 模型名称
MODEL_NAME = "gpt-4-turbo"

print("--- 开始连接测试 ---")
print(f"目标URL: {BASE_URL}")
print(f"使用模型: {MODEL_NAME}")

try:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=BASE_URL,
    )
    print("\n[步骤 1/2] 客户端初始化成功。")

    print("[步骤 2/2] 正在发送测试消息 '你好'...")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "你好"}],
        temperature=0,
        max_tokens=50
    )


    print("\n 连接成功！")
    print("--------------------")
    print("模型回复内容:")
    print(response.choices[0].message.content)
    print("--------------------")

except Exception as e:

    print("\n 连接失败！")
    print("--------------------")
    print("错误类型:", type(e).__name__)
    print("详细错误信息:")
    traceback.print_exc()
    print("--------------------")

finally:
    print("\n--- 测试结束 ---")