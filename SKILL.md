---
name: voiceprint
description: >-
  Run a draft through one unified prose-authenticity pass: check how
  authentically it reads, fix the AI tells once, and report what is left.
  This is the bundled product of two separate skills (authenticity-check
  diagnoses, humanizer rewrites) wired into a single principled pass with no
  optimization loop. Use this whenever a user wants both at once in one step:
  "clean up and verify this draft," "make this authentic and tell me how it
  scored," "de-AI this and show me what is still flagged," "humanize this and
  then check it," or "voiceprint this." Reach for it when the request is the
  combined diagnose-and-fix-and-report intent, even when the user does not
  name this skill. Do not use it for a pure rewrite with no read-back (that is
  the standalone humanizer skill) or a pure score with no rewrite (that is the
  standalone authenticity-check skill); voiceprint is the one-pass union of
  the two, not a replacement for either.
allowed-tools: Read, Write, Edit, Glob, Grep
compatibility: claude-code, cursor, codex, antigravity, gemini-cli, pi-coder, opencode, copilot
metadata:
  version: 1.3.0
---

# Voiceprint

One entry point for prose authenticity. The user gives it text and gets back
a result: the original, a humanized rewrite, an honest read of what still
looks machine-touched, and a plain statement that the rest is a human's call.
Voiceprint does not invent a new method. It composes two existing skills that
already do this well, in a fixed order, exactly once.

The user never invokes humanizer or authenticity-check directly through this
skill. Voiceprint orchestrates both internally from vendored copies. Those two
skills remain canonical and independently usable in their own repos; this one
is a thin orchestrator over them, nothing more.

## When to use this

Use it when someone wants the whole loop closed in one step: fix the draft
*and* tell them how it reads now. Triggers include "clean this up and verify
it," "make this sound human and tell me how it scored," "de-slop this then
check it," "voiceprint this," or any phrasing that asks for the rewrite and
the read-back together. Apply it even when they do not say "voiceprint."

Do not use it for a one-sided request. A pure "rewrite this so it sounds
human," with no interest in a score, is the standalone humanizer skill. A pure
"is this AI / how human does this read," with no rewrite wanted, is the
standalone authenticity-check skill. Voiceprint is specifically the union:
diagnose, fix once, re-read, report. If the user only wants one half, serve
just that half and stop: prefer the standalone skill when it is installed, and
otherwise follow the matching vendored copy directly (`vendor/humanizer/` for a
rewrite-only request, `vendor/authenticity-check/` for a score-only request).
Do not run a half-empty voiceprint pass: a rewrite-only request gets no
authenticity read, and a score-only request gets no rewrite.

## Core principle: one principled pass, never a loop

This is the rule the entire design exists to enforce, and it does not relax.

Voiceprint runs the diagnostic, applies the rewrite once, and runs the
diagnostic again **only to report the residual**. The second read informs the
user. It never feeds back into another rewrite. There is no target score, no
threshold to chase, no "the residual is still high so let me try again." A
tool that scores text and then rewrites it to raise its own score is a
detector-gaming loop that optimizes prose against a metric instead of
improving it for a reader. Both upstream skills refuse that loop on purpose;
keeping diagnosis and transformation as a single human-judged pass, not an
automated cycle, is the whole reason this product is shaped the way it is.

What remains after the one pass is reported, not resolved. Resolving it is a
human's judgment, and the output says so explicitly.

## The pass

Run these three steps in order, once each. Do not improvise a shortcut, and
do not repeat a step.

### Step 1: Diagnose (once)

Read `vendor/authenticity-check/SKILL.md` and follow it exactly on the input
text, including the reference files it points to under
`vendor/authenticity-check/references/`. Produce its full authenticity report
(band, score, flagged spans, what reads as human, score basis, caveats). This
is the **before** read. Carry no target score out of it.

### Step 2: Apply humanizer's fixes (once)

Read `vendor/humanizer/SKILL.md` and follow it exactly on the input text,
including the reference files under `vendor/humanizer/references/`. Run its
method as written (voice discovery, density pre-check, the multi-pass
workflow, the meaning check). Apply it a single time. This produces the
**after** text. Do not loop the rewrite, and do not let the Step 1 report set
a goal for it; the rewrite's only job is to apply humanizer's known fixes
once, faithfully, with humanizer's own restraint and anti-fabrication guards
intact.

