# TD2 report: the quorum, then the routing rule

Sub-group 4 (DIA 1), session of 18 November 2026. Everything here comes from the stored TD 1 results ([traces](../../td1/traces-td1.csv), [references](../../td1/reference-td1.csv), [database](../../td1/data/boutique.sqlite)). No new network call was made. Our TD 1 report is [here](../../td1/reports/td1.md).

## 1. Work attempted and completed

| Step | Pair | Attempted | Completed |
|---|---|---|---|
| 1. The k-of-n vote | A | `Orchestrateur.vote_k_sur_n` and the 20-question table, 2-of-3 against 3-of-5 | Yes. 13 tests written first, all pass. Table in section 2. |
| 2. The wrong consensus | B | Find two models with the same wrong value, isolate the SQL fault, write the delta query | Yes, on our own case C09 (not the fallback). Section 3. |
| 3. The routing rule | C | One rule per question family from the exact TD 1 rates, adapted simulator, priority analysis | Yes. Section 4. |

## 2. Step 1 (Pair A): the k-of-n vote

### How the vote works

- n is the size of the panel, errors included. Only `executed` proposals that have a value cast a vote. A 429 or a rejected SQL stays in n but votes for nothing.
- k has to be a strict majority: `n // 2 < k <= n`, else `ValueError`. Two proposals from the same (provider, model) also raise `ValueError`.
- A value with at least k votes wins. Since 2k > n, two different values can never both reach k, so there is no tie to break.
- If nobody reaches k the vote abstains: `consensus False`, `value None`, `votes` = the biggest count. It never picks a "best guess".
- The vote never sees the reference. We compare to `reference-td1.csv` after the decision.
- `0` is a real value (several TD1 answers are 0 cents), so the code tests `value is not None`, never `if value`.

### 20 questions, 2-of-3 vs 3-of-5

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

### Where the decision changes (C02 and C09)

- **C02** (reference 590320). 2-of-3: 120b and qwen both return 590320, cohere returns 0 (incorrect), so 590320 gets 2 of 2 needed. 3-of-5: the two extra models are wrong and different: 20b returns 362580 and dots returns 135000. The correct value still has only 2 votes and k is now 3, so the vote abstains. The two extra voters did not add a confirming vote, they just raised the bar.
- **C09** (reference 487980). 2-of-3: 120b and qwen return 487980, cohere returns 0, so 2 votes, consensus. 3-of-5: 20b adds 369240 (incorrect) and dots adds 0 (incorrect). Now 487980 has 2 votes, 0 also has 2 votes (cohere and dots), and k = 3, so nothing wins and it abstains. The wrong 0 was one vote short of a wrong consensus.

### Where the decision does not change but the votes do

- **C08 and C11:** dots returned `sql_rejected` (no value), so it stays in n = 5 with no vote. The three correct models (120b, 20b, qwen) give exactly the 3 votes needed. Cohere is wrong (1553040 on C08, 0 on C11) and is outvoted.
- **C15, C16, C18, C20:** 3-of-5 has more correct voters (4 votes) than the 2-of-3 (2 or 3).
- **C20 and C17:** qwen got a 429 (`not_executed`). On C20 the 2-of-3 still wins with 120b and cohere (2 of 2 needed), since the missing member stays in n=3 but k=2 is still reachable. On C17 the same missing qwen leaves 2-of-3 with only 120b correct (cohere returned 197080), so it abstains with 1 vote. The 3-of-5 also abstains on C17: 120b and 20b agree on 258180 (2 votes), dots returns 822540, so 2 < 3.
- **C10 and C19:** 120b is correct on both, but alone. On C10 qwen returns 119410, cohere 0, so 2-of-3 abstains. 3-of-5 abstains too (558980 x2 vs 119410 x2, qwen and dots). On C19 qwen 83580, cohere 13930, dots 71640, so all three are scattered and only 120b and 20b agree on 1990, which is 2 < 3. Abstaining is the right behaviour here: the vote cannot tell which lone answer is the correct one.

