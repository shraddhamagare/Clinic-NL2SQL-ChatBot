import os
from dotenv import load_dotenv
load_dotenv()

from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.google import GeminiLlmService

DB_PATH = os.path.join(os.path.dirname(__file__), "clinic.db")

class DefaultUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(id="default_user", email="user@clinic.com", group_memberships=["users"])

def create_agent():
    llm_service = GeminiLlmService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-2.5-flash",
    )
    sql_runner = SqliteRunner(DB_PATH)
    memory = DemoAgentMemory()

    tools = ToolRegistry()
    tools.register_local_tool(RunSqlTool(sql_runner=sql_runner), access_groups=["users"])
    tools.register_local_tool(VisualizeDataTool(), access_groups=["users"])

    agent = Agent(
        llm_service=llm_service,
        tool_registry=tools,
        user_resolver=DefaultUserResolver(),
        agent_memory=memory,
        config=AgentConfig()
    )
    print("✅ Vanna 2.0 Agent initialized successfully.")
    return agent, memory

_agent = None
_memory = None

def get_agent():
    global _agent, _memory
    if _agent is None:
        _agent, _memory = create_agent()
    return _agent

def get_memory():
    global _memory
    if _memory is None:
        get_agent()
    return _memory