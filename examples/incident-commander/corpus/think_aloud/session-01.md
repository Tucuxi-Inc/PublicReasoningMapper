# Think-aloud session 1 - Morgan Vale

*Fictional example transcript. Facilitator prompts in italics; Morgan's words otherwise. Recorded and transcribed locally.*

## Problem 1: disk filling on the primary database at 2am

*Facilitator: You're paged at 2am. The primary database disk is at 91% and climbing about 1% every ten minutes. Talk me through it.*

Okay. First thing, I'm doing arithmetic - 91, one percent per ten minutes, so I have roughly an hour and a half before it's full, less if it accelerates. That tells me how much time I have to think, and it's not nothing, so I don't need to do anything rash.

Second thing, what changed. On Osprey - that is our main shipping database - did a job start? Did a migration kick off? Did somebody turn on verbose logging? At 2am it's usually a batch job or a log level. I'd look at what's writing, not at the disk.

If it's logs, I'd turn the log level back down - that's reversible, it costs nothing. If it's a batch job, I'd pause it rather than kill it, because pausing I can undo. What I would not do at 2am is start deleting files on the primary to buy space. That's the irreversible move, and 2am is exactly when people make irreversible mistakes. If I'm wrong about which files are safe, I've turned a disk problem into a data problem.

And who's affected? Nobody yet. So this is not a wake-everyone-up incident. It's me and maybe the database on-call. If it gets to 97 with no fix in sight, that changes and I'd page more people.

## Problem 2: a partner asks to waive the maintenance-window notice

*Facilitator: A large partner's account manager emails: they want us to skip the usual 72-hour notice and do a database upgrade tomorrow because it fixes a bug that's hurting them. What do you do?*

My instinct is to want to help, and the bug really is hurting them. But the 72 hours isn't there for this partner - it's there for every other customer who plans around our windows. So the first thing I'm asking is who else carries the cost if I say yes. If the upgrade goes badly, the partner who asked accepted that risk, but forty other customers didn't.

Second, is the upgrade reversible? If we can roll the database back in minutes, the risk to everyone else is small and I'd be more willing. If it's a one-way schema change, then no, not without notice.

Third, is there a smaller version? Can we hotfix just the bug for them, or apply the upgrade to a replica they can be moved to? Usually there's a way to give them most of what they need without spending everyone else's trust.

So my answer is probably "not tomorrow for everyone, but here's what we can do for you tomorrow", and I'd say why, so the account manager can take that back to the partner.
