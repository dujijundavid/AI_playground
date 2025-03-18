import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# 环境变量加载
load_dotenv()

# LLM初始化 (DeepSeek)
llm = ChatOpenAI(
    model="deepseek/deepseek-chat",
    temperature=0.5,
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# 专利评估处理器（避免继承问题）
class PatentEvaluator:
    def __init__(self):
        self.criteria = {
            "novelty": 0.3,
            "feasibility": 0.25,
            "market": 0.2,
            "defensibility": 0.15,
            "cost": 0.1
        }
    
    def evaluate(self, ideas: List[Dict]) -> List[Tuple[Dict, float]]:
        """专利评估算法"""
        scores = []
        for idea in ideas:
            score = sum(idea.get(k, 0)*v for k,v in self.criteria.items())
            scores.append((idea, score))
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def check_diversity(self, ideas: List[str]) -> bool:
        """创新点去重检查"""
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(ideas)
        similarity = cosine_similarity(matrix)
        return np.all(similarity < 0.3)

# 智能体初始化
idea_agent = Agent(
    role="首席专利架构师",
    goal="生成三个完全独立的专利创意",
    backstory="拥有十年专利开发经验的技术专家",
    verbose=True,
    llm=llm,
    memory=True,
    allow_delegation=False
)

evaluator_agent = Agent(
    role="专利评估专家",
    goal="量化评估专利创意的商业价值",
    backstory="曾任国际专利局审查委员的技术经济学家",
    verbose=True,
    llm=llm
)

tech_agent = Agent(
    role="技术文档专家",
    goal="撰写符合专利法要求的详细技术文档",
    backstory="具有法律和技术双重背景的专利律师",
    verbose=True,
    llm=llm
)

# 任务流水线
brainstorm_task = Task(
    description="为梅赛德斯奔驰生成三个独立的专利方向，确保技术领域不重叠",
    expected_output="""三个创新方案，每个包含：
    1. 技术原理示意图（文字描述）
    2. 创新性声明
    3. 可行性初步分析""",
    agent=idea_agent,
    output_file="patent_ideas.md"
)

evaluation_task = Task(
    description="对生成的专利方案进行量化评分",
    expected_output="""Markdown表格包含：
    | 方案 | 新颖性 | 可行性 | 市场 | 防御性 | 成本 | 总分 |""",
    agent=evaluator_agent,
    context=[brainstorm_task],
    output_file="evaluation.md",
    human_input=True  # 允许人工干预评分
)

draft_task = Task(
    description="对最优方案进行专利文档开发",
    expected_output="完整的中文专利文档，包含：\n- 技术领域\n- 背景技术\n- 发明内容\n- 具体实施方式",
    agent=tech_agent,
    context=[evaluation_task],
    output_file="final_patent.md",
    async_execution=True  # 异步执行
)

# 系统执行
patent_system = Crew(
    agents=[idea_agent, evaluator_agent, tech_agent],
    tasks=[brainstorm_task, evaluation_task, draft_task],
    process=Process.sequential,
    verbose=2
)

if __name__ == "__main__":
    # 专利生成流程
    result = patent_system.kickoff()
    
    # 后处理
    evaluator = PatentEvaluator()
    ideas = [task.output for task in brainstorm_task.results]
    
    # 创新性检查
    if not evaluator.check_diversity(ideas):
        print("警告：检测到创意相似度过高，建议重新生成！")
    
    print("专利生成流程完成！")
    print(result)