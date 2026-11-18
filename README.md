# Trustworthy generative AI, ESILV: sub-group 4 (DIA 1)

Public repository shared from TD 1 to TD 3. Each session has its own folder, with its own README.

## Team

| Full name | GitHub username |
|---|---|
| Youssef DAMAK | JoeDmk |
| Haoyu SONG | Co1d3r |
| Sharan Raj JANAKIRAMAN | Sharankohli |
| Zinyu ZHU | xinyuzhu-ai |
| Eliott PALETHORPE | eliottpalethorpe |
| Ismael CHARNI | IsmaLeThug |

## The three sessions

| Folder | Session | What is in it | Report |
|---|---|---|---|
| [td1](td1/README.md) | 21 October 2026: compare five models on twenty SQL questions | The kit (database, skeleton as used in TD 1, sandbox, models, questions), references, traces, comparison tables | [td1/reports/td1.md](td1/reports/td1.md) |
| [td2](td2/README.md) | 18 November 2026: the k-of-n vote, then the routing rule | Skeleton with `vote_k_sur_n`, vote and routing workshops, tests, wrong-consensus evidence | [td2/reports/td2.md](td2/reports/td2.md) |
| [td3](td3/README.md) | 11 December 2026: cost of each configuration and the choice for a use case | Assignment (work to come) | to come |

## Routing policies

Which model runs first for each kind of question, how its answer is checked (dashboard, customer figure, payout) and the fallback: see [td2/README.md#routing-policies](td2/README.md#routing-policies), with the full rule in [td2/reports/group-c/routing-rule.md](td2/reports/group-c/routing-rule.md).

## Reading order

1. `td1/`: where the data and the stored traces come from.
2. `td2/`: reuses the TD 1 traces and data (no new network call). It reads them from `../td1`.
3. `td3/`: builds on both.

## Notes

- `.gitignore` stays at the root: it keeps keys, virtual environments and caches out of this public repository.
- Run every command from inside the folder of its session (`cd td1`, `cd td2`).
