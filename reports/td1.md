# TD 1 report: five models, twenty revenue questions

Repo: https://github.com/Sharankohli/next-generation-ai-td
The hand-in commit hash is in our Moodle entry (it's the commit that holds this file).

## 1. What we did

We did all three steps. Two cells didn't run, more on that below.

**Step 1, the references.** Twenty SQLite queries and their values are in [`reference-td1.csv`](../reference-td1.csv). Each query returns one row, `revenue_cents`, using the protocol conventions: periods closed on the left and open on the right, age counted as completed years from month and day, cents without VAT, and 0 (not NULL) when nothing matches.

**Step 2, the models.** 100 cells, 20 questions times 5 models, all real calls. We used the skeleton as it came, temperature 0, same prompt for everybody. Raw traces and state files for every run are in the repo ([A](../traces-A.csv), [B](../traces-B.csv), [C](../traces-C.csv), [D](../traces-D.csv), [E](../traces-E.csv)). [`traces-td1.csv`](../traces-td1.csv) merges them with every attempt kept: 103 rows, which is the 100 cells plus 3 retries, all on model D. We checked the merged file and every question has exactly one prompt fingerprint across the five models.

**Step 3, the summaries.** [`model-question-comparison-en.csv`](../model-question-comparison-en.csv) has one final row per model and question (100 rows, status from the last attempt, a cause in `explanation`). [`five-model-summary-en.csv`](../five-model-summary-en.csv) has the five models.

The prompt is the skeleton's own, unchanged. Nothing replayed or simulated is in the deliverables. We ran `--demo` once to test the setup and never committed it.

## 2. Results

| Model | Correct | Not correct | Other |
|---|---|---|---|
| A, gpt-oss-120b (Groq) | 20/20 | none | |
| B, gpt-oss-20b (Groq) | 18/20 | C02, C09 | |
| C, cohere/north-mini-code:free (OpenRouter) | 12/20 | C02, C08, C09, C10, C11, C16, C17, C19 | |
| D, qwen3.8-27b (Groq) | 15/20 | C10, C15, C19 | C17 and C20 not executed (HTTP 429) |
| E, dots-3-note-preview:free (OpenRouter) | 12/20 | C02, C09, C10, C17, C18, C19 | C08 and C11 rejected, SQL came back inside a markdown code fence |

The split by question family (period, age, product, combined) is in the five-model summary.

## 3. Why things failed

It's the age rule, mostly. 23 cells aren't correct and 19 of them are age mistakes, either age on a reference date or age at the time of the order. The other four are D's two blocked cells and E's two format rejections.

What the age mistakes look like in the SQL:
- a birth window shifted by a year (B, C02);
- a calendar-year window that drops people born late the year before (B, C09);
- a condition that can never be true, because two bounds contradict each other (C on C11) or the same string is compared in both directions (D on C15);
- no age filter at all, because a year like `2001` gets compared with a full date (D on C19);
- "year difference is 25 and the birthday has passed", which misses people whose year difference is 26 and whose birthday isn't here yet (D on C10, E on C10 and C18).

E's C08 and C11 are a different story. The sandbox refused the SQL (`not_select`) because the model wrapped it in a code fence. No value came out, so we know nothing about the convention on those two.

D's C17 and C20 are access failures, not wrong answers. Groq answered 429 twice on each (output tokens per minute, limit 1000, 864 already used, 175 asked). The retry limit was gone after that, no SQL ran, and they are `not_executed`. C19 on D got a 429 on the first try too, and then answered wrong on the retry. That's our real failed-access example.

Qwen is also not stable. Two of us ran it with the same prompt fingerprints ([`traces-D.csv`](../traces-D.csv) and [`traces-D-Qwen.csv`](../traces-D-Qwen.csv)) and the results differ on four questions: C09, C10, C16, C17. Temperature was 0 both times. We took one whole run as the official D, the one with more correct answers (15 against 14), and did not pick the best cell from each, since that would hide exactly this problem.

Guess, for this batch only: A copes with the age rules and the smaller free models mostly don't. The questions most models miss are the age ones (C02, C08 to C11, C15 to C19). They're the ones to bring back for the routing work in TD 2.

## 4. Limits

- One run at temperature 0, one sample per question. Fine for a routing hypothesis, useless as a ranking.
- Free routes change. D's two blocked cells are a rate limit, and it could go differently another day.
- E's run in the repo is Sharan's. An earlier E run from another member (commit `01ac2b3`) got replaced and is still in the git history.
- The kit's summary template had `inclusionai/ling-3.0-flash-sante:free` as the third model. The authorised model C in `modeles-autorises.json` is `cohere/north-mini-code:free` and that's what was run, so we changed the row. The portfolio has no entry for C's model or E's, so their index and prices are N/A with the reason written next to them. The same goes for the paid routes of B and D, there isn't a same-model one in the portfolio.
- Index and price data come from `portefeuille-modeles-2026-09-28.csv`.

## 5. AI help

Joe used Claude (Anthropic) as an assistant, and here's exactly where.

- **References.** Claude drafted the SQL and values for C10, C11 and C17 to C20, and recounted all twenty a second way in plain Python over the CSV files. They match. For C13 to C16, Joe used Claude's cross-checked queries. Sharan wrote his own SQL for C17 to C20 (branch `c17-c20-clean`) and got the same values. No amount that came from an LLM was ever used as a reference without that recount.
- **Setup and merge.** Claude helped with the environment, merged the traces, ran the one-fingerprint-per-question check, and drafted the comparison explanations for B, C and D from the SQL in the traces. People should read those. One of them, C on C08, is marked TO CONFIRM in the comparison file because the cause came from a partial look at the SQL.
- **Git.** Claude ran some git commands on Joe's machine when he asked it to.

## 6. Who did what (from the commit history, everyone please check your line)

| Member (GitHub) | What |
|---|---|
| JoeDmk | references C13 to C16, C10, C11, C17 to C20; `.gitignore`; model D run (`traces-D.csv`); model B run (`traces-B.csv`), done for the group because the assigned operator couldn't be reached; fixing the shared files after overwritten pushes; merged traces; comparison and summary rows for B, C, D; this report |
| Sharankohli | owns the repo; independent SQL for C17 to C20; model E traces, comparison and summary row |
| xinyuzhu-ai | model A run, `comparison-A.csv`, `summary-A.csv`; merged references C01 to C09 and C12 to C16 |
| Co1d3r | references C05 to C08; the second Qwen run (`traces-D-Qwen.csv`) |
| IsmaLeThug | reference C12; model C run (`traces-C.csv`) |
| eliottpalethorpe | reference C09; the first E run (replaced later) |

## 7. TD 2

Write the k-of-n vote on the stored traces and look hard at the questions where several models agree on a wrong value. The age ones are where a wrong consensus is most likely. After that, build the routing rule from the family results: cheapest model that's good enough per family, and something that answers C17 and C20, since D never did. Roles rotate. And D's per-minute output limit has to go into the routing assumptions, because it will bite again.
