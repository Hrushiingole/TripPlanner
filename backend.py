import asyncio
import os
import certifi
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from typing import TypedDict,Annotated
import operator
import uuid

import psycopg
from psycopg.rows import dict_row

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    AnyMessage
)
from langchain_groq import ChatGroq
# from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

# mcp imports
from mcp_client_test import tavily_mcp_search

import os

def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL is not set in the environment variables."
        )

    return database_url

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set in the environment variables."
    )

# =====================
# LLM
# =====================
llm = ChatGroq(
   model="openai/gpt-oss-120b",
    api_key=SecretStr(GROQ_API_KEY)
)

# =====================
# State
# =====================

class TravelState(TypedDict):
    message: Annotated[list[AnyMessage],operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary:str
    llm_calls: int


# =====================
# Flight Agent
# =====================

def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data=search_flights(query)

    return {
        "flight_results":flight_data,
        "message":[
           AIMessage(content="Flight results fetched successfully.")
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }




# =====================
# Hotel Agent
# =====================
def hotel_agent(state: TravelState):
    query=f"Best hotels for {state['user_query']}"
    # hotel_results=tavily_search(query)

    hotel_results=asyncio.run(tavily_mcp_search(query))

    return {
        "hotel_results":hotel_results,
        "message":[
            AIMessage(content="Hotel results fetched successfully.")
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }





# =====================
# Itinerary Agent ( here we will use LLM to generate itinerary based on flight and hotel results)
# =====================
def itinerary_agent(state: TravelState):
    prompt=f"""

    create a complete travel itinerary for the following trip based on the flight and hotel results.
    user query: {state['user_query']}
    flight results: {state['flight_results']}
    hotel results: {state['hotel_results']}

    make the itinerary practical , budget-aware and easy to follow. 
    provide a day-wise breakdown of activities, including sightseeing, dining, and any other relevant information.
    ensure that the itinerary is well-structured and provides a seamless travel experience for the user.
    """

    response=llm.invoke([
        SystemMessage(content="You are a expert travel planner that creates travel itineraries based on flight and hotel results."),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary":response.content,
        "message":[
            AIMessage(content="Itinerary generated successfully.")
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }



# =====================
# Final Response Agent
# =====================

def final_agent(state: TravelState):
    final_prompt=f"""
    generate the final travel response for user.

    user request: {state['user_query']}
    flight results: {state['flight_results']}
    hotel results: {state['hotel_results']}
    itinerary: {state['itinerary']}

    format the final answer beautifully using these sections:

    1. Trip Summary
    2. Flight Information
    3. Hotel Information
    4. Day-wise Itinerary
    5. estimated Budget
    6. final Recommendations

    important:
    - be clear and practical.
    - mention that live flight api may not provide ticket prices if prices is unavailable.
    - keep the response useful for real travel planning.
"""
    response= llm.invoke([
        SystemMessage(content="You are a professional AI travel booking assistant."),
        HumanMessage(content=final_prompt)
    ])
    return {
        "message":[response],
        "llm_calls":state.get("llm_calls",0)+1
    }



# =====================
# Build Graph
# =====================

graph=StateGraph(TravelState)

graph.add_node("flight_agent",flight_agent)
graph.add_node("hotel_agent",hotel_agent)
graph.add_node("itinerary_agent",itinerary_agent)
graph.add_node("final_agent",final_agent)

graph.add_edge(START,"flight_agent")
graph.add_edge("flight_agent","hotel_agent")
graph.add_edge("hotel_agent","itinerary_agent")
graph.add_edge("itinerary_agent","final_agent")
graph.add_edge("final_agent",END)

# =====================
# Postgres Checkpointer
# =====================
DATABASE_URL = get_database_url()

__conn=psycopg.connect(
    DATABASE_URL,
    autocommit=True,
    row_factory=dict_row # type: ignore[arg-type]
)

checkpointer=PostgresSaver(__conn) # type: ignore
checkpointer.setup()

travel_graph=graph.compile(checkpointer=checkpointer)

# ====================
# Function for FastAPI
# ====================

def run_travel_agent(user_input:str, thread_id: str | None = None):
    if not thread_id:
       thread_id=f"user_{uuid.uuid4().hex}"

    config={
        "configurable":{
            "thread_id":thread_id
        }
    }

    result=travel_graph.invoke(
        {
            "message":[
                HumanMessage(content=user_input)
            ],
            "user_query":user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls":0
        },
        config=config # type: ignore
    )
    final_answer=result["message"][-1].content
    return {
        "thread_id":thread_id,
        "final_answer":final_answer,
        "flight_results": result.get("flight_results",""),
        "hotel_results": result.get("hotel_results",""),
        "itinerary": result.get("itinerary",""),
        "llm_calls": result.get("llm_calls",0)
    }