import certifi

from tools.tavily_tool import tavily_search

from tools.flight_tool import search_flights

# rs=search_flights("Plan a 7 days Nepal trip from Bangladesh")
# print(rs)

# res = tavily_search("Best travel destinations in Europe")
# print(res)


from backend import run_travel_agent

user_input=input("Enter your travel request: ")

response=run_travel_agent(
    user_input=user_input,
    thread_id="test_user"
)

print("\n FINAL RESPONSE:\n")
print(response["final_answer"])
