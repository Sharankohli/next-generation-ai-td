# TD2, Step 1 (Pair A): the k-of-n vote

Draft section for `reports/td2.md`. Pair A. Everything below comes from the stored TD1 traces (`traces-td1.csv`, all `nature = real`), no new network call. Vote code: `Orchestrateur.vote_k_sur_n` in `skeleton-multi-llm-en.py`. Tests: `test_vote_k_sur_n.py` (13 tests, written first and seen failing before the code existed).

## How the vote works

- n is the size of the panel, errors included. Only `executed` proposals that have a value cast a vote. A 429 or a rejected SQL stays in n but votes for nothing.
- k has to be a strict majority: `n // 2 < k <= n`, else `ValueError`. Two proposals from the same (provider, model) also raise `ValueError`.
- A value with at least k votes wins. Since 2k > n, two different values can never both reach k, so there is no tie to break.
- If nobody reaches k the vote abstains: `consensus False`, `value None`, `votes` = the biggest count. It never picks a "best guess".
- The vote never sees the reference. We compare to `reference-td1.csv` after the decision.
- `0` is a real value (several TD1 answers are 0 cents), so the code tests `value is not None`, never `if value`.

## 20 questions, 2-of-3 vs 3-of-5

2-of-3 panel (k = 2): gpt-oss-120b, cohere north-mini-code, qwen3.8-27b. 3-of-5 (k = 3): those three plus gpt-oss-20b and dots-3-note-preview. Values in cents excl. VAT. "votes" is the size of the winning group, or the biggest group when it abstains.

| Q | Reference | 2-of-3 | 3-of-5 | Same decision? |
|---|---|---|---|---|
| C01 | 792800 | 792800 (3 votes) | 792800 (5) | yes |
| C02 | 590320 | 590320 (2) | abstain (2) | **no** |
| C03 | 936350 | 936350 (3) | 936350 (5) | yes |
| C04 | 2826250 | 2826250 (3) | 2826250 (5) | yes |
| C05 | 38480 | 38480 (3) | 38480 (5) | yes |
| C06 | 0 | 0 (3) | 0 (5) | yes |
| C07 | 13970 | 13970 (3) | 13970 (5) | yes |
| C08 | 605580 | 605580 (2) | 605580 (3) | yes |
| C09 | 487980 | 487980 (2) | abstain (2) | **no** |
| C10 | 558980 | abstain (1) | abstain (2) | yes, both abstain |
| C11 | 446690 | 446690 (2) | 446690 (3) | yes |
| C12 | 1666490 | 1666490 (3) | 1666490 (5) | yes |
| C13 | 107740 | 107740 (3) | 107740 (5) | yes |
| C14 | 0 | 0 (3) | 0 (5) | yes |
| C15 | 168680 | 168680 (2) | 168680 (4) | yes |
| C16 | 376740 | 376740 (2) | 376740 (4) | yes |
| C17 | 258180 | abstain (1) | abstain (2) | yes, both abstain |
| C18 | 62480 | 62480 (3) | 62480 (4) | yes |
| C19 | 1990 | abstain (1) | abstain (2) | yes, both abstain |
| C20 | 1106090 | 1106090 (2) | 1106090 (4) | yes |

Agreement with the reference: **2-of-3 reaches a consensus on 17 questions and all 17 equal the reference, it abstains on 3 (C10, C17, C19). 3-of-5 reaches a consensus on 15 and all 15 equal the reference, it abstains on 5 (C02, C09, C10, C17, C19).** Neither vote returned a wrong value on these traces.

## Where the decision changes (C02 and C09)

- **C02** (reference 590320). 2-of-3: 120b and qwen both return 590320, cohere returns 0 (incorrect), so 590320 gets 2 of 2 needed. 3-of-5: the two extra models are wrong and different: 20b returns 362580 and dots returns 135000. The correct value still has only 2 votes and k is now 3, so the vote abstains. The two extra voters did not add a confirming vote, they just raised the bar.
- **C09** (reference 487980). 2-of-3: 120b and qwen return 487980, cohere returns 0, so 2 votes, consensus. 3-of-5: 20b adds 369240 (incorrect) and dots adds 0 (incorrect). Now 487980 has 2 votes, 0 also has 2 votes (cohere and dots), and k = 3, so nothing wins and it abstains. The wrong 0 was one vote short of a wrong consensus.

## Where the decision does not change but the votes do

- **C08 and C11:** dots returned `sql_rejected` (no value), so it stays in n = 5 with no vote. The three correct models (120b, 20b, qwen) give exactly the 3 votes needed. Cohere is wrong (1553040 on C08, 0 on C11) and is outvoted.
- **C15, C16, C18, C20:** 3-of-5 has more correct voters (4 votes) than the 2-of-3 (2 or 3).
- **C20 and C17:** qwen got a 429 (`not_executed`). On C20 the 2-of-3 still wins with 120b and cohere (2 of 2 needed), since the missing member stays in n=3 but k=2 is still reachable. On C17 the same missing qwen leaves 2-of-3 with only 120b correct (cohere returned 197080), so it abstains with 1 vote. The 3-of-5 also abstains on C17: 120b and 20b agree on 258180 (2 votes), dots returns 822540, so 2 < 3.
- **C10 and C19:** 120b is correct on both, but alone. On C10 qwen returns 119410, cohere 0, so 2-of-3 abstains. 3-of-5 abstains too (558980 x2 vs 119410 x2, qwen and dots). On C19 qwen 83580, cohere 13930, dots 71640, so all three are scattered and only 120b and 20b agree on 1990, which is 2 < 3. Abstaining is the right behaviour here: the vote cannot tell which lone answer is the correct one.

## Wrong values shared by two models (to hand to Pair B)

These never reached k in either vote, but they are shared wrong values:
- **C09:** cohere and dots both return 0 (reference 487980).
- **C10:** qwen and dots both return 119410 (reference 558980).

A 2-of-5 vote would have made both a wrong consensus. This is the argument for k > half, and for keeping the fixed panel to models that are not in the same family.

## Limits

- Only one run per model and question (temperature 0), so this says nothing about run-to-run variance.
- With 2-of-3 and one member down (429), the vote needs both remaining members to agree, which is why availability matters as much as accuracy.
- Verdicts used to decide whether a trace is a valid vote (`correct` or `incorrect`, with a value) come from the TD1 trace columns; the vote itself ignores the verdict and the reference.