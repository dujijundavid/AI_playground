#!/usr/bin/env python
# coding: utf-8

# # L6: Building Your Crew for Production

# ⏳ Note (Kernel Starting): This notebook takes about 30 seconds to be ready to use. You may start and watch the video while you wait.

# ## Initial Imports

# Warning control
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
from Deep_learning_AI_Courses.crew_ai_course1.crewAI_course2.helper import load_env
load_env()

# 💻 &nbsp; Access requirements.txt and helper.py files: 1) click on the "File" option on the top menu of the notebook and then 2) click on "Open". For more help, please see the "Appendix - Tips and Help" Lesson.

# ## Creating a new project

get_ipython().system(' crewai create crew new_project --provider openai')

# ## Setting up the Environment

# ⏳ Note: The following line might take a few minutes to finish.

get_ipython().system(' cd new_project && crewai install')

# ## Setting Environment Variables

get_ipython().system(' cat new_project/.env')

# ## Running the Crew

get_ipython().system(' cd new_project && crewai run')

# ## Flows CLI - Command Line Interface

get_ipython().system(' crewai create flow new_flow')

get_ipython().system(' ls -1 new_flow')

get_ipython().system(' ls -1 new_flow/src/new_flow/')