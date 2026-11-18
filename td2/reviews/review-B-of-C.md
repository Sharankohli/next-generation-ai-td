# Review of Pair C's work, by Pair B

Reviewer: Pair B (Haoyu Song, Sharan Raj Janakiraman). Reviewed: Pair C (Xinyu Zhu, Ismael Charni), step 3, the routing rule. Commit reviewed: `d246f83` (their last push). The checks were run on Sharan's machine, from inside `td2`.

## What we checked and how

| Check | Result |
|---|---|
| Do their tests pass? (`python -m unittest test_routing`) | Yes, 6 tests pass. |
| Are the per-family rates right? (`python scripts/analyze-routing.py`) | Yes. Every correct / executed number in the table of `routing-rule.md` matches the script (see remark 1 for qwen). |
| Is `routing-before.txt` the original simulator? | Yes. It is exactly the output of `atelier-routage-original.py`. |
| Is `routing-after.txt` the adapted simulator? | Yes. It is exactly the output of `atelier-routage.py`. |
| Are the prices right? | Yes. We compared with `td1/portefeuille-modeles-2026-09-28.csv`: Groq gpt-oss-120b, gpt-oss-20b and qwen are free, and the paid OpenRouter route of gpt-oss-120b is 0.15 / 0.60 per million tokens. The estimate of $0.00045 per request is correct for 1,000 input and 500 output tokens. |
| Consistency constraint ("none" only for a low-stakes dashboard and a family where the model was 100% correct) | Respected. In `choose()` a model is only eligible if it is 100% correct and fully executed on the family. Customer figures use a reference SQL check and payouts use reconciliation plus human approval. |
| Does each decision in the simulator have a reason? | Yes, each decision carries a reason string with the cases behind it. |

## What we found and changed

Nothing. We did not edit Pair C's files; every point is listed below for them to fix.

## Remaining remarks (not changed)

1. **Qwen's denominator.** The table counts qwen as 5/5 on period questions and 0/1 on the C17 and C19 group, because it leaves out the two HTTP 429 cells. The assignment asks for the exact `correct / cases` ratio, which would be 5/6 and 0/2. The footnote explains it, but the rule should say which ratio it uses.
2. **The tie-break.** All the free Groq routes cost 0, so the first model comes from "Pair C preference", which is a hand-written list in `atelier-routage.py`. Say how it was chosen.
3. **Small samples.** Families with one TD 1 question (C10, C15, C16, C18) are weak evidence. For example B is first for C10 because of a 1/1 result, and A is also 1/1. The order there is a preference, not proof.
4. **The subscription priority.** The adapted simulator has no subscription route, so the priority analysis covers the original `choose()` only. The reason is fair (the portfolio lists none for these models), but the rule should say plainly that this part is not simulated.
5. **A leftover file.** `atelier-routage-pair-c-before-adaptation.py` gives an output different from `routing-before.txt`, so its name is misleading. Remove it or say what it is.
6. **Scores typed by hand.** The family scores are written directly in `atelier-routage.py`. They are correct today, but nothing reads them from the traces, so they could drift.

Overall: the rates are exact, the code and the outputs agree, and the checking rule follows the error costs. The remarks are about explanation, not about results.
