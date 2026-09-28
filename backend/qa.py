"""Syllabus topic: question answering over inference traces and what-if evidence."""
from __future__ import annotations

from typing import Any

from backend.diagnosis import run_diagnosis
from backend.logic.resolution import resolution_refutation
from backend.logic.unification import Atom
from backend.nlp.parser import extract_symptoms

FAULT_ALIASES = {
    "battery": "weak_or_dead_battery", "alternator": "faulty_alternator", "starter": "failed_starter_motor",
    "brake pads": "worn_brake_pads", "rotors": "warped_brake_rotors", "brake fluid": "brake_fluid_leak_or_air_in_lines",
    "spark plugs": "ignition_or_spark_plug_failure", "fuel filter": "clogged_fuel_injector_or_filter",
    "catalytic converter": "faulty_o2_sensor_or_catalytic_converter", "oil leak": "low_oil_or_oil_leak",
    "transmission": "transmission_fluid_low_or_clutch_wear", "suspension": "worn_suspension_or_wheel_misalignment",
    "thermostat": "faulty_thermostat", "coolant leak": "coolant_leak",
}


def answer_question(question: str, prior_payload: dict[str, Any], diagnosis: dict[str, Any] | None = None) -> dict[str, Any]:
    normalized = question.lower()
    if any(phrase in normalized for phrase in ("what if", "if ")) and "absent" in normalized:
        catalog = __import__("backend.diagnosis", fromlist=["symptom_catalog"]).symptom_catalog()
        mentioned = extract_symptoms(question, catalog)
        if not mentioned:
            return {"kind": "clarification", "answer": "Name the symptom you want to treat as absent, for example: What if low coolant is absent?"}
        absent_symptom = mentioned[0]
        changed = dict(prior_payload)
        changed["symptoms"] = [value for value in prior_payload.get("symptoms", []) if value != absent_symptom]
        changed["absent_symptoms"] = list(set(prior_payload.get("absent_symptoms", [])) | {absent_symptom})
        result = run_diagnosis(changed)
        before = diagnosis["top_faults"][0] if diagnosis and diagnosis.get("top_faults") else None
        after = result["top_faults"][0]
        return {"kind": "what_if", "symptom": absent_symptom, "previous_top_fault": before, "diagnosis": result, "answer": f"Without {absent_symptom.replace('_', ' ')}, the leading estimate is {after['label']} ({after['probability']:.0%})."}

    if "why" in normalized:
        current = diagnosis or run_diagnosis(prior_payload)
        leading = current["top_faults"][0]
        reasons = ", ".join(item.replace("_", " ") for item in leading["contributing_symptoms"]) or "the overall evidence pattern"
        rules = ", ".join(item["rule_id"] for item in leading["fired_rules"]) or "no complete rule fired; this result is probabilistic"
        return {"kind": "why", "answer": f"{leading['label']} leads because of {reasons}. Supporting rules: {rules}.", "fault": leading, "fired_rules": leading["fired_rules"], "unification_steps": current["unification_steps"], "posterior_table": current["posterior_table"]}

    target = next((fault for alias, fault in FAULT_ALIASES.items() if alias in normalized), None)
    if target:
        current = diagnosis or run_diagnosis(prior_payload)
        derived_faults = {rule["derived"].rsplit(", ", 1)[-1].rstrip(")") for rule in current["fired_rules"]}
        closure = [Atom("Fault", (current["vehicle_id"], entry["fault"])) for entry in current["posterior_table"] if entry["fault"] in derived_faults]
        result = resolution_refutation(closure, Atom("Fault", (current["vehicle_id"], target)))
        label = next((item["label"] for item in current["posterior_table"] if item["fault"] == target), target.replace("_", " "))
        result["answer"] = f"The logic engine {'can' if result['entailed'] else 'cannot'} establish {label} from the current selected symptoms."
        result["kind"] = "yes_no"
        return result

    return {"kind": "general", "answer": "Ask ‘Why this fault?’, ‘Is it the battery?’, or ‘What if low coolant is absent?’ and I’ll use the current evidence to answer."}
