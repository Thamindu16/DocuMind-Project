import ast
import operator

from src.documind.ingestion.indexer import list_documents
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


def list_indexed_documents():
    """List the documents the assistant can search."""
    documents = list_documents()
    if not documents:
        return "No documents are indexed yet."
    return "\n".join(f"- {d['source']} ({d['chunks']} passages)" for d in documents)


# Tool descriptions the LLM reads to decide when to use each tool
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search the company documents, including policies and any files the user uploaded. Use for any question about their content.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "A short English search query"}},
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
    {
        "type": "function",
        "function": {
            "name": "list_indexed_documents",
            "description": "List the documents available to search. Use when the user asks what you can help with or which documents you know.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

TOOL_FUNCTIONS = {
    "search_documents": search_documents,
    "calculate": calculate,
    "list_indexed_documents": list_indexed_documents,
}