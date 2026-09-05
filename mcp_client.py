import os
import asyncio
import certifi
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from pydantic import SecretStr

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY=os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set in the environment variables."
    )


llm = ChatGroq(
   model="openai/gpt-oss-120b",
    api_key=SecretStr(GROQ_API_KEY)
)

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
        },

        "aviationstack": {
            "transport": "stdio",
            "command": "uvx",
            "args": [
                "--with",
                "mcp<2",
                "aviationstack-mcp",
            ],
            "env": {
                "AVIATION_STACK_API_KEY": AVIATIONSTACK_API_KEY,
            },
        },
        "weather": {
            "transport": "stdio",

            # Use the same Python environment that runs app.py.
            "command": r"D:\Projects\TripPlanner\travel\Scripts\python.exe",

            # Automatically use custom_weather_mcp_server.py
            # from the current project directory.
            "args": [
               r"D:\Projects\TripPlanner\custom_weather_mcp_server.py"
            ],

            "env": {
                "OPENWEATHER_API_KEY":OPENWEATHER_API_KEY
            }
        }
    } # type: ignore
)


async def get_all_tools():
    tools=await client.get_tools()
    print("\nAvailable MCP Tools:\n")

    for tool in tools:
        print(tool.name)



# =================
#  tavily and aviation tools
# =================

search_tool=None
aviation_tools={}

async def initialize_mcp():
    global search_tool
    global aviation_tools

    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()

    print("\nAvailable MCP Tools:\n")

    for tool in tools:
        print(tool.name)

    search_tool= next(
        tool
        for tool in tools
        if tool.name== "tavily_search"
    )

    aviation_tools={
        tool.name:tool
        for tool in tools
        if tool.name!="tavily_search"
    }

async def tavily_mcp_search(query: str):
    await initialize_mcp()
    result=await search_tool.ainvoke( # type: ignore
        {"query":query}
    )
    # print(result)
    return result

async def avaiation_mcp_call(
        tool_name:str,
        tool_args:dict=None # type: ignore
):
    tools=await client.get_tools()
    tool=next(
        t for t in tools
        if t.name == tool_name
    )

    result = await tool.ainvoke(
        tool_args or {}
    )
    return result


# ================
# weather tools
# ================

weather_tool=None
forecast_tool=None
async def initialize_weather_tools():
    global weather_tool,forecast_tool

    if weather_tool is not None:
        return

    tools=await client.get_tools()

    weather_tool=next(
        t for t in tools
        if t.name=="get_current_weather"
    )

    forecast_tool=next(
        t for t in tools
        if t.name=="get_forecast"
    )

async def weather_mcp_search(city:str):
    await initialize_weather_tools()

    return await weather_tool.ainvoke( # type: ignore
        {
            "city":city
        }
    )

async def forecast_mcp_search(city: str):
    await initialize_weather_tools()

    return await forecast_tool.ainvoke( # type: ignore
        {
            "city":city
        }
    )

# ==========================
# Destination Extractor
# ==========================

def extract_destination(query: str):
    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    return only destination name.

"""
    response =llm.invoke(prompt)

    return response.content.strip() # type: ignore