### Wrong values shared by two models (C09 is analysed in section 3)

These never reached k in either vote, but they are shared wrong values:
- **C09:** cohere and dots both return 0 (reference 487980).
- **C10:** qwen and dots both return 119410 (reference 558980).

A 2-of-5 vote would have made both a wrong consensus. This is the argument for k > half, and for keeping the fixed panel to models that are not in the same family.

### Limits

- Only one run per model and question (temperature 0), so this says nothing about run-to-run variance.
- With 2-of-3 and one member down (429), the vote needs both remaining members to agree, which is why availability matters as much as accuracy.
- Verdicts used to decide whether a trace is a valid vote (`correct` or `incorrect`, with a value) come from the TD1 trace columns; the vote itself ignores the verdict and the reference.

## 3. Step 2 (Pair B): a wrong value shared by two models on C09

### Source and scope

This is an observed TD1 case, not a synthetic or historical example. We examined the latest attempt for each of the 100 question/model cells in the team’s merged `traces-td1.csv` at TD1 commit `7defca1`. Qwen contains retries; the last CSV record for a cell is retained, not counted as another model. C09 and C10 contain shared incorrect values in this scan; this report analyses C09. No network calls were made.

C09 asks for total revenue excluding VAT, in euro cents, across all orders of customers aged exactly 25 on **2026-09-26**. The independent reference in `reference-td1.csv` is **487,980 cents (€4,879.80)**, reproduced on `data/boutique.sqlite`.

### Identification and declared quorum results

| Model | Source | Value (cents) | Stored verdict | Fixed panel member |
|---|---|---:|---|---|
| openai/gpt-oss-120b | traces-td1.csv | 487980 | correct | yes |
| openai/gpt-oss-20b | traces-td1.csv | 369240 | incorrect | no |
| cohere/north-mini-code:free | traces-td1.csv | 0 | incorrect | yes |
| qwen/qwen3.8-27b | traces-td1.csv | 487980 | correct | yes |
| dots-studio/dots-3-note-preview:free | traces-td1.csv | 0 | incorrect | no |

- Fixed **2-of-3**, k=2: GPT-OSS-120B and Qwen return 487980; Cohere returns 0 → consensus **487980**, two votes, correct.
- Full **3-of-5**, k=3: two votes for 487980, two for 0, one for 369240 → **abstention**, maximum two votes. The shared wrong value does not reach either declared quorum.

These are manual counts from the stored values, independently checked by the evidence script. They do not claim validation of Group A's `vote_k_sur_n`. The vote sees execution success and integer values, not the reference or correctness verdict; `correct` and `incorrect` here both denote successfully executed SQL. Adding Dots adds support for the shared wrong value, causing the larger quorum to abstain. GPT-OSS-20B also errs, but its different value does not support the zero consensus.

### Faulty SQL and root causes

#### cohere/north-mini-code:free

Original complete SQL from `traces-td1.csv`:

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
  -- Compute age on 2026-09-26
  (
    -- Age = year difference
    CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) +
    -- Adjust if birthday hasn't occurred yet this year
    CASE
      WHEN SUBSTR(c.birth_date, 6, 2) > '09' THEN -1
      WHEN SUBSTR(c.birth_date, 6, 2) = '09' AND SUBSTR(c.birth_date, 9, 2) > '26' THEN -1
      ELSE 0
    END
  ) = 25;
