import unittest

from backend.diagnosis import run_diagnosis
from backend.logic.resolution import resolution_refutation
from backend.logic.unification import Atom, unify
from backend.nlp.parser import extract_symptoms
from backend.tests.cases import CASES


class DiagnosisCases(unittest.TestCase):
    def test_fifteen_labeled_cases(self):
        for payload, expected_fault in CASES:
            with self.subTest(expected_fault=expected_fault):
                result = run_diagnosis(payload)
                self.assertEqual(result["top_faults"][0]["fault"], expected_fault)

    def test_returns_ranked_posteriors_and_utility(self):
        result = run_diagnosis({"symptoms": ["oil_pressure_light", "oil_leak_under_car"]})
        self.assertEqual(len(result["top_faults"]), 3)
        self.assertEqual(len(result["expected_utilities"]), 4)
        self.assertIn(result["recommended_action"]["id"], {"continue_driving", "inspect_soon", "repair_now", "tow_vehicle"})

    def test_rejects_unknown_and_conflicting_evidence(self):
        with self.assertRaises(ValueError):
            run_diagnosis({"symptoms": ["made_up_symptom"]})
        with self.assertRaises(ValueError):
            run_diagnosis({"symptoms": ["low_coolant"], "absent_symptoms": ["low_coolant"]})

    def test_unification_and_resolution_refutation(self):
        substitution = unify(Atom("Fault", ("?vehicle", "coolant_leak")), Atom("Fault", ("car-1", "coolant_leak")))
        self.assertEqual(substitution, {"?vehicle": "car-1"})
        result = resolution_refutation([Atom("Fault", ("car-1", "coolant_leak"))], Atom("Fault", ("car-1", "coolant_leak")))
        self.assertTrue(result["entailed"])

    def test_free_text_synonym_extraction(self):
        from backend.diagnosis import symptom_catalog
        found = extract_symptoms("The headlights are dim and the engine keeps stalling", symptom_catalog())
        self.assertEqual(set(found), {"dim_headlights", "engine_stalling"})


if __name__ == "__main__":
    unittest.main()
