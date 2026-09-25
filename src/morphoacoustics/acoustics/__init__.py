"""Acoustic models, backend contracts, and solver primitives."""

from .backend import SegmentedTubeBackend
from .protocol import AcousticBackend, AcousticResponse
from .segmented_tube import SegmentedTube
from .uniform_tube import UniformTube

__all__ = [
    "AcousticBackend",
    "AcousticResponse",
    "SegmentedTube",
    "SegmentedTubeBackend",
    "UniformTube",
]