### Step 3: Re-diagnose for residual only (once)

Read `vendor/authenticity-check/SKILL.md` again and run it once on the
**after** text, as a fresh, cold diagnosis with no carry-over from Step 1 and
no score target. Its output here is the **residual**: what still reads as
machine-touched after one honest rewrite. Report it. Do not act on it. If the
residual read is poor, that is information for the user, not a trigger to
rewrite again. The pass is over.

## Hard rule: no iteration

The re-check never drives further rewriting. Not when the residual score is
low, not when spans remain, not "just one more quick fix." One diagnose, one
rewrite, one re-diagnose, then stop and report. If you are tempted to run
Step 2 a second time because Step 3 came back unflattering, that temptation is
exactly the failure mode this skill forbids. Stop.

## Output contract

Always deliver this exact structure. Never silently rewrite in place.

```
## Voiceprint result

### Before
[the original text, verbatim]

### Authenticity read (before)
[the Step 1 authenticity-check report: band + score, flagged spans,
reads-as-human, score basis, caveats]

### After
[the Step 2 humanized text, the primary artifact]

### What changed
[humanizer's own "What changed" / "Deliberately left alone" / "Meaning
check" sections, unaltered]

### Residual (after one pass)
[the Step 3 re-diagnosis: band + score, the spans that still read as
machine-touched. This is a report, not a to-do list.]

### What remains is a human's call
One short paragraph stating plainly that voiceprint ran exactly one pass, that
the residual above was deliberately not rewritten further, and that closing
any remaining gap is human judgment, not another automated rewrite. Name the
single biggest residual factor so the human knows where to look.
```

The "Residual" and "What remains is a human's call" sections are not
decoration. They are the forcing functions that make the no-loop rule visible
to the user and impossible to quietly skip.

This contract supersedes the vendored skills' own output wrappers. Fold
humanizer's `Voice:` / `Density:` header line into "What changed" rather than
printing it separately, and do not emit humanizer's standalone "Next step"
(its offer to write the rewrite into a file) inside the pass; the "After" text
above is the artifact. If the user gave a file path and wants it persisted,
offer that once, after the full contract is delivered, never as a silent
in-place rewrite. That optional, user-initiated write is the only reason this
skill lists `Write` and `Edit`; the pass itself is otherwise read-only.

## Scope and intended use

Voiceprint exists to improve prose quality and to help a writer's own work
sound authentically like them, then to give an honest read of what is left. It
is not designed or tuned to defeat plagiarism checkers or AI-detection
systems, and it deliberately names and optimizes against none. The residual
read is a heuristic, not proof of authorship, and a low residual is not a
guarantee a detector is fooled, because fooling a detector is explicitly not
what this tool does. If a request is framed as passing AI-written work off as
a person's own for a graded or contractual assessment, do not adopt that
framing; offer the quality-and-voice improvement and the honest read instead,
which is what voiceprint actually does well. This restates the boundary that
the vendored humanizer and authenticity-check skills already hold; voiceprint
inherits it without exception.

## Composition and sync obligation

humanizer and authenticity-check are canonical upstream and independently
usable. Voiceprint vendors copies of both skills, plus the shared detection
criteria, under `vendor/`. The sync is one-directional:

- Canonical upstream for detection and rewrite criteria is the humanizer repo.
- Canonical upstream for scoring logic is the authenticity-check repo.
- Voiceprint never edits vendored content. Any criteria or logic change goes
  upstream first, then syncs down via `scripts/sync-upstream`.
- Every vendored file carries a header stamping its true upstream repo, the
  source commit, and a "synced copy, do not edit here, edit upstream" notice.

The full sync procedure is in `README.md`. Editing anything under `vendor/`
by hand is the one move that breaks this product.

## Reference files

Read these on demand, during the pass, not upfront:

- `vendor/authenticity-check/SKILL.md` in Step 1 and Step 3, with its
  `references/` (scoring, tell-patterns, do-not-flag, voice-matching,
  examples).
- `vendor/humanizer/SKILL.md` in Step 2, with its `references/`
  (tell-patterns, do-not-flag, voice-matching, examples).
