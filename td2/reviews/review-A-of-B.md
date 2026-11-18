# Review of Pair B's work, by Pair A

Reviewer: Pair A (Youssef Damak, Eliott Palethorpe). Reviewed: Pair B (Haoyu Song, Sharan Raj Janakiraman), step 2, the wrong value shared on C09. Commit reviewed: `330202c` (their last push), re-run on `9ac49c5`. The checks were run on Youssef's machine with Claude's help.

## What we checked and how

| Check | Result |
|---|---|
| Does the shared wrong value exist in the traces? | Yes. In `td1/traces-td1.csv`, cohere/north-mini-code:free and dots-3-note-preview:free both return 0 on C09 (verdict incorrect). Reference is 487980. |
| Do their quorum counts match our `vote_k_sur_n`? | Yes. `atelier-vote.py` on C09 gives 2-of-3: 487980 with 2 votes (gpt-oss-120b and qwen). 3-of-5: no value reaches k = 3 (487980 x2, 0 x2, 369240 x1), so it abstains. Same as their table. |
| Does the delta add up? | Yes. 135000 + 25920 + 47900 + 118740 + 99090 + 61330 = 487980, the reference, so it accounts for the exact cent difference. |
| Does their script reproduce? | Yes, after one fix (below). Re-run on Windows, the three evidence files (`c09-delta.csv`, `c09-diagnostic.sql`, `c09-results.json`) came out byte for byte identical, and its assertions on the reference value and the replayed model SQL did not fail. |
| Are the two SQL diagnoses right? | We read both. Cohere never uses `2026 - birth_year` in its age test, so nothing matches. Dots requires the birthday to be both on or before and after 26 September, which cannot hold. We agree. |

## What we found and changed

1. **The script crashed on Windows and overwrote its output.** File writes had no encoding, so the arrow character failed on a cp1252 console, after the script had already truncated `td2.md`. Fixed: UTF-8 and LF line endings on every write.
2. **The script wrote straight into `reports/td2.md`**, which is the assembled report. Re-running it would have erased the other steps. Fixed: it now writes `reports/group-b/report-group-b.md`. The Group B text is embedded in `td2.md` section 3.
3. **Paths after the repo split.** The script read the data from the repo root. It now reads `../td1/`.

## Remaining remarks (not changed)

- The report says C10 also has a shared wrong value (qwen and dots, 119410) but analyses only C09. That meets the assignment (one case); it could say why C10 was not chosen.
- "Group A/B/C" and "Pair A/B/C" are both used in their text.

Overall: the case, the SQL diagnosis and the delta are correct and reproducible.
