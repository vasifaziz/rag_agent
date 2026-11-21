import re


def _tokens(text):
    return set(re.findall(r"\w+", text.lower()))


def _similarity(left, right):
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union) if union else 0.0


def rerank(_query, candidates, top_k=3):
    remaining = list(candidates)
    selected = []

    while remaining and len(selected) < top_k:
        def score(candidate):
            redundancy = max(
                (_similarity(candidate["text"], item["text"]) for item in selected),
                default=0.0,
            )
            relevance = candidate["combined_score"]
            return 0.75 * relevance + 0.25 * (1 - redundancy)

        best = max(remaining, key=score)
        remaining.remove(best)
        selected.append({**best, "rerank_score": score(best)})

    return selected
