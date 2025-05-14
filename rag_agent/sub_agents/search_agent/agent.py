from google.adk.tools import google_search

from google.adk.agents import Agent
from google.adk.tools import google_search

search_agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    description="Search agent",
    instruction="""
    You are a helpful assistant that can search the web for information.

    When asked about general visa information, you should use the google_search tool to search for the information.

    """,
    tools=[google_search],
)
