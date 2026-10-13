"""Experiment 039 only: typed passive acoustic organ graph -> prepared serial backend.

This module is NOT a stable Core API and does NOT claim general organ graphs.
Protocol: PREREGISTRATION.md; frozen independent reference: wolfram/og2_oracle.json.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math

import numpy as np
import numpy.typing as npt

from morphoacoustics.acoustics import UniformTube

BACKEND_ID = "research.og2.serial_uniform_tube.v1"
SCHEMA = "og2.blueprint.v1"
PORT_KIND = "acoustic.p_u"
SERIES_LAW = "ideal.series.p_u"
BRANCH_LAW = "ideal.branch3.p_u"
ADOPTED_BASELINE_SHA = "8868df1188443fc4523533c6cb0bb9cd72995c32"


class GraphError(ValueError):
    """A typed research outcome; INVALID is not UNSUPPORTED or INFEASIBLE."""

    def __init__(self, status: str, code: str, path: str) -> None:
        self.status = status
        self.code = code
        self.path = path
        super().__init__(f"{status}:{code}:{path}")


def invalid(code: str, path: str) -> None:
    raise GraphError("INVALID", code, path)


@dataclass(frozen=True, slots=True)
class Port:
    id: str
    direction: str
    kind: str = PORT_KIND


@dataclass(frozen=True, slots=True)
class Organ:
    id: str
    revision: str
    length_m: float
    area_m2: float
    inlet: Port
    outlet: Port
    sound_speed_m_s: float = 343.0
    air_density_kg_m3: float = 1.21


@dataclass(frozen=True, slots=True)
class Junction:
    id: str
    law: str
    ports: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Blueprint:
    schema: str
    organs: tuple[Organ, ...]
    junctions: tuple[Junction, ...]
    source_port: str
    load_ports: tuple[str, ...]
    termination: str = "matched"


@dataclass(frozen=True, slots=True)
class PreparedPhysicalGraph:
    """Immutable bindings; each retained physical node is a separate UniformTube."""

    blueprint: Blueprint
    organs_in_path_order: tuple[Organ, Organ]
    tubes_in_path_order: tuple[UniformTube, UniformTube]
    junction: Junction
    port_mapping: tuple[tuple[str, str, str], ...]
    preparation_digest: str
    backend_id: str = BACKEND_ID

    @property
    def reference_impedance(self) -> float:
        return self.tubes_in_path_order[0].characteristic_impedance_pa_s_m3

    def transfer_matrix(self, frequencies_hz: npt.ArrayLike) -> np.ndarray:
        """[p_A.in,U_A.in] = (T_A @ I_junction @ T_B)[p_B.out,U_B.out]."""
        a, b = self.tubes_in_path_order
        junction_p_u: npt.NDArray[np.complex128] = np.eye(2, dtype=np.complex128)
        return a.transfer_matrix(frequencies_hz) @ junction_p_u @ b.transfer_matrix(
            frequencies_hz
        )

    def scaled_transfer_matrix(self, frequencies_hz: npt.ArrayLike) -> np.ndarray:
        """Dimensionless S T S^-1, S=diag(1,Z_ref)."""
        z = self.reference_impedance
        d: npt.NDArray[np.complex128] = np.diag([1.0, z]).astype(np.complex128)
        dinv: npt.NDArray[np.complex128] = np.diag([1.0, 1.0 / z]).astype(np.complex128)
        return d @ self.transfer_matrix(frequencies_hz) @ dinv

    def outlet_load_impedance(self) -> float:
        if self.blueprint.termination == "pressure_release":
            return 0.0
        return self.tubes_in_path_order[-1].characteristic_impedance_pa_s_m3

    def interface_scattering(self) -> tuple[float, float, float, float]:
        """Isolated, matched traveling-wave interface, NOT finite-tube outlet power."""
        za = self.tubes_in_path_order[0].characteristic_impedance_pa_s_m3
        zb = self.tubes_in_path_order[1].characteristic_impedance_pa_s_m3
        reflected = (zb - za) / (zb + za)
        transmitted = 1.0 + reflected
        return (
            reflected,
            transmitted,
            reflected * reflected,
            (za / zb) * transmitted * transmitted,
        )


def _positive_finite(value: object, path: str) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        invalid("NONPOSITIVE_OR_NONFINITE", path)


def _text(value: object, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        invalid("EMPTY_IDENTIFIER", path)


def _canonical_blueprint(blueprint: Blueprint) -> dict[str, object]:
    # Deliberately use typed SI quantities, not implicit display values or Python
    # object repr; sorted order is independent of input tuple ordering.
    return {
        "schema": blueprint.schema,
        "backend_id": BACKEND_ID,
        "baseline_sha": ADOPTED_BASELINE_SHA,
        "organs": [
            {
                "id": organ.id,
                "revision": organ.revision,
                "length_m": organ.length_m,
                "area_m2": organ.area_m2,
                "sound_speed_m_s": organ.sound_speed_m_s,
                "air_density_kg_m3": organ.air_density_kg_m3,
                "inlet": (organ.inlet.id, organ.inlet.direction, organ.inlet.kind),
                "outlet": (organ.outlet.id, organ.outlet.direction, organ.outlet.kind),
            }
            for organ in sorted(blueprint.organs, key=lambda item: item.id)
        ],
        "junctions": [
            {"id": edge.id, "law": edge.law, "ports": list(edge.ports)}
            for edge in sorted(blueprint.junctions, key=lambda item: item.id)
        ],
        "source_port": blueprint.source_port,
        "load_ports": sorted(blueprint.load_ports),
        "termination": blueprint.termination,
    }


def validate(blueprint: Blueprint) -> None:
    """Structural validity first; solver capability is checked by prepare()."""
    if blueprint.schema != SCHEMA:
        invalid("UNKNOWN_SCHEMA", "schema")
    if not blueprint.organs:
        invalid("NO_ORGANS", "organs")
    if not blueprint.junctions:
        invalid("NO_JUNCTIONS", "junctions")
    if blueprint.termination not in ("matched", "pressure_release"):
        invalid("UNKNOWN_TERMINATION", "termination")

    nodes: set[str] = set()
    ports: dict[str, tuple[str, str]] = {}
    for organ in blueprint.organs:
        _text(organ.id, "organ.id")
        _text(organ.revision, f"organ.{organ.id}.revision")
        if organ.id in nodes:
            invalid("DUPLICATE_ORGAN", organ.id)
        nodes.add(organ.id)
        for field in ("length_m", "area_m2", "sound_speed_m_s", "air_density_kg_m3"):
            _positive_finite(getattr(organ, field), f"organ.{organ.id}.{field}")
        # Numeric validity extends to the *derived* p/U state, not just SI inputs.
        # Valid positive subnormal areas can make rho*c/A infinite in float64;
        # a positive but subnormal impedance can make S^-1 nonfinite instead.
        impedance = (
            organ.air_density_kg_m3 * organ.sound_speed_m_s / organ.area_m2
        )
        if (
            not math.isfinite(impedance)
            or impedance <= 0.0
            or not math.isfinite(1.0 / impedance)
        ):
            invalid("NONFINITE_DERIVED_IMPEDANCE", f"organ.{organ.id}.impedance")
        for role, port in (("inlet", organ.inlet), ("outlet", organ.outlet)):
            _text(port.id, f"organ.{organ.id}.{role}.id")
            if port.kind != PORT_KIND:
                invalid("WRONG_PORT_KIND", port.id)
            if port.direction != role:
                invalid("WRONG_PORT_DIRECTION", port.id)
            if port.id in ports:
                invalid("DUPLICATE_PORT", port.id)
            ports[port.id] = (organ.id, role)

    _text(blueprint.source_port, "source_port")
    if blueprint.source_port not in ports:
        invalid("UNKNOWN_SOURCE_PORT", blueprint.source_port)
    if ports[blueprint.source_port][1] != "inlet":
        invalid("WRONG_SOURCE_DIRECTION", blueprint.source_port)
    if not blueprint.load_ports:
        invalid("MISSING_LOAD", "load_ports")
    assigned: set[str] = {blueprint.source_port}
    for load in blueprint.load_ports:
        if load not in ports:
            invalid("UNKNOWN_LOAD_PORT", load)
        if ports[load][1] != "outlet":
            invalid("WRONG_LOAD_DIRECTION", load)
        if load in assigned:
            invalid("DUPLICATE_CONNECTION", load)
        assigned.add(load)

    edge_ids: set[str] = set()
    for edge in blueprint.junctions:
        _text(edge.id, "junction.id")
        if edge.id in edge_ids:
            invalid("DUPLICATE_JUNCTION", edge.id)
        edge_ids.add(edge.id)
        if edge.law not in (SERIES_LAW, BRANCH_LAW):
            invalid("UNKNOWN_JUNCTION_LAW", edge.id)
        n = 2 if edge.law == SERIES_LAW else 3
        if len(edge.ports) != n:
            invalid("JUNCTION_ARITY", edge.id)
        expected_roles = ("outlet",) + ("inlet",) * (n - 1)
        for i, (port_id, expected_role) in enumerate(zip(edge.ports, expected_roles)):
            if port_id not in ports:
                invalid("UNKNOWN_EDGE_PORT", f"{edge.id}:{port_id}")
            if ports[port_id][1] != expected_role:
                invalid("WRONG_EDGE_DIRECTION", f"{edge.id}:{port_id}@{i}")
            if port_id in assigned:
                invalid("DUPLICATE_CONNECTION", f"{edge.id}:{port_id}")
            assigned.add(port_id)
        if len({ports[port][0] for port in edge.ports}) != n:
            invalid("SELF_CONNECTION", edge.id)

    unassigned = sorted(set(ports) - assigned)
    if unassigned:
        invalid("UNCONNECTED_PORT", unassigned[0])

    # Serial two-node and three-port branch fixtures are acyclic by design;
    # these checks reject accidentally disconnected or cyclic general fixtures.
    adjacency: dict[str, set[str]] = {organ.id: set() for organ in blueprint.organs}
    for edge in blueprint.junctions:
        upstream = ports[edge.ports[0]][0]
        for port_id in edge.ports[1:]:
            adjacency[upstream].add(ports[port_id][0])
    visited: set[str] = set()
    active: set[str] = set()

    def visit(node: str) -> None:
        if node in active:
            invalid("CYCLE", node)
        if node in visited:
            return
        active.add(node)
        for downstream in sorted(adjacency[node]):
            visit(downstream)
        active.remove(node)
        visited.add(node)

    visit(ports[blueprint.source_port][0])
    if visited != nodes:
        invalid("DISCONNECTED_GRAPH", ",".join(sorted(nodes - visited)))


def prepare(blueprint: Blueprint) -> PreparedPhysicalGraph:
    """Only the explicitly declared two-node one-junction series backend."""
    validate(blueprint)
    if (
        len(blueprint.organs) != 2
        or len(blueprint.junctions) != 1
        or blueprint.junctions[0].law != SERIES_LAW
        or len(blueprint.load_ports) != 1
    ):
        raise GraphError("UNSUPPORTED", "SERIAL_BACKEND_ONLY", BACKEND_ID)
    nodes = {organ.id: organ for organ in blueprint.organs}
    inlet_owner = next(
        organ for organ in blueprint.organs
        if organ.inlet.id == blueprint.source_port
    )
    outlet_owner = next(
        organ for organ in blueprint.organs
        if organ.outlet.id == blueprint.load_ports[0]
    )
    edge = blueprint.junctions[0]
    if edge.ports != (inlet_owner.outlet.id, outlet_owner.inlet.id):
        invalid("EDGE_PATH_MISMATCH", edge.id)
    if inlet_owner.id == outlet_owner.id:
        invalid("SAME_TERMINAL_ORGAN", inlet_owner.id)
    if (
        inlet_owner.sound_speed_m_s != outlet_owner.sound_speed_m_s
        or inlet_owner.air_density_kg_m3 != outlet_owner.air_density_kg_m3
    ):
        raise GraphError("UNSUPPORTED", "MIXED_MEDIUM", edge.id)

    ordered = (inlet_owner, outlet_owner)
    tubes = tuple(
        UniformTube(
            length_m=organ.length_m,
            area_m2=organ.area_m2,
            sound_speed_m_s=organ.sound_speed_m_s,
            air_density_kg_m3=organ.air_density_kg_m3,
        )
        for organ in ordered
    )
    data = _canonical_blueprint(blueprint)
    encoded = json.dumps(
        data, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    mapping = (
        (inlet_owner.id, inlet_owner.inlet.id, inlet_owner.outlet.id),
        (outlet_owner.id, outlet_owner.inlet.id, outlet_owner.outlet.id),
    )
    return PreparedPhysicalGraph(
        blueprint=blueprint,
        organs_in_path_order=ordered,
        tubes_in_path_order=(tubes[0], tubes[1]),
        junction=edge,
        port_mapping=mapping,
        preparation_digest=sha256(encoded).hexdigest(),
    )


def fixture(
    *, area_b: float = 0.0006, revision_b: str = "r1",
    termination: str = "matched",
) -> Blueprint:
    """Immutable frozen research fixture; no implicit physics inferred from a UI."""
    a = Organ(
        "organ-A", "r1", 0.08, 0.0003,
        Port("organ-A.in", "inlet"), Port("organ-A.out", "outlet"),
    )
    b = Organ(
        "organ-B", revision_b, 0.09, area_b,
        Port("organ-B.in", "inlet"), Port("organ-B.out", "outlet"),
    )
    return Blueprint(
        SCHEMA, (a, b),
        (Junction("edge-AB", SERIES_LAW, ("organ-A.out", "organ-B.in")),),
        "organ-A.in", ("organ-B.out",), termination,
    )


def branch_fixture() -> Blueprint:
    """A *valid* 3-port junction graph; outside serial backend capability."""
    ab = fixture()
    c = Organ(
        "organ-C", "r1", 0.07, 0.0004,
        Port("organ-C.in", "inlet"), Port("organ-C.out", "outlet"),
    )
    return Blueprint(
        SCHEMA, (*ab.organs, c),
        (Junction("branch-ABC", BRANCH_LAW,
                  ("organ-A.out", "organ-B.in", "organ-C.in")),),
        "organ-A.in", ("organ-B.out", "organ-C.out"), "matched",
    )
