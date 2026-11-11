import json

from src.documind.agent.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS
from src.documind.config import LLM_MODEL
from src.documind.llm.client import get_client

MAX_STEPS = 5  # safety limit so the agent can never loop forever

AGENT_PROMPT = (
    "You are DocuMind, a company assistant that answers ONLY from company documents. "
    "For every question, first call search_documents, even if you think you know the answer. "
    "Base your answer only on the tool results and never use your own general knowledge. "
    "If the documents do not contain the answer, reply exactly: I don't know based on the available documents. "
    "For any arithmetic, including simple subtraction, you must call the calculate tool and never compute in your head. "
    "Exception: a pure arithmetic question that needs no company information may use calculate alone. "
    "Keep answers short."
)


def run_agent(question):
    """Let the LLM call tools in a loop until it produces a final answer."""
    messages = [
        {"role": "system", "content": AGENT_PROMPT},
        {"role": "user", "content": question},
    ]

    for _ in range(MAX_STEPS):
        response = get_client().chat.completions.create(
            model=LLM_MODEL, messages=messages, tools=TOOL_SCHEMAS, temperature=0
        )
        message = response.choices[0].message

        # No tool requested: this is the final answer
        if not message.tool_calls:
            return message.content

        # Record the assistant's tool request, then run each requested tool
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {"name": call.function.name, "arguments": call.function.arguments},
                    }
                    for call in message.tool_calls
                ],
            }
        )
        for call in message.tool_calls:
            arguments = json.loads(call.function.arguments)
            print(f"  [tool] {call.function.name}({arguments})")
            result = TOOL_FUNCTIONS[call.function.name](**arguments)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    return "I could not finish within the step limit."


if __name__ == "__main__":
    questions = [
        "How many days of annual leave do I get?",
        "What is 15% of 2500?",
        "If I use 9 of my annual leave days, how many do I have left?",
        "What is the capital of France?",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {run_agent(q)}")