import os

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()

llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
embedder = SentenceTransformer("all-MiniLM-L6-v2")
collection = chromadb.PersistentClient(path="data/vectorstore").get_collection("documind")

SYSTEM_PROMPT = (
    "You are a company knowledge assistant. "
    "Answer the question using ONLY the context provided. "
    "If the answer is not in the context, reply exactly: I don't know based on the available documents. "
    "Keep the answer short and mention the source file name."
    "Do not mention sources when you answer I don’t know"
)


def retrieve(question, k=3):
    """Find the k chunks closest in meaning to the question."""
    results = collection.query(
        query_embeddings=embedder.encode(question).tolist(),
        n_results=k,
    )
    return [
        {"text": text, "source": meta["source"]}
        for text, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def answer(question):
    """Retrieve relevant chunks, then let the LLM answer from them."""
    chunks = retrieve(question)
    context = "\n\n".join(f"[{c['source']}] {c['text']}" for c in chunks)

    response = llm.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


questions = [
    "How many days of annual leave do I get?",
    "What is the maximum number of leave days I can carry over?",
    "How often must I change my password?",
    "Who is the CEO of TechNova?",
]

for question in questions:
    print(f"\nQ: {question}")
    print(f"A: {answer(question)}")