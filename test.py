from tools.tavily_tool import tavily_search

from tools.flight_tool import search_flights

rs=search_flights("Plan a 7 days Nepal trip from Bangladesh")
print(rs)

# res = tavily_search("Best travel destinations in Europe")
# print(res)