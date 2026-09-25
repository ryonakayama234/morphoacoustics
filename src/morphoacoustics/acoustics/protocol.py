from __future__ import annotations

from typing import Protocol, TypeVar

StateT = TypeVar("StateT")
RequestT = TypeVar("RequestT")
ObservationT = TypeVar("ObservationT")


class AcousticBackend(Protocol[StateT, RequestT, ObservationT]):
    """Evaluate an acoustic request for one backend-specific physical state."""

    def simulate_snapshot(
        self,
        state: StateT,
        request: RequestT,
    ) -> ObservationT:
        ...
