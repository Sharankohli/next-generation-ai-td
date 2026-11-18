import importlib.util
import unittest
from pathlib import Path


MODULE_SPEC = importlib.util.spec_from_file_location(
    "atelier_routage", Path(__file__).with_name("atelier-routage.py")
)
router = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(router)


class RoutingPolicyTests(unittest.TestCase):
    def test_selects_first_eligible_free_model(self):
        result = router.choose(
            {"family": "F1", "use_case": "internal", "can_wait": True,
             "deadline_minutes": 60, "budget": 0.01},
            router.RESOURCES,
        )
        self.assertEqual((result["action"], result["resource"]), ("run", "A-groq-free"))
        self.assertIn("C01,C04-C07,C20", result["reason"])

    def test_falls_back_to_next_eligible_free_model(self):
        resources = [
            dict(resource, available=False)
            if resource["id"] == "A-groq-free" else dict(resource)
            for resource in router.RESOURCES
        ]
        result = router.choose(
            {"family": "F1", "use_case": "internal", "can_wait": False,
             "deadline_minutes": 0, "budget": 0},
            resources,
        )
        self.assertEqual((result["action"], result["resource"]), ("run", "B-groq-free"))

    def test_defers_when_free_quota_can_refill(self):
        resources = [
            dict(resource, available=False, reset_minutes=30)
            if resource["access"] == "free" else dict(resource, available=False)
            for resource in router.RESOURCES
        ]
        result = router.choose(
            {"family": "F1+F2+F3", "use_case": "internal", "can_wait": True,
             "deadline_minutes": 60, "budget": 0.01},
            resources,
        )
        self.assertEqual((result["action"], result["wake_in_minutes"]), ("defer", 30))

    def test_uses_paid_fallback_only_within_budget(self):
        resources = [
            dict(resource, available=False, reset_minutes=None)
            if resource["access"] == "free" else dict(resource)
            for resource in router.RESOURCES
        ]
        request = {"family": "F1+F2+F3", "use_case": "internal", "can_wait": False,
                   "deadline_minutes": 5, "budget": router.PAID_A_COST}
        result = router.choose(request, resources)
        self.assertEqual((result["action"], result["resource"]),
                         ("run", "A-openrouter-paid"))
        request["budget"] = 0
        self.assertEqual(router.choose(request, resources)["action"], "abstain")

    def test_payout_requires_independent_reconciliation_and_approval(self):
        result = router.choose(
            {"family": "F2", "use_case": "payout", "can_wait": True,
             "deadline_minutes": 60, "budget": 0},
            router.RESOURCES,
        )
        self.assertIn("source verification and human approval", result["checks"])

    def test_unknown_family_abstains(self):
        result = router.choose(
            {"family": "unknown", "use_case": "internal", "can_wait": False,
             "deadline_minutes": 0, "budget": 0},
            router.RESOURCES,
        )
        self.assertEqual(result["action"], "abstain")
        self.assertIn("No matching TD1 family evidence exists", result["reason"])
        self.assertIn("among cases C01-C20", result["reason"])


if __name__ == "__main__":
    unittest.main()
