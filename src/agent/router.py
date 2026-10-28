from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from src.config import GROQ_API_KEY, LLM_MODEL_NAME
from src.tools.web_search import get_web_search_tool
from src.tools.calculator import calculator
from src.tools.rag_tool import search_internal_docs

def get_agent():
    print("Initializing Agent and loading tools...")
    
    # 1. Initialize the LLM (Groq is fast and free)
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL_NAME,
        temperature=0
    )
    
    # 2. Gather all the tools we created
    tools = [
        search_internal_docs,
        get_web_search_tool(),
        calculator
    ]
    
    # 3. Create the Agent using LangGraph
    # The system prompt tells the agent how to behave
    system_prompt = """You are a helpful and professional Enterprise AI Assistant. 
    You have access to internal company documents, web search, and a calculator.
    Always try to answer using the internal documents first. 
    If the answer is not in the documents, use the web search.
    If you don't know the answer, say 'I don't know'."""
    
    agent_executor = create_react_agent(
        model=llm, 
        tools=tools, 
        prompt=system_prompt
    )
    
    return agent_executor