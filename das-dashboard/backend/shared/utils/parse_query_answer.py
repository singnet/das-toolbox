import re

SCORES_PATTERN = re.compile(r" \(([-\d.]+),\s*([-\d.]+)\)\s*$")
ASSIGNMENT_PATTERN = re.compile(r"\{([^}]+)\}")


def parse_query_answer(text: str) -> dict:
    scores_match = SCORES_PATTERN.search(text)
    strength = 0.0
    importance = 0.0
    body = text

    if scores_match:
        strength = float(scores_match.group(1))
        importance = float(scores_match.group(2))
        body = text[: scores_match.start()]

    assignment_label = None
    assignment_match = ASSIGNMENT_PATTERN.search(body)
    if assignment_match:
        assignment_label = assignment_match.group(1).strip()

    return {
        "answer_text": text,
        "strength": strength,
        "importance": importance,
        "assignment_label": assignment_label,
    }
