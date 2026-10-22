"""CPU-only eligibility and preference-pair feasibility tests for E003 pilot."""

import copy
import unittest

from scripts.pilot_dpo_preferences import candidate_is_eligible, group_is_mixed


BASE = {
    "native_eos_stop": True,
    "reached_token_cap": False,
    "extraction_status": "valid",
    "unwanted_continuation": False,
    "response": " 2+2=4.\nThe answer is 4.",
    "correct": True,
}


class TestDPOPreferencePilot(unittest.TestCase):
    def test_correct_and_incorrect_both_eligible(self):
        correct = copy.deepcopy(BASE)
        incorrect = {**BASE, "correct": False, "response": "The answer is 5."}
        self.assertTrue(candidate_is_eligible(correct))
        self.assertTrue(candidate_is_eligible(incorrect))
        self.assertTrue(group_is_mixed([correct, incorrect]))

    def test_reject_unterminated_response(self):
        candidate = {**BASE, "native_eos_stop": False}
        self.assertFalse(candidate_is_eligible(candidate))
        self.assertFalse(group_is_mixed([BASE, candidate]))

    def test_reject_token_cap_and_ambiguous_answer(self):
        self.assertFalse(candidate_is_eligible({**BASE, "reached_token_cap": True}))
        self.assertFalse(candidate_is_eligible({**BASE, "extraction_status": "ambiguous"}))

    def test_reject_unwanted_continuation_and_missing_final_marker(self):
        self.assertFalse(candidate_is_eligible({**BASE, "unwanted_continuation": True}))
        self.assertFalse(candidate_is_eligible({**BASE, "response": "4"}))

    def test_no_pair_when_all_correct(self):
        self.assertFalse(group_is_mixed([BASE, BASE]))


if __name__ == "__main__":
    unittest.main()
