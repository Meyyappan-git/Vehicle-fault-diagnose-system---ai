"""Syllabus topic: resolution refutation for ground yes/no queries."""
from __future__ import annotations

from .unification import Atom, Literal, unify


def resolution_refutation(entailed_facts: list[Atom], query: Atom) -> dict[str, object]:
    """Refute the negated ground query against the forward-chained Horn closure.

    Unit clauses for entailed ground facts and the negated query are resolved;
    the complementary predicate unifies exactly when the query is entailed.
    """
    clauses = [[Literal(fact)] for fact in entailed_facts]
    negated_query = Literal(query, negated=True)
    trace: list[dict[str, object]] = [{"step": "negate_query", "literal": f"NOT {query.predicate}({', '.join(query.terms)})"}]
    for clause in clauses:
        literal = clause[0]
        if literal.negated == negated_query.negated:
            continue
        substitutions = unify(literal.atom, negated_query.atom)
        if substitutions is not None:
            trace.append({"step": "resolve_complementary_units", "fact": f"{literal.atom.predicate}({', '.join(literal.atom.terms)})", "substitutions": substitutions, "resolvent": "empty clause"})
            return {"entailed": True, "trace": trace, "method": "resolution_refutation"}
    trace.append({"step": "no_empty_clause", "resolvent": "query not established"})
    return {"entailed": False, "trace": trace, "method": "resolution_refutation"}
