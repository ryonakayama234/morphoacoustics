"""Opt-in Core-repository acoustic research companion; not the default Core backend.

This separate import namespace keeps frozen legacy Core scientific evidence immutable.
""" 

from .observations import MouthPortMonitorTake, render_mouth_port_monitor
from .passive_waveguide import (
    PassiveWaveguideConfig,
    PassiveWaveguideSession,
    WaveguideStep,
    scatter_pressures,
)

__all__ = [
    "MouthPortMonitorTake",
    "render_mouth_port_monitor",
    "PassiveWaveguideConfig",
    "PassiveWaveguideSession",
    "WaveguideStep",
    "scatter_pressures",
]
