import os
from openai import OpenAI
from dotenv import load_dotenv
from context import context

# 从 .env 文件加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# Non-streaming:
print("----- standard request -----")
completion = client.chat.completions.create(
    model = "deepseek-r1-250120",  # your model endpoint ID
    messages = [
        {"role": "system", "content": "你是人工智能助手"},
        {"role": "user", "content": "常见的十字花科植物有哪些？"},
    ],
)
print(completion.choices[0].message.content)

# Streaming:
print("----- streaming request -----")
stream = client.chat.completions.create(
    model = "deepseek-r1-250120",  # your model endpoint ID
    messages = [
        {"role": "system", "content": "你是人工智能助手"},
        {"role": "user", "content": "常见的十字花科植物有哪些？"},
    ],
    stream=True
)

for chunk in stream:
    if not chunk.choices:
        continue
    print(chunk.choices[0].delta.content, end="")
print()