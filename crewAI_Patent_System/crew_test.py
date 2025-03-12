import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from crewai import Agent, Task, Crew, Process

# Load environment variables from .env file
load_dotenv()

# Initialize the language model
# llm = ChatOpenAI(
#     model_name="gpt-3.5-turbo",
#     temperature=0.7,
#     openai_api_key=os.getenv("OPENAI_API_KEY")
# )
llm = ChatOpenAI(
model_name="deepseek-chat",
temperature=0.7,
openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
openai_api_base="https://api.deepseek.com/v1"
)

# Define agents with detailed roles, goals, and backstories
initial_idea_agent = Agent(
    role="Harvard graduate McKinsey Consultant",
    goal="Help clarify and enhance initial patent ideas",
    backstory="With rich consulting experience, skilled in logical thinking, creative thinking, and critical analysis. Provides strategic insight for innovative solutions.",
    verbose=True,
    llm=llm
)

innovation_agent = Agent(
    role="Top OpenAI Prompt Engineer",
    goal="Identify effective questions and discover new patentable innovations",
    backstory="Specializing in prompt design and patent discovery, with a focus on AI and creative thinking for novel technological advancements.",
    verbose=True,
    llm=llm
)

qa_agent = Agent(
    role="Senior Patent Expert",
    goal="Answer patent drafting-related questions, ensuring accuracy and compliance with patent law",
    backstory="Expert in patent law, patent application procedures, and USPTO guidelines. Ensures that the patent meets all legal and technical requirements.",
    verbose=True,
    llm=llm
)

customization_agent = Agent(
    role="Patent Drafter",
    goal="Collaborate with experts to draft patents with technical details, incorporating mathematical formulas and deep learning methods",
    backstory="Experienced in AI, automotive data science, and mathematical modeling. Bridges the gap between cutting-edge technology and patent documentation.",
    verbose=True,
    llm=llm
)

deep_improvement_agent = Agent(
    role="Senior Algorithm Architect and Senior Patent Drafting Advisor",
    goal="Deeply improve patent drafts by enhancing technical feasibility, patentability, and clarity",
    backstory="Rich experience in AI algorithm research, patent drafting, and deep research in battery and vehicle data analysis. Ensures technical depth and innovation.",
    verbose=True,
    llm=llm
)

# Define tasks with detailed descriptions and expected outputs
initial_idea_task = Task(
    description="""Help conceptualize and refine Mercedes-Benz's initial patent idea. The core problem to solve involves [describe the specific problem]. Provide at least three specific improvement suggestions, each with detailed explanations and potential technical implementation methods.""",
    expected_output="Refined ideas with three potential improvements, including implementation methods and technical depth.",
    agent=initial_idea_agent,
    output_file="initial_ideas.md"
)

innovation_task = Task(
    description="""Identify and mine new patentable innovations. Propose effective questions and provide at least three new patent innovation points. For each, describe its uniqueness, background, and potential applications. Evaluate and select the most relevant innovations for Mercedes-Benz.""",
    expected_output="Three innovative points with clear descriptions, uniqueness, and applications.",
    agent=innovation_agent,
    output_file="innovations.md"
)

qa_task = Task(
    description="""Answer standard patent-related questions in detail, ensuring technical accuracy. Questions should cover the work done for the invention, its technical problems, existing related technologies, solutions, advantages, and a concise summary of the invention.""",
    expected_output="Complete, detailed answers to each question using professional terminology.",
    agent=qa_agent,
    output_file="qa_answers.md"
)

customization_task = Task(
    description="""Draft the patent document with technical details, including mathematical formulas and deep learning algorithms. Ensure the formulas are in a format that can be directly pasted into Word (no LaTeX), and use symbols like ∑, xᵢ, yⱼ, ∫, ⊕, ⊗, etc. Provide technical implementation details and algorithm descriptions, ensuring the content is highly actionable and professional.""",
    expected_output="A professional patent document in Chinese, including technical details, mathematical formulas, and algorithm descriptions.",
    agent=customization_agent,
    output_file="patent_draft.md"
)

deep_improvement_task = Task(
    description="""Perform deep improvements on the technical details, mathematical principles, and deep learning algorithms. Compare with existing technologies, highlight novelty, and enhance the patent document structure, including Background Technology, Invention Content, Specific Implementation Methods, and Claims.""",
    expected_output="Final improved patent document, exceeding 4000 words, with refined technical details, better logical structure, and improved patentability.",
    agent=deep_improvement_agent,
    output_file="final_patent.md"
)

# Create a crew with the agents and tasks, running them sequentially
patent_crew = Crew(
    agents=[
        initial_idea_agent,
        innovation_agent,
        qa_agent,
        customization_agent,
        deep_improvement_agent
    ],
    tasks=[
        initial_idea_task,
        innovation_task,
        qa_task,
        customization_task,
        deep_improvement_task
    ],
    process=Process.sequential,  # Define the order of task execution
    verbose=True
)

# Execute the patent drafting process
if __name__ == "__main__":
    result = patent_crew.kickoff()
    print("Patent Drafting Process Completed!")
    print(result)
