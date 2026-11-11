import ast
import operator

from src.documind.retrieval.retriever import retrieve

# Only these arithmetic operations are allowed
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _evaluate(node):
    """Evaluate a parsed arithmetic expression without using eval()."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")


def calculate(expression):
    """Safely calculate a basic arithmetic expression such as '14 - 9'."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculation error: {error}"


def search_documents(query):
    """Search the company documents and return the most relevant passages."""
    chunks = retrieve(query)
    return "\n\n".join(f"[{c['source']}] {c['text']}" for c in chunks)


# Tool descriptions the LLM reads to decide when to use each tool
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search company HR and IT policy documents. Use for any question about company rules.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "What to look for"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a basic arithmetic expression using + - * / and numbers.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "For example: 14 - 9"}},
                "required": ["expression"],
            },
        },
    },
]

TOOL_FUNCTIONS = {"search_documents": search_documents, "calculate": calculate}