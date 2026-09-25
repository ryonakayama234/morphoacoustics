"""Acoustic models, backend contracts, and solver primitives."""

from .backend import ImpedanceRequest, ImpedanceResponse, SegmentedTubeBackend
from .protocol import AcousticBackend
from .segmented_tube import SegmentedTube
from .uniform_tube import UniformTube

__all__ = [
    "AcousticBackend",
    "ImpedanceRequest",
    "ImpedanceResponse",
    "SegmentedTube",
    "SegmentedTubeBackend",
    "UniformTube",
]
