# TD 2: the quorum, then the routing rule

Session of 18 November 2026. Assignment: [enonce-td2-en.md](enonce-td2-en.md) ([html](enonce-td2-en.html), [pdf](enonce-td2-en.pdf)). Main index: [../README.md](../README.md). No network call: everything works from the stored TD 1 results in [../td1](../td1).

| Step | Pair | Work | Where |
|---|---|---|---|
| 1. The k-of-n vote | A | `vote_k_sur_n`, 13 tests, 20-question table (2-of-3 against 3-of-5) | [reports/td2-step1-vote.md](reports/td2-step1-vote.md) |
| 2. The wrong consensus | B | C09: cohere and dots both return 0, with the delta query | [reports/td2.md](reports/td2.md), [reports/group-b/](reports/group-b/) |
| 3. The routing rule | C | One rule per question family, adapted simulator, priority analysis | [reports/group-c/routing-rule.md](reports/group-c/routing-rule.md), [reports/group-c/priority-analysis.md](reports/group-c/priority-analysis.md) |

## Routing policies

The policy decides, for each question family, which model runs first, how its answer is checked, and what happens when it is unavailable. The source of truth is [reports/group-c/routing-rule.md](reports/group-c/routing-rule.md). It is built on the exact TD 1 results per family (correct / executed cases per model), not on estimates.

**Latest policy** (Pair C, commit `024b2d4`, implemented in `atelier-routage.py`):

| Family (TD 1 cells) | First model | Next free model |
|---|---|---|
| Period (C01, C04 to C07, C20) | A (gpt-oss-120b) | B (gpt-oss-20b) |
| Age at a date (C02, C08, C09, C11) | A | D (qwen3.8-27b) |
| Age at the order (C10) | B | A |
| Product list (C03, C12 to C14) | A | B |
| Period + age (C15) | B | A |
| Age + product (C16) | A | B |
| Period + age + product (C17, C19) | A | B |
| Period + age at the order (C18) | B | A |

**Checking depends on what the figure is used for:**

| Use | Check |
|---|---|
| Internal dashboard | One eligible free model, no quorum. The executed SQL and value are kept for audit. |
| Figure shown to a customer | Compare with an independent read-only reference SQL. |
| Payout | Reconcile with the source rows and require human approval. |

**Fallback:** try the next free model; if none is available and the deadline allows, defer to a quota refill and check again that capacity is really there; otherwise use the paid route (A on OpenRouter) only within the authorised budget; otherwise abstain. A failed verification also means defer or abstain.

Limits: C and E have no price row in the portfolio, so the rule makes no claim about their routes. Quotas and refill times in the simulator are synthetic, not measured.

**How the policy changed during TD 2:**

| Version | File | Output |
|---|---|---|
| Original simulator (three fictitious resources) | `atelier-routage-original.py` | [routing-before.txt](routing-before.txt) |
| Pair C, before adaptation | `atelier-routage-pair-c-before-adaptation.py` | |
| Latest (our models, TD 1 family results, portfolio prices) | `atelier-routage.py` | [routing-after.txt](routing-after.txt) |

## Files

| File | Role |
|---|---|
| `skeleton-multi-llm-en.py` | The orchestrator skeleton with `Orchestrateur.vote_k_sur_n` completed (step 1). It finds the database, schema, sandbox, questions and models in `../td1`. |
| `test_vote_k_sur_n.py` | 13 unit tests for the vote, written before the code. |
| `atelier-vote.py` | Runs the vote on four synthetic examples, or on the stored traces of one question. |
| `atelier-routage.py` | The routing simulator, adapted to our rule (step 3). |
| `test_routing.py` | 6 tests for the adapted routing rule. |
| `scripts/analyse-group-b.py` | Replays stored SQL read-only and regenerates the wrong-consensus evidence (step 2). |
| `scripts/analyze-routing.py` | Computes the per-family rates for the routing rule (step 3). |
| `reports/` | The session reports, one section per step (see the table above). |

## Commands

```bash
cd td2
python3 -m unittest test_vote_k_sur_n -v                          # the vote tests
python3 -m unittest test_routing -v                               # the routing tests
python3 atelier-vote.py                                           # four synthetic examples
python3 atelier-vote.py --traces ../td1/traces-td1.csv --case C02 # real traces of one question
python3 atelier-routage.py                                        # the seven routing scenarios
python3 atelier-routage.py --scenario deferrable                  # one scenario
```

## Inputs from TD 1

`../td1/traces-td1.csv` (merged traces), `../td1/reference-td1.csv` (our references), `../td1/data/boutique.sqlite` (the database, never modified).
