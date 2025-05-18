
import os
import re
import yaml
from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process

# ========== 环境变量加载 ==========
load_dotenv()

# ========== 1) 准备初始想法 ==========
initial_idea_file = "initial_idea.txt"
if os.path.exists(initial_idea_file):
    with open(initial_idea_file, encoding="utf-8") as f:
        initial_idea = f.read().strip()
else:
    initial_idea = (
        "基于奔驰电动车的技术创新，比如针对其电池管理系统（BMS）、电机优化，"
        "或智能电控调度等相关专利的构思。"
        "请从中选取一个具体场景或核心技术进行发散。"
    )

# ========== 2) 生成专利名称 ==========
def get_patent_name(text: str) -> str:
    clean = re.sub(r"[^\w\u4e00-\u9fa5 ]+", "", text)
    parts = clean.split()
    if len(parts) >= 5:
        name = "_".join(parts[:5])
    else:
        chars = [c for c in clean if c.strip()]
        name = "".join(chars[:5])
    return re.sub(r"[^\w\u4e00-\u9fa5]+", "_", name) or "patent_default"

patent_name = get_patent_name(initial_idea)

# ========== 3) 准备输出目录 ==========
BASE_OUTPUT_DIR = os.path.join("generated_patent", patent_name)
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# ========== 4) 加载全局配置 ==========
with open("config.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# ========== 5) 初始化 LLM ==========
llm = ChatOpenAI(
    model="deepseek/deepseek-chat",
    temperature=0.6,
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# ========== 6) 定义 Agents ==========
agents = {
    "creative_brainstorm_agent": Agent(
        role="Creative Brainstorm Agent",
        goal="基于给定问题/场景，提出3个相关且具有清晰技术思路的发明方案",
        backstory="发散思维专家，擅长专利创新点",
        llm=llm, verbose=True
    ),
    "idea_evaluator_agent": Agent(
        role="Idea Evaluator Agent",
        goal="对比3个想法的技术可行性、市场潜力、法律风险，选出最优方案",
        backstory="商业&专利评估专家",
        llm=llm, verbose=True
    ),
    "qa_agent": Agent(
        role="Senior Patent Expert",
        goal="就选定发明想法回答专利撰写常见问题",
        backstory="专利法和技术双背景专家",
        llm=llm, verbose=True
    ),
    "deep_improvement_agent": Agent(
        role="Deep Improvement Agent",
        goal="审校并深度改进已有专利草稿，补充技术细节与商业模式",
        backstory="资深多领域专家",
        llm=llm, verbose=True
    ),
    "review_explanation_agent": Agent(
        role="Review Clarification Agent",
        goal="列出5个潜在疑问，并提供专业解答",
        backstory="从读者视角发现疑问并答疑",
        llm=llm, verbose=True
    ),
    "mermaid_chart_agent": Agent(
        role="Mermaid Chart Generator",
        goal="根据选定方案生成 mermaid 格式流程图",
        backstory="专利技术可视化专家",
        llm=llm, verbose=True
    )
}

# 如果 config.yaml 中有额外 agents，也一并初始化
for a in cfg.get("agents", []):
    agents[a["name"]] = Agent(
        role=a["role"], goal=a["goal"], backstory=a["backstory"],
        llm=llm, verbose=True
    )

# ========== 7) 构建 Tasks ==========
tasks = []
prev_file = None

for t_conf in cfg["tasks"]:
    desc = t_conf["description"]
    if prev_file:
        desc = desc.replace("{prev_output_file}", prev_file)
    out_path = os.path.join(BASE_OUTPUT_DIR, t_conf["output_file"])
    tasks.append(
        Task(
            description=desc,
            expected_output=t_conf["expected_output"],
            agent=agents[t_conf["agent"]],
            output_file=out_path
        )
    )
    prev_file = t_conf["output_file"]

    # 在评估想法后插入 Mermaid 任务
    if t_conf["agent"] == "idea_evaluator_agent":
        mermaid_desc = (
            f"请根据被选中的专利方案（文件：{prev_file}）生成一个 mermaid 格式的流程图，"
            "只输出 mermaid 代码块，不要其他内容。"
        )
        mermaid_out = os.path.join(BASE_OUTPUT_DIR, "mermaid_chart.md")
        tasks.append(
            Task(
                description=mermaid_desc,
                expected_output="mermaid 格式流程图代码块",
                agent=agents["mermaid_chart_agent"],
                output_file=mermaid_out
            )
        )
        prev_file = "mermaid_chart.md"

# ========== 8) 组装并运行 Crew ==========
patent_crew = Crew(
    agents=list(agents.values()),
    tasks=tasks,
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    result = patent_crew.kickoff()
    print("✅ 专利撰写流程完成，所有文件已保存到：", BASE_OUTPUT_DIR)
    print(result)
