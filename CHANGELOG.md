# Changelog

All notable changes to this skill are documented here. This project adheres
to semantic versioning.

## [Unreleased]

## [1.4.0] - 2026-08-15

### Added

- Added a dependency-free deterministic Unicode hygiene stage, inspired by
  [watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover),
  at the start of Voiceprint Step 2. The original remains verbatim for
  `Before` and the before diagnosis; one cleaned working copy reaches the
  existing single humanizer invocation.
- Added `scripts/text_hygiene.py` with importable inspection and cleanup APIs,
  `inspect` and `clean` CLI operations, deterministic code-point manifests,
  same-family script preservation, Unicode Emoji 17.0 ZWJ pair data, exact
  UTF-8 output, a 4 MiB input cap, exact unit and CLI fixtures, and CI coverage.
- Added hygiene behavior evals for positive findings, zero findings,
  load-bearing Unicode preservation, and detector-framed requests.

### Changed

- The six-section result now reports detected, removed, normalized, and
  deliberately preserved hygiene counts inside `What changed`. The residual
  remains report-only and cannot trigger another cleanup or rewrite.
- Clarified that Unicode cleanup does not establish watermark presence,
  vendor provenance, or a detector signal. Statistical watermark rewriting,
  metadata removal, media processing, NFKC normalization, confusable mapping,
  and detector optimization remain outside Voiceprint's scope.
- Manifests now report the Python Unicode database version and pinned Emoji
  ZWJ version. Unknown format controls are preserved conservatively with a
  reason instead of being removed as a class.
- The 200 ms p95 release benchmark is opt-in through
  `VOICEPRINT_RELEASE_BENCHMARK=1`; routine CI remains timing-independent.

### Security

- Restricted path input to unchanged regular, non-symbolic-link files using
  pre-open and post-open identity checks, no-follow behavior where available,
  and nonblocking open behavior where available. Symlinks, FIFOs, and
  check-then-open replacements fail without exposing input or blocking.
- Narrowed variation-selector and emoji-joiner preservation claims to the
  evidence the pinned policy actually establishes. The validation workflow
  now uses read-only repository permissions and immutable action revisions.

## [1.3.0] - 2026-05-29

### Added

- `scripts/check-upstream-freshness` and a scheduled `upstream-freshness`
  workflow (weekly, plus manual dispatch) that compare each vendored skill's
  stamped source commit against its canonical upstream's latest commit and fail
  when a re-sync is due. Closes the gap that let the vendored copies drift a
  full version behind: the one-directional sync obligation no longer depends on
  a maintainer remembering to re-pull. The check is read-only (GitHub API via
  `gh` / `GH_TOKEN`), distinguishes stale (exit 1) from could-not-check
  (exit 2), and is covered by the existing CI script syntax-lint.

## [1.2.0] - 2026-05-29

### Changed

- Re-synced the vendored skills to their upstream 1.1.1 releases (humanizer
  @ 17c544e, authenticity-check @ 71c3ec9), refreshing content vendored from
  the earlier 1.0.0-era commits. Pulls in the upstream 1.1.x work (expanded
  worked examples, SKILL.md refinements, scoring additions); the vendored
  frontmatter now reads version 1.1.1. voiceprint adds no method of its own,
  so this is purely a refresh of the bundled behavior, re-stamped and
  validated by `scripts/check-vendor-headers`.

### Fixed

- Resolved the `Scriven` -> `Scriveno` naming drift the documentation audit
  surfaced in `vendor/`. humanizer had already corrected it upstream; a missed
  occurrence in authenticity-check's `SKILL.md` was fixed upstream and pulled
  in by this re-sync. No bare `Scriven` remains in `vendor/`.

## [1.1.1] - 2026-05-29

### Fixed

- README Layout: the `.github/workflows/` descriptor now reflects the full CI
  scope as of 1.1.0 (sync-header gate plus sync-script lint and an evals.json
  parse check), instead of naming only the sync-header gate.
- README compatibility note: names the specific tools authenticity-check
  declares beyond voiceprint's eight-adapter set (windsurf, cline, continue,
  zed, aider) instead of an imprecise "a few," from a full documentation audit.

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
  [humanizer](https://github.com/hannsxpeter/humanizer) repo:
  `vendor/humanizer/SKILL.md` and its `references/` (tell-patterns,
  do-not-flag, voice-matching, examples). Last synced 2026-05-16 from
  humanizer commit `ddb4b6f`.
- Vendored authenticity-check skill, synced from the canonical
  [authenticity-check](https://github.com/hannsxpeter/authenticity-check) repo:
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
