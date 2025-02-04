from typing import Optional
from langchain.tools import BaseTool

class ScrapeWebsiteTool(BaseTool):
    """
    A custom tool to scrape relevant documentation.
    """
    name: str = "Docs Scraper"
    description: str = "Scrapes relevant documentation for a given query."

    def _run(self, query: str) -> str:
        # In a real scenario, implement your scraping logic here.
        # For now, we'll just return a placeholder.
        return f"[Scraped content for '{query}']"

    async def _arun(self, query: str) -> str:
        # Async version if needed
        return self._run(query)

import os
from langchain.llms import OpenAI
from langchain.agents import Tool, initialize_agent
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Get the OpenAI API key from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'



# 1) Instantiate the LLM
llm = OpenAI(temperature=0)

# 2) Create a standard LangChain Tool wrapper
scrape_tool = ScrapeWebsiteTool()
tool_for_agent = Tool(
    name="Docs Scraper",
    func=scrape_tool.run,
    description=scrape_tool.description
)

# 3) Put the wrapped tool in a list (the agent can use multiple tools)
tools = [tool_for_agent]
