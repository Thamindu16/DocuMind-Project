import contextlib
import io
import json
import time
from pathlib import Path

from src.documind.agent.agent import run_agent
from src.documind.rag.pipeline import answer
from src.documind.retrieval.retriever import retrieve

EVAL_DIR = Path(__file__).resolve().parent
REFUSAL = "i don't know"


def normalize(text):
    """Lowercase, unify apostrophes, drop markdown bold and collapse every kind of whitespace."""
    text = text.lower().replace("\u2019", "'").replace("*", "")
    # split() treats non-breaking spaces as whitespace, join() restores plain spaces
    return " ".join(text.split())


def contains_any(text, keywords):
    """True if any expected keyword appears in the text."""
    text = normalize(text)
    return any(normalize(keyword) in text for keyword in keywords)


def retrieval_rank(question, keywords):
    """Rank (1-3) of the first retrieved chunk containing the answer, else None."""
    for rank, chunk in enumerate(retrieve(question, k=3), start=1):
        if contains_any(chunk["text"], keywords):
            return rank
    return None


def percent(count, total):
    return round(100 * count / total, 1) if total else 0.0


cases = json.loads((EVAL_DIR / "test_set.json").read_text(encoding="utf-8"))
answerable = [c for c in cases if c["answerable"]]
unanswerable = [c for c in cases if not c["answerable"]]

stats = {"hit1": 0, "hit3": 0, "pipeline_ok": 0, "agent_ok": 0,
         "pipeline_refused": 0, "agent_refused": 0}
details = []

for case in cases:
    question = case["question"]
    pipeline_reply = answer(question)["answer"]
    # Silence the agent's [tool] log lines during evaluation
    with contextlib.redirect_stdout(io.StringIO()):
        agent_reply = run_agent(question)

    record = {"question": question, "pipeline": pipeline_reply, "agent": agent_reply}

    if case["answerable"]:
        rank = retrieval_rank(question, case["keywords"])
        pipeline_correct = contains_any(pipeline_reply, case["keywords"])
        agent_correct = contains_any(agent_reply, case["keywords"])
        stats["hit1"] += rank == 1
        stats["hit3"] += rank is not None
        stats["pipeline_ok"] += pipeline_correct
        stats["agent_ok"] += agent_correct
        record.update(rank=rank, pipeline_correct=pipeline_correct, agent_correct=agent_correct)
    else:
        stats["pipeline_refused"] += REFUSAL in normalize(pipeline_reply)
        stats["agent_refused"] += REFUSAL in normalize(agent_reply)

    details.append(record)
    time.sleep(2)  # stay under the API rate limit

n, m = len(answerable), len(unanswerable)
summary = {
    "answerable_questions": n,
    "unanswerable_questions": m,
    "retrieval_hit@1_%": percent(stats["hit1"], n),
    "retrieval_hit@3_%": percent(stats["hit3"], n),
    "pipeline_answer_accuracy_%": percent(stats["pipeline_ok"], n),
    "agent_answer_accuracy_%": percent(stats["agent_ok"], n),
    "pipeline_refusal_rate_%": percent(stats["pipeline_refused"], m),
    "agent_refusal_rate_%": percent(stats["agent_refused"], m),
}

print("\n=== DocuMind evaluation ===")
for key, value in summary.items():
    print(f"{key}: {value}")

print("\n=== Failures ===")
for record in details:
    if record.get("pipeline_correct") is False or record.get("agent_correct") is False:
        print(f"\nQ: {record['question']}\n  pipeline: {record['pipeline']}\n  agent: {record['agent']}")

(EVAL_DIR / "results.json").write_text(
    json.dumps({"summary": summary, "details": details}, indent=2), encoding="utf-8"
)
print("\nSaved eval/results.json")