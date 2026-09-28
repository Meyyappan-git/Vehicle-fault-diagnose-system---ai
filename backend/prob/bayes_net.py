"""Syllabus topic: Bayes' Theorem and Bayesian networks."""
from __future__ import annotations

import math
from typing import Any

try:
    from pgmpy.inference import VariableElimination
    try:
        from pgmpy.models import DiscreteBayesianNetwork
    except ImportError:
        from pgmpy.models import BayesianNetwork as DiscreteBayesianNetwork
    from pgmpy.factors.discrete import TabularCPD
    PGMPY_AVAILABLE = True
except ImportError:
    PGMPY_AVAILABLE = False


def _posterior_with_pgmpy(fault: str, data: dict[str, Any], evidence: dict[str, bool], false_positive: float) -> float:
    model = DiscreteBayesianNetwork()
    fault_node = f"fault_{fault}"
    model.add_node(fault_node)
    prior = float(data["prior"])
    model.add_cpds(TabularCPD(fault_node, 2, [[1 - prior], [prior]]))
    evidence_nodes: dict[str, str] = {}
    for symptom, probability in data["symptoms"].items():
        symptom_node = f"symptom_{symptom}"
        evidence_nodes[symptom] = symptom_node
        model.add_edge(fault_node, symptom_node)
        absent_given_fault = 1 - float(probability)
        model.add_cpds(TabularCPD(
            symptom_node,
            2,
            [[1 - false_positive, absent_given_fault], [false_positive, float(probability)]],
            evidence=[fault_node],
            evidence_card=[2],
        ))
    model.check_model()
    observed = {evidence_nodes[name]: int(value) for name, value in evidence.items() if name in evidence_nodes}
    distribution = VariableElimination(model).query(variables=[fault_node], evidence=observed, show_progress=False)
    return float(distribution.values[1])


def _posterior_exact(data: dict[str, Any], evidence: dict[str, bool], false_positive: float) -> float:
    prior = float(data["prior"])
    log_true = math.log(prior)
    log_false = math.log1p(-prior)
    for symptom, observed in evidence.items():
        if symptom not in data["symptoms"]:
            continue
        likelihood = float(data["symptoms"][symptom]) if observed else false_positive
        if not observed:
            likelihood = 1 - float(data["symptoms"][symptom])
        log_true += math.log(max(likelihood, 1e-12))
        log_false += math.log(max(false_positive if observed else 1 - false_positive, 1e-12))
    difference = log_false - log_true
    return 1 / (1 + math.exp(difference)) if difference < 700 else 0.0


def posterior_probabilities(cpts: dict[str, Any], present: set[str], absent: set[str]) -> tuple[dict[str, float], str]:
    """Compute binary posterior per fault, then normalize for ranked display."""
    evidence = {symptom: True for symptom in present} | {symptom: False for symptom in absent}
    false_positive = float(cpts["false_positive_default"])
    raw: dict[str, float] = {}
    engine = "pgmpy" if PGMPY_AVAILABLE else "exact-bayes-fallback"
    for fault, data in cpts["faults"].items():
        if PGMPY_AVAILABLE:
            raw[fault] = _posterior_with_pgmpy(fault, data, evidence, false_positive)
        else:
            raw[fault] = _posterior_exact(data, evidence, false_positive)
    total = sum(raw.values()) or 1.0
    return {fault: value / total for fault, value in raw.items()}, engine
