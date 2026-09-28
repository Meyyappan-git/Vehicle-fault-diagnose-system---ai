"""Syllabus topic: decision networks and expected utility maximization."""
from __future__ import annotations

from typing import Any


def expected_utilities(probabilities: dict[str, float], utility_data: dict[str, Any]) -> dict[str, float]:
    actions = utility_data["actions"]
    scores = {
        action: sum(probability * utility_data["utilities"][fault][action] for fault, probability in probabilities.items())
        for action in actions
    }
    return {action: round(score, 2) for action, score in scores.items()}


def choose_action(scores: dict[str, float]) -> str:
    return max(scores, key=scores.get)
