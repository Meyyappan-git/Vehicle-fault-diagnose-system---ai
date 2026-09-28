"""Syllabus topic: Modus Ponens and data-driven forward chaining."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .unification import Atom, unify


@dataclass(frozen=True)
class HornRule:
    rule_id: str
    antecedents: tuple[Atom, ...]
    consequent: Atom
    explanation: str


def _match_body(antecedents: tuple[Atom, ...], facts: list[Atom], substitutions: dict[str, str] | None = None) -> Iterable[dict[str, str]]:
    if not antecedents:
        yield substitutions or {}
        return
    first, *remaining = antecedents
    for fact in facts:
        matched = unify(first.substitute(substitutions or {}), fact, substitutions)
        if matched is not None:
            yield from _match_body(tuple(remaining), facts, matched)


def forward_chain(initial_facts: Iterable[Atom], rules: Iterable[HornRule]) -> tuple[list[Atom], list[dict[str, object]]]:
    """Apply Horn clauses until no new ground facts can be derived."""
    facts = list(dict.fromkeys(initial_facts))
    known = set(facts)
    fired: list[dict[str, object]] = []
    changed = True
    while changed:
        changed = False
        for rule in rules:
            for substitutions in _match_body(rule.antecedents, facts):
                conclusion = rule.consequent.substitute(substitutions)
                if any(term.startswith("?") for term in conclusion.terms) or conclusion in known:
                    continue
                known.add(conclusion)
                facts.append(conclusion)
                changed = True
                fired.append({"rule_id": rule.rule_id, "explanation": rule.explanation, "substitutions": substitutions, "derived": f"{conclusion.predicate}({', '.join(conclusion.terms)})"})
    return facts, fired
