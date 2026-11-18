# TD 2: the quorum, then the routing rule

Session of 18 November 2026. Assignment: [enonce-td2-en.md](enonce-td2-en.md) ([html](enonce-td2-en.html), [pdf](enonce-td2-en.pdf)). Main index: [../README.md](../README.md). No network call: everything works from the stored TD 1 results in [../td1](../td1).

## Files

| File | Role |
|---|---|
| `skeleton-multi-llm-en.py` | The orchestrator skeleton with `Orchestrateur.vote_k_sur_n` completed (step 1). It finds the database, schema, sandbox, questions and models in `../td1`. |
| `test_vote_k_sur_n.py` | 13 unit tests for the vote, written before the code. |
| `atelier-vote.py` | Runs the vote on four synthetic examples, or on the stored traces of one question. |
| `atelier-routage.py` | The routing simulator, to adapt to our rule (step 3). |
| `scripts/analyse-group-b.py` | Replays stored SQL read-only and regenerates the wrong-consensus evidence (step 2). |
| `reports/td2.md` | The session report. |
| `reports/td2-step1-vote.md` | Step 1: the 20-question table, 2-of-3 against 3-of-5, with commentary. |
| `reports/group-b/` | Step 2 evidence: delta rows, diagnostic SQL, results. |

## Commands

```bash
cd td2
python3 -m unittest test_vote_k_sur_n -v                          # the vote tests
python3 atelier-vote.py                                           # four synthetic examples
python3 atelier-vote.py --traces ../td1/traces-td1.csv --case C02 # real traces of one question
python3 atelier-routage.py                                        # the seven routing scenarios
python3 atelier-routage.py --scenario deferrable                  # one scenario
```

## Inputs from TD 1

`../td1/traces-td1.csv` (merged traces), `../td1/reference-td1.csv` (our references), `../td1/data/boutique.sqlite` (the database, never modified).
