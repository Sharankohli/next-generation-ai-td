"""Tests for Orchestrateur.vote_k_sur_n (TD 2, step 1). No network.

    .venv\Scripts\python.exe -m unittest test_vote_k_sur_n -v
"""
import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location("skel", Path(__file__).with_name("skeleton-multi-llm-en.py"))
skel = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = skel
spec.loader.exec_module(skel)

A = ("groq", "openai/gpt-oss-120b")
B = ("openrouter", "cohere/north-mini-code:free")
C = ("groq", "qwen/qwen3.8-27b")
D = ("groq", "openai/gpt-oss-20b")
E = ("openrouter", "dots-studio/dots-3-note-preview:free")


def prop(member, value):
    return SimpleNamespace(provider=member[0], model_requested=member[1], value=value,
                           verdict="executed" if value is not None else "error")


def vote(proposals, k):
    return skel.Orchestrateur.vote_k_sur_n(None, proposals, k)


class VoteKSurN(unittest.TestCase):
    def test_two_of_three_agree(self):
        r = vote([prop(A, 100), prop(B, 100), prop(C, 120)], 2)
        self.assertEqual(r, {"consensus": True, "value": 100, "votes": 2,
                             "models": ["groq:openai/gpt-oss-120b", "openrouter:cohere/north-mini-code:free"]})

    def test_all_disagree_abstains(self):
        r = vote([prop(A, 100), prop(B, 110), prop(C, 120)], 2)
        self.assertEqual(r, {"consensus": False, "value": None, "votes": 1, "models": []})

    def test_unavailable_members_stay_in_n(self):
        # n = 3, k = 2: one vote is not enough, even though nobody disagrees
        r = vote([prop(A, 100), prop(B, None), prop(C, None)], 2)
        self.assertEqual(r, {"consensus": False, "value": None, "votes": 1, "models": []})

    def test_error_with_a_value_does_not_vote(self):
        bad = SimpleNamespace(provider=B[0], model_requested=B[1], value=100, verdict="error")
        r = vote([prop(A, 100), bad, prop(C, 120)], 2)
        self.assertFalse(r["consensus"])
        self.assertEqual(r["votes"], 1)

    def test_zero_is_a_real_value(self):
        r = vote([prop(A, 0), prop(B, 0), prop(C, 100)], 2)
        self.assertTrue(r["consensus"])
        self.assertEqual(r["value"], 0)
        self.assertEqual(r["votes"], 2)

    def test_three_of_five(self):
        r = vote([prop(A, 5), prop(B, 5), prop(C, 7), prop(D, 5), prop(E, None)], 3)
        self.assertTrue(r["consensus"])
        self.assertEqual((r["value"], r["votes"]), (5, 3))
        self.assertEqual(len(r["models"]), 3)

    def test_three_of_five_with_two_unavailable_abstains(self):
        r = vote([prop(A, 5), prop(B, 5), prop(C, None), prop(D, None), prop(E, 9)], 3)
        self.assertEqual(r, {"consensus": False, "value": None, "votes": 2, "models": []})

    def test_k_must_be_strict_majority(self):
        with self.assertRaises(ValueError):
            vote([prop(A, 1), prop(B, 1), prop(C, 1)], 1)       # 3 // 2 = 1, k must be > 1
        with self.assertRaises(ValueError):
            vote([prop(A, 1), prop(B, 1), prop(C, 1), prop(D, 1)], 2)  # 4 // 2 = 2, k must be > 2

    def test_k_cannot_exceed_n(self):
        with self.assertRaises(ValueError):
            vote([prop(A, 1), prop(B, 1), prop(C, 1)], 4)

    def test_unanimity_allowed(self):
        r = vote([prop(A, 9), prop(B, 9), prop(C, 9)], 3)
        self.assertTrue(r["consensus"])
        self.assertEqual(r["votes"], 3)

    def test_duplicate_provider_model_refused(self):
        with self.assertRaises(ValueError):
            vote([prop(A, 100), prop(A, 100), prop(C, 120)], 2)

    def test_same_model_name_other_provider_is_distinct(self):
        other = ("openrouter", "openai/gpt-oss-120b")
        r = vote([prop(A, 100), prop(other, 100), prop(C, 120)], 2)
        self.assertTrue(r["consensus"])

    def test_wrong_consensus_is_still_a_consensus(self):
        # the vote never sees the reference: two models agreeing on 0 win
        r = vote([prop(A, 0), prop(B, 0), prop(C, 100)], 2)
        self.assertEqual((r["consensus"], r["value"]), (True, 0))


if __name__ == "__main__":
    unittest.main()
