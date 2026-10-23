"""Pure-stdlib tests for E003 candidate preview, no data or GPU needed."""
import importlib.util
import unittest
from pathlib import Path

p=Path(__file__).resolve().parents[1] / 'scripts/build_e003_candidate124_v1.py'
if not p.is_file():
    p=Path(__file__).with_name('build_e003_candidate124_v1.py')
spec=importlib.util.spec_from_file_location('preview_builder_under_test', p)
b=importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def fake(source, sample, correct, tokens=25):
    eos=151643
    ids=[17]*(tokens-1)+[eos]
    return {'source_index':source, 'sample_index':sample,
            'sample_seed':42+source*100+sample,
            'prompt':'Question: 2+2?\nAnswer:',
            'reference_answer':'4' if source!=5436 else '55',
            'response':f' 2 + 2 = 4. The answer is {4 if correct else 5}.',
            'generated_token_ids':ids,'generated_tokens':len(ids),
            'native_eos_stop':True, 'reached_token_cap':False,
            'eligible':True,'extraction_status':'valid',
            'unwanted_continuation':False,'correct':correct}


class Candidate124Tests(unittest.TestCase):
    def test_normal_pair_status_is_not_approved(self):
        ch=fake(100,1,True,25);rj=fake(100,2,False,32)
        out=b.make_pair(100,ch,rj,review_status='ADVISORY_NOT_INDEPENDENTLY_APPROVED',
            review_source='screen',approved_pair=False,original_reference='4',
            training_reference='4',expected_gap=7)
        self.assertEqual((out['chosen_sample_index'],out['rejected_sample_index']),(1,2))
        self.assertFalse(out['training_authorized'])
        self.assertFalse(out['independent_pair_signoff'])
        self.assertEqual(out['chosen_generated_token_ids'][-1],151643)
        self.assertEqual(out['chosen'],ch['response'])

    def test_5436_corrected_exception_only_pair_level(self):
        ch=fake(5436,2,False,74);rj=fake(5436,0,True,46)
        out=b.make_pair(5436,ch,rj,review_status='INDEPENDENTLY_APPROVED_EXCEPTION_PAIR_ONLY',
            review_source='pair_approval',approved_pair=True,original_reference='55',
            training_reference='50',expected_gap=28)
        self.assertTrue(out['reference_training_only_erratum'])
        self.assertTrue(out['independent_pair_signoff'])
        self.assertFalse(out['training_authorized'])

    def test_reject_ineligible_and_missing_eos(self):
        ch=fake(100,1,True);rj=fake(100,2,False)
        ch['eligible']=False
        with self.assertRaises(ValueError):
            b.make_pair(100,ch,rj,review_status='a',review_source='b',
                approved_pair=False,original_reference='4',training_reference='4',expected_gap=0)
        ch['eligible']=True;ch['generated_token_ids'][-1]=151645
        with self.assertRaises(ValueError):
            b.make_pair(100,ch,rj,review_status='a',review_source='b',
                approved_pair=False,original_reference='4',training_reference='4',expected_gap=0)

    def test_reject_correctness_swap_and_length_mismatch(self):
        ch=fake(100,1,False);rj=fake(100,2,True)
        with self.assertRaises(ValueError):
            b.make_pair(100,ch,rj,review_status='a',review_source='b',
                approved_pair=False,original_reference='4',training_reference='4',expected_gap=0)
        ch=fake(100,1,True);rj=fake(100,2,False)
        with self.assertRaises(ValueError):
            b.make_pair(100,ch,rj,review_status='a',review_source='b',
                approved_pair=False,original_reference='4',training_reference='4',expected_gap=200)

    def test_canonical_serialization_is_stable(self):
        val=[{'z':2,'a':1}]
        self.assertEqual(b.canonical_jsonl(val),b'{"a":1,"z":2}\n')
        self.assertEqual(b.canonical_json({'z':2,'a':1}),b'{\n  "a": 1,\n  "z": 2\n}\n')


if __name__=='__main__':
    unittest.main()
