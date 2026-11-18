# Review of Pair A's work, by Pair B

Reviewer: Pair B (Haoyu Song, Sharan Raj Janakiraman). Reviewed: Pair A (Youssef Damak, Eliott Palethorpe), step 1, the k-of-n vote. Commit reviewed: `d246f83` (their last push). The checks were run on Sharan's machine, from inside `td2`.

## What we checked and how

| Check | Result |
|---|---|
| Do their tests pass? (`python -m unittest test_vote_k_sur_n`) | Yes, 13 tests pass. |
| Are the rules of the vote respected? | Yes. We read the code and the tests: n counts members that failed, only `executed` proposals with a value vote, k must be a strict majority (`n // 2 < k <= n`), a duplicate (provider, model) raises `ValueError`, and no majority returns `consensus False` with `value None`. The value `0` is treated as a real value, not as "no answer". |
| Does the vote avoid the reference? | Yes. The reference is only compared after the decision. |
| Is the 20-row table right? | Yes. We recomputed both panels (2-of-3 and 3-of-5) from `td1/traces-td1.csv` and every row matches, including the votes and the three abstentions of the 2-of-3 panel (C10, C17, C19). |
| Does the vote script give the same answer? (`python atelier-vote.py --traces ../td1/traces-td1.csv --case C09`) | Yes. 2-of-3 gives 487980 with 2 votes (gpt-oss-120b and qwen), which is the reference. |

## What we found and changed

1. **"Both a wrong consensus" was not right.** The report said a 2-of-5 vote "would have made both a wrong consensus" (C09 and C10). In both questions the correct value also gets 2 votes: on C09, 487980 x2 against 0 x2, and on C10, 558980 x2 against 119410 x2. With k = 2 that is a tie between a right and a wrong value, not a wrong consensus. Fixed: the sentence now says it is a tie that a 2-of-5 rule could only break by luck. Changed in `td2-step1-vote.md` and in `td2.md`.
2. **No script for the 20-row table.** Nothing in the repo regenerated the table. Fixed: new `scripts/vote-table.py` rebuilds the 2-of-3 and 3-of-5 columns from `td1/traces-td1.csv` with Pair A's `vote_k_sur_n`. Its 20 rows are identical to the table in `td2.md`. The command is now written under the table in both files.

## Remaining remarks (not changed)

- The step 1 text exists twice (`td2-step1-vote.md` and section 2 of `td2.md`), so a fix has to be made in both places, as we just did. One of them could link to the other.

Overall: the vote is correct and well tested, and the table is exact. We fixed one wrong sentence and added the script for the table.