```

The expression starts with the birth year (around 2000/2001), then subtracts at most one, and compares that number with 25. It omits `2026 - birth_year`. No customer passes; the empty SUM becomes zero through COALESCE.

#### dots-studio/dots-3-note-preview:free

Original complete SQL from `traces-td1.csv`:

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
    (c.birth_date IS NOT NULL)
    AND (
        CAST(strftime('%Y', '2026-09-26') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 25
        AND (
            CAST(strftime('%m', c.birth_date) AS INTEGER) < 9
            OR (CAST(strftime('%m', c.birth_date) AS INTEGER) = 9 AND CAST(strftime('%d', c.birth_date) AS INTEGER) <= 26)
        )
        AND (
            CAST(strftime('%m', c.birth_date) AS INTEGER) > 9
            OR (CAST(strftime('%m', c.birth_date) AS INTEGER) = 9 AND CAST(strftime('%d', c.birth_date) AS INTEGER) > 26)
        )
    );
```

The first birthday condition requires month/day <= September 26, while the second simultaneously requires month/day > September 26. They cannot both hold. Its year-difference condition alone would also miss some customers born in late 2000 who are still 25.

### Independent check and exact delta

Being 25 on 2026-09-26 means **2000-09-26 < birth_date <= 2001-09-26**. The older endpoint is excluded because that customer has turned 26; the younger endpoint is included because that customer has just turned 25. All their orders count, with no order-date restriction.

The saved reference uses this birth-date window. We independently recomputed completed age as year difference minus one if the birthday has not occurred, then aggregated integer `quantity_product * price`. Both methods return 487,980 cents.

Independent query:

```sql
SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c JOIN orders o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE ((2026 - CAST(strftime('%Y', c.birth_date) AS INTEGER)) - ('09-26' < strftime('%m-%d', c.birth_date))) = 25
GROUP BY c.customer_id, c.birth_date ORDER BY c.customer_id;
```

For each faulty query, `c09-diagnostic.sql` also executes the independent age condition AND NOT that model's original WHERE predicate. Each returns exactly the same omitted customers:

| customer_id | birth_date | Order revenue excluding VAT (cents) |
|---|---|---:|
| C001 | 2001-09-25 | 135000 |
| C002 | 2001-09-24 | 25920 |
| C003 | 2001-09-26 | 47900 |
| C007 | 2000-11-30 | 118740 |
| C008 | 2001-05-15 | 99090 |
| C009 | 2001-03-10 | 61330 |

**Sum: 487,980 cents = reference 487,980 − faulty output 0.** Thus the row-level diagnostic accounts for the entire discrepancy for each of the two queries. All five stored model SQL statements were replayed, including GPT-OSS-20B's distinct incorrect result, and matched their recorded values.

### Consequence for checking and limitations

Two models can agree on a wrong value even when their SQL mistakes differ. Here the fixed 2-of-3 panel returns the correct value, while the 3-of-5 quorum abstains. The shared wrong value is not a winning majority under either declared panel. Customer-visible or payout amounts therefore need an independent deterministic check of the age predicate and revenue calculation; a larger quorum alone is insufficient evidence of correctness. This single observed case does not establish a general quorum error rate.

**Cross-check by Pair A.** Running our completed `vote_k_sur_n` on the stored C09 traces (`python3 atelier-vote.py --traces ../td1/traces-td1.csv --case C09`) gives the same declared 2-of-3 result: 487980 with two votes. The 3-of-5 vote abstains with two votes at most, as counted by hand above.

Evidence: [faulty and reference SQL](group-b/c09-diagnostic.sql), [exact rows](group-b/c09-delta.csv), [recorded inputs and checks](group-b/c09-results.json). Reproduce with `python3 scripts/analyse-group-b.py` from the `td2` folder (standard library only, SQLite opened read-only). It rewrites `group-b/report-group-b.md`, the original Group B text, not this file.

## 4. Step 3 (Pair C): the routing rule

Full rule: [group-c/routing-rule.md](group-c/routing-rule.md). Priority analysis: [group-c/priority-analysis.md](group-c/priority-analysis.md). Simulator output before ([routing-before.txt](../routing-before.txt), the original three fictitious resources) and after adaptation ([routing-after.txt](../routing-after.txt)). Code: [atelier-routage.py](../atelier-routage.py), tests: [test_routing.py](../test_routing.py) (6 pass).

