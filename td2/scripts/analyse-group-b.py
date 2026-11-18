"""Replay stored TD1 SQL read-only and regenerate Group B evidence; no API calls."""
import csv
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TD1 = ROOT.parent / 'td1'
OUT = ROOT / 'reports/group-b'
OUT.mkdir(parents=True, exist_ok=True)
latest = {}
for path in [TD1 / 'traces-td1.csv']:
    for record in csv.DictReader(path.open(encoding='utf-8-sig')):
        latest[record['case_id'], record['provider'], record['model_requested']] = dict(record, source=path.name)
refs = {r['case_id']: r for r in csv.DictReader((TD1/'reference-td1.csv').open(encoding='utf-8-sig', newline=''))}
shared = []
for case in sorted(refs):
    groups = defaultdict(list)
    for (qid, _, _), r in latest.items():
        if qid == case and r['verdict'] == 'incorrect':
            groups[r['value']].append(r['model_requested'])
    shared.extend({'case': case, 'value': value, 'models': models} for value, models in groups.items() if len(models) >= 2)
rows = [r for (case, _, _), r in latest.items() if case == 'C09']
con = sqlite3.connect(f'file:{TD1 / "data/boutique.sqlite"}?mode=ro', uri=True)
ref = refs['C09']
expected = int(ref['revenue_cents'])
assert con.execute(ref['sql']).fetchone()[0] == expected
for row in rows:
    if row['value']:
        actual = con.execute(row['sql']).fetchone()[0]
        assert actual == int(row['value']), (row['model_requested'], actual)

