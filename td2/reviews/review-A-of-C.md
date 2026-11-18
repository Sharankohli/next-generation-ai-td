# Review of Pair C's work, by Pair A

Reviewer: Pair A (Youssef Damak, Eliott Palethorpe). Reviewed: Pair C (Xinyu Zhu, Ismael Charni), step 3, the routing rule. Commit reviewed: `024b2d4`. The checks were run on Youssef's machine with Claude's help.

## What we checked and how

| Check | Result |
|---|---|
| Are the per-family rates right? | Yes. We recomputed correct / cases per model from `td1/traces-td1.csv` (last attempt per cell) and every family matches their table (the only difference is how qwen is counted, see remark 1): age at a date (C02, C08, C09, C11) is 4/4 for gpt-oss-120b and qwen, 2/4 for gpt-oss-20b, 0/4 for cohere and dots; C15, C16, C18 and the C17 and C19 group also match. |
| Do their tests pass? | Yes, `python3 -m unittest test_routing`: 6 tests pass. |
| Is `routing-before.txt` the original simulator? | Yes. It is exactly the output of `atelier-routage-original.py`. |
| Is `routing-after.txt` the adapted simulator? | Yes. It is exactly the output of `atelier-routage.py`. |
| Consistency constraint ("none" only for a low-stakes dashboard and a family where the model was 100% correct) | Respected. For the dashboard the first model of every family has a perfect score on that family in TD 1. Customer figures use a reference-SQL check and payouts use reconciliation plus human approval. |
| Does each decision in the simulator have a reason? | Yes, each decision carries a reason string and the cases behind it. |

## Remarks (to be defended by Pair C)

1. **Qwen's denominator.** The table counts qwen as 5/5 on period questions and 0/1 on the C17 and C19 group, because it leaves out the two HTTP 429 cells (C17, C20). The assignment asks for the exact `correct / cases` ratio, which would be 5/6 and 0/2. The footnote explains it, but the report should state which one it uses.
2. **The subscription priority.** The assignment asks why `choose` runs an immediately available subscription before deferring for an exhausted free resource. The adapted simulator has no subscription resource, because the portfolio lists none for these models. The priority analysis therefore covers the original `choose`. That is a reasoned choice, and they must be ready to say it.
3. **"First model = cheapest."** All Groq routes cost 0, so the first model comes from a tie broken by "Pair C preference". Say what that preference is (for instance, the smaller model when it is 100% correct on the family).

Overall: the rates are exact, the code and the outputs agree, and the checking rule follows the error costs.
