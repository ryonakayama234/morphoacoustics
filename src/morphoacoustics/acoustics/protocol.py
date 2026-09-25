from __future__ import annotations

from typing import Protocol, TypeVar

StateT_contra = TypeVar("StateT_contra", contravariant=True)
RequestT_contra = TypeVar("RequestT_contra", contravariant=True)
ObservationT_co = TypeVar("ObservationT_co", covariant=True)


class AcousticBackend(Protocol[StateT_contra, RequestT_contra, ObservationT_co]):
    """Evaluate an acoustic request for one backend-specific physical state."""

    def simulate_snapshot(
        self,
        state: StateT_contra,
        request: RequestT_contra,
    ) -> ObservationT_co:
        ...
