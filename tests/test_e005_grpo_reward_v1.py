"""E005 GRPO reward contract and edge-case tests."""

import unittest

from llm_post_training.training.grpo_reward import (
    GRPO_REWARD_VERSION,
    gsm8k_exact_numeric_reward,
)


class E005GRPORewardTests(unittest.TestCase):
    def score(self, completions, solutions):
        return gsm8k_exact_numeric_reward(
            completions=completions,
            answer=solutions,
            prompts=["Question: sample"] * len(completions),
            completion_ids=[[]] * len(completions),
            source_index=[182] * len(completions),
            trainer_state=None,
        )

    def test_version(self):
        self.assertEqual(
            GRPO_REWARD_VERSION,
            "gsm8k_exact_numeric_v1",
        )

    def test_correct_and_incorrect(self):
        self.assertEqual(
            self.score(
                ["The answer is 42.", "The answer is 41."],
                ["Calculation.\n#### 42"] * 2,
            ),
            [1.0, 0.0],
        )

    def test_four_completion_grpo_group(self):
        self.assertEqual(
            self.score(
                [
                    "The answer is 42.",
                    "The answer is 41.",
                    "The answer is 42.",
                    "No numerical final answer.",
                ],
                ["#### 42"] * 4,
            ),
            [1.0, 0.0, 1.0, 0.0],
        )

    def test_negative_answers(self):
        self.assertEqual(
            self.score(
                [
                    "Final answer: -3,500",
                    "Final answer: 3,500",
                ],
                ["#### -3500", "#### -3500"],
            ),
            [1.0, 0.0],
        )

    def test_decimal_answers(self):
        self.assertEqual(
            self.score(
                [
                    "The answer is 2.50.",
                    "The answer is 2.51.",
                ],
                ["#### 2.5", "#### 2.5"],
            ),
            [1.0, 0.0],
        )

    def test_comma_separated_answers(self):
        self.assertEqual(
            self.score(
                ["Final answer: 1,250"],
                ["#### 1250"],
            ),
            [1.0],
        )

    def test_boxed_answer(self):
        self.assertEqual(
            self.score(
                [r"\boxed{100}"],
                ["#### 100"],
            ),
            [1.0],
        )

    def test_missing_answer(self):
        self.assertEqual(
            self.score(
                ["There are 20 objects in total."],
                ["#### 20"],
            ),
            [0.0],
        )

    def test_conflicting_final_answers(self):
        self.assertEqual(
            self.score(
                ["The answer is 42. The answer is 43."],
                ["#### 42"],
            ),
            [0.0],
        )

    def test_repeated_agreeing_final_answers(self):
        self.assertEqual(
            self.score(
                ["The answer is 42. Final answer: 42"],
                ["#### 42"],
            ),
            [1.0],
        )

    def test_unwanted_next_question(self):
        self.assertEqual(
            self.score(
                ["The answer is 42.\nQuestion: Solve another problem."],
                ["#### 42"],
            ),
            [0.0],
        )

    def test_zero_and_signed_zero(self):
        self.assertEqual(
            self.score(
                ["The answer is -0."],
                ["#### 0"],
            ),
            [1.0],
        )

    def test_empty_completion(self):
        self.assertEqual(
            self.score([""], ["#### 42"]),
            [0.0],
        )

    def test_batch_length_mismatch(self):
        with self.assertRaisesRegex(ValueError, "length mismatch"):
            self.score(
                ["The answer is 1."],
                ["#### 1", "#### 2"],
            )

    def test_invalid_reference_fails(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid GSM8K reference",
        ):
            self.score(
                ["The answer is 42."],
                ["Answer is 42"],
            )

    def test_conflicting_reference_fails(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid GSM8K reference",
        ):
            self.score(
                ["The answer is 42."],
                ["#### 42\n#### 43"],
            )

    def test_non_string_completion_fails(self):
        with self.assertRaisesRegex(TypeError, "not a string"):
            self.score(
                [None],
                ["#### 42"],
            )

    def test_non_string_reference_fails(self):
        with self.assertRaisesRegex(TypeError, "not a string"):
            self.score(
                ["The answer is 42."],
                [None],
            )

    def test_scalar_completion_fails(self):
        with self.assertRaisesRegex(
            TypeError,
            "sequence of strings",
        ):
            self.score(
                "The answer is 42.",
                ["#### 42"],
            )

    def test_scalar_reference_fails(self):
        with self.assertRaisesRegex(
            TypeError,
            "sequence of GSM8K solutions",
        ):
            self.score(
                ["The answer is 42."],
                "#### 42",
            )


if __name__ == "__main__":
    unittest.main()
