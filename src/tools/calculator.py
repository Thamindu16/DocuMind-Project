from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Useful for when you need to answer questions about math. 
    Input should be a mathematical expression like '2 + 2' or '10 * 5'."""
    try:
        # Safely evaluate basic math expressions
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error in calculation: {str(e)}"