from typing import Optional
from crewai import Agent, Task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool

# Define the support agent
support_agent = Agent(
    role="Senior Support Representative",
    goal="Be the most friendly and helpful support representative in your team",
    backstory=(
        "You work at crewAI (https://crewai.com) and are now working on providing "
        "support to {customer}, a supepip r important customer for your company. "
        "You need to make sure that you provide the best support! "
        "Make sure to provide full complete answers, and make no assumptions."
    ),
    allow_delegation=False,
    verbose=True
)

# Properly initialize the ScrapeWebsiteTool from crewai_tools with a URL
docs_scrape_tool = ScrapeWebsiteTool(website_url="https://crewai.com/docs")

# Define the inquiry resolution task
inquiry_resolution = Task(
    description=(
        "{customer} just reached out with a super important ask:\n"
        "{inquiry}\n\n"
        "{person} from {customer} is the one that reached out. "
        "Make sure to use everything you know to provide the best support possible. "
        "You must strive to provide a complete and accurate response to the customer's inquiry."
    ),
    expected_output=(
        "A detailed, informative response to the customer's inquiry that addresses "
        "all aspects of their question.\n"
        "The response should include references to everything you used to find the answer, "
        "including external data or solutions. "
        "Ensure the answer is complete, leaving no questions unanswered, and maintain a helpful and friendly "
        "tone throughout."
    ),
    tools=[docs_scrape_tool],  # Now using a properly initialized tool from crewai_tools
    agent=support_agent,
)