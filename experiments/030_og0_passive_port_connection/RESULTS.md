# OG-0 results — provisional

- Wolfram independently calculated oracle: [og0_wolfram.json](../../tests/scientific/oracles/og0_wolfram.json).
- Local preliminary smoke testing: six targeted tests passed against a **minimal local reconstruction of the published Fidelity-0 class interfaces**. This is not equivalent to testing the real repository integration.
- GitHub Actions `tests` workflow on this Draft PR: **pending verification**. Record the exact run and failure/closure before adopting.
- Independent numerical/physical audit: **pending**.
- Independent code audit: **pending**.
- Accepted scientific decision: **NOT ADOPTED**.

The locally reconstructed smoke run at Python 3.13.5 / NumPy 2.3.5 reported a normalized equal-area matrix error `2.22e-16`, determinant error `2.22e-16`, mismatched 733-Hz input-impedance relative error `3.08e-16`, and junction pressure, flow, mean-power normalized residuals of `3.78e-16`, `1.06e-16`, and `1.54e-16`. Recheck all against the *real repo* before claiming integration success. Do not treat small numerical errors alone as general proof of organ-graph validity.
