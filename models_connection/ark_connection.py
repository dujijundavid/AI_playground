import os
from openai import OpenAI
from dotenv import load_dotenv
# from context import context

# 从 .env 文件加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# Non-streaming:
if 0:
    print("----- standard request -----")
    completion = client.chat.completions.create(
        model = "deepseek-r1-250120",  # your model endpoint ID
        messages = [
            {"role": "system", "content": "你是人工智能助手"},
            {"role": "user", "content": "常见的十字花科植物有哪些？"},
        ],
    )
    print(completion.choices[0].message.content)

if 1:
# Streaming:
    print("----- streaming request -----")
    stream = client.chat.completions.create(
        model = "deepseek-r1-250120",  # your model endpoint ID
        messages = [
            {"role": "system", "content": "你是人工智能助手"},
            {"role": "user", "content": """任务：基于我得情况帮助我讲解 object oriented programming.我需要提高自己的理解深度

我是一名数据科学家，现在碰到了跟AI交互能力的瓶颈。

**可以完成的任务：**

1. 做出end to end 的data application，设计数据收集解析的executable scripts， 前后端搭建.
2. 常规机器学习与深度学习的任务。
3. 日常数据分析任务
4. 中等难度编程任务以及数据项复杂编程任务
5. Large scale analysis and engineering with Pyspark, spark SQL

**完成的不够好的：**

1. 复杂的machine learning system design.
2. production level software projects.

**我尝试学习以及掌握：**

1. prompt engineering 的最佳实践。
2. 通过api 调用不同的大模型。
3. 自动化的专利系统。通过CrewAI 框架。

**我认为自己的痛点：**

1. 每次交互的代码量大后，交互效率很低 （>300行）
2. 虽然code 包含classes 或者functions, 但是缺少testing.
3. 我不够理解classes, 很多时候是为了follow 软件工程的最佳实践而让ai这样生成。
4. 在databricks中使用 jupyternotebook导致有很多代码冗余和重复。
5. 没有学习过Cursor 相关的sde tools, 已经使用的copilot感觉不如直接与gpt交互。

思考我应该如何解决这些问题。定位我当前的水平。？"""},
        ],
        stream=True
    )

for chunk in stream:
    if not chunk.choices:
        continue
    print(chunk.choices[0].delta.content, end="")
print()