# Changelog

All notable changes to this skill are documented here. This project adheres
to semantic versioning.

## [1.1.0] - 2026-05-29

### Changed

- Clarified one-sided-request handling in `SKILL.md` and every tool adapter: a
  rewrite-only or score-only request is served as just that half (the
  standalone skill when installed, otherwise the matching vendored copy under
  `vendor/`), never a half-empty voiceprint pass. The verification cases for
  those two requests now assert that observable behavior instead of naming a
  routing target that may not be installed.
- Stated that voiceprint's output contract supersedes the vendored skills' own
  output wrappers: humanizer's `Voice:` / `Density:` header folds into "What
  changed," and its standalone "Next step" file-write offer is not emitted
  inside the pass. An optional, user-initiated write of the "After" text is the
  only reason the skill lists `Write` and `Edit`; the pass is otherwise
  read-only.
- Noted in `README.md` that voiceprint ships adapters for the eight tools both
  upstreams share, and that a vendored skill's own broader `compatibility:`
  frontmatter is upstream's, synced verbatim, not a voiceprint adapter claim.
- Added the missing `examples` reference to the authenticity-check entry in the
  `SKILL.md` reference-file list.

### Tooling

- `scripts/check-vendor-headers` now iterates vendored files with a
  here-doc-fed `while read` loop, tolerating spaces in a path while keeping the
  fail flag in the current shell.
- CI (`vendor-sync-check`) additionally syntax-checks both sync scripts and
  validates that `evals/evals.json` parses, so a broken script or malformed
  eval spec fails the build instead of landing silently.

## [1.0.0] - 2026-05-15

First stable release.

### Added

- Thin-orchestrator `voiceprint` skill: `SKILL.md` plus vendored copies of
  the two upstream skills. It adds no method of its own; the behavior lives
  entirely in the vendored content.
- The one-pass guarantee: run authenticity-check once on the input, apply
  humanizer's fixes once, run authenticity-check again only to report the
  residual. No iteration toward a score threshold. The re-check informs the
  user and never drives further rewriting. A silent score-optimization loop
  is exactly what this design forbids.
- Output contract: before text, before authenticity read, humanized after
  text with humanizer's own what-changed / deliberately-left-alone /
  meaning-check report, the residual read after the single pass, and an
  explicit statement that what remains is human judgment, not another
  automated rewrite.
- Scope and intended-use boundary inherited verbatim in spirit from the
  vendored skills: not designed or tuned to defeat plagiarism or
  AI-detection systems, names and targets no detector, reframes
  assessment-evasion requests toward genuine quality and voice.
- Non-colliding trigger description: fires on the combined diagnose-fix-report
  intent ("clean up and verify," "make this authentic and tell me how it
  scored," "voiceprint this") and explicitly defers pure-rewrite requests to
  the standalone humanizer skill and pure-score requests to the standalone
  authenticity-check skill.
- Vendored humanizer skill, synced from the canonical
  [humanizer](https://github.com/aihxp/humanizer) repo:
  `vendor/humanizer/SKILL.md` and its `references/` (tell-patterns,
  do-not-flag, voice-matching, examples). Last synced 2026-05-16 from
  humanizer commit `ddb4b6f`.
- Vendored authenticity-check skill, synced from the canonical
  [authenticity-check](https://github.com/aihxp/authenticity-check) repo:
  `vendor/authenticity-check/SKILL.md` and its native `references/`
  (scoring, examples). Last synced 2026-05-16 from authenticity-check commit
  `119f666`.
- Shared detection criteria (`tell-patterns.md`, `do-not-flag.md`,
  `voice-matching.md`) re-vendored through the authenticity-check tree to keep
  its `SKILL.md` paths intact; their header names the true canonical upstream,
  the humanizer repo, not authenticity-check. Last synced 2026-05-16 from
  humanizer commit `ddb4b6f`.
- Sync tooling: `scripts/sync-upstream` re-pulls the vendored runtime files
  from the two upstream repos and stamps every file with its sync header. It
  refuses to run when an upstream working tree is dirty, so the stamped
  commit always reproduces the vendored bytes. `scripts/check-vendor-headers`
  validates every file under `vendor/` carries a well-formed header.
- CI sync-header gate (`.github/workflows/vendor-sync-check.yml`): the build
  fails if any vendored file is missing a valid sync header.
- **Vendored-content sync obligation (recorded here as a standing
  commitment):** every file under `vendor/` is a synced copy, not the source
  of truth. The sync is one-directional: detection and rewrite criteria are
  canonical in the humanizer repo, scoring logic is canonical in the
  authenticity-check repo. When upstream criteria or logic change, the
  vendored copies must be re-synced via `scripts/sync-upstream`. They must
  never be edited in this repo independently, or voiceprint silently disagrees
  with the skills it advertises. The header stamp on each file is the
  contract.
- Multi-tool support mirroring humanizer: Claude Code, Cursor, Codex,
  Antigravity, Gemini CLI, Pi Coder, OpenCode, and GitHub Copilot, via
  `SKILL.md`, `AGENTS.md`, `.cursor/rules/voiceprint.mdc`, `GEMINI.md`, and
  `.github/copilot-instructions.md`. Every adapter points the agent at the
  same `SKILL.md` and the same vendored skills.
- Verification eval set (`evals/evals.json`) asserting the one-pass behavior
  and that no iteration toward a score occurs, with a voice-mode fixture
  (`evals/files/VOICE.md`). MIT license.

### Deviations from the upstream repos

- `voiceprint` adds a `scripts/` directory and a `.github/workflows/` CI
  check. The upstream humanizer and authenticity-check skills are pure-prompt
  with no scripts and no CI. These additions are required: voiceprint carries
  a vendoring sync obligation that the standalone skills do not, so it needs a
  sync tool and a check that the obligation is being met.
