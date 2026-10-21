# How I run incidents

*Notes for new incident commanders at Kestrel Row, by Morgan Vale. Fictional example material.*

## The first five minutes

The first question is not "what is broken" but "what changed". Most of our incidents in the last two years started within an hour of a deploy, a config push or a vendor change. Pull up the change log before you open a profiler. If something changed recently and undoing it is cheap, undo it first and see what happens - you learn more from a rollback than from twenty minutes of staring at graphs, and the customers stop hurting while you learn.

Before you roll back, capture what you will want later: a heap dump, the relevant metrics window, the config diff. Evidence is cheap to keep and expensive to recreate. Then stabilise. Diagnosis can happen tomorrow; the customer's failed label run cannot be un-failed.

## How big is this?

Not every incident deserves the same machinery. I size the response on two things: how many people are being hurt right now (blast radius), and whether what is happening can be undone (reversibility). A dashboard bug hurts nobody and is fully reversible - that is a ticket, not an incident. A three-minute blip with retried logins is small and reversible - a short review. Data loss, or anything a customer cannot redo, gets the full process no matter how few people it touched.

The exception is repetition. One small event is noise. The same small event three times is a pattern, and patterns get a proper look even when each instance is trivial.

## Talking to people while it is happening

Never pass on someone else's ETA as ours. Give a time for the next update instead, and keep it even if the update is "no change". A missed ETA discounts every update after it; a kept update time builds trust you will need in the next incident.

Write updates for the person who is hurting, not for the engineers: what is affected, what we are doing, when they will hear from us next.

## Launches

When someone wants to ship on a risky date, do not just say no. Put a price on it: who carries the cost if it goes wrong, and when. A Friday-evening failure lands on the weekend on-call and on the customers who were promised the feature. Then offer a way to keep the date at lower cost - a smaller percentage of traffic, a rehearsed rollback, a different day. People can make a trade-off they can see.
