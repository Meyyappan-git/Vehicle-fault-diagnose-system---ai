"""Syllabus topic: symptom input normalization with keyword/synonym matching."""
from __future__ import annotations

import re
from typing import Any

SYNONYMS = {
    "engine_overheating": ["running hot", "overheating", "temperature too high"],
    "knocking_noise": ["engine knock", "knocking", "tapping from engine"],
    "rough_idling": ["rough idle", "idles roughly", "engine shakes at idle"],
    "engine_stalling": ["engine stalls", "keeps stalling", "cuts out"],
    "hard_starting": ["hard to start", "slow to start", "difficult starting"],
    "loss_of_power": ["lost power", "power loss", "weak acceleration"],
    "black_smoke": ["black smoke", "sooty exhaust"],
    "blue_smoke": ["blue smoke", "oil smoke"],
    "white_smoke": ["white smoke", "white exhaust"],
    "check_engine_light": ["check engine", "engine warning light", "mil light"],
    "poor_mileage": ["bad gas mileage", "poor fuel economy", "using more fuel"],
    "fuel_smell": ["smell of fuel", "gas smell", "petrol smell"],
    "engine_misfire": ["misfiring", "misfire", "engine misses"],
    "hesitation_on_acceleration": ["hesitates when accelerating", "hesitation", "stumbles on acceleration"],
    "low_coolant": ["coolant is low", "low antifreeze", "losing coolant"],
    "coolant_puddle_under_car": ["coolant puddle", "coolant leak on ground", "antifreeze under car"],
    "temperature_warning_light": ["temperature light", "temp warning", "hot warning light"],
    "steam_from_hood": ["steam under hood", "steam from bonnet", "smoke from hood"],
    "no_crank_clicking_sound": ["clicking but won't start", "click no crank", "won't crank"],
    "dim_headlights": ["headlights are dim", "dim lights", "lights dimming"],
    "battery_warning_light": ["battery light", "charging light"],
    "accessories_failing": ["electrical accessories failing", "radio cuts out", "electrics failing"],
    "squealing_brakes": ["brakes squeal", "brake squeal", "squeaky brakes"],
    "grinding_brakes": ["brakes grind", "grinding when braking", "metal on metal brakes"],
    "spongy_brake_pedal": ["soft brake pedal", "spongy brakes", "brake pedal sinks"],
    "pulling_when_braking": ["pulls when braking", "pulling under braking"],
    "brake_warning_light": ["brake light", "brake warning"],
    "vibration_when_braking": ["brake vibration", "vibrates when braking", "steering shakes when braking"],
    "gear_slipping": ["transmission slipping", "gear slips", "clutch slipping"],
    "delayed_gear_engagement": ["delayed shifting", "slow gear engagement", "delay shifting into gear"],
    "burning_smell_from_transmission": ["transmission burning smell", "burning clutch smell"],
    "steering_wheel_vibration": ["steering wheel shakes", "steering vibration"],
    "vehicle_pulls_to_one_side": ["car pulls left", "car pulls right", "pulls to one side"],
    "clunking_over_bumps": ["clunk over bumps", "suspension knocking", "clunking noise over bumps"],
    "uneven_tire_wear": ["uneven tyre wear", "uneven tire wear", "tires wearing unevenly"],
    "rotten_egg_smell": ["rotten egg smell", "sulfur smell", "sulphur exhaust smell"],
    "loud_exhaust_noise": ["loud exhaust", "exhaust is loud", "exhaust leak noise"],
    "oil_pressure_light": ["oil light", "oil pressure warning"],
    "oil_leak_under_car": ["oil puddle", "oil leaking", "oil under car"],
    "burning_oil_smell": ["burning oil smell", "smells like burning oil"]
}


def _contains_phrase(text: str, phrase: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text) is not None


def extract_symptoms(text: str, symptoms: list[dict[str, Any]]) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.lower().replace("_", " ")).strip()
    found: list[str] = []
    for symptom in symptoms:
        identifier = symptom["id"]
        phrases = [symptom["label"].lower(), identifier.replace("_", " "), *SYNONYMS.get(identifier, [])]
        if any(_contains_phrase(normalized, phrase) for phrase in phrases) and identifier not in found:
            found.append(identifier)
    return found
