# TD2 — Group B: a wrong consensus on C09

## Source and scope

This is an observed TD1 case, not a synthetic or historical example. We examined the latest attempt for each of the 100 question/model cells in the team’s merged `traces-td1.csv` at TD1 commit `7defca1`. Qwen contains retries; the last CSV record for a cell is retained, not counted as another model. C09 and C10 contain shared incorrect values in this scan; this report analyses C09. No network calls were made.

C09 asks for total revenue excluding VAT, in euro cents, across all orders of customers aged exactly 25 on **2026-09-26**. The independent reference in `reference-td1.csv` is **487,980 cents (€4,879.80)**, reproduced on `data/boutique.sqlite`.

## Identification and declared quorum results

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

## Faulty SQL and root causes

### cohere/north-mini-code:free

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

### dots-studio/dots-3-note-preview:free

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

## Independent check and exact delta

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

## Consequence for checking and limitations

Two models can agree on a wrong value even when their SQL mistakes differ. Here the fixed 2-of-3 panel returns the correct value, while the 3-of-5 quorum abstains. The shared wrong value is not a winning majority under either declared panel. Customer-visible or payout amounts therefore need an independent deterministic check of the age predicate and revenue calculation; a larger quorum alone is insufficient evidence of correctness. This single observed case does not establish a general quorum error rate.

Reproduce with `python3 scripts/analyse-group-b.py` from the repository root. This uses Python's standard library and opens SQLite read-only. Evidence: [SQL](group-b/c09-diagnostic.sql), [exact rows](group-b/c09-delta.csv), [recorded inputs and checks](group-b/c09-results.json). Group A should cross-check the declared quorum results with its completed method during internal review. Group C's routing rule and Group A's 20-question table are outside this Group B report. Member names and the team's final combined review remain to be supplied by the team.
