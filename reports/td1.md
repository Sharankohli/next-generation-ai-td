# TD 1 report: comparing five models on twenty revenue questions

Sub-group repository: https://github.com/Sharankohli/next-generation-ai-td
Hand-in commit: see the Moodle entry (full hash of the commit that contains this report).

## 1. What was attempted and completed

- **Step 1, references (done):** the twenty reference queries and values are in [`reference-td1.csv`](../reference-td1.csv), one SQLite `SELECT` returning `revenue_cents` per question, with the course conventions (period closed on the left and open on the right, completed age from month and day, cents excluding VAT, 0 and not NULL when nothing matches).
- **Step 2, five models (done, with two unexecuted cells):** 100 cells (20 questions x 5 models), all `nature = real`, run with the skeleton `skeleton-multi-llm-en.py` at temperature 0, same prompt for every model. Raw traces and state files are kept for every run: [`traces-A.csv`](../traces-A.csv), [`traces-B.csv`](../traces-B.csv), [`traces-C.csv`](../traces-C.csv), [`traces-D.csv`](../traces-D.csv), [`traces-E.csv`](../traces-E.csv) with `state-*.jsonl`. They are merged, all attempts kept, in [`traces-td1.csv`](../traces-td1.csv) (103 rows: 100 cells plus 3 retry attempts, all on model D).
- **Step 3, summaries (done):** [`model-question-comparison-en.csv`](../model-question-comparison-en.csv) (one final row per model and question, 100 rows, final status from the last attempt, cause in `explanation`) and [`five-model-summary-en.csv`](../five-model-summary-en.csv).
- **Prompt:** the system message and user template are those of the unmodified skeleton, identical for all models. There is exactly one prompt fingerprint per question across all five models (checked on the merged traces).
- **Replayed or synthetic data:** none in the deliverables. The offline `--demo` run was used only to test the setup and is not committed.

## 2. Results

| Model | Correct | Not correct | Other |
|---|---|---|---|
| A, openai/gpt-oss-120b (Groq) | 20/20 | none | |
| B, openai/gpt-oss-20b (Groq) | 18/20 | C02, C09 | |
| C, cohere/north-mini-code:free (OpenRouter) | 12/20 | 8 (C02, C08, C09, C10, C11, C16, C17, C19) | |
| D, qwen/qwen3.8-27b (Groq) | 15/20 | C10, C15, C19 | C17 and C20 not executed (HTTP 429) |
| E, dots-studio/dots-3-note-preview:free (OpenRouter) | 12/20 | C02, C09, C10, C17, C18, C19 | C08 and C11 `sql_rejected` (SQL inside a markdown code fence) |

Question families (period, age, product, combined) are broken down per model in the five-model summary.

## 3. Observed causes (read from the SQL and error fields)

- **Completed-age convention is the dominant failure.** Of the 23 cells that are not correct, 19 fail on the age rules (completed age on a reference date, or at the order date); the other four are the two unexecuted D cells (access) and E's two rejected outputs (format). Typical patterns seen in the SQL: a birth window shifted by a year (B, C02); a calendar-year window that drops people born late the previous year (B, C09); a condition that can never be true because two bounds contradict each other or compare the same string in both directions (C on C11, D on C15, E on C09); no age filter at all because a year string is compared with a full date (D, C19); and "year difference = 25 and birthday passed", which misses people whose year difference is 26 and birthday not yet reached (D on C10, E on C10 and C18).
- **Output format, not convention:** E's C08 and C11 were rejected by the read-only sandbox because the SQL came back inside a markdown code fence (`not_select`); no value was produced, so the convention was not tested on these two cells.
- **Refused access, not a wrong answer:** D's C17 and C20 ended in HTTP 429 on both attempts (Groq output-tokens-per-minute limit for qwen/qwen3.8-27b: limit 1000, used 864, requested 175). The one-retry limit was used up, no SQL was executed, and they are recorded as `not_executed`. D's C19 also got a 429 on the first attempt; its retry answered, but with a wrong age filter. This is the real failed-access case for the R3 discussion.
- **Model variability at temperature 0:** two operators ran Qwen with the same prompt fingerprints (`traces-D.csv` and `traces-D-Qwen.csv`). They differ on four questions (C09, C10, C16, C17). The official D in the summary is the run in `traces-D.csv` (15 correct, against 14 for the other run). We kept the better of the two runs as a whole, not the best cell from each, so that no cells are mixed between runs.