**Rates.** For each family the rule uses the exact TD 1 result per model (correct / executed cases). Age-at-a-date questions (C02, C08, C09, C11) are the hard family: gpt-oss-120b and qwen get 4/4, gpt-oss-20b 2/4, cohere and dots 0/4. Period and product questions are easy for every model.

| Family (TD 1 cells) | First model | Next free model |
|---|---|---|
| Period (C01, C04 to C07, C20) | gpt-oss-120b | gpt-oss-20b |
| Age at a date (C02, C08, C09, C11) | gpt-oss-120b | qwen3.8-27b |
| Age at the order (C10) | gpt-oss-20b | gpt-oss-120b |
| Product list (C03, C12 to C14) | gpt-oss-120b | gpt-oss-20b |
| Period + age (C15) | gpt-oss-20b | gpt-oss-120b |
| Age + product (C16) | gpt-oss-120b | gpt-oss-20b |
| Period + age + product (C17, C19) | gpt-oss-120b | gpt-oss-20b |
| Period + age at the order (C18) | gpt-oss-20b | gpt-oss-120b |

**Checking by error cost.**

| Use | Check |
|---|---|
| Internal dashboard | One eligible free model, no quorum. The executed SQL and value are kept for audit. |
| Figure shown to a customer | Compare with an independent read-only reference SQL. |
| Payout | Reconcile with the source rows and require human approval. |

**Fallback.** Next free model; if none is available and the deadline allows, defer to a quota refill and check again that capacity is really there; otherwise the paid OpenRouter route of gpt-oss-120b only within the authorised budget; otherwise abstain. A failed verification means defer or abstain.

**Simulator decisions after adaptation** (`python3 atelier-routage.py`, synthetic): simple, complex and high impact run on the free gpt-oss-120b route; deferrable defers for a free refill; urgent runs on the paid route; budget exhausted and unknown capability abstain.

**Priority analysis.** The original `choose` runs an immediately available included-capacity resource (`cash == 0`, `allocation > 0`, the subscription) before deferring for an exhausted free resource (`cash == 0`, `allocation == 0`) that refills before `deadline_minutes`. Waiting costs time and risks the deadline, while the subscription adds no new per-token cost. The priority should be reversed when the request can safely wait until the refill, and the included capacity is scarce enough that saving it for urgent requests is worth more than the delay. At wake-up availability must be measured again, because a reset time is not proof that quota is back. Pair C's adapted simulator has no subscription route, since the portfolio lists none for the selected models, so this analysis is about the original `choose`.

## 5. Successes and failures

- **The vote never returned a wrong value on our traces.** 2-of-3 reached a consensus on 17 of 20 questions and all 17 equal the reference. 3-of-5 reached 15 and all 15 equal the reference. See the table in section 2.
- **Abstention worked as designed.** On C10, C17 and C19 both votes abstained, because no value reached k. C02 and C09 are abstentions of the 3-of-5 only.
- **Unavailable members.** Qwen got HTTP 429 on C17 and C20 ([traces-D.csv](../../td1/traces-D.csv)). It stays in n and casts no vote, which is why 2-of-3 abstains on C17 but still decides C20.
- **A shared wrong value exists.** On C09 cohere and dots both return 0 (reference 487980). Neither declared quorum reaches it (section 3). On C10 qwen and dots both return 119410 (reference 558980); we did not analyse that case further.
- **Failure on the first run of Pair B's script.** The evidence script crashed on Windows (file encoding) and overwrote its own output. We fixed it, and its three evidence files reproduced byte for byte.

## 6. Causes and hypotheses

