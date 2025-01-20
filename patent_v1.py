import os
import openai
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_agent(agent_info, task_prompt, model="gpt-4o-mini", max_tokens=250, temperature=0.7):
    """
    Calls OpenAI API to generate a response.
    :param agent_info: Dictionary containing agent's role, goal, and backstory.
    :param task_prompt: Task description for the agent.
    :return: Generated response text.
    """
    system_message = (
        f"You are a {agent_info['role']}. Your goal is: {agent_info['goal']}. "
        f"Backstory: {agent_info['backstory']}"
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": task_prompt}
    ]

    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

# Define agent details
agents = {
    "initial_idea_agent": {
        "role": "Harvard-educated McKinsey Consultant",
        "goal": "Develop and refine initial ideas for patent drafting",
        "backstory": "An expert with extensive consulting experience, skilled in logical, creative, and critical thinking."
    },
    "innovation_agent": {
        "role": "Top OpenAI Prompt Engineer",
        "goal": "Identify effective questions and uncover new patentable ideas",
        "backstory": "A specialist in prompt design and patent mining, capable of generating innovative ideas."
    },
    "qa_agent": {
        "role": "Patent Expert",
        "goal": "Answer specific questions related to patent drafting",
        "backstory": "An expert in patent law and drafting techniques, familiar with USPTO guidelines."
    },
    "customization_agent": {
        "role": "Patent Drafter",
        "goal": "Collaborate with mathematicians, deep learning researchers, and Mercedes-Benz data scientists to draft a patent containing mathematical formulas, rules, and deep learning concepts.",
        "backstory": "A highly skilled patent drafter with expertise in AI, automotive data science, and mathematical modeling."
    }
}

# Read initial idea from file
initial_idea_file = "initial_idea.txt"
with open(initial_idea_file, "r", encoding="utf-8") as f:
    initial_idea_input = f.read().strip()


# Generate folder name based on key words from input
folder_name = "patent_" + "_".join(re.findall(r"\w+", user_input)[:5])  # Limit folder name to first 5 words
output_dir = os.path.join("patent_outputs", folder_name)
os.makedirs(output_dir, exist_ok=True)

# Execute tasks

tasks = {
    "initial_idea": ("Refine the following messy idea into a clear and effective patent concept: " + initial_idea_input, 500),
    "innovation": ("Based on the refined idea, identify three innovative and patentable ideas that expand or refine the concept.", 800),
    "qa": ("What are the key elements of a successful patent application, and how can technical details be effectively translated into legally robust descriptions?", 500),
    "customization": ("Using the previous outputs as reference, draft a complete patent document suitable for Mercedes-Benz, integrating mathematical formulas, deep learning models, and structured rules.", 3000)
}

results = {}
for task_name, (task_prompt, token_limit) in tasks.items():
    agent_key = task_name + "_agent" if task_name != "customization" else "customization_agent"
    results[task_name] = call_agent(agents[agent_key], task_prompt, max_tokens=token_limit)
    output_file = os.path.join(output_dir, f"{task_name}_output.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(results[task_name])
    print(f"=== {task_name.replace('_', ' ').title()} ===")
    print(results[task_name])
    print(f"Output saved to {output_file}\n")
