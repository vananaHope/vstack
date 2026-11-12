---
name: blast-radius
description: "Find what a change could break somewhere else before it ships, beyond the diff, and prove the one fact it's safe because of by running real code instead of writing it up. Use for /vstack:blast-radius, 'blast radius of X', 'what could this break', or reviewing a small diff you don't trust."
disable-model-invocation: true
---

> vstack copy of pstack `blast-radius` (0.15.36). Local edits are listed in UPSTREAM.md. In a vstack task, "the manager" is whoever assigned the task; outside one, it is the user.

# Blast radius

Find what a change breaks somewhere else, before it ships. Use for "blast radius of X", "what could this break", or reviewing a small diff you don't trust yet.

This is a different question from what the code does or why it's shaped that way. Blast radius tells you what it breaks somewhere else.

Listing the callers is not the job. The agent can grep those in a second. The job is the breakage grep won't show you.

## Don't trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it's true. So don't hand back the writeup. Find the one or two facts the whole thing depends on and prove them by running code.

### How sure are you

For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line. A real `file:line`, or the library's own source.
3. You showed the bad case can't happen. You walked the failure step by step and it doesn't reach.
4. You ran it. A script or test that calls the real code and fails loud if you're wrong.
5. You reproduced it in the running app.

Step 4 is usually one small script that imports the same library the app ships and calls the exact function you're worried about.

## Steps

1. Read the change. The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff doesn't spell out. Pull the commits and the PR behind it: `git log --oneline <base>..<head>`, `git log -1 --format=%B <commit>` for each substantive commit, and `gh pr view <number> --json title,body,comments` when there is a PR. In a vstack task the change is the task's target: `git diff <B>...<H>`.
2. Find the one fact it's safe because of. Most changes that look risky are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else". Find that fact. If it holds, most risky cases are cleared at once. Spend your time here, not on a long list of maybes.
3. Look where grep stops. Read the source of the library you call, and check its pinned version and any local patch. Work out when things run: microtasks, unmount and teardown, Solid versus React. Follow what a symbol search misses: the JSON an API returns, a DB column, a wire format, another language reading the same bytes, a feature flag, code three hops downstream.
4. Be honest about each risk. Give it a real chance of happening and a real cost if it does. Keep the risks you confirmed. List the ones you checked and cleared separately. Cite a real `file:line`, a search that finds nothing is still an answer, and never make up a caller or an API.
5. Prove the one fact. Write a script or test that runs the real code, run it, and paste what happened. Put the script where "Where the proof lives" below says, never in the product tree.
6. For a big or wide change, one read is not enough. Say so in what you hand back and name the part you are least sure of, so the manager can get a second read from a different model family. Different models catch different real bugs. Do not spawn other agents yourself.

## What to hand back

- **What it does.** What changed, including the part that isn't obvious.
- **The one fact it's safe because of.** State it, say which step you got it to, and show the proof. If you couldn't prove it, write unproven. If running it showed the fact is false, or false under some condition, write disproven, name the condition, and list what breaks under Risks.
- **Risks.** Each names how it breaks, the `file:line`, how likely and how bad, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it's fine.
- **Before you merge.** The cheapest test or repro that catches the real bug, including the script you wrote.

Write it plainly, cite real code, and strip anything private before it goes anywhere public.

## Where the proof lives

- In a vstack task: scripts, copies and temporary data go in the scratch folder the spec names. The command you ran and its output go in your evidence folder under `process/`. A reviewer does not edit product source or tests and does not commit. The reviewer puts the handback in the review report: each risk becomes a finding with a severity, and an unproven safety fact is a finding or an item for a human to check, never a silent pass. An implementer puts the handback in the completion report.
- Level 5 (the running app) in a vstack task: start the app only through the verify skill or the setup steps the spec gives. If that opens a real desktop window, do it only under the locked desktop command the spec gives. If the spec gives no way to run the app, or a window is needed and there is no lock command, stop at level 4 and say so.
- Outside a vstack task: scripts go in the folder whoever asked names, or else a new folder under the OS temp directory. Do not leave them in the working tree. For level 5, follow the project's own instructions for running the app.

**Reply:** the writeup above, with the one safety fact marked proven, disproven, or unproven. Unproven means you could neither prove it nor show it false.
