import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from datetime import datetime

# ========== 环境变量加载 ==========
load_dotenv()

# ========== 1) 自定义 LLM 对象 ==========

llm = ChatOpenAI(
    model="deepseek/deepseek-chat",  # 这里根据你的实际模型名称修改
    temperature=0.6,
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
# llm = ChatOpenAI(
#     model_name="gpt-4o-mini",
#     temperature=0.7,
#     openai_api_key=os.getenv("OPENAI_API_KEY")
# )

# ========== 2) 检查 initial_idea.txt 是否存在，如果存在就读取，否则生成默认想法 ==========

initial_idea_file_path = "initial_idea.txt"

if os.path.exists(initial_idea_file_path):
    with open(initial_idea_file_path, "r", encoding="utf-8") as f:
        initial_idea_content = f.read().strip()
    print("已检测到 initial_idea.txt 文件，使用其中的初始想法：")
    print(initial_idea_content)
else:
    # 如果没有 initial_idea.txt，则给出一个默认的想法，用于后续任务
    initial_idea_content = (
        "基于奔驰电动车的技术创新，比如针对其电池管理系统（BMS）、电机优化，"
        "或智能电控调度等相关专利的构思。"
        "请从中选取一个具体场景或核心技术进行发散。"
    )
    print("未找到 initial_idea.txt 文件，使用默认的奔驰电动车相关专利初始想法：")
    print(initial_idea_content)


# ========== 3) 定义所需代理人 (Agents) ==========

# A. 创意头脑风暴代理 - 产生 3 个相互独立的专利/技术方案
creative_brainstorm_agent = Agent(
    role="Creative Brainstorm Agent",
    goal="基于给定问题/场景，选择一个最佳方向，深入思考并且提出3 个相关且具有清晰技术思路的发明方案",
    backstory="发散思维专家，善于从不同角度提供具有潜在专利价值的创新点",
    llm=llm,
    verbose=True
)

# B. 方案评估/筛选代理 - 从 3 个想法中选出最优
idea_evaluator_agent = Agent(
    role="Idea Evaluator Agent",
    goal="对比 3 个想法的技术可行性、市场潜力、法律风险等，并选出最优方案",
    backstory="具备丰富的商业和专利评估经验",
    llm=llm,
    verbose=True
)

# C. 专利撰写问答代理 - 基于选定想法，回答专利撰写常见问题
qa_agent = Agent(
    role="Senior Patent Expert",
    goal="就选定发明想法回答标准专利撰写问题（技术问题、现有技术、核心创新点等）",
    backstory="专利法背景深厚，擅长专利技术与法律风险审阅",
    llm=llm,
    verbose=True
)

# D. 深度改进代理 - 审校与改进专利草稿，融入最佳实践
deep_improvement_agent = Agent(
    role="Deep Improvement Agent",
    goal="审阅并深度改进已有专利草稿，补充技术细节、商业模式、规避设计等",
    backstory="资深多领域专家，拥有批判性思维和专利实战经验",
    llm=llm,
    verbose=True
)

# E. 审阅与疑问解答代理 - 提出并解答 5 个可能的疑问点
review_explanation_agent = Agent(
    role="Review Clarification Agent",
    goal="阅读最终文档，列出可能难以理解的 5 个问题，并给出专业、简洁的解答",
    backstory="能够从读者视角发现潜在疑问，并提供详细且易于理解的回答",
    llm=llm,
    verbose=True
)


# ========== 4) 定义各个任务 (Tasks) ==========
# 辅助函数：统一将输出写入动态生成的文件夹中
def save_to_patent_folder(output: str, filename: str):
    """
    将输出内容保存到一个以时间戳命名的文件夹下，确保每次运行时都生成新的文件夹。
    """
    # 创建一个以当前时间戳为名称的文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join("patents", timestamp)
    os.makedirs(folder_path, exist_ok=True)

    # 保存文件
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Output saved to: {file_path}")

# 任务 1：头脑风暴，输出 3 个独立想法
brainstorm_task = Task(
    description=(
        f"初始想法背景：\n{initial_idea_content}\n\n"
        "请围绕【具体的技术/业务问题】头脑风暴出 3 个完全独立、互不重叠的解决方案；"
        "每个方案都需要具备清晰的技术原理、潜在应用场景和实现要点，"
        "并注意：若出现公式或算法描述，请使用可直接粘贴到 Word 的符号，如 ∑, xᵢ, yⱼ, ⊕ 等，不要使用 LaTeX。"
        "\n\n"
        "在输出中："
        "1) 以列表形式给出 3 个想法；"
        "2) 对每个想法分别阐述核心技术、可能应用场景；"
        "3) 不要合并想法或进行融合。"
    ),
    expected_output=(
        "以 Markdown 列表形式给出 3 个分隔明确的创新点；"
        "对各自的可行性、应用、关键技术进行简要阐述。"
    ),
    agent=creative_brainstorm_agent,
    output_file="brainstorm_ideas.md",  # This is now passed properly
    post_process=lambda output: save_to_patent_folder(output, "brainstorm_ideas.md")  # Using output_file dynamically
)

# 任务 2：评估筛选，选出最优方案
evaluate_task = Task(
    description=(
        "请阅读前一任务（3 个想法）的输出，对比它们在技术难度、原创性、"
        "等方面的优缺点，选出一个【最优】想法；"
        "并说明其它两个想法被淘汰的主要原因。"
        "\n\n"
        "最终输出：只需要保留被选中想法的核心描述，并附带其他两个想法的缺点总结。"
    ),
    expected_output=(
        "1) 最优想法的详细描述；"
        "2) 两个被淘汰想法的缺点或被淘汰原因。"
    ),
    agent=idea_evaluator_agent,
    output_file="selected_idea.md",  # Pass this as well
    post_process=lambda output: save_to_patent_folder(output, "selected_idea.md")  # Use output_file dynamically
)

# 任务 3：针对选出的最佳想法，回答标准专利相关问题
qa_task = Task(
    description=(
        "基于【上一步选出的最佳想法】，回答以下标准专利撰写问题：\n"
        "1) 该发明要解决的技术问题是什么？\n"
        "2) 现有类似技术有哪些？它们的不足或难点？\n"
        "3) 本发明的核心技术方案及实现方式；若需公式，请使用 ∑, xᵢ 等 Unicode 符号。\n"
        "4) 该发明所带来的优势和创新点；\n"
        "5) 简要的发明摘要。\n\n"
        "请使用专业且易理解的语言描述，并保证可直接粘贴到 Word。"
    ),
    expected_output=(
        "针对 1)~5) 的完整回答，"
        "能够用于专利草稿的核心描述。"
    ),
    agent=qa_agent,
    output_file="qa_answers.md",  # Pass this as well
    post_process=lambda output: save_to_patent_folder(output, "qa_answers.md")  # Use output_file dynamically
)

# 任务 4：深度改进（融入最佳实践）
deep_improvement_task = Task(
    description=(
        "现在我们已有一份专利草稿，请根据最佳实践做深度改进，"
        "并特别注意以下几点：\n"
        "1) 检查是否可补充更完整的技术细节（如算法步骤或公式，可用 ∫, ⊗, xᵢ, yⱼ 等符号）；\n"
        "2) 思考是否可能加入更多的技术细节，如深度学习或者LLM中的算法，以增加专利的技术深度；\n"
        "3) 思考是否应该加入阈值方便专利的原创性。；\n"
        "3) 综合各方面优化，使整体更易通过审查；\n"
        "4) 若涉及计算过程，请确保公式能被 Word 直接使用（无需 LaTeX）。\n\n"
        "请输出改进后的完整专利草稿，确保语言简洁专业、条理清晰。"
    ),
    expected_output="改进后的专利草稿全文。",
    agent=deep_improvement_agent,
    output_file="deep_improved_draft.md",  # Pass this as well
    post_process=lambda output: save_to_patent_folder(output, "deep_improved_draft.md")  # Use output_file dynamically
)

# 任务 5：提出并回答 5 个可能的疑问
confusion_task = Task(
    description=(
        "阅读前面所有步骤后得到的最终专利草稿，"
        "列出 5 个可能让读者感到困惑或难以理解的问题，"
        "并针对每个问题进行简要而准确的回答。"
        "\n\n"
        "你的输出应包括：\n"
        "1) 清晰列出 5 个问题；\n"
        "2) 逐一给出回答，侧重解释疑点和提供必要的背景或技术补充；\n"
        "3) 保证回答在专业性与可理解度之间达到平衡。"
    ),
    expected_output=(
        "最终输出中含 5 个问答对，每个问答都要明确问题点和解答要点。"
    ),
    agent=review_explanation_agent,
    output_file="confusion_and_answers.md",  # Pass this as well
    post_process=lambda output: save_to_patent_folder(output, "confusion_and_answers.md")  # Use output_file dynamically
)



# ========== 5) 将所有任务组装进一个 Crew 并串行执行 ==========

patent_crew = Crew(
    agents=[
        creative_brainstorm_agent,
        idea_evaluator_agent,
        qa_agent,
        deep_improvement_agent,
        review_explanation_agent
    ],
    tasks=[
        brainstorm_task,
        evaluate_task,
        qa_task,
        deep_improvement_task,
        confusion_task
    ],
    process=Process.sequential,
    verbose=True
)


if __name__ == "__main__":
    result = patent_crew.kickoff()
    print("Patent Drafting Process Completed!")
    print(result)