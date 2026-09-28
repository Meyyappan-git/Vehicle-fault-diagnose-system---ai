"""Small illustrative labeled set for measuring top-1 symptom-triage accuracy."""
CASES = [
    ({"symptoms": ["engine_overheating", "low_coolant", "coolant_puddle_under_car"]}, "coolant_leak"),
    ({"symptoms": ["engine_overheating", "temperature_warning_light"]}, "faulty_thermostat"),
    ({"symptoms": ["no_crank_clicking_sound", "dim_headlights", "hard_starting"]}, "weak_or_dead_battery"),
    ({"symptoms": ["battery_warning_light", "dim_headlights", "accessories_failing"]}, "faulty_alternator"),
    ({"symptoms": ["no_crank_clicking_sound", "hard_starting"], "absent_symptoms": ["dim_headlights", "battery_warning_light"]}, "failed_starter_motor"),
    ({"symptoms": ["squealing_brakes", "grinding_brakes", "brake_warning_light"]}, "worn_brake_pads"),
    ({"symptoms": ["vibration_when_braking", "pulling_when_braking", "squealing_brakes"]}, "warped_brake_rotors"),
    ({"symptoms": ["spongy_brake_pedal", "brake_warning_light", "pulling_when_braking"]}, "brake_fluid_leak_or_air_in_lines"),
    ({"symptoms": ["rough_idling", "engine_misfire", "hard_starting"]}, "ignition_or_spark_plug_failure"),
    ({"symptoms": ["hesitation_on_acceleration", "poor_mileage", "engine_misfire"]}, "clogged_fuel_injector_or_filter"),
    ({"symptoms": ["rotten_egg_smell", "check_engine_light", "loss_of_power"]}, "faulty_o2_sensor_or_catalytic_converter"),
    ({"symptoms": ["oil_pressure_light", "oil_leak_under_car", "burning_oil_smell"]}, "low_oil_or_oil_leak"),
    ({"symptoms": ["gear_slipping", "delayed_gear_engagement", "burning_smell_from_transmission"]}, "transmission_fluid_low_or_clutch_wear"),
    ({"symptoms": ["steering_wheel_vibration", "vehicle_pulls_to_one_side", "uneven_tire_wear"]}, "worn_suspension_or_wheel_misalignment"),
    ({"free_text": "It runs hot, has low antifreeze, and leaves a coolant puddle under the car."}, "coolant_leak"),
]
