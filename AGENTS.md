# voiceprint (agent instructions)

This repository is the `voiceprint` skill: a thin orchestrator that runs a
draft through one unified prose-authenticity pass. It does not invent a
method. It composes two vendored skills, authenticity-check (diagnose) and
humanizer (rewrite), in a fixed order, exactly once. It is the entry point for
any AI coding tool that reads `AGENTS.md` (Codex, OpenCode, Antigravity, Pi
Coder, and others).

## When to apply this skill

Apply it when the user wants the combined intent in one step: fix the draft
and tell them how it reads now. Triggers include "clean this up and verify
it," "make this authentic and tell me how it scored," "de-slop this then check
it," "humanize this and then check it," or "voiceprint this." Apply it even
when they do not say "voiceprint."

Do not apply it to a one-sided request. A pure rewrite with no read-back is
the standalone humanizer skill. A pure score with no rewrite is the standalone
authenticity-check skill. voiceprint is the union of the two, not a substitute
for either. Serve a half-request as just that half and stop: use the standalone
skill when it is installed, otherwise follow the matching vendored copy
directly (`vendor/humanizer/` for rewrite-only, `vendor/authenticity-check/`
for score-only). Do not run a half-empty voiceprint pass.

## How to run it

Read `SKILL.md` in this repository and follow it exactly. Do not improvise a
shortcut. In brief, run these three steps in order, once each:

1. **Diagnose once.** Read `vendor/authenticity-check/SKILL.md` and follow it
   on the input. This is the before read. Carry no target score out of it.
2. **Rewrite once.** Read `vendor/humanizer/SKILL.md` and follow it on the
   input, including its voice discovery, density pre-check, multi-pass
   workflow, and meaning check. Apply it a single time. This is the after
   text.
3. **Re-diagnose once, for residual only.** Read
   `vendor/authenticity-check/SKILL.md` again and run it on the after text as
   a fresh, cold diagnosis. Report the residual. Do not act on it.

Emit the exact output contract from `SKILL.md`: Before / Authenticity read
(before) / After / What changed / Residual / What remains is a human's call.

## Hard rule (one pass, never a loop)

The re-check never drives further rewriting. Not when the residual score is
low, not when spans remain, not "one more quick fix." One diagnose, one
rewrite, one re-diagnose, then stop and report. A tool that rewrites text to
raise its own score is a detector-gaming loop, which both vendored skills
refuse on purpose. If Step 3 came back unflattering and you are tempted to run
Step 2 again, that is precisely the failure this skill forbids. Stop.

## Scope

voiceprint improves prose quality and authentic voice, then gives an honest
read of what is left. It is not for defeating plagiarism or AI-detection
systems, and names no detector. Reframe such requests toward genuine quality
and voice (see `SKILL.md` "Scope and intended use"). This is the same boundary
the vendored skills hold.

## Vendored content

Everything under `vendor/` is a synced copy, not the source of truth. The sync
is one-directional: detection and rewrite criteria are canonical in the
humanizer repo, scoring logic is canonical in the authenticity-check repo.
Never edit a vendored file. A fix belongs upstream and is then re-synced via
`scripts/sync-upstream`. Each vendored file's header stamp is the contract;
see `README.md` for the full procedure.
