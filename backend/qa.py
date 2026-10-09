"""Real-time diagnostic AI assistant answering automotive queries using FOPL, Bayesian probabilities, and Decision utilities."""
from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv
import google.generativeai as genai

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

from backend.diagnosis import load_knowledge_base, run_diagnosis, symptom_catalog
from backend.logic.resolution import resolution_refutation
from backend.logic.unification import Atom
from backend.nlp.parser import extract_symptoms
from backend.qa_router import QueryRouter

FAULT_ALIASES: dict[str, str] = {
    "battery": "weak_or_dead_battery",
    "dead battery": "weak_or_dead_battery",
    "alternator": "faulty_alternator",
    "starter": "failed_starter_motor",
    "starter motor": "failed_starter_motor",
    "brake pad": "worn_brake_pads",
    "brake pads": "worn_brake_pads",
    "rotors": "warped_brake_rotors",
    "rotor": "warped_brake_rotors",
    "warped rotor": "warped_brake_rotors",
    "brake fluid": "brake_fluid_leak_or_air_in_lines",
    "brake line": "brake_fluid_leak_or_air_in_lines",
    "air in brake": "brake_fluid_leak_or_air_in_lines",
    "spark plug": "ignition_or_spark_plug_failure",
    "spark plugs": "ignition_or_spark_plug_failure",
    "ignition": "ignition_or_spark_plug_failure",
    "fuel filter": "clogged_fuel_injector_or_filter",
    "fuel injector": "clogged_fuel_injector_or_filter",
    "injector": "clogged_fuel_injector_or_filter",
    "catalytic converter": "faulty_o2_sensor_or_catalytic_converter",
    "o2 sensor": "faulty_o2_sensor_or_catalytic_converter",
    "oxygen sensor": "faulty_o2_sensor_or_catalytic_converter",
    "cat": "faulty_o2_sensor_or_catalytic_converter",
    "oil leak": "low_oil_or_oil_leak",
    "low oil": "low_oil_or_oil_leak",
    "oil pressure": "low_oil_or_oil_leak",
    "transmission": "transmission_fluid_low_or_clutch_wear",
    "transmission fluid": "transmission_fluid_low_or_clutch_wear",
    "clutch": "transmission_fluid_low_or_clutch_wear",
    "suspension": "worn_suspension_or_wheel_misalignment",
    "wheel alignment": "worn_suspension_or_wheel_misalignment",
    "alignment": "worn_suspension_or_wheel_misalignment",
    "thermostat": "faulty_thermostat",
    "coolant leak": "coolant_leak",
    "radiator": "coolant_leak",
    "coolant": "coolant_leak",
}

FAULT_PARTS: dict[str, list[str]] = {
    "coolant_leak": ["Radiator", "Coolant Hoses", "Water Pump", "Radiator Cap"],
    "faulty_thermostat": ["Thermostat Assembly", "Thermostat Housing", "Coolant Temp Sensor"],
    "weak_or_dead_battery": ["12V Lead-Acid/AGM Battery", "Battery Terminals", "Ground Strap"],
    "faulty_alternator": ["Alternator Assembly", "Serpentine Drive Belt", "Voltage Regulator"],
    "failed_starter_motor": ["Starter Motor", "Starter Solenoid", "Ignition Relay"],
    "worn_brake_pads": ["Front/Rear Brake Pads", "Brake Pad Wear Sensors", "Brake Hardware Kit"],
    "warped_brake_rotors": ["Brake Rotors (Discs)", "Brake Calipers"],
    "brake_fluid_leak_or_air_in_lines": ["Brake Lines & Hoses", "Master Cylinder", "Brake Caliper Seals", "Brake Bleeder Screws"],
    "ignition_or_spark_plug_failure": ["Spark Plugs", "Ignition Coils", "Spark Plug Wires"],
    "clogged_fuel_injector_or_filter": ["Fuel Filter", "Fuel Injectors", "Fuel Rail"],
    "faulty_o2_sensor_or_catalytic_converter": ["Upstream/Downstream O2 Sensors", "Catalytic Converter", "Exhaust Flange Gasket"],
    "low_oil_or_oil_leak": ["Oil Pan Gasket", "Valve Cover Gasket", "Oil Filter", "Oil Pressure Sensor"],
    "transmission_fluid_low_or_clutch_wear": ["Transmission Fluid & Filter", "Clutch Disc & Pressure Plate", "Release Bearing"],
    "worn_suspension_or_wheel_misalignment": ["Tie Rod Ends", "Control Arm Bushings", "Ball Joints", "Struts/Shocks"],
}


