"""Explicit real-model retrieval quality check; not part of offline CI."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.settings import Settings
from rag import Retriever


def evaluate(retriever, cases):
    rows, hits, reciprocal = [], 0, 0.0
    for case in cases:
        docs = retriever.search(case["query"])
        sources = [d["source"] for d in docs]
        rank = next(
            (i + 1 for i, source in enumerate(sources) if source == case["expected_source"]), None
        )
        hits += rank is not None
        reciprocal += 1 / rank if rank else 0
        rows.append({"query": case["query"], "sources": sources, "rank": rank})
    return {
        "cases": len(cases),
        "hit_at_k": hits / len(cases) if cases else 0,
        "mrr": reciprocal / len(cases) if cases else 0,
        "details": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "knowledge" / "eval_cases.json",
    )
    args = parser.parse_args()
    config = Settings()
    retriever = Retriever(config).prepare()
    print(
        json.dumps(
            evaluate(retriever, json.loads(args.cases.read_text(encoding="utf-8"))),
            ensure_ascii=False,
            indent=2,
        )
    )
