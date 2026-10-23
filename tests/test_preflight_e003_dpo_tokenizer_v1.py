#!/usr/bin/env python3
"""Offline contract tests using synthetic data only; no model/DPO training."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('e003_preflight', ROOT/'scripts/preflight_e003_dpo_tokenizer_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FakeTokenizer:
    def __init__(self):
        self.pad_token_id = 151643
        self._eos = 151645
        self.eos_token = '<|im_end|>'
    @property
    def eos_token_id(self):
        return 151643 if self.eos_token == '<|endoftext|>' else 151645
    def convert_ids_to_tokens(self, i):
        return {151643: '<|endoftext|>', 151645: '<|im_end|>'}[i]
    def convert_tokens_to_ids(self, x):
        return {'<|endoftext|>': 151643, '<|im_end|>': 151645}[x]
    def __call__(self, text, add_special_tokens=False):
        return {'input_ids': [ord(c) for c in text]}


def fake_tokenize(row, processing_class, max_prompt_length, max_completion_length, add_special_tokens):
    t=processing_class
    if add_special_tokens or max_prompt_length is not None or max_completion_length is not None:
        raise ValueError('Unexpected input options')
    return {'prompt_input_ids': t(row['prompt'])['input_ids'],
            'chosen_input_ids': t(row['chosen'])['input_ids']+[t.eos_token_id],
            'rejected_input_ids': t(row['rejected'])['input_ids']+[t.eos_token_id]}


class FakeCollator:
    def __init__(self, pad_token_id):
        self.pad=pad_token_id
    def __call__(self, xs):
        import torch
        out={}
        for fld in ('chosen', 'rejected'):
            maxlen=max(len(row[fld+'_input_ids']) for row in xs)
            values=[row[fld+'_input_ids'] for row in xs]
            out[fld+'_input_ids'] = torch.tensor([v+[self.pad]*(maxlen-len(v)) for v in values])
            out[fld+'_attention_mask'] = torch.tensor([[1]*len(v)+[0]*(maxlen-len(v)) for v in values])
        maxlen=max(len(row['prompt_input_ids']) for row in xs)
        out['prompt_attention_mask'] = torch.tensor([[0]*(maxlen-len(row['prompt_input_ids']))+[1]*len(row['prompt_input_ids']) for row in xs])
        return out


class Tests(unittest.TestCase):
    def setUp(self):
        self.rows = [{'prompt':'Q: ', 'chosen':'12','rejected':'13'},
                     {'prompt':'Q: XY ', 'chosen':'7','rejected':'888'}]
        self.notes=[]
        for row in self.rows:
            self.notes.append({'source_index':len(self.notes),
                               'chosen_generated_token_ids': [ord(x) for x in row['chosen']]+[151643],
                               'rejected_generated_token_ids': [ord(x) for x in row['rejected']]+[151643]})
        self.stub1=types.ModuleType('trl')
        self.stub2=types.ModuleType('trl.trainer')
        self.stub3=types.ModuleType('trl.trainer.dpo_trainer')
        self.stub3.DataCollatorForPreference=FakeCollator

    def test_native_eos_and_masks(self):
        with patch.dict(sys.modules, {'trl':self.stub1, 'trl.trainer':self.stub2,
                                      'trl.trainer.dpo_trainer':self.stub3}):
            size, mismatch, boundary = mod.analyze_pairs(FakeTokenizer(),self.rows,self.notes,fake_tokenize)
        self.assertEqual(size['chosen'],3)
        self.assertEqual(size['rejected'],4)
        self.assertFalse(mismatch)
        self.assertFalse(boundary)

    def test_bad_raw_eos_rejected(self):
        t=FakeTokenizer()
        t._eos=151645
        # Only source completion EOS policy may be overridden; the starting
        # tokenizer must still have the historic Qwen configured EOS.
        t.eos_token='<|endoftext|>'
        with self.assertRaisesRegex(RuntimeError,'as-shipped EOS'):
            mod.analyze_pairs(t,self.rows,self.notes,fake_tokenize)

    def test_unexpected_completion_internal_eos_rejected(self):
        def bad(row, processing_class, **kwargs):
            result=fake_tokenize(row,processing_class,**kwargs)
            result['chosen_input_ids'].insert(1,151643)
            return result
        with patch.dict(sys.modules, {'trl':self.stub1, 'trl.trainer':self.stub2,
                                      'trl.trainer.dpo_trainer':self.stub3}):
            with self.assertRaisesRegex(RuntimeError,'Unexpected native EOS inside response'):
                mod.analyze_pairs(FakeTokenizer(),self.rows,self.notes,bad)

    def test_digest_stable(self):
        self.assertEqual(mod.digest(b'abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')


if __name__=='__main__':
    unittest.main(verbosity=2)
