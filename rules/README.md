# Rules vs skills — where a line belongs

`AGENTS.md` (project root) holds **invariants**: things that must never happen, checkable in a
sentence. `ultra:*` skills hold **procedures**: steps with a completion criterion. `library/` holds
**reference**: how a technology works.

Test for a line before adding it here:

| Question | If yes |
|---|---|
| Would violating it be a defect regardless of task? | AGENTS.md |
| Does it only matter while doing a particular kind of work? | a skill |
| Is it a fact about a language or framework rather than this project? | library |
| Could a linter or hook check it? | hook, not prose |

Sediment rule: when you add a rule, delete the older wording it replaces. A rules file that grows
monotonically is read by nobody and costs every turn.

Ceiling: ~70 lines of project rules, ~12 invariants. Beyond that, the rules compete with the work.
