import os
import openai
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_agent(agent_info, user_prompt, max_tokens=3000):
    """
    Calls the OpenAI Chat Completion endpoint with a system and user message,
    including agent_info in the system message.
    """
    system_message = f"""你是一位帮助梅赛德斯-奔驰进行专利撰写的AI专家。
你的专属角色是：{agent_info['role']}
你的目标是：{agent_info['goal']}
你的背景是：{agent_info['backstory']}

请注意以下要求：
1. 数学公式必须使用可在Word中直接粘贴的格式（不要使用LaTeX）。
2. 使用标准数学符号，如：∑, xᵢ, yⱼ, ∫, ⊕, ⊗, 矩阵表示等。
3. 公式可直接复制到Word中，而无需任何转换。

务必遵守上述约定。
"""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",  # 如果需要，可替换为合适的GPT或OpenAI模型
        messages=messages,
        temperature=0.7,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

# 定义各个代理的信息
agents = {
    "initial_idea_agent": {
        "role": "毕业于Harvard的McKinsey Consultant",
        "goal": "帮助明确和提升初步专利想法",
        "backstory": "具有丰富咨询经验，善于逻辑思考、创新思维及批判性分析。"
    },
    "innovation_agent": {
        "role": "顶尖OpenAI Prompt Engineer",
        "goal": "识别有效问题并挖掘新的可专利创新点",
        "backstory": "专注于prompt设计和专利发掘，拥有创造性思维。"
    },
    "qa_agent": {
        "role": "资深专利专家",
        "goal": "回答专利撰写的相关疑问",
        "backstory": "精通专利法和专利申请流程，熟悉USPTO指南。"
    },
    "customization_agent": {
        "role": "专利撰写人",
        "goal": "与数学家、深度学习研究者以及奔驰数据科学家合作，撰写包含数学公式、规则和深度学习方法的专利",
        "backstory": "在AI、汽车数据科学及数学建模领域具备丰富经验。"
    }
}

# 读取初步想法的文本文件
initial_idea_file = "initial_idea.txt"
with open(initial_idea_file, "r", encoding="utf-8") as f:
    initial_idea_input = f.read().strip()

# 基于初步想法生成输出文件夹名称
folder_name = "patent_" + "_".join(re.findall(r"\w+", initial_idea_input)[:5])
output_dir = os.path.join("patent_outputs", folder_name)
os.makedirs(output_dir, exist_ok=True)

# 准备所需的任务及对应的token限制
tasks = {
    "initial_idea": (
        # Step1: 描述信息
        "### Step1: 描述信息\n\n"
        "目标：\n\n"
        "[我需要你去帮助我构思并且梳理观点，它的主题是：\n\n"
        "核心需要解决的问题：\n\n"
        "首先，请毕业于**stanford的Databricks Senior Software engineer and Data Engineer**，"
        "揣摩我的观点，帮助我思考并完善这个点子。带有强的逻辑性，创造性，以及批判性思维。\n",
        500
    ),
    "innovation": (
        # Step2: 交互挖掘创新点
        "### Step2： 交互挖掘创新点\n\n"
        "- 首先，请顶尖的**open AI prompt engineer** 帮助我思考，提出有效的问题，并且挖掘新的专利点\n\n"
        "不着急，think step by step, 加入你的思考逻辑，描述出三个创新点\n",
        800
    ),
    "qa": (
        # Step3: 抛出常规的问题
        "### Step3: 抛出常规的问题\n\n"
        "1. 为了这项发明进行了哪些工作？\n"
        "2. 本发明解决了哪些技术问题？\n"
        "3. 知悉与本发明相关的背景知识或现有技术吗（例如专利文献、竞品等），其存在的缺点是什么？\n"
        "4. 问题的解决方案是什么？\n"
        "5. 本发明可以实现哪些有益效果和/或优势？\n"
        "6. 以简短摘要的形式用英文概括本发明的核心内容？\n",
        1000
    ),
    "customization": (
        # Step4: 技术细节与专利撰写
        "### Step4: 请合适的专家团队设计技术细节\n\n"
        "针对以下问题解决方案：为Mercedes Benz 写出customized patent，要有4000+字符，"
        "请数学家优化并且加入逻辑与公式，让Tech Lead 加入更多技术实现和算法的细节。"
        "细节需要公式化，模型化，参照以下的样例。\n\n"
        "已经通过的专利案例\n\n"
        "请深入思考并且改进，挑出亮点或者缺失的部分，加入到现有的专利系统中，改进。\n\n"
        "另外输出得专利应该是中文而不是英文。\n",
        16000
    )
}

results = {}
for task_name, (task_prompt, token_limit) in tasks.items():
    # 根据任务名称决定所用的代理
    agent_key = task_name + "_agent" if task_name != "customization" else "customization_agent"
    
    # 调用对应代理获取输出
    results[task_name] = call_agent(
        agents[agent_key],
        task_prompt,
        max_tokens=token_limit
    )

    # 将输出写入文件
    output_file = os.path.join(output_dir, f"{task_name}_output.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(results[task_name])

    # 在控制台打印结果
    print(f"=== {task_name.replace('_', ' ').title()} ===")
    print(results[task_name])
    print(f"Output saved to {output_file}\n")
