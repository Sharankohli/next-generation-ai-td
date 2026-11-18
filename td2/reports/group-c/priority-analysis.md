# Subscription Capacity and Refill Priority

## Original simulator

The original `choose()` checked eligible, available zero-cash capacity before considering a deferred route whose quota reset fit the deadline. That made an immediately available `senior-subscription` resource run before waiting for a refill. This is reasonable when the route is authorized and evidence-eligible, the request is time-sensitive, and the cost of delay or a missed deadline exceeds the opportunity cost of using included capacity. It avoids unnecessary waiting without incurring a new per-token charge.

Reverse the priority for a request that can safely wait until a free refill before its deadline, when preserving scarce included capacity is more valuable than the delay. Defer only within the deadline, then recheck actual availability; a reset estimate is not proof that quota has returned.

## Pair C resources

The current Pair C simulator does not model a subscription route. Its TD1-supported, portfolio-priced routes are free Groq A/B/D and paid OpenRouter A. The supplied portfolio does not list a subscription route for these selected resources, so adding a subscription resource or assigning it a price would invent evidence. Pair C therefore chooses an eligible available free route first, defers for a simulated free-route refill when appropriate, then uses paid A only within budget or abstains.
