"""Tests for deterministic SFT batching and token-weighted accumulation."""

import random
import unittest

from dataclasses import replace

import torch

from llm_post_training.training.sft_plan import (
    build_sft_epoch_plan,
)
from llm_post_training.training.sft_tokenization import (
    SFTTokenizedExample,
)


EOS = 151645


def make_examples(count):
    examples = []

    for index in range(count):
        completion = (200 + index,) * (1 + index % 5)
        prompt = (100,)
        ids = prompt + completion + (EOS,)

        examples.append(
            SFTTokenizedExample(
                source_index=1000 + index,
                input_ids=ids,
                attention_mask=(1,) * len(ids),
                labels=(-100,) + completion + (EOS,),
                prompt_token_count=1,
                completion_token_count=len(completion),
            )
        )

    return examples


def plan(
    examples,
    *,
    epoch=0,
    microbatch_size=4,
    accumulation=2,
    limit=512,
):
    return build_sft_epoch_plan(
        examples,
        epoch=epoch,
        seed=42,
        microbatch_size=microbatch_size,
        gradient_accumulation_steps=accumulation,
        max_sequence_length=limit,
    )


class TestSFTEpochPlan(unittest.TestCase):

    def test_partial_final_optimizer_group(self):
        result = plan(make_examples(10))

        self.assertEqual(result.microbatch_count, 3)
        self.assertEqual(result.optimizer_steps, 2)

        self.assertEqual(
            [len(b) for b in result.groups[0].microbatches],
            [4, 4],
        )

        self.assertEqual(
            [len(b) for b in result.groups[1].microbatches],
            [2],
        )

    def test_every_example_appears_exactly_once(self):
        examples = make_examples(33)
        result = plan(examples)

        seen = [
            index
            for group in result.groups
            for batch in group.microbatches
            for index in batch
        ]

        self.assertEqual(
            sorted(seen),
            list(range(len(examples))),
        )

    def test_reproducible_but_different_between_epochs(self):
        examples = make_examples(30)

        first = plan(examples)

        self.assertEqual(first, plan(examples))

        self.assertNotEqual(
            first.groups,
            plan(examples, epoch=1).groups,
        )

    def test_weights_reflect_supervised_tokens(self):
        examples = make_examples(9)
        result = plan(examples)

        for group in result.groups:
            expected_counts = tuple(
                sum(
                    examples[index].completion_token_count + 1
                    for index in batch
                )
                for batch in group.microbatches
            )

            self.assertEqual(
                group.supervised_tokens_per_batch,
                expected_counts,
            )

            self.assertEqual(
                group.total_supervised_tokens,
                sum(expected_counts),
            )

            self.assertAlmostEqual(
                sum(group.loss_weights),
                1.0,
            )

            for count, weight in zip(
                expected_counts,
                group.loss_weights,
            ):
                self.assertAlmostEqual(
                    weight,
                    count / sum(expected_counts),
                )

    def test_weighted_gradients_equal_global_token_mean(self):
        examples = make_examples(7)

        group = plan(
            examples,
            microbatch_size=2,
            accumulation=4,
        ).groups[0]

        theta = torch.tensor(
            0.3,
            dtype=torch.float64,
            requires_grad=True,
        )

        reference_theta = torch.tensor(
            0.3,
            dtype=torch.float64,
            requires_grad=True,
        )

        def token_losses(value, batch):
            return [
                (value - index / 10.0).square()
                for index in batch
                for _ in range(
                    examples[index].completion_token_count + 1
                )
            ]

        # Accumulate gradients from separate microbatch means.
        for batch, weight in zip(
            group.microbatches,
            group.loss_weights,
        ):
            torch.stack(
                token_losses(theta, batch)
            ).mean().mul(weight).backward()

        # Reference: compute one mean over all supervised tokens.
        positions = [
            index
            for batch in group.microbatches
            for index in batch
        ]

        torch.stack(
            token_losses(reference_theta, positions)
        ).mean().backward()

        self.assertAlmostEqual(
            theta.grad.item(),
            reference_theta.grad.item(),
            places=12,
        )

    def test_no_mutation_of_global_random_state(self):
        random.seed(2026)

        before = random.getstate()

        plan(make_examples(20))

        self.assertEqual(
            random.getstate(),
            before,
        )

    def test_duplicate_source_index_rejected(self):
        examples = make_examples(2)

        examples[1] = replace(
            examples[1],
            source_index=examples[0].source_index,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Duplicate",
        ):
            plan(examples)

    def test_overlong_sequence_rejected_without_truncation(self):
        with self.assertRaisesRegex(
            ValueError,
            "exceeds",
        ):
            plan(make_examples(5), limit=3)

    def test_invalid_metadata_and_configuration_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            plan([])

        with self.assertRaisesRegex(ValueError, "nonnegative"):
            plan(make_examples(3), epoch=-1)

        with self.assertRaisesRegex(ValueError, "positive"):
            plan(make_examples(3), microbatch_size=0)

        with self.assertRaisesRegex(ValueError, "positive"):
            plan(make_examples(3), accumulation=0)

        examples = make_examples(3)

        examples[0] = replace(
            examples[0],
            labels=(-100,) * examples[0].sequence_length,
        )

        with self.assertRaisesRegex(
            ValueError,
            "supervised token count",
        ):
            plan(examples)


if __name__ == "__main__":
    unittest.main()
