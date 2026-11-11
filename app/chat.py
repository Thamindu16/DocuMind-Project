import chainlit as cl
import httpx

API_URL = "http://127.0.0.1:8000/ask"


@cl.on_chat_start
async def start():
    await cl.Message(
        content="Welcome to **DocuMind**. Ask me anything about the company HR and IT policies."
    ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    try:
        # Forward the user's question to the FastAPI backend
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(API_URL, json={"question": message.content})
        response.raise_for_status()
        data = response.json()

        text = data["answer"]
        # Show sources only when the assistant actually found an answer
        if data["sources"] and not text.startswith("I don't know"):
            text += "\n\n*Sources: " + ", ".join(data["sources"]) + "*"
    except Exception as error:
        text = f"Could not reach the DocuMind API. Is the server running? ({error})"

    await cl.Message(content=text).send()