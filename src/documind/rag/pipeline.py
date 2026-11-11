from src.documind.llm.client import generate
from src.documind.rag.prompts import SYSTEM_PROMPT
from src.documind.retrieval.retriever import retrieve


def answer(question):
    """Retrieve relevant chunks and let the LLM answer from them."""
    chunks = retrieve(question)
    context = "\n\n".join(f"[{c['source']}] {c['text']}" for c in chunks)
    reply = generate(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
    )
    return {"answer": reply, "sources": sorted({c["source"] for c in chunks})}


if __name__ == "__main__":
    for q in ["How many days of annual leave do I get?", "What is the capital of France?"]:
        result = answer(q)
        print(f"\nQ: {q}\nA: {result['answer']}\nRetrieved from: {result['sources']}")