# Independent completed-age arithmetic; then remove rows selected by each faulty query.
age = "((2026 - CAST(strftime('%Y', c.birth_date) AS INTEGER)) - ('09-26' < strftime('%m-%d', c.birth_date))) = 25"
base = f'''SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c JOIN orders o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE {age}
GROUP BY c.customer_id, c.birth_date ORDER BY c.customer_id;'''
cur = con.execute(base)
delta = cur.fetchall()
assert sum(r[2] for r in delta) == expected
with (OUT/'c09-delta.csv').open('w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, lineterminator="\n"); writer.writerow([d[0] for d in cur.description]); writer.writerows(delta)
wrong = [r for r in rows if r['value'] == '0']
queries = []
for row in wrong:
    predicate = row['sql'].split('WHERE', 1)[1].strip().rstrip(';')
    query = base.replace(f'WHERE {age}', f'WHERE {age}\nAND NOT ({predicate})')
    assert con.execute(query).fetchall() == delta
    queries.append((row['model_requested'], query))
(OUT/'c09-diagnostic.sql').write_text('\n\n'.join(['-- Reference SQL from reference-td1.csv\n'+ref['sql'].rstrip(';')+';'] + ['-- Stored faulty SQL: '+r['model_requested']+'\n'+r['sql'] for r in wrong] + ['-- Independent completed-age calculation\n'+base] + ['-- Exact omitted rows: '+model+'\n'+query for model, query in queries])+'\n', encoding='utf-8', newline='\n')
fixed = {'openai/gpt-oss-120b','cohere/north-mini-code:free','qwen/qwen3.8-27b'}
def count(panel, k):
    counts = Counter(int(r['value']) for r in panel if r['value'] and r['verdict'] in {'correct','incorrect','executed'})
    value, votes = counts.most_common(1)[0]
    return {'n': len(panel), 'k': k, 'consensus': votes >= k, 'value': value if votes >= k else None, 'votes': votes}
votes = {'2-of-3': count([r for r in rows if r['model_requested'] in fixed],2), '3-of-5':count(rows,3)}
evidence = {'latest_cells':len(latest),'selection':'Last CSV row per case/provider/model, matching atelier-vote.py; repeats are not extra votes.','shared_wrong_cases':shared,'reference_cents':expected,'database_sha256':hashlib.sha256((TD1/'data/boutique.sqlite').read_bytes()).hexdigest(),'C09':rows,'manual_quorum_counts':votes,'delta_rows':delta,'delta_sum':sum(r[2] for r in delta),'checks':'All five stored C09 SQL outputs reproduced; saved reference reproduced; independent age arithmetic agrees; exact omitted-row query for each of the two zero-valued SQL statements returns the same six customers.'}
(OUT/'c09-results.json').write_text(json.dumps(evidence,indent=2)+'\n', encoding='utf-8', newline='\n')
report = '''# TD2 — Group B: a wrong consensus on C09

## Source and scope

This is an observed TD1 case, not a synthetic or historical example. We examined the latest attempt for each of the 100 question/model cells in the team’s merged `traces-td1.csv` at TD1 commit `7defca1`. Qwen contains retries; the last CSV record for a cell is retained, not counted as another model. C09 and C10 contain shared incorrect values in this scan; this report analyses C09. No network calls were made.

C09 asks for total revenue excluding VAT, in euro cents, across all orders of customers aged exactly 25 on **2026-09-26**. The independent reference in `reference-td1.csv` is **487,980 cents (€4,879.80)**, reproduced on `data/boutique.sqlite`.

## Identification and declared quorum results

| Model | Source | Value (cents) | Stored verdict | Fixed panel member |
|---|---|---:|---|---|
'''
for r in rows:
    report += f"| {r['model_requested']} | {r['source']} | {r['value']} | {r['verdict']} | {'yes' if r['model_requested'] in fixed else 'no'} |\n"
report += '''
- Fixed **2-of-3**, k=2: GPT-OSS-120B and Qwen return 487980; Cohere returns 0 → consensus **487980**, two votes, correct.
- Full **3-of-5**, k=3: two votes for 487980, two for 0, one for 369240 → **abstention**, maximum two votes. The shared wrong value does not reach either declared quorum.

These are manual counts from the stored values, independently checked by the evidence script. They do not claim validation of Group A's `vote_k_sur_n`. The vote sees execution success and integer values, not the reference or correctness verdict; `correct` and `incorrect` here both denote successfully executed SQL. Adding Dots adds support for the shared wrong value, causing the larger quorum to abstain. GPT-OSS-20B also errs, but its different value does not support the zero consensus.

## Faulty SQL and root causes

'''
explanations = {
'cohere/north-mini-code:free': 'The expression starts with the birth year (around 2000/2001), then subtracts at most one, and compares that number with 25. It omits `2026 - birth_year`. No customer passes; the empty SUM becomes zero through COALESCE.',
'qwen/qwen3.8-27b': 'The question specifies age on 2026-09-26, but this query uses the order date. In addition, adding 26 years preserves the month/day for these customers, so the query requires the order month/day to be both >= and < the birthday month/day. This conjunction excludes all rows.',
'dots-studio/dots-3-note-preview:free': 'The first birthday condition requires month/day <= September 26, while the second simultaneously requires month/day > September 26. They cannot both hold. Its year-difference condition alone would also miss some customers born in late 2000 who are still 25.'}
for r in wrong:
    report += f"### {r['model_requested']}\n\nOriginal complete SQL from `{r['source']}`:\n\n```sql\n{r['sql']}\n```\n\n{explanations[r['model_requested']]}\n\n"
report += '''## Independent check and exact delta

Being 25 on 2026-09-26 means **2000-09-26 < birth_date <= 2001-09-26**. The older endpoint is excluded because that customer has turned 26; the younger endpoint is included because that customer has just turned 25. All their orders count, with no order-date restriction.

The saved reference uses this birth-date window. We independently recomputed completed age as year difference minus one if the birthday has not occurred, then aggregated integer `quantity_product * price`. Both methods return 487,980 cents.

Independent query:

```sql
'''+base+'''\n```

For each faulty query, `c09-diagnostic.sql` also executes the independent age condition AND NOT that model's original WHERE predicate. Each returns exactly the same omitted customers:

| customer_id | birth_date | Order revenue excluding VAT (cents) |
|---|---|---:|
'''
for customer,birth,revenue in delta:
    report += f'| {customer} | {birth} | {revenue} |\n'
report += f'''
**Sum: {expected:,} cents = reference {expected:,} − faulty output 0.** Thus the row-level diagnostic accounts for the entire discrepancy for each of the two queries. All five stored model SQL statements were replayed, including GPT-OSS-20B's distinct incorrect result, and matched their recorded values.

## Consequence for checking and limitations

Two models can agree on a wrong value even when their SQL mistakes differ. Here the fixed 2-of-3 panel returns the correct value, while the 3-of-5 quorum abstains. The shared wrong value is not a winning majority under either declared panel. Customer-visible or payout amounts therefore need an independent deterministic check of the age predicate and revenue calculation; a larger quorum alone is insufficient evidence of correctness. This single observed case does not establish a general quorum error rate.

Reproduce with `python3 scripts/analyse-group-b.py` from the `td2` folder; it rewrites `reports/group-b/report-group-b.md` (the Group B section of `td2.md`), not `td2.md` itself. This uses Python's standard library and opens SQLite read-only. Evidence: [SQL](group-b/c09-diagnostic.sql), [exact rows](group-b/c09-delta.csv), [recorded inputs and checks](group-b/c09-results.json). Group A should cross-check the declared quorum results with its completed method during internal review. Group C's routing rule and Group A's 20-question table are outside this Group B report. Member names and the team's final combined review remain to be supplied by the team.
'''
(OUT/'report-group-b.md').write_text('\n'.join(line.rstrip() for line in report.splitlines())+'\n', encoding='utf-8', newline='\n')
query_path = OUT/'c09-diagnostic.sql'
query_path.write_text('\n'.join(line.rstrip() for line in query_path.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'cells':len(latest),'shared':shared,'votes':votes,'delta':delta,'total':expected},indent=2))