Hypothesis, for this batch only: the largest model (A) handles the age conventions that the smaller or free models miss. The questions that most models miss in this sample are the age ones (C02, C08 to C11, C15 to C19), which is the point to bring back in TD 2 for routing.

## 4. Limitations

- One run at temperature 0 and one sample per question: this supports a routing hypothesis for this batch, not a ranking of the models.
- Free routes: rate limits and availability can change; D's two unexecuted cells come from such a limit.
- E's run in the repo is the one committed by Sharankohli; an earlier E run by another member (commit `01ac2b3`) was replaced and remains in the git history.
- The kit's summary template named `inclusionai/ling-3.0-flash-sante:free` for the third row, but the authorised model C in `modeles-autorises.json` and the one actually run is `cohere/north-mini-code:free`. The row was changed accordingly. The portfolio has no row for C's model and none for E's, so index and prices are `N/A` with the reason.
- Prices and public index come from `portefeuille-modeles-2026-09-28.csv`; there is no documented paid route of the exact same model for B, D, C and E.

## 5. AI assistance declaration

Claude (Anthropic) was used by JoeDmk as a coding and analysis assistant during the session:
- **References:** for C10, C11 and C17 to C20 the SQL and values were drafted by Claude and recounted independently in plain Python on the CSV files (all 20 values match). For C13 to C16, Joe took Claude's cross-checked queries and values. Sharankohli wrote independent SQL for C17 to C20 (branch `c17-c20-clean`) that gives the same values. An LLM amount was never used as a reference without that recount.
- **Tooling and merge:** Claude helped set up the environment, ran the merge of the traces, the one-fingerprint-per-question check, and drafted the comparison explanations for models B, C and D from the SQL in the traces. The members should read those explanations; one of them (C on C08) is marked TO CONFIRM in the comparison file because the cause was read from a partial view of the SQL.
- **Git operations:** Claude ran some of the git commands on Joe's machine at his request.

## 6. Contributions (from the commit history, each member to confirm)

| Member (GitHub) | Contribution |
|---|---|
| JoeDmk | references C13 to C16, C10, C11, C17 to C20; `.gitignore`; model D run (`traces-D.csv`) and model B run (`traces-B.csv`, done for the sub-group because the assigned operator could not be reached); repair of the shared files after overwritten pushes; merged traces, comparison rows and summary rows for B, C and D; this report |
| Sharankohli | repository owner; independent SQL for C17 to C20; model E traces, comparison and summary row (current `traces-E.csv`, `comparison-E.csv`) |
| xinyuzhu-ai | model A run, `comparison-A.csv`, `summary-A.csv`; merged references C01 to C09 and C12 to C16 |
| Co1d3r | references C05 to C08; second Qwen run (`traces-D-Qwen.csv`) |
| IsmaLeThug | reference C12; model C run (`traces-C.csv`) |
| eliottpalethorpe | reference C09; first E run (replaced) |

## 7. Next steps (TD 2)

- Write the k-of-n vote (`vote_k_sur_n`) on the stored traces and read the questions where several models agree on a wrong value, since the age questions are where a wrong consensus is most likely.
- Build the routing rule from the family results: cheapest adequate model per family, and check the unexecuted cells (D, C17 and C20) with a model that answers them.
- Rotate roles, as the assignment says, and keep the rate limits (D's output-tokens-per-minute) in the routing assumptions.
