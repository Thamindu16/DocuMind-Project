import os
from pathlib import Path

import chainlit as cl
import httpx
from chainlit.input_widget import Switch

# start.py sets this when it has to use a different port
API_URL = os.getenv("DOCUMIND_API_URL", "http://127.0.0.1:8000")
APP_NAME = "DocuMind"
HISTORY_TURNS = 8  # how many recent messages are sent along with each question


@cl.set_starters
async def starters():
    """Suggested messages shown on the welcome screen."""
    return [
        cl.Starter(label="What can you do?", message="Hi! What can you help me with?"),
        cl.Starter(label="Annual leave", message="How many days of annual leave do I get?"),
        cl.Starter(label="Health insurance", message="What does the health insurance cover?"),
        cl.Starter(label="Explain RAG", message="What is retrieval-augmented generation?"),
    ]


@cl.on_chat_start
async def start():
    # Each chat keeps its own conversation history and its own answer mode
    cl.user_session.set("history", [])
    settings = await cl.ChatSettings(
        [
            Switch(
                id="general",
                label="Answer general questions too",
                initial=True,
                description="Off: DocuMind answers only from the documents.",
            )
        ]
    ).send()
    cl.user_session.set("general", settings["general"])


@cl.on_settings_update
async def update_settings(settings):
    cl.user_session.set("general", settings["general"])


async def upload_files(elements):
    """Send each attached file to the API for indexing and report the result."""
    for element in elements:
        async with cl.Step(name=f"Reading {element.name}") as step:
            try:
                data = Path(element.path).read_bytes()
                mime = getattr(element, "mime", None) or "application/octet-stream"
                async with httpx.AsyncClient(timeout=180) as client:
                    response = await client.post(
                        f"{API_URL}/upload", files={"file": (element.name, data, mime)}
                    )
                if response.status_code == 200:
                    info = response.json()
                    step.output = f"Indexed {info['chunks']} passages"
                    await cl.Message(
                        content=f"**{info['filename']}** is ready ({info['chunks']} passages). You can ask questions about it now.",
                        author=APP_NAME,
                    ).send()
                else:
                    detail = response.json().get("detail", "Unknown error")
                    step.output = "Failed"
                    await cl.Message(
                        content=f"I could not use **{element.name}**: {detail}", author=APP_NAME
                    ).send()
            except Exception as error:
                step.output = "Failed"
                await cl.Message(
                    content=f"Could not reach the DocuMind API. Is the server running? ({error})",
                    author=APP_NAME,
                ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    # Index any attached files first, so a question in the same message can use them
    files = [e for e in (message.elements or []) if getattr(e, "path", None)]
    if files:
        await upload_files(files)

    question = message.content.strip()
    if not question:
        return

    history = cl.user_session.get("history") or []
    general = cl.user_session.get("general", True)
    answer_text, sources, succeeded = "", [], False

    async with cl.Step(name="Thinking") as step:
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                response = await client.post(
                    f"{API_URL}/chat",
                    json={
                        "message": question,
                        "history": history[-HISTORY_TURNS:],
                        "general_knowledge": general,
                    },
                )
            response.raise_for_status()
            data = response.json()
            answer_text, sources, succeeded = data["answer"], data["sources"], True
            step.output = "Searched: " + ", ".join(sources) if sources else "Answered directly"
        except Exception as error:
            answer_text = f"Could not reach the DocuMind API. Is the server running? ({error})"
            step.output = "Request failed"

    # Remember the exchange so follow-up questions make sense
    if succeeded:
        history += [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer_text},
        ]
        cl.user_session.set("history", history)

    # Show sources only when the assistant actually found an answer
    shown = answer_text
    if sources and not answer_text.startswith("I don't know"):
        shown += "\n\n**Sources:** " + ", ".join(sources)

    await cl.Message(content=shown, author=APP_NAME).send()