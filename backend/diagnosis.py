"""Syllabus topic: FOPL evidence construction, inference, and diagnosis orchestration."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.logic.forward_chain import HornRule, forward_chain
from backend.logic.unification import Atom
from backend.nlp.parser import extract_symptoms
from backend.prob.bayes_net import posterior_probabilities
from backend.prob.decision_net import choose_action, expected_utilities

KB_DIR = Path(__file__).parent / "kb"


def load_knowledge_base() -> dict[str, Any]:
    return {name: json.loads((KB_DIR / f"{name}.json").read_text(encoding="utf-8")) for name in ("facts", "rules", "cpts", "utilities")}


def symptom_catalog() -> list[dict[str, Any]]:
    return load_knowledge_base()["facts"]["symptoms"]


def run_diagnosis(payload: dict[str, Any], knowledge_base: dict[str, Any] | None = None) -> dict[str, Any]:
    kb = knowledge_base or load_knowledge_base()
    facts_data = kb["facts"]
    catalog = facts_data["symptoms"]
    valid_symptoms = {item["id"] for item in catalog}
    supplied = set(payload.get("symptoms", []))
    absent = set(payload.get("absent_symptoms", []))
    unknown = (supplied | absent) - valid_symptoms
    if unknown:
        raise ValueError(f"Unknown symptom identifiers: {', '.join(sorted(unknown))}")
    if supplied & absent:
        raise ValueError("A symptom cannot be both present and absent.")
    extracted = extract_symptoms(payload.get("free_text", ""), catalog)
    present = supplied | set(extracted)
    if not present and not absent:
        raise ValueError("Select or describe at least one symptom before diagnosis.")
    vehicle_id = str(payload.get("vehicle_id") or "vehicle").strip() or "vehicle"
    initial = [Atom("Symptom", (vehicle_id, symptom)) for symptom in sorted(present)]
    initial.extend(Atom("Part", (item["component"], item["system"])) for item in facts_data["parts"])
    rules = [
        HornRule(
            rule["id"],
            tuple(Atom("Symptom", ("?vehicle", symptom)) for symptom in rule["when"]),
            Atom("Fault", ("?vehicle", rule["fault"])),
            rule["text"],
        )
        for rule in kb["rules"]["rules"]
    ]
    closure, fired = forward_chain(initial, rules)
    probabilities, inference_engine = posterior_probabilities(kb["cpts"], present, absent)
    fault_by_id = {fault["id"]: fault for fault in facts_data["faults"]}
    utilities = expected_utilities(probabilities, kb["utilities"])
    recommended_action = choose_action(utilities)
    action_labels = kb["utilities"]["labels"]
    rule_map = {item["rule_id"]: item for item in fired}

    ranked = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    top_faults: list[dict[str, Any]] = []
    for fault_id, probability in ranked[:3]:
        associated = kb["cpts"]["faults"][fault_id]["symptoms"]
        contributors = sorted(
            (symptom for symptom in present if symptom in associated),
            key=lambda symptom: associated[symptom] / kb["cpts"]["false_positive_default"],
            reverse=True,
        )[:3]
        fired_for_fault = [item for item in fired if item["derived"].endswith(f", {fault_id})")]
        top_faults.append({
            **fault_by_id[fault_id],
            "fault": fault_id,
            "probability": round(probability, 4),
            "contributing_symptoms": contributors,
            "fired_rules": fired_for_fault,
            "recommended_action": action_labels[recommended_action],
        })

    unification_steps = [
        {"rule_id": item["rule_id"], "variable": variable, "value": value}
        for item in fired
        for variable, value in item["substitutions"].items()
    ]
    return {
        "vehicle": payload.get("vehicle", {}),
        "vehicle_id": vehicle_id,
        "symptoms": sorted(present),
        "absent_symptoms": sorted(absent),
        "extracted_symptoms": extracted,
        "top_faults": top_faults,
        "confidence": top_faults[0]["probability"],
        "severity": top_faults[0]["severity"],
        "recommended_action": {"id": recommended_action, "label": action_labels[recommended_action], "expected_utility": utilities[recommended_action]},
        "expected_utilities": [{"action": key, "label": action_labels[key], "value": value} for key, value in utilities.items()],
        "fired_rules": fired,
        "unification_steps": unification_steps,
        "posterior_table": [{"fault": fault_id, "label": fault_by_id[fault_id]["label"], "probability": round(probability, 4), "severity": fault_by_id[fault_id]["severity"]} for fault_id, probability in ranked],
        "inference_engine": inference_engine,
        "assumptions": kb["cpts"]["assumptions"],
        "safety_note": "This educational estimate is not a substitute for a qualified inspection. Stop driving and seek assistance for brake, oil-pressure, severe overheating, or other critical warnings.",
    }
