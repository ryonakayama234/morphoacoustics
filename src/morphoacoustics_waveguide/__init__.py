"""Opt-in Core-repository acoustic research companion; not the default Core backend.

This separate import namespace keeps frozen legacy Core scientific evidence immutable.
""" 

from .passive_waveguide import (
    PassiveWaveguideConfig,
    PassiveWaveguideSession,
    WaveguideStep,
    scatter_pressures,
)

__all__ = [
    "PassiveWaveguideConfig",
    "PassiveWaveguideSession",
    "WaveguideStep",
    "scatter_pressures",
]
