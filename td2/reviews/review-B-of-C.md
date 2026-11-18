# Review of Pair C's work, by Pair B

Reviewer: Pair B (Haoyu Song, Sharan Raj Janakiraman). Reviewed: Pair C (Zinyu Zhu, Ismael Charni), step 3, the routing rule. Commit reviewed: `d246f83` (their last push). The checks were run on Sharan's machine, from inside `td2`.

## What we checked and how

| Check | Result |
|---|---|
| Do their tests pass? (`python -m unittest test_routing`) | Yes, 6 tests pass. |
| Are the per-family rates right? (`python scripts/analyze-routing.py`) | Yes. Every correct / executed number in the table of `routing-rule.md` matches the script (see the first point below for qwen). |
| Is `routing-before.txt` the original simulator? | Yes. It is exactly the output of `atelier-routage-original.py`. |
| Is `routing-after.txt` the adapted simulator? | Yes. It is exactly the output of `atelier-routage.py`. |
| Are the prices right? | Yes. We compared with `td1/portefeuille-modeles-2026-09-28.csv`: Groq gpt-oss-120b, gpt-oss-20b and qwen are free, and the paid OpenRouter route of gpt-oss-120b is 0.15 / 0.60 per million tokens. The estimate of $0.00045 per request is correct for 1,000 input and 500 output tokens. |
| Consistency constraint ("none" only for a low-stakes dashboard and a family where the model was 100% correct) | Respected. In `choose()` a model is only eligible if it is 100% correct and fully executed on the family. Customer figures use a reference SQL check and payouts use reconciliation plus human approval. |
| Does each decision in the simulator have a reason? | Yes, each decision carries a reason string with the cases behind it. |

## What we found and changed

1. **Qwen's denominator was not stated.** The table counts qwen as 5/5 on period questions and 0/1 on the C17 and C19 group, because it leaves out the two HTTP 429 cells. The assignment asks for the exact `correct / cases` ratio. Fixed: `routing-rule.md` now says that over all cases qwen is 5/6 and 0/2, that the rule uses correct / executed, and that qwen is excluded for both families either way.
2. **Weak evidence was not flagged.** Families with one TD 1 question (C10, C15, C16, C18) give weak evidence: B is first for C10 because of a 1/1 result, and A is also 1/1. Fixed: `routing-rule.md` now says the order there is a preference, not proof.
3. **The subscription priority was not simulated.** The adapted simulator has no subscription route, so the priority analysis covers the original `choose()` only. The reason is fair (the portfolio lists none for these models). Fixed: `routing-rule.md` now says so plainly and points to `priority-analysis.md`.

## Remaining remarks (not changed)

1. **The tie-break.** All the free Groq routes cost 0, so the first model comes from "Pair C preference", which is a hand-written list in `atelier-routage.py`. Pair C must say how it was chosen. We could not do this for them.
2. **A leftover file.** `atelier-routage-pair-c-before-adaptation.py` gives an output different from `routing-before.txt`, so its name is misleading. Remove it or say what it is.
3. **Scores typed by hand.** The family scores are written directly in `atelier-routage.py`. They are correct today, but nothing reads them from the traces, so they could drift.

Overall: the rates are exact, the code and the outputs agree, and the checking rule follows the error costs. We fixed three points of explanation; three remain for Pair C.
