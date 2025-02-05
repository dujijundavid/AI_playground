#!/usr/bin/env python
# coding: utf-8

# # L4: Support Data Insight Analysis

# ⏳ Note (Kernel Starting): This notebook takes about 30 seconds to be ready to use. You may start and watch the video while you wait.

# ## Initial Imports

# Warning control
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
from Deep_learning_AI_Courses.crew_ai_course1.crewAI_course2.helper import load_env
load_env()

import os
import yaml
from crewai import Agent, Task, Crew

# 💻 &nbsp; Access requirements.txt and helper.py files: 1) click on the "File" option on the top menu of the notebook and then 2) click on "Open". For more help, please see the "Appendix - Tips and Help" Lesson.

# ## Loading Tasks and Agents YAML files

# Define file paths for YAML configurations
files = {
    'agents': 'config/agents.yaml',
    'tasks': 'config/tasks.yaml'
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']

# ## Using FileReadTool

from crewai_tools import FileReadTool
csv_tool = FileReadTool(file_path='./support_tickets_data.csv')

# ## Creating Agents, Tasks and Crew

# Creating Agents
suggestion_generation_agent = Agent(
  config=agents_config['suggestion_generation_agent'],
  tools=[csv_tool]
)

reporting_agent = Agent(
  config=agents_config['reporting_agent'],
  tools=[csv_tool]
)

chart_generation_agent = Agent(
  config=agents_config['chart_generation_agent'],
  allow_code_execution=True
)

# Creating Tasks
suggestion_generation = Task(
  config=tasks_config['suggestion_generation'],
  agent=suggestion_generation_agent
)

table_generation = Task(
  config=tasks_config['table_generation'],
  agent=reporting_agent
)

chart_generation = Task(
  config=tasks_config['chart_generation'],
  agent=chart_generation_agent
)

final_report_assembly = Task(
  config=tasks_config['final_report_assembly'],
  agent=reporting_agent,
  context=[suggestion_generation, table_generation, chart_generation]
)

# Creating Crew
support_report_crew = Crew(
  agents=[
    suggestion_generation_agent,
    reporting_agent,
    chart_generation_agent
  ],
  tasks=[
    suggestion_generation,
    table_generation,
    chart_generation,
    final_report_assembly
  ],
  verbose=True
)

# ## Testing our Crew

support_report_crew.test(n_iterations=1, openai_model_name='gpt-4o')

# ## Training your crew and agents

support_report_crew.train(n_iterations=1, filename='training.pkl')

# ## Comparing new test results

support_report_crew.test(n_iterations=1, openai_model_name='gpt-4o')

# Display the Trello screenshot
from IPython.display import Image, display

# Load and display the image
test_image = Image(filename='test_before_training.png', width=368)
display(test_image)

# ## Kicking off Crew

result = support_report_crew.kickoff()

# ## Result

from IPython.display import display, Markdown
display(Markdown(result.raw))