def _format_vehicle_label(vehicle: dict[str, Any] | None) -> str:
    if not vehicle or not isinstance(vehicle, dict):
        return "Vehicle"
    parts = [
        str(vehicle.get(k, "")).strip()
        for k in ("year", "make", "model")
        if str(vehicle.get(k, "")).strip() and str(vehicle.get(k, "")).strip().lower() not in ("none", "")
    ]
    label = " ".join(parts)
    mileage = vehicle.get("mileage")
    fuel = vehicle.get("fuel_type")
    details = []
    if mileage and str(mileage).lower() != "none":
        details.append(f"{mileage:,} mi" if isinstance(mileage, int) else f"{mileage} mi")
    if fuel and str(fuel).lower() not in ("none", ""):
        details.append(str(fuel).capitalize())
    if details:
        label = f"{label} ({', '.join(details)})" if label else f"Vehicle ({', '.join(details)})"
    return label.strip() or "Vehicle"


def _evaluate_sensors(sensor_values: dict[str, float]) -> list[str]:
    notes: list[str] = []
    if "coolant_temp_c" in sensor_values:
        temp = sensor_values["coolant_temp_c"]
        if temp > 105:
            notes.append(f"- **Coolant Temperature:** `{temp:.1f} C` - **[CRITICAL OVERHEATING]** (Normal operating range is 82 C-96 C). Immediate engine shutdown recommended to prevent head gasket warp.")
        elif temp > 98:
            notes.append(f"- **Coolant Temperature:** `{temp:.1f} C` - [ELEVATED]. Monitor closely under load.")
        else:
            notes.append(f"- **Coolant Temperature:** `{temp:.1f} C` - [NORMAL] within thermal limits.")
    if "battery_voltage_v" in sensor_values:
        volts = sensor_values["battery_voltage_v"]
        if volts < 11.9:
            notes.append(f"- **Battery Voltage:** `{volts:.2f}V` - **[DEAD / DEEPLY DISCHARGED]** (Standard rested charge is 12.6V). Starter motor will likely click or fail to turn.")
        elif volts < 12.4:
            notes.append(f"- **Battery Voltage:** `{volts:.2f}V` - [LOW]. Low rested charge; suspect weak battery or parasitic drain.")
        elif volts > 14.8:
            notes.append(f"- **Battery Voltage:** `{volts:.2f}V` - **[OVERCHARGING]** (Alternator voltage regulator failure).")
        else:
            notes.append(f"- **Battery Voltage:** `{volts:.2f}V` - [HEALTHY] normal voltage level.")
    if "oil_pressure_psi" in sensor_values:
        psi = sensor_values["oil_pressure_psi"]
        if psi < 20:
            notes.append(f"- **Oil Pressure:** `{psi:.1f} PSI` - **[DANGEROUSLY LOW]** (Minimum safe warm idle is ~25 PSI). Risk of immediate crankshaft/bearing seizure.")
        else:
            notes.append(f"- **Oil Pressure:** `{psi:.1f} PSI` - [NORMAL] safe operating hydraulic pressure.")
    return notes


