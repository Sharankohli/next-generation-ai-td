#!/usr/bin/env python3
"""TD2 Pair C: evidence-based routing simulator (no API calls or keys).

Model/family evidence comes from the team's TD1 C01-C20 traces. 20 cases
support batch-specific observations, not guaranteed future correctness.
Availability, quotas and the token envelope below are simulated.
"""
import argparse
import json

# Each ratio is correct/executed; D did not execute C17 and C20.
FAMILIES = {
    "F1": {"cases": "C01,C04,C05,C06,C07,C20", "scores": {"A": (6, 6), "B": (6, 6), "C": (6, 6), "D": (5, 5), "E": (6, 6)}, "incomplete": ("D",)},
    "F2": {"cases": "C02,C08,C09,C11", "scores": {"A": (4, 4), "B": (2, 4), "C": (0, 4), "D": (4, 4), "E": (0, 4)}, "incomplete": ()},
    "F2b": {"cases": "C10", "scores": {"A": (1, 1), "B": (1, 1), "C": (0, 1), "D": (0, 1), "E": (0, 1)}, "incomplete": ()},
    "F3": {"cases": "C03,C12,C13,C14", "scores": {"A": (4, 4), "B": (4, 4), "C": (4, 4), "D": (4, 4), "E": (4, 4)}, "incomplete": ()},
    "F1+F2": {"cases": "C15", "scores": {"A": (1, 1), "B": (1, 1), "C": (1, 1), "D": (0, 1), "E": (1, 1)}, "incomplete": ()},
    "F2+F3": {"cases": "C16", "scores": {"A": (1, 1), "B": (1, 1), "C": (0, 1), "D": (1, 1), "E": (1, 1)}, "incomplete": ()},
    "F1+F2+F3": {"cases": "C17,C19", "scores": {"A": (2, 2), "B": (2, 2), "C": (0, 2), "D": (0, 1), "E": (0, 2)}, "incomplete": ("D",)},
    "F1+F2b": {"cases": "C18", "scores": {"A": (1, 1), "B": (1, 1), "C": (1, 1), "D": (1, 1), "E": (0, 1)}, "incomplete": ()},
}

# Tie-break among zero-cash, fully correct routes: documented TD1 preference.
# C and E were free in TD1 traces, but are not priced in the supplied portfolio.
PREFERENCE = {
    "F1": ["C", "A", "B", "E", "D"],
    "F2": ["A", "D"],
    "F2b": ["B", "A"],
    "F3": ["C", "A", "B", "D", "E"],
    "F1+F2": ["B", "A", "C", "E"],
    "F2+F3": ["A", "B", "D", "E"],
    "F1+F2+F3": ["A", "B"],
    "F1+F2b": ["B", "A", "C", "D"],
}

# Paid A route: portfolio USD 0.15/M input + USD 0.60/M output.
# ASSUMED fixed envelope: 1000 input + 500 output tokens/request.
PAID_A_COST = 0.15 * 1000 / 1_000_000 + 0.60 * 500 / 1_000_000
RESOURCES = [
    {"id": "A-groq-free", "model": "A", "access": "free", "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "B-groq-free", "model": "B", "access": "free", "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "C-openrouter-free", "model": "C", "access": "free", "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "D-groq-free", "model": "D", "access": "free", "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "E-openrouter-free", "model": "E", "access": "free", "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "A-openrouter-paid", "model": "A", "access": "tokens", "available": True, "cash": PAID_A_COST, "allocation": PAID_A_COST, "reset_minutes": None},
]


def choose(request, resources):
    """Select by TD1 family evidence, simulated availability, risk and budget."""
    family = request.get("family")
    if family not in FAMILIES:
        return {"action": "abstain", "resource": None, "cash": 0,
                "checks": "manual classification required",
                "reason": "No matching TD1 family among C01-C20; abstain until classified"}

    evidence = FAMILIES[family]
    cases = evidence["cases"]
    risk = request.get("use_case", "internal")
    if risk == "internal":
        checks = "none only for TD1 100%-correct family; otherwise deterministic SQL check"
    elif risk == "customer":
        checks = "deterministic read-only SQL execution and value verification"
    elif risk == "payout":
        checks = "deterministic SQL reconciliation, source verification and human approval"
    else:
        return {"action": "abstain", "resource": None, "cash": 0,
                "checks": "manual risk classification required",
                "reason": f"Unknown business use case for {family} ({cases}); abstain"}

    # An eligible model was correct on every executed case in this family AND
    # has no unexecuted cases in that family. This is not a future guarantee.
    eligible_models = {
        model for model, (correct, executed) in evidence["scores"].items()
        if executed > 0 and correct == executed and model not in evidence["incomplete"]
    }
    eligible = [r for r in resources if r["model"] in eligible_models]
    rank = {model: i for i, model in enumerate(PREFERENCE[family])}
    def order(r):
        return (r["cash"], rank.get(r["model"], 999), r["allocation"], r["id"])
    def reason(r, decision):
        c, n = evidence["scores"][r["model"]]
        return (f"{decision}: {family} TD1 cells {cases}; model {r['model']} "
                f"correct {c}/{n} executed, complete coverage; "
                f"cash ${r['cash']:.6f}/request (simulated token envelope); "
                "zero-cash ties use documented preference, not public score")

    # Existing zero-cash capacity is used before waiting; this avoids delay.
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=order)
        return {"action": "run", "resource": chosen["id"], "cash": 0,
                "checks": checks, "reason": reason(chosen, "available included capacity")}

    # Waiting is considered before newly paid tokens when the deadline permits.
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"], order(r)))
        return {"action": "defer", "resource": chosen["id"], "cash": 0,
                "checks": checks,
                "reason": reason(chosen, "wait for simulated quota reset; recheck at wake-up"),
                "wake_in_minutes": chosen["reset_minutes"]}

    paid = [r for r in eligible if r["available"] and r["cash"] > 0
            and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=order)
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"],
                "checks": checks, "reason": reason(chosen, "authorized paid fallback")}

    return {"action": "abstain", "resource": None, "cash": 0,
            "checks": checks,
            "reason": f"No eligible available or deferrable route within budget/deadline for {family}; TD1 cells {cases}"}


def scenarios():
    base = {"family": "F1", "use_case": "internal", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.30}
    # Exhaust every free route to exercise deferral, paid fallback and abstention.
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
