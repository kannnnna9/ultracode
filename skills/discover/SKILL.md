---
name: discover
description: Turn a vague build request into an approved design before any code.
version: 1.0.0
author: Hermes operator, derived from obra/superpowers brainstorming (MIT) + ECC product-lens (MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [brainstorm, design, requirements, gate]
    related_skills: [plan, library]
---

# Discover — what are we actually building

Use for **L/XL** work: a new feature, a behaviour change with several plausible shapes, anything
where building the wrong thing costs more than ten minutes of questions. Skip for S/M — go to
`ultra:plan` or just build.

## Step 0 — Recon before questions

Read what the operator already gave you: the spec, the files they pointed at, the code the change
touches, the last session's notes. Keep reading until you can explain how the relevant part works
today and what this change would touch.

Never ask what the repo or their message already answers. Never reopen a decision they already made.

## Step 1 — First message

One of two shapes, ~200 words total:

**They described it well.** Play it back in your own words — what it is, who it serves, why — plus
what you found that bears on it (a constraint, a conflict, a cheaper path). End with **one** open
question about the thing that would change the build most, or with the short design and a request
to approve.

**They described it thinly.** One open question, in their words, about the biggest unsettled thing,
and say what the answer would change. No menu of options.

Then stop. Do not implement, scaffold, or install anything.

## Step 2 — The conversation

- Ask only when the answer changes what gets built *and* neither the request nor the code answers it.
- One question at a time. Plain language at their level, their vocabulary, no process jargon.
- When a decision has nameable choices, sketch two or three concretely with the trade-off and say
  which you would pick. A proposal they can correct beats a question.
- When they say "you decide", decide, state it as your call, and move on.
- Play back each chunk you understand (~200 words) and ask what is wrong or missing. Playback and
  questions alternate.

Ground to cover — territory, not a script: what kind of thing this is and what makes it different;
why now and what success looks like; goals, non-goals, anti-goals (what would make this a failure
even if it works); prior art they loved or hated; what exists today; the details they care about.

## Step 3 — Approaches (one message of their own)

Before writing anything up, lay out the ways to build it: two or three real alternatives, weak ones
already dropped, each grounded in this codebase with its trade-off. Recommend one and say why, then
ask which way to go. If they handed you the "how", state your pick instead of asking.

If there is genuinely one sensible way, say so and explain why the others do not fit.

## Step 4 — Size it, then write the design

| Size | Document |
|---|---|
| small change | a short design in chat: intent, approach, what changes, what it costs |
| project | a written design doc |

Full doc covers: intent and why · goals / non-goals / anti-goals · constraints · approaches
considered and the one chosen · decisions they made · what is left to the builder.

Save to `docs/ultra/specs/YYYY-MM-DD-<topic>-design.md` in a repo, commit it, and say where it is.
Operator preference overrides the path.

**Builder check** (projects only): dispatch a fresh subagent with the design and this instruction —
"you are the implementer; list every place this document is ambiguous enough that you would have to
guess". Sort the answers: already answered → put it in the doc; minor → decide it and mark it as
your call; theirs → one message, most important first. One round only.

## Hard gate

```
Nothing gets built until the design is approved.
Built = product code, scaffolding, dependencies, project creation, or invoking an implementation skill.
Reading, exploring, and throwaway spikes are fine.
```

A "sounds good" to the idea is not approval of a document they have not seen. After approval, the
next skill is `ultra:plan` and nothing else.

## Anti-patterns

| Temptation | Reality |
|---|---|
| offer a menu of what they might want | options steer; make them describe it first |
| fill in defaults silently | fine, but say them out loud — an unheard default is one they could not reject |
| write the doc before laying out approaches | the approach choice is theirs |
| ask five questions in one message | one at a time; each answer changes the next question |
| keep interviewing after the picture is clear | size it and write the doc |
| build a "quick prototype" to show them | that is a spike: label it throwaway and ask first |
