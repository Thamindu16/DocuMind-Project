import chainlit as cl
import httpx

API_URL = "http://127.0.0.1:8000/ask"
APP_NAME = "DocuMind"


@cl.set_starters
async def starters():
    """Suggested questions shown on the welcome screen."""
    return [
        cl.Starter(label="Annual leave", message="How many days of annual leave do I get?"),
        cl.Starter(label="Remote work", message="How many days per week can I work remotely?"),
        cl.Starter(label="Password policy", message="What is the password policy?"),
        cl.Starter(label="Expense claims", message="Which expense claims need director approval?"),
    ]


@cl.on_message
async def handle_message(message: cl.Message):
    answer_text, sources = "", []

    # Show the retrieval step as a collapsible item above the answer
    async with cl.Step(name="Searching company documents") as step:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(API_URL, json={"question": message.content})
            response.raise_for_status()
            data = response.json()
            answer_text, sources = data["answer"], data["sources"]
            step.output = "Found in: " + ", ".join(sources) if sources else "No documents used"
        except Exception as error:
            answer_text = f"Could not reach the DocuMind API. Is the server running? ({error})"
            step.output = "Request failed"

    # Show sources only when the assistant actually found an answer
    if sources and not answer_text.startswith("I don't know"):
        answer_text += "\n\n**Sources:** " + ", ".join(sources)

    await cl.Message(content=answer_text, author=APP_NAME).send()