from langchain_community.tools import DuckDuckGoSearchRun

def get_web_search_tool():
    # Free DuckDuckGo search tool
    search = DuckDuckGoSearchRun()
    return search