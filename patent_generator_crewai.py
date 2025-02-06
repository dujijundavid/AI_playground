#!/usr/bin/env python
# coding: utf-8

import os
import re
import yaml
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase
import pandas as pd

# 加载环境变量
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 配置 DeepSeek LLM
deepseek_llm = LLM(
    model="deepseek/deepseek-chat",  # 或 "deepseek/deepseek-reasoner"
    api_key=api_key,
    temperature=0.7
)
# --------------------------
# Load YAML Configurations
# --------------------------
def load_config():
    """Load configurations from YAML files."""
    config_files = {
        'agents': 'config/agents.yaml',
        'tasks': 'config/tasks.yaml'
    }
    configs = {}
    for key, path in config_files.items():
        with open(path, "r", encoding="utf-8") as f:
            configs[key] = yaml.safe_load(f)
    return configs

configs = load_config()
agents_config = configs["agents"]
tasks_config = configs["tasks"]

# -----------------------------------------
# Create Agents from YAML configuration
# -----------------------------------------
# Each agent is responsible for a particular patent drafting step.
initial_idea_agent = Agent(
    config=agents_config["initial_idea_agent"],
    llm=deepseek_llm
)

innovation_agent = Agent(
    config=agents_config["innovation_agent"],
    llm=deepseek_llm
)

qa_agent = Agent(
    config=agents_config["qa_agent"],
    llm=deepseek_llm
)

customization_agent = Agent(
    config=agents_config["customization_agent"],
    llm=deepseek_llm
)

deep_improvement_agent = Agent(
    config=agents_config["deep_improvement_agent"],
    llm=deepseek_llm
)
# -----------------------------------------
# Create Tasks using YAML configuration
# -----------------------------------------
# In your tasks.yaml, the steps are defined under a "steps" key.
# We create one Task per step using the configuration (description and max_tokens).
# Note: Here we assume the order of steps in tasks_config["steps"] matches:
# initial_idea, innovation, qa, customization, deep_improvement

steps = tasks_config["steps"]

initial_idea_task = Task(
    config=steps[0],
    agent=initial_idea_agent
)

innovation_task = Task(
    config=steps[1],
    agent=innovation_agent
)

qa_task = Task(
    config=steps[2],
    agent=qa_agent
)

customization_task = Task(
    config=steps[3],
    agent=customization_agent
)

deep_improvement_task = Task(
    config=steps[4],
    agent=deep_improvement_agent
)

# -----------------------------------------
# Create the Patent Crew
# -----------------------------------------
# The Crew groups all the Agents and Tasks.
# Using a sequential process ensures that each Task is executed one after the other,
# allowing the output of a previous task to be available as context if desired.
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
    process=Process.sequential,  # Sequential execution (or use Process.hierarchical if preferred)
    verbose=True
)

# -----------------------------------------
# Prepare Initial Input & Run the Crew
# -----------------------------------------
# Read the initial patent idea from file
initial_idea_file = "initial_idea.txt"
with open(initial_idea_file, "r", encoding="utf-8") as f:
    initial_idea_input = f.read().strip()

# Prepare inputs; here we pass the initial idea so that the first task can use it.
inputs = {"initial_idea": initial_idea_input}

# Kick off the crew to run all tasks sequentially.
result = patent_crew.kickoff(inputs=inputs)

# -----------------------------------------
# Save Task Outputs
# -----------------------------------------
# Create an output directory using a sanitized version of the initial idea.
folder_name = "patent_" + "_".join(re.findall(r"\w+", initial_idea_input)[:5])
output_dir = os.path.join("patent_outputs", folder_name)
os.makedirs(output_dir, exist_ok=True)

# Assuming each task output is accessible in the crew's final result, extract and save them.
# (Depending on your CrewAI configuration, outputs can be accessed via result.pydantic or as a dict.)
outputs = result.to_dict() if hasattr(result, "to_dict") else {}

# Loop through each step and write its output to a corresponding file.
for step in ["initial_idea", "innovation", "qa", "customization", "deep_improvement"]:
    output_file = os.path.join(output_dir, f"{step}_output.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(outputs.get(step, ""))
    print(f"Output for {step} saved to {output_file}")

# -----------------------------------------
# Estimate and Display Costs
# -----------------------------------------
# If your CrewAI instance tracks usage metrics, you can compute the estimated cost.
usage_metrics = patent_crew.usage_metrics  # This assumes usage_metrics is provided by the Crew after execution.
costs = 0.150 * (usage_metrics.prompt_tokens + usage_metrics.completion_tokens) / 1_000_000
print(f"Total estimated cost: ${costs:.4f}")

