import os
import openai
import re
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_agent(agent_info, user_prompt, max_tokens=3000):
    """
    调用 OpenAI Chat Completion，组合 agent_info 到 system_message 中，并发送 user_prompt。
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
        {"role": "user", "content": user_prompt},
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",   # 或者你自己的模型名称，比如"gpt-4o-mini"
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        print(f"OpenAI API 错误: {e}")
        return ""

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

# 改进后的任务定义
tasks = {
    "initial_idea": (
        "### Step1: 描述信息\n\n"
        "**目标：**\n"
        "帮助构思并梳理梅赛德斯-奔驰的初步专利想法。\n\n"
        "**核心需要解决的问题：**\n"
        "[在此详细描述需要解决的技术问题或需求]\n\n"
        "**任务指令：**\n"
        "请以**斯坦福大学毕业的Tesla 数据科学家，以及宁德时代电化学专家**的身份，"
        "揣摩我的观点，帮助我思考并完善这个点子。输出应具备强逻辑性、创造性和批判性思维。\n\n"
        "**要求：**\n"
        "1. 提供至少三个具体的改进建议。\n"
        "2. 每个建议应包括详细的说明和潜在的技术实现方法。\n",
        600
    ),
    "innovation": (
        "### Step2：交互挖掘创新点\n\n"
        "**任务背景：**\n"
        "基于初步想法，识别和挖掘新的可专利创新点。\n\n"
        "**任务指令：**\n"
        "请作为顶尖的**OpenAI Prompt Engineer**，提出有效的问题并挖掘出至少三个新的专利创新点。"
        "请详细描述每个创新点的独特性和潜在应用。\n\n"
        "**要求：**\n"
        "1. 每个创新点应包括背景说明、创新之处及其优势。\n"
        "2. 逻辑清晰，步骤分明，便于后续专利撰写。\n"
        "3. 评估并且选出最有可能实现，且与奔驰合适的专利\n",
        900
    ),
    "qa": (
        "### Step3: 抛出常规的问题\n\n"
        "**任务背景：**\n"
        "为确保专利撰写的全面性和深度，需回答一系列常规问题。\n\n"
        "**任务指令：**\n"
        "请作为资深专利专家，针对以下问题提供详细回答：\n\n"
        "1. 为了这项发明进行了哪些工作？\n"
        "2. 本发明解决了哪些技术问题？\n"
        "3. 了解与本发明相关的背景知识或现有技术吗（例如专利文献、竞品等），其存在的缺点是什么？\n"
        "4. 问题的解决方案是什么？\n"
        "5. 本发明可以实现哪些有益效果和/或优势？\n"
        "6. 以简短摘要的形式用英文概括本发明的核心内容？\n\n"
        "**要求：**\n"
        "1. 每个问题的回答应详尽且具体。\n"
        "2. 使用专业术语，确保内容的准确性和权威性。\n",
        1200
    ),
    "customization": (
        "### Step4: 技术细节与专利撰写\n\n"
        "**任务背景：**\n"
        "基于前几步的输出，设计专利的技术细节，并撰写完整的专利文档。\n\n"
        "**任务指令：**\n"
        "请作为**专利撰写人**，与数学家、深度学习研究者以及梅赛德斯-奔驰的数据科学家合作，"
        "撰写包含数学公式、规则和深度学习方法的专利。具体要求如下：\n\n"
        "1. **数学公式**：优化并加入逻辑与公式，使用可在Word中直接粘贴的格式（不使用LaTeX），"
        "使用标准数学符号（如∑, xᵢ, yⱼ, ∫, ⊕, ⊗, 矩阵表示等）。\n"
        "2. **技术实现**：加入更多技术实现和算法的细节，确保内容具有高度的技术性和可操作性。\n"
        "3. **结构和格式**：参照以下的样例专利案例，确保内容结构清晰、逻辑严谨。\n\n"
        "**样例专利案例：**\n"
        "[在此插入已通过的专利案例的摘要或链接]\n\n"
        "**要求：**\n"
        "1. 专利文档需以中文撰写。\n"
        "2. 深入思考并改进，挑出现有专利系统中的亮点或缺失部分，进行补充和优化。\n"
        "3. 整体输出应超过4000个字符，内容详尽、专业。\n",
        16000
    )
}

# 定义一个函数用于拼接提示，把前面步骤的输出也融进来
def build_prompt_for_step(step_name, tasks, results):
    """
    根据当前 step_name，拼接该 step 的任务提示 + 前面步骤的输出摘要（若需要）。
    """
    # 取当前 step 的基础任务提示
    base_prompt = tasks[step_name][0]

    # 根据不同 step，加入对前面步骤结果的引用
    if step_name == "initial_idea":
        # Step1 没有前序步骤
        return base_prompt
    
    elif step_name == "innovation":
        # Step2 需要引用 Step1 的结果
        previous_output = results.get("initial_idea", "")
        prompt = (
            base_prompt
            + "\n\n---\n\n"
            + "这是基于上一步（Step1）的输出，请在此基础上进行思考：\n"
            + previous_output
        )
        return prompt
    
    elif step_name == "qa":
        # Step3 需要引用 Step1 & Step2 的结果
        step1_output = results.get("initial_idea", "")
        step2_output = results.get("innovation", "")
        prompt = (
            base_prompt
            + "\n\n---\n\n"
            + "参考之前步骤：\n\n"
            + "【Step1 输出】\n" + step1_output + "\n\n"
            + "【Step2 输出】\n" + step2_output
        )
        return prompt
    
    elif step_name == "customization":
        # Step4 需要引用 Step1, Step2 & Step3 的结果
        step1_output = results.get("initial_idea", "")
        step2_output = results.get("innovation", "")
        step3_output = results.get("qa", "")
        prompt = (
            base_prompt
            + "\n\n---\n\n"
            + "以下是前面三个步骤的内容，请整合利用：\n\n"
            + "【Step1】\n" + step1_output + "\n\n"
            + "【Step2】\n" + step2_output + "\n\n"
            + "【Step3】\n" + step3_output
        )
        return prompt

    else:
        # 默认返回
        return base_prompt

# 存储每个步骤的输出
results = {}

# 按顺序执行四个步骤
for task_name in ["initial_idea", "innovation", "qa", "customization"]:
    # 获取对应的代理信息
    agent_key = {
        "initial_idea": "initial_idea_agent",
        "innovation": "innovation_agent",
        "qa": "qa_agent",
        "customization": "customization_agent"
    }[task_name]
    
    # 获取该步骤的 max_tokens
    token_limit = tasks[task_name][1]
    
    # 构建当前 step 的提示，包含前面步骤输出
    user_prompt = build_prompt_for_step(task_name, tasks, results)
    
    # 调用对应代理
    result = call_agent(
        agents[agent_key],
        user_prompt,
        max_tokens=token_limit
    )
    
    if result:
        results[task_name] = result
        # 将输出写入文件
        output_file = os.path.join(output_dir, f"{task_name}_output.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        
        print(f"=== {task_name.replace('_', ' ').title()} ===")
        print(result)
        print(f"Output saved to {output_file}\n")
    else:
        print(f"=== {task_name.replace('_', ' ').title()} ===")
        print("未能获取有效的输出。请检查API调用或提示内容。")
        print("\n")
