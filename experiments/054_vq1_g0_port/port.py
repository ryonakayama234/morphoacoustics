"""VQ-1 G0-P research-only inlet port on the adopted Core FIFO waveguide.

NOT a public morphoacoustics API, tissue force, fluid solver, or audio renderer.
Read-only prediction is fixed to CORE-WG-1's *pre-shift* reflected wave.
Do not import SFI-2 / SFI-3 / VF unmerged research branches.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from numbers import Real

from morphoacoustics_waveguide import PassiveWaveguideSession
from morphoacoustics_waveguide.passive_waveguide import WaveguideStep


@dataclass(frozen=True, slots=True)
class PortSnapshot:
    """Immutable, process-local identity for a *single* native FIFO tick."""

    owner_token: int
    tick: int
    state_digest: str
    b_pa: float
    z0_pa_s_m3: float
    dt_s: float


@dataclass(frozen=True, slots=True)
class PortPrediction:
    snapshot: PortSnapshot
    flow_m3_s: float
    pressure_pa: float
    source_work_j: float


class StalePortSnapshot(ValueError):
    """A snapshot is foreign, reused, or no longer describes live Core state."""


class FixedWaveguideInletPort:
    """Single-thread research adapter; public Core step/physics stay unchanged.

    The backend fingerprint intentionally reads CORE-WG-1 private FIFOs and B0 q.
    It is explicitly *not* an ABI or a concurrent, production atomic transaction.
    """

    def __init__(self, session: PassiveWaveguideSession) -> None:
        if type(session) is not PassiveWaveguideSession:
            raise TypeError("G0 supports only the native PassiveWaveguideSession")
        self._session = session

    def _state_digest(self) -> str:
        s = self._session
        # Include config so even direct outside-the-adapter configuration
        # replacement invalidates the snapshot. No float rounding or quantization.
        state = (
            s.config,
            s.ticks,
            tuple(tuple(q) for q in s.forward),
            tuple(tuple(q) for q in s.backward),
            None if s._radiation is None else s._radiation.q,
        )
        return sha256(repr(state).encode("utf-8")).hexdigest()

    def snapshot(self) -> PortSnapshot:
        s = self._session
        return PortSnapshot(
            owner_token=id(self),
            tick=s.ticks,
            state_digest=self._state_digest(),
            b_pa=float(s.backward[0][0]),
            z0_pa_s_m3=float(s.config.characteristic_impedances_pa_s_m3[0]),
            dt_s=float(s.config.timestep_s),
        )

    def _require_live(self, snapshot: PortSnapshot) -> None:
        if not isinstance(snapshot, PortSnapshot):
            raise TypeError("PortSnapshot required")
        # The digest alone does not authenticate the *payload* in a snapshot:
        # dataclasses.replace(snapshot, b_pa=...) must never change the
        # predictor without invalidating this reference.
        if snapshot != self.snapshot():
            raise StalePortSnapshot(
                "foreign, changed, stale, or already committed native snapshot"
            )

    @staticmethod
    def _real_flow(flow_m3_s: float) -> float:
        if isinstance(flow_m3_s, bool) or not isinstance(flow_m3_s, Real):
            raise ValueError("signed volume flow must be a finite real [m3/s]")
        try:
            flow = float(flow_m3_s)
        except (OverflowError, ValueError) as exc:
            raise ValueError("volume flow is not representable") from exc
        if not isfinite(flow):
            raise ValueError("signed volume flow must be finite [m3/s]")
        return flow

    def peek(self, snapshot: PortSnapshot, flow_m3_s: float) -> PortPrediction:
        """Predict inlet p and work *without advancing any Core state*."""
        self._require_live(snapshot)
        flow = self._real_flow(flow_m3_s)
        pressure = 2.0 * snapshot.b_pa + snapshot.z0_pa_s_m3 * flow
        work = snapshot.dt_s * pressure * flow
        if not isfinite(pressure) or not isfinite(work):
            raise FloatingPointError("nonfinite inlet port candidate")
        return PortPrediction(snapshot, flow, pressure, work)

    def commit_once(self, snapshot: PortSnapshot, flow_m3_s: float) -> WaveguideStep:
        """Perform exactly one *real Core step*; Core owns failure atomicity.

        A failed step must not advance the real session; the same snapshot may
        be retried after an overflow with an independently valid flow.
        """
        prediction = self.peek(snapshot, flow_m3_s)  # one validated flow value
        return self._session.step(prediction.flow_m3_s)