- **Age rule.** In TD 1, 19 of the 23 cells that were not correct were age mistakes (see the [TD 1 report](../../td1/reports/td1.md)). Pair B shows two different mistakes behind the same wrong 0 on C09: cohere compares the birth year, not `2026 - birth_year`, to 25; dots requires the birthday to be both before and after 26 September.
- **Hypothesis, not tested here:** two models can agree on a wrong value even with different SQL mistakes. The Lecture 2 argument that models trained on close data err together is consistent with C09 but one case does not prove it.
- **Consequence for checking:** a larger quorum is not proof. Customer figures and payouts need a deterministic check of the age predicate and the revenue calculation.

## 7. Limitations

- One run per model and question at temperature 0: no information on run-to-run variance.
- Only 20 questions and one pure product question (C12), so family rates rest on few cells (C10 is a single cell).
- Qwen's two 429 cells are not accuracy: Pair C's table leaves them out of the denominator (executed cases), while a plain `correct / 20` view would count them.
- The simulator's quotas, refill times and costs are synthetic, not provider measurements. Cohere and dots have no price row in the portfolio.
- The single observed shared wrong value does not give a general quorum error rate.

## 8. Replayed and synthetic material

| Material | Nature |
|---|---|
| 20-question vote table (section 2) | Replay of stored real TD 1 traces, no new call |
| The four examples of `atelier-vote.py` and the unit tests | Synthetic values in cents, not shop data |
| C09 faulty queries and delta query | Stored model SQL replayed read-only on `boutique.sqlite` |
| Routing simulator scenarios, quotas, refills and costs | Synthetic |

## 9. Prompts

Unchanged since TD 1. The prompt in `skeleton-multi-llm-en.py` is identical to the TD 1 version; the only changes to the skeleton are `vote_k_sur_n` and the resource lookup into `../td1`.

## 10. Contributions

| Pair | Member (GitHub) | Contribution |
|---|---|---|
| A | Youssef Damak (JoeDmk) | `vote_k_sur_n`, tests, 20-question table, repo split into `td1`/`td2`/`td3`, READMEs, assembly of this report |
| A | Eliott Palethorpe (eliottpalethorpe) | Member of Pair A; no commit under this name in TD 2 |
| B | Haoyu Song (Co1d3r) | C09 analysis, delta query, evidence script (pushed it) |
| B | Sharan Raj Janakiraman (Sharankohli) | Member of Pair B; no commit under this name in TD 2 |
| C | Zinyu Zhu (xinyuzhu-ai) | Routing rule, adapted simulator, tests, priority analysis (pushed it) |
| C | Ismael Charni (IsmaLeThug) | Member of Pair C; no commit under this name in TD 2 |

The commit history shows who pushed; it does not show who worked on what inside a pair.

## 11. AI assistance

The sub-group used AI assistance at a moderate to fairly high level in this session.

Pair A, in detail: Claude (AI assistant) wrote the tests-first implementation of `vote_k_sur_n`, computed the 20-question table from the stored traces, did the repo restructure, and drafted and assembled this report. Youssef ran the tests and the commands, and the team reviews the result before hand-in. Pairs B and C do not itemise their own use here.

## 12. Next steps (TD 3)

- Put a cost on each configuration: single model, 2-of-3, 3-of-5, reference check, review. Use the token counts in the TD 1 traces and the dated prices of the portfolio.
- Questions that no free model handles alone are where checking costs matter most: the age-at-a-date family and every combination that includes age.
- Run the cross-review: each member explains the other two steps back, and the corrections go into a second commit.

## 13. Cross-review

Each pair reviews the other two, six reviews in all, in [../reviews/](../reviews/). Pair A's are done: [A reviews B](../reviews/review-A-of-B.md) and [A reviews C](../reviews/review-A-of-C.md). Pair C's reviews are now available: [C reviews A](../reviews/review-C-of-A.md) and [C reviews B](../reviews/review-C-of-B.md). The other two are B's reviews of A and C. Change made after Pair A's reviews: the evidence script of Pair B now writes its own file and runs on Windows.
