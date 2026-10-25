# CORE-WG-1 Amendment 01 — frozen scientific source identity boundary

Status: PROSPECTIVE correction to **packaging location only**, recorded *before* moving code. Date: 2026-10-25 JST.

## Observed failure (preserved)
The exact candidate HEAD `87229c1b9a9141e8135fffde67e79421bff1eb3f` has final Codex review (no major issues), but GitHub Actions [tests #40153560727](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40153560727) **FAILED** (5 failed, 749 passed, 9 skipped on Python 3.13), and [pinned B2-A differential #40153560707](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40153560707) **FAILED** before comparison. This is not a physical validation pass.

Actual root cause from CI logs: adding `src/morphoacoustics/acoustics/passive_waveguide.py` changes the complete immutable package inventory deliberately pinned by `src/morphoacoustics/integration/limited_live.py::_verify_frozen_sources_before_import`, and also by Experiment 028's implementation identity check (which enumerates `src/morphoacoustics/acoustics/*.py`). These checks correctly reject unrecognized modifications to an old frozen scientific runtime. **Do not weaken or rebaseline old frozen manifests, mutate tests, or rewrite historical results.**

## Proposed boundary correction
Put the *identical proposed physics candidate* in a new explicit opt-in in-repository scientific package `src/morphoacoustics_waveguide/passive_waveguide.py`, with a package initializer, rather than adding to `src/morphoacoustics/acoustics/`. The new package depends on, but does not mutate, Core's `Tract1DGeometry`. It belongs to the Core repo as a **companion candidate**, not an adopted built-in backend. Change new tests and differential audit imports only. Remove the unadopted old candidate path. The existing published Core package source inventory, legacy X2a, frozen Experiment 028 and their previously accepted evidence must remain byte-for-byte unchanged. No public Core export or runtime switch.

Scientific acceptance thresholds, 16-section waveform clock, B0 port and provenance frozen in Gate A remain **unchanged**. This correction does not authorize new scientific claims; independently re-run physics and archived differential gates on the new HEAD and re-request code review as appropriate.

## Later production adoption
A real public Core replacement requires a *new prospective* frozen-manifest evolution plan (separate immutable runtime version and explicit upstream adapter), not silently editing or allowing unregistered additions through the historical preimport audit. The companion package can itself be merged into `main` as opt-in, once passed, without replacing existing `morphoacoustics`. The later built-in default path is a separate decision supported by full regressions and Studio physical-Take testing.

## Required falsification
- Old frozen tests must pass **without test/baseline changes**.
- A deliberately modified old audited module must still fail closed.
- New candidate tests and pinned B2-A M0/M1 + B0 nonzero-state differential must execute and pass.
- Evidence ledger must record which source SHA, exact action run and reviewer result were tested.
