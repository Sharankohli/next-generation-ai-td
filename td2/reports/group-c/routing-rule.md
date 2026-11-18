# TD2 — Pair C: Routing Rule

TD1 evidence is the final executed result per question (20 cases, not a future
error-rate estimate). A = GPT-OSS-120B, B = GPT-OSS-20B, C = North Mini Code,
D = Qwen3.8-27B, E = Dots-3. Correct/executed:

| Family and TD1 cells | A | B | C | D | E | First; next free |
|---|---:|---:|---:|---:|---:|---|
| Period C01,C04-C07,C20 | 6/6 | 6/6 | 6/6 | 5/5* | 6/6 | A; B |
| Age on date C02,C08,C09,C11 | 4/4 | 2/4 | 0/4 | 4/4 | 0/4 | A; D |
| Age at order C10 | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 | B; A |
| Product list C03,C12-C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | A; B |
| Period + age C15 | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 | B; A |
| Age + product C16 | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | A; B |
| Period + age + product C17,C19 | 2/2 | 2/2 | 0/2 | 0/1* | 0/2 | A; B |
| Period + age-at-order C18 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | B; A |

*D did not execute C17 or C20 (HTTP 429); incomplete coverage is not eligible.
Prices/routes: portfolio G5 lists free Groq A, B and D. A's paid OpenRouter
route is $0.15/M input and $0.60/M output tokens. C and E appear in traces but
have no price row in this portfolio, so this rule does not claim their routes
are the cheapest portfolio options. Free routes tie at $0 incremental cash;
the first/next choices use complete TD1 correctness, then Pair C preference.

For internal dashboards, run one eligible free model; no model quorum, and
retain the executed SQL/value for audit. For figures shown to customers, check
against an independent read-only reference SQL and compare the value. For
payouts, reconcile independently to source rows and require human approval.
TD1 correctness is not a guarantee; failed verification means defer or abstain.

When a free model is unavailable, try the next listed free model. If none is
available and the deadline permits, defer to a quota refill and recheck actual
availability. Otherwise use paid A only within the authorized budget; else
abstain. Its simulator estimate assumes 1,000 input + 500 output tokens:
$0.00045/request. Actual cost varies with tokens. Quotas and refill times are
simulated, not provider measurements. The router logs family cells, score,
resource, estimated cost and decision reason. See [before outputs](../../routing-before.txt)
and [after outputs](../../routing-after.txt) for the seven scenarios.
