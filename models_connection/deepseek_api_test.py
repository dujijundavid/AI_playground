# 请先安装依赖: pip install openai python-dotenv
import os
from openai import OpenAI
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

# 获取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

# 初始化 DeepSeek API 客户端
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
print(client.models.list())
# # 发送请求
# response = client.chat.completions.create(
#     model="deepseek-chat",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": "Hello"},
#     ],
#     stream=False
# )

# # 输出返回结果
# print(response.choices[0].message.content)



