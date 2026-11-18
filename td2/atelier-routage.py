#!/usr/bin/env python3
"""TD 2 and TD 3: read the decisions of a routing rule, then adapt it to your own.

Synthetic resources, no API call, no key.

Costs are fictional USD excluding tax per request, with a fixed token envelope.
Capability levels 1/2/3 describe eligibility for this exercise, not model IQ.
Quota availability is supplied as a scenario, not measured from a provider.
"""
import argparse
import json

FAMILIES = {
    "F1": {"cases": "C01,C04-C07,C20", "scores": {"A": (6, 6), "B": (6, 6), "C": (6, 6), "D": (5, 5), "E": (6, 6)}, "incomplete": ("D",)},
    "F2": {"cases": "C02,C08,C09,C11", "scores": {"A": (4, 4), "B": (2, 4), "C": (0, 4), "D": (4, 4), "E": (0, 4)}, "incomplete": ()},
    "F2b": {"cases": "C10", "scores": {"A": (1, 1), "B": (1, 1), "C": (0, 1), "D": (0, 1), "E": (0, 1)}, "incomplete": ()},
    "F3": {"cases": "C03,C12-C14", "scores": {"A": (4, 4), "B": (4, 4), "C": (4, 4), "D": (4, 4), "E": (4, 4)}, "incomplete": ()},
    "F1+F2": {"cases": "C15", "scores": {"A": (1, 1), "B": (1, 1), "C": (1, 1), "D": (0, 1), "E": (1, 1)}, "incomplete": ()},
    "F2+F3": {"cases": "C16", "scores": {"A": (1, 1), "B": (1, 1), "C": (0, 1), "D": (1, 1), "E": (1, 1)}, "incomplete": ()},
    "F1+F2+F3": {"cases": "C17,C19", "scores": {"A": (2, 2), "B": (2, 2), "C": (0, 2), "D": (0, 1), "E": (0, 2)}, "incomplete": ("D",)},
    "F1+F2b": {"cases": "C18", "scores": {"A": (1, 1), "B": (1, 1), "C": (1, 1), "D": (1, 1), "E": (0, 1)}, "incomplete": ()},
}

PREFERENCE = {
    "F1": ["A", "B"],
    "F2": ["A", "D"],
    "F2b": ["B", "A"],
    "F3": ["A", "B", "D"],
    "F1+F2": ["B", "A"],
    "F2+F3": ["A", "B", "D"],
    "F1+F2+F3": ["A", "B"],
    "F1+F2b": ["B", "A", "D"],
}

PAID_A_COST = 0.15 * 1000 / 1_000_000 + 0.60 * 500 / 1_000_000
RESOURCES = [
    {"id": "A-groq-free", "model": "A", "access": "free", "available": True,
     "cash": 0.0, "reset_minutes": None},
    {"id": "B-groq-free", "model": "B", "access": "free", "available": True,
     "cash": 0.0, "reset_minutes": None},
    {"id": "D-groq-free", "model": "D", "access": "free", "available": True,
     "cash": 0.0, "reset_minutes": None},
    {"id": "A-openrouter-paid", "model": "A", "access": "tokens", "available": True,
     "cash": PAID_A_COST, "reset_minutes": None},
]


def choose(request, resources):
    """Choose an eligible TD1 route and state the risk check and evidence."""
    family = request.get("family")
    if family not in FAMILIES:
        return {"action": "abstain", "resource": None, "cash": 0,
                "checks": "manual classification required",
            "reason": "No matching TD1 family evidence exists for this request among cases C01-C20; abstain pending classification"}

    evidence = FAMILIES[family]
    cases = evidence["cases"]
    risk = request.get("use_case", "internal")
    if risk == "internal":
        checks = "none for a TD1 100%-correct route; otherwise deterministic SQL verification"
    elif risk == "customer":
        checks = "independent read-only reference SQL and value verification"
    elif risk == "payout":
        checks = "independent SQL reconciliation, source verification and human approval"
    else:
        return {"action": "abstain", "resource": None, "cash": 0,
                "checks": "manual risk classification required",
                "reason": f"Unknown business use case for {family} ({cases}); abstain"}

    eligible_models = {
        model for model, (correct, executed) in evidence["scores"].items()
        if executed > 0 and correct == executed and model not in evidence["incomplete"]
    }
    eligible = [r for r in resources if r["model"] in eligible_models]
    rank = {model: index for index, model in enumerate(PREFERENCE[family])}

    def order(resource):
        return (resource["cash"], rank.get(resource["model"], 999), resource["id"])

    def reason(resource, decision):
        correct, executed = evidence["scores"][resource["model"]]
        return (f"{decision}: TD1 {family} cells {cases}; model {resource['model']} "
                f"correct {correct}/{executed} executed; cash ${resource['cash']:.6f}/request "
                "(paid-route token envelope is an estimate); equal-price routes use the "
                "documented group preference, not public score")

    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=order)
        return {"action": "run", "resource": chosen["id"], "cash": 0,
                "checks": checks, "reason": reason(chosen, "available free capacity")}

    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"], order(r)))
        return {"action": "defer", "resource": chosen["id"], "cash": 0,
                "checks": checks,
                "reason": reason(chosen, "wait for simulated refill; recheck availability at wake-up"),
                "wake_in_minutes": chosen["reset_minutes"]}

    paid = [r for r in eligible if r["available"] and r["cash"] > 0
            and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=order)
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"],
                "checks": checks, "reason": reason(chosen, "authorized paid fallback")}

    return {"action": "abstain", "resource": None, "cash": 0,
            "checks": checks,
            "reason": f"No eligible available or deferrable route within budget/deadline; TD1 cells {cases}"}


def scenarios():
    base = {"family": "F1", "use_case": "internal", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.30}
    exhausted = [dict(r, available=False, reset_minutes=60)
                 if r["access"] == "free" else dict(r) for r in RESOURCES]
    return [
        ("simple", base, RESOURCES),
        ("complex", {**base, "family": "F1+F2+F3"}, RESOURCES),
        ("deferrable", {**base, "family": "F1+F2+F3"}, exhausted),
        ("urgent", {**base, "family": "F1+F2+F3", "can_wait": False, "deadline_minutes": 5}, exhausted),
        ("budget exhausted", {**base, "family": "F1+F2+F3", "can_wait": False, "budget": 0}, exhausted),
        ("high impact", {**base, "family": "F2", "use_case": "payout"}, RESOURCES),
        ("unknown capability", {**base, "family": "unknown"}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