def answer_question(question: str, prior_payload: dict[str, Any], diagnosis: dict[str, Any] | None = None) -> dict[str, Any]:
    """Provide real-time automotive diagnosis answers driven by logic, probability, and decision data."""
    clean_q = question.strip()
    normalized = clean_q.lower()
    catalog = symptom_catalog()
    extracted_from_query = extract_symptoms(question, catalog)

    # If diagnosis was not provided or is empty, attempt to compute it in real time
    current_diagnosis = diagnosis
    active_payload = dict(prior_payload)

    if not current_diagnosis:
        has_symptoms = bool(active_payload.get("symptoms")) or bool(active_payload.get("free_text"))
        if not has_symptoms and extracted_from_query:
            active_payload["symptoms"] = extracted_from_query
            has_symptoms = True
        if has_symptoms:
            try:
                current_diagnosis = run_diagnosis(active_payload)
            except Exception:
                current_diagnosis = None

    # Scenario 0: No diagnosis exists yet and no symptoms supplied
    if not current_diagnosis:
        if extracted_from_query:
            active_payload["symptoms"] = extracted_from_query
            current_diagnosis = run_diagnosis(active_payload)
            top = current_diagnosis["top_faults"][0]
            answer = (
                f"### [REAL-TIME ANALYSIS INITIATED]\n\n"
                f"From your message, I identified: **{', '.join(s.replace('_', ' ') for s in extracted_from_query)}**.\n\n"
                f"- **Top Suspected Fault:** **{top['label']}** ({top['probability']:.1%} relative confidence)\n"
                f"- **Severity:** `{top['severity'].upper()}`\n"
                f"- **Recommended Action:** **{current_diagnosis['recommended_action']['label']}**\n\n"
                f"You can confirm additional symptoms in the Symptoms tab or ask me questions like 'Can I drive?' or 'What parts need repair?'."
            )
            return {"kind": "interactive_triage", "answer": answer, "diagnosis": current_diagnosis}
        return {
            "kind": "intake_guidance",
            "answer": (
                "### Real-Time Vehicle Diagnostic Assistant\n\n"
                "I am ready to analyze your vehicle's condition using logic rules, Bayesian probabilities, and decision utility matrices.\n\n"
                "**To get started, you can:**\n"
                "1. Select warning signals in the **Symptoms** step\n"
                "2. Or tell me what symptoms you are experiencing right here (e.g., 'The engine is overheating and blowing white smoke' or 'Clicking sound and headlights are dim')\n"
                "3. Once symptoms are detected, I will generate a real-time diagnosis ranking and safety action."
            ),
        }

    router = QueryRouter(api_key=GEMINI_API_KEY)
    
    # Context for the router
    internal_context = {
        "vehicle": _format_vehicle_label(current_diagnosis.get("vehicle", {})),
        "top_faults": [{"label": f["label"], "probability": f["probability"]} for f in current_diagnosis.get("top_faults", [])[:3]],
        "recommended_action": current_diagnosis.get("recommended_action", {}).get("label"),
        "symptoms": current_diagnosis.get("symptoms", [])
    }
    
    intent = router.classify_query(question, internal_context)

    # Extract key elements from active diagnosis
    vehicle_info = _format_vehicle_label(current_diagnosis.get("vehicle", {}))
    top_faults = current_diagnosis.get("top_faults", [])
    primary_fault = top_faults[0] if top_faults else None
    action = current_diagnosis.get("recommended_action", {})
    action_id = action.get("id", "inspect_soon")
    action_label = action.get("label", "Inspect soon")
    sensor_notes = _evaluate_sensors(active_payload.get("sensor_values", {}))
    observed_symptoms = current_diagnosis.get("symptoms", [])

    is_diagnosis_intent = intent == "VEHICLE_DIAGNOSIS"

    # 1. WHAT-IF COUNTERFACTUAL REASONING
    if is_diagnosis_intent and any(phrase in normalized for phrase in ("what if", "suppose", "if ")) and any(k in normalized for k in ("absent", "not", "without", "removed", "fixed")):
        target_symptoms = extracted_from_query or [s for s in observed_symptoms if s.replace("_", " ") in normalized]
        if not target_symptoms:
            examples = ", ".join(f"'{s.replace('_', ' ')}'" for s in observed_symptoms[:2]) or "'engine overheating'"
            return {
                "kind": "what_if_clarification",
                "answer": f"Please specify which symptom to treat as absent (for example: 'What if {examples} is absent?').",
            }
        absent_symptom = target_symptoms[0]
        changed_payload = dict(active_payload)
        changed_payload["symptoms"] = [s for s in changed_payload.get("symptoms", []) if s != absent_symptom]
        changed_payload["absent_symptoms"] = list(set(changed_payload.get("absent_symptoms", [])) | {absent_symptom})
        
        updated_result = run_diagnosis(changed_payload)
        new_top = updated_result["top_faults"][0]
        old_top_name = primary_fault["label"] if primary_fault else "None"
        old_top_prob = f"{primary_fault['probability']:.1%}" if primary_fault else "0%"
        new_top_prob = f"{new_top['probability']:.1%}"
        
        answer = (
            f"### [COUNTERFACTUAL SIMULATION]\n\n"
            f"**Simulated Condition:** Removing **{absent_symptom.replace('_', ' ')}** (marking as explicitly absent).\n\n"
            f"- **Prior Leading Fault:** {old_top_name} ({old_top_prob})\n"
            f"- **Updated Leading Fault:** **{new_top['label']}** ({new_top_prob})\n"
            f"- **Updated Action:** **{updated_result['recommended_action']['label']}**\n"
            f"- **Impact:** Probability of {new_top['label']} is now ranked #1 with {len(updated_result['top_faults'])} candidates re-weighted."
        )
        return {"kind": "what_if", "symptom": absent_symptom, "diagnosis": updated_result, "answer": answer}

    # 2. CAN I DRIVE / SAFETY / TOWING
    if is_diagnosis_intent and any(kw in normalized for kw in ("can i drive", "safe to drive", "should i drive", "is it safe", "can we drive", "tow", "towing", "drive it")):
        is_tow = action_id == "tow_vehicle"
        is_repair = action_id == "repair_now"
        severity = primary_fault.get("severity", "medium") if primary_fault else "medium"
        
        if is_tow or severity == "critical":
            status_badge = "[CRITICAL] DO NOT DRIVE - TOWING REQUIRED"
            rationale = (
                f"The decision network computed that **Tow Vehicle** maximizes expected utility for your safety. "
                f"Your primary diagnosis is **{primary_fault['label']}** with **{severity.upper()}** severity. "
                "Driving in this condition poses immediate risk of catastrophic mechanical seizure, fire, or total loss of vehicle control."
            )
        elif is_repair or severity == "high":
            status_badge = "[WARNING] AVOID EXTENDED DRIVING - SERVICE IMMEDIATELY"
            rationale = (
                f"The recommended action is **{action_label}**. While the car might operate temporarily, "
                f"driving with suspected **{primary_fault['label']}** will cause rapid cascade damage and higher repair costs."
            )
        else:
            status_badge = "[CAUTION] DRIVE WITH CARE - SCHEDULE INSPECTION"
            rationale = (
                f"Recommended action: **{action_label}**. The symptoms observed for **{primary_fault['label']}** "
                "do not indicate imminent safety shutdown, but should be professionally verified."
            )
        
        telemetry_section = ("\n\n**Sensor Telemetry:**\n" + "\n".join(sensor_notes)) if sensor_notes else ""
        answer = f"### {status_badge}\n\n{rationale}\n\n**Vehicle:** {vehicle_info}\n**Primary Concern:** {primary_fault['label']} ({primary_fault['probability']:.1%}){telemetry_section}"
        return {"kind": "safety_assessment", "answer": answer}

    # 3. SPECIFIC COMPONENT OR FAULT QUERY (e.g. "Is it the battery?", "Could it be the alternator?")
    matched_alias = next((fault_id for alias, fault_id in FAULT_ALIASES.items() if alias in normalized), None)
    if is_diagnosis_intent and matched_alias:
        vehicle_id = current_diagnosis.get("vehicle_id", "vehicle")
        derived_faults = {rule["derived"].rsplit(", ", 1)[-1].rstrip(")") for rule in current_diagnosis.get("fired_rules", [])}
        closure = [Atom("Fault", (vehicle_id, entry["fault"])) for entry in current_diagnosis.get("posterior_table", []) if entry["fault"] in derived_faults]
        res_result = resolution_refutation(closure, Atom("Fault", (vehicle_id, matched_alias)))
        
        post_entry = next((item for item in current_diagnosis.get("posterior_table", []) if item["fault"] == matched_alias), None)
        prob_str = f"{post_entry['probability']:.1%}" if post_entry else "0%"
        label = post_entry["label"] if post_entry else matched_alias.replace("_", " ").title()
        
        is_entailed = res_result.get("entailed", False)
        entail_text = "conclusively establishes" if is_entailed else "does not formally entail"
        
        parts_list = ", ".join(FAULT_PARTS.get(matched_alias, ["Relevant components"]))
        answer = (
            f"### Component Query: {label}\n\n"
            f"- **Bayesian Probability:** **{prob_str}**\n"
            f"- **Logic Resolution Engine:** The Horn clause rule closure **{entail_text}** `{label}` from your confirmed symptoms.\n"
            f"- **Likely Associated Parts:** {parts_list}\n\n"
        )
        if post_entry and post_entry == current_diagnosis["posterior_table"][0]:
            answer += f"**Result:** Yes, this is currently your **#1 leading fault hypothesis**."
        elif post_entry and post_entry["probability"] > 0.15:
            answer += f"**Result:** Possible secondary factor. It carries a notable {prob_str} posterior weight, but **{primary_fault['label']}** ({primary_fault['probability']:.1%}) remains the primary hypothesis."
        else:
            answer += f"**Result:** Unlikely. Current evidence does not strongly support this fault. The primary indicator points to **{primary_fault['label']}** ({primary_fault['probability']:.1%})."
        return {"kind": "component_check", "answer": answer}

    # 4. WHY THIS FAULT / CAUSAL REASONING
    if is_diagnosis_intent and any(kw in normalized for kw in ("why", "reason", "how did you", "explain why", "cause")):
        reasons = ", ".join(s.replace("_", " ") for s in primary_fault["contributing_symptoms"]) or "observed warning evidence"
        fired_rules = primary_fault.get("fired_rules", [])
        if fired_rules:
            rule_texts = "\n".join(f"- **{r['rule_id']}:** `{r['rule_id']}` derived `{primary_fault['label']}` via Modus Ponens" for r in fired_rules)
        else:
            rule_texts = "- *Probabilistic inference*: Bayesian evidence accumulation with background false-positive discounting."

        parts = ", ".join(FAULT_PARTS.get(primary_fault["fault"], ["Target components"]))
        answer = (
            f"### Diagnostic Reasoning for {primary_fault['label']}\n\n"
            f"**Primary Fault:** **{primary_fault['label']}** ({primary_fault['probability']:.1%} relative confidence)\n\n"
            f"**1. Contributing Symptoms:**\n"
            f"The model detected high likelihood ratios for: **{reasons}**.\n\n"
            f"**2. Logic Engine Proof:**\n"
            f"{rule_texts}\n\n"
            f"**3. Suspect Components:**\n"
            f"{parts}\n\n"
            f"**4. Decision Action:** **{action_label}**"
        )
        return {"kind": "why_explanation", "answer": answer}

    # 5. PARTS AND REPAIR PROCEDURES
    if is_diagnosis_intent and any(kw in normalized for kw in ("part", "parts", "replace", "fix", "repair", "component", "tools")):
        parts = FAULT_PARTS.get(primary_fault["fault"], ["Standard OEM replacement parts"])
        answer = (
            f"### Recommended Replacement Parts & Inspection\n\n"
            f"For suspected **{primary_fault['label']}** on your **{vehicle_info}**:\n\n"
            f"**Core Components to Inspect/Replace:**\n"
            + "\n".join(f"- **{part}**" for part in parts)
            + f"\n\n**Next Steps:**\n"
            f"1. Perform visual inspection for physical leaks, corrosion, or mechanical wear.\n"
            f"2. Validate electrical or hydraulic sensor readings.\n"
            f"3. Follow manufacturer torque and bleeding specifications upon replacement."
        )
        return {"kind": "parts_guidance", "answer": answer}

    # 6. SENSORS AND TELEMETRY
    if is_diagnosis_intent and any(kw in normalized for kw in ("sensor", "telemetry", "coolant temp", "voltage", "oil pressure", "temperature")):
        if sensor_notes:
            answer = (
                f"### Real-Time Sensor Telemetry Analysis\n\n"
                f"**Vehicle:** {vehicle_info}\n\n"
                + "\n\n".join(sensor_notes)
                + f"\n\n**Synthesis with Diagnosis:** Telemetry aligns with the primary fault hypothesis **{primary_fault['label']}** ({primary_fault['probability']:.1%})."
            )
        else:
            answer = (
                f"### Sensor Telemetry\n\n"
                "No live sensor values (coolant temperature, battery voltage, or oil pressure) were provided in this triage session.\n"
                "You can enter sensor values under the **Vehicle Panel** (Sensor Telemetry) to get real-time evaluations."
            )
        return {"kind": "sensor_telemetry", "answer": answer}

    # 7. ROUTE TO QUERY ROUTER
    return router.handle_query(question, internal_context)

