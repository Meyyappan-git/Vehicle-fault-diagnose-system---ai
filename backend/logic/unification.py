"""Syllabus topic: first-order predicate logic unification and substitutions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Atom:
    predicate: str
    terms: tuple[str, ...]

    def substitute(self, substitutions: Mapping[str, str]) -> "Atom":
        return Atom(self.predicate, tuple(resolve(term, substitutions) for term in self.terms))


@dataclass(frozen=True)
class Literal:
    atom: Atom
    negated: bool = False


def is_variable(term: str) -> bool:
    return term.startswith("?")


def resolve(term: str, substitutions: Mapping[str, str]) -> str:
    seen: set[str] = set()
    while is_variable(term) and term in substitutions and term not in seen:
        seen.add(term)
        term = substitutions[term]
    return term


def unify_terms(left: str, right: str, substitutions: dict[str, str]) -> bool:
    left = resolve(left, substitutions)
    right = resolve(right, substitutions)
    if left == right:
        return True
    if is_variable(left):
        substitutions[left] = right
        return True
    if is_variable(right):
        substitutions[right] = left
        return True
    return False


def unify(left: Atom, right: Atom, substitutions: Mapping[str, str] | None = None) -> dict[str, str] | None:
    """Unify two predicates and return the most-general substitution, if any."""
    result = dict(substitutions or {})
    if left.predicate != right.predicate or len(left.terms) != len(right.terms):
        return None
    for left_term, right_term in zip(left.terms, right.terms):
        if not unify_terms(left_term, right_term, result):
            return None
    return {key: resolve(value, result) for key, value in result.items()}


def unify_with_trace(left: Atom, right: Atom) -> tuple[dict[str, str] | None, list[dict[str, str]]]:
    trace: list[dict[str, str]] = []
    substitutions: dict[str, str] = {}
    if left.predicate != right.predicate or len(left.terms) != len(right.terms):
        return None, [{"step": "predicate_or_arity_mismatch", "left": left.predicate, "right": right.predicate}]
    for left_term, right_term in zip(left.terms, right.terms):
        before = dict(substitutions)
        if not unify_terms(left_term, right_term, substitutions):
            trace.append({"step": "term_conflict", "left": left_term, "right": right_term})
            return None, trace
        trace.append({"step": "matched_terms", "left": left_term, "right": right_term, "substitutions": {key: resolve(value, substitutions) for key, value in substitutions.items()}, "changed": before != substitutions})
    return {key: resolve(value, substitutions) for key, value in substitutions.items()}, trace
