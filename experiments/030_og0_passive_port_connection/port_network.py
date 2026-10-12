"""OG-0 research-only two-organ passive acoustic port junction.

Not a universal organ graph API. Linear, rigid, lossless 1D plane waves,
one zero-volume junction, common rho/c, exp(+j omega t).
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite
from typing import Literal

import numpy as np
import numpy.typing as npt
from morphoacoustics.acoustics import UniformTube

MODEL_VERSION = "og0-experimental-0.1"


class InvalidGraph(ValueError):
    """INVALID: malformed organ/port/edge/boundary assignment."""
    status = "INVALID"


class UnsupportedGraph(ValueError):
    """UNSUPPORTED: valid topology outside the two-organ serial capability."""
    status = "UNSUPPORTED"


@dataclass(frozen=True, slots=True)
class RigidTubeOrgan:
    organ_id: str
    length_m: float
    area_m2: float

    def __post_init__(self) -> None:
        if not isinstance(self.organ_id, str) or not self.organ_id.strip():
            raise InvalidGraph("organ_id must be a nonempty string")
        for name in ("length_m", "area_m2"):
            value = getattr(self, name)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not isfinite(value) or value <= 0):
                raise InvalidGraph(f"{name} must be finite and > 0")


@dataclass(frozen=True, slots=True)
class AcousticPort:
    organ_id: str
    port_id: str
    role: Literal["inlet", "outlet"]
    kind: str = "acoustic"


@dataclass(frozen=True, slots=True)
class AcousticConnection:
    source: AcousticPort
    target: AcousticPort
    law: str = "ideal_series_junction"


@dataclass(frozen=True, slots=True)
class PortNetworkSpec:
    organs: tuple[RigidTubeOrgan, ...]
    connections: tuple[AcousticConnection, ...]
    observation_inlet: AcousticPort
    pressure_release_outlet: AcousticPort
    sound_speed_m_s: float = 343.0
    air_density_kg_m3: float = 1.2


@dataclass(frozen=True, slots=True)
class PreparedSerialGraph:
    upstream: RigidTubeOrgan
    downstream: RigidTubeOrgan
    connection: AcousticConnection
    observation_inlet: AcousticPort
    pressure_release_outlet: AcousticPort
    sound_speed_m_s: float
    air_density_kg_m3: float
    graph_sha256: str

    def _tube(self, organ: RigidTubeOrgan) -> UniformTube:
        return UniformTube(
            length_m=organ.length_m, area_m2=organ.area_m2,
            sound_speed_m_s=self.sound_speed_m_s,
            air_density_kg_m3=self.air_density_kg_m3,
        )

    def transfer_matrix(self, frequencies_hz: npt.ArrayLike) -> np.ndarray:
        frequencies = _frequencies(frequencies_hz)
        # J=I at an ideal junction in global (pressure,volume-flow) coordinates.
        return np.matmul(
            self._tube(self.upstream).transfer_matrix(frequencies),
            self._tube(self.downstream).transfer_matrix(frequencies),
        )

    def input_impedance(self, frequencies_hz: npt.ArrayLike) -> np.ndarray:
        """Pressure-release outlet; ideal poles are not regularized or hidden."""
        matrix = self.transfer_matrix(frequencies_hz)
        with np.errstate(divide="ignore", invalid="ignore"):
            return matrix[..., 0, 1] / matrix[..., 1, 1]

    def junction_audit(
        self, frequency_hz: float, *,
        outlet_flow_m3_s: complex = 1e-6,
        outlet_load: Literal["matched", "pressure_release"] = "matched",
    ) -> dict[str, float]:
        """Calculate each side via independent matrix paths, not state copying.

        B inlet uses its local B matrix; A outlet is obtained by solving
        T_A^-1 against the independently assembled whole-network inlet.
        """
        f = _frequencies([frequency_hz])
        flow = complex(outlet_flow_m3_s)
        if not (isfinite(flow.real) and isfinite(flow.imag)) or flow == 0:
            raise InvalidGraph("outlet flow must be finite and nonzero")
        if outlet_load not in ("matched", "pressure_release"):
            raise InvalidGraph("unsupported audit load")
        z_down = self.air_density_kg_m3 * self.sound_speed_m_s / self.downstream.area_m2
        p_out = z_down * flow if outlet_load == "matched" else 0j
        state_out = np.asarray([p_out, flow], dtype=np.complex128)
        t_a = self._tube(self.upstream).transfer_matrix(f)[0]
        t_b = self._tube(self.downstream).transfer_matrix(f)[0]
        p_b, u_b = t_b @ state_out
        whole_in = self.transfer_matrix(f)[0] @ state_out
        p_a, u_a = np.linalg.solve(t_a, whole_in)
        power_a = float(np.real(p_a * np.conjugate(u_a)) / 2)
        power_b = float(np.real(p_b * np.conjugate(u_b)) / 2)
        z_up = self.air_density_kg_m3 * self.sound_speed_m_s / self.upstream.area_m2
        forward = (p_b + z_up * u_b) / 2
        backward = (p_b - z_up * u_b) / 2
        r = backward / forward
        return {
            "pressure_residual_rel": float(abs(p_a-p_b)/max(1., abs(p_a), abs(p_b))),
            "flow_residual_rel": float(abs(u_a-u_b)/max(1e-12, abs(u_a), abs(u_b))),
            "power_residual_rel": float(abs(power_a-power_b)/max(1e-12, abs(power_a), abs(power_b))),
            "mean_power_w": power_b,
            "reflection_pressure_real": float(np.real(r)),
            "reflection_pressure_imag": float(np.imag(r)),
            "junction_pressure_real_pa": float(np.real(p_b)),
            "junction_pressure_imag_pa": float(np.imag(p_b)),
            "junction_flow_real_m3_s": float(np.real(u_b)),
            "junction_flow_imag_m3_s": float(np.imag(u_b)),
        }


def _frequencies(frequencies_hz: npt.ArrayLike) -> np.ndarray:
    try:
        f = np.asarray(frequencies_hz, dtype=np.float64)
    except (ValueError, TypeError, OverflowError) as exc:
        raise InvalidGraph("invalid frequencies_hz") from exc
    if (f.ndim != 1 or f.size == 0 or np.any(~np.isfinite(f))
            or np.any(f < 0)):
        raise InvalidGraph("frequency grid must be nonempty 1-D, finite and >= 0 Hz")
    return f


def _port(organ_id: str, role: str) -> AcousticPort:
    return AcousticPort(organ_id, role, role)


def vars_organ(organ: RigidTubeOrgan) -> dict[str, object]:
    return {"organ_id": organ.organ_id, "length_m": float(organ.length_m), "area_m2": float(organ.area_m2)}


def vars_port(port: AcousticPort) -> tuple[str, str, str, str]:
    return port.organ_id, port.port_id, port.role, port.kind


def prepare_serial_graph(spec: PortNetworkSpec) -> PreparedSerialGraph:
    """Validate exactly one typed A.out -> B.in edge and preserve both identities."""
    if not spec.organs:
        raise InvalidGraph("no organs")
    ids = [organ.organ_id for organ in spec.organs]
    if len(ids) != len(set(ids)):
        raise InvalidGraph("duplicate organ IDs")
    if len(spec.organs) > 2:
        raise UnsupportedGraph("only exactly two serial organs are supported")
    if len(spec.organs) != 2:
        raise InvalidGraph("exactly two organs required")
    for name in ("sound_speed_m_s", "air_density_kg_m3"):
        value = getattr(spec, name)
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not isfinite(value) or value <= 0):
            raise InvalidGraph(f"{name} must be finite and > 0")
    if not spec.connections:
        raise InvalidGraph("missing required A.out -> B.in connection")
    if len(spec.connections) != 1:
        if len(set(spec.connections)) != len(spec.connections):
            raise InvalidGraph("duplicate connections")
        raise UnsupportedGraph("multiple connections / cycles / branches unsupported")
    edge = spec.connections[0]
    by_id = {organ.organ_id: organ for organ in spec.organs}
    if not isinstance(edge, AcousticConnection):
        raise InvalidGraph("edge must be AcousticConnection")
    for port in (edge.source, edge.target, spec.observation_inlet, spec.pressure_release_outlet):
        if not isinstance(port, AcousticPort):
            raise InvalidGraph("port must be AcousticPort")
        if port.organ_id not in by_id:
            raise InvalidGraph(f"unknown organ in port: {port.organ_id!r}")
        if (port.kind != "acoustic" or port.role not in ("inlet", "outlet")
                or port.port_id != port.role):
            raise InvalidGraph("unrecognized port type/role/id")
    if edge.law != "ideal_series_junction":
        raise InvalidGraph("unsupported junction law")
    if edge.source.role != "outlet" or edge.target.role != "inlet":
        raise InvalidGraph("connection must point outlet -> inlet")
    if edge.source.organ_id == edge.target.organ_id:
        raise InvalidGraph("cannot connect an organ to itself")
    expected_in = _port(edge.source.organ_id, "inlet")
    expected_out = _port(edge.target.organ_id, "outlet")
    if spec.observation_inlet != expected_in or spec.pressure_release_outlet != expected_out:
        raise InvalidGraph("exposed inlet and pressure-release outlet do not match graph")
    payload = {
        "model_version": MODEL_VERSION,
        "upstream": vars_organ(by_id[edge.source.organ_id]),
        "downstream": vars_organ(by_id[edge.target.organ_id]),
        "connection": [list(vars_port(edge.source)), list(vars_port(edge.target)), edge.law],
        "observation_inlet": list(vars_port(expected_in)),
        "pressure_release_outlet": list(vars_port(expected_out)),
        "sound_speed_m_s": float(spec.sound_speed_m_s),
        "air_density_kg_m3": float(spec.air_density_kg_m3),
    }
    digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    return PreparedSerialGraph(
        upstream=by_id[edge.source.organ_id],
        downstream=by_id[edge.target.organ_id],
        connection=edge, observation_inlet=expected_in,
        pressure_release_outlet=expected_out,
        sound_speed_m_s=spec.sound_speed_m_s,
        air_density_kg_m3=spec.air_density_kg_m3,
        graph_sha256=digest,
    )


def reference_spec(
    *, downstream_area_m2: float = 3e-4,
    organ_order: tuple[str, str] = ("A", "B"),
) -> PortNetworkSpec:
    organs = {
        "A": RigidTubeOrgan("A", 0.08, 3e-4),
        "B": RigidTubeOrgan("B", 0.09, downstream_area_m2),
    }
    return PortNetworkSpec(
        organs=tuple(organs[organ_id] for organ_id in organ_order),
        connections=(AcousticConnection(_port("A", "outlet"), _port("B", "inlet")),),
        observation_inlet=_port("A", "inlet"),
        pressure_release_outlet=_port("B", "outlet"),
    )
