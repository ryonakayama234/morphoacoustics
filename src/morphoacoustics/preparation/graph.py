"""OG-3 Gate B candidate: typed two-tube graph preparation and acoustic observation.

No Experiment039 runtime import, no general graph solver, no WAV generation.
Review/adoption of this new public-facing submodule is pending.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
import struct
from typing import Any

import numpy as np
import numpy.typing as npt

from morphoacoustics.acoustics.uniform_tube import UniformTube
from morphoacoustics.physical.organ_graph import (
    AcousticJunction, AcousticPort, BRANCH_LAW, OrganGraphBlueprint,
    PORT_KIND, SERIES_LAW, SCHEMA, PassiveTubeOrgan, graph_from_dict,
    graph_to_dict,
)

BACKEND_ID = "og3.fixed.passive.serial2.pu.v1"
DIGEST_VERSION = "og3.binary64-be-json.v1"
MAX_FREQUENCY_HZ = 4000.0
MAX_FREQUENCY_POINTS = 4096
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class GraphError(ValueError):
    """INVALID, UNSUPPORTED, or NUMERICALLY_UNRESOLVED; never silently repair."""

    def __init__(self, status: str, code: str, path: str) -> None:
        self.status = status
        self.code = code
        self.path = path
        super().__init__(f"{status}:{code}:{path}")


def _invalid(code: str, path: str) -> None:
    raise GraphError("INVALID", code, path)


def _id(s: object, path: str) -> None:
    if not isinstance(s, str) or not _ID.fullmatch(s):
        _invalid("BAD_ASCII_IDENTIFIER", path)


def _positive_number(value: object, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _invalid("BAD_NUMERIC_TYPE", path)
    try:
        f = float(value)
    except (OverflowError, ValueError):
        _invalid("NONFINITE_SI_QUANTITY", path)
    if not math.isfinite(f) or f <= 0:
        _invalid("NONPOSITIVE_OR_NONFINITE", path)
    return f


def _impedance(node: PassiveTubeOrgan) -> float:
    rho = _positive_number(node.air_density_kg_m3, f"{node.id}.rho")
    c = _positive_number(node.sound_speed_m_s, f"{node.id}.c")
    area = _positive_number(node.area_m2, f"{node.id}.area_m2")
    z = rho * c / area
    if (not math.isfinite(z) or z <= 0 or
            not math.isfinite(1 / z) or 1 / z == 0):
        _invalid("NONFINITE_DERIVED_IMPEDANCE", f"{node.id}.impedance")
    return z


def validate_graph(graph: OrganGraphBlueprint) -> None:
    """Structural/physical validity only; capability is tested by prepare_graph."""
    if not isinstance(graph, OrganGraphBlueprint):
        _invalid("WRONG_BLUEPRINT_TYPE", "graph")
    if graph.schema != SCHEMA:
        _invalid("UNKNOWN_SCHEMA", "schema")
    if not isinstance(graph.organs, tuple) or not graph.organs:
        _invalid("NO_ORGANS", "organs")
    if not isinstance(graph.junctions, tuple) or not graph.junctions:
        _invalid("NO_JUNCTIONS", "junctions")
    if graph.termination not in ("matched", "pressure_release"):
        _invalid("UNKNOWN_TERMINATION", "termination")
    nodes: dict[str, PassiveTubeOrgan] = {}
    ports: dict[str, tuple[str, str]] = {}
    for organ in graph.organs:
        if not isinstance(organ, PassiveTubeOrgan):
            _invalid("WRONG_ORGAN_TYPE", "organs")
        _id(organ.id, "organ.id")
        _id(organ.revision, f"{organ.id}.revision")
        if organ.id in nodes:
            _invalid("DUPLICATE_ORGAN", organ.id)
        nodes[organ.id] = organ
        _positive_number(organ.length_m, f"{organ.id}.length_m")
        _impedance(organ)
        for direction, port in (("inlet", organ.inlet), ("outlet", organ.outlet)):
            if not isinstance(port, AcousticPort):
                _invalid("WRONG_PORT_TYPE", f"{organ.id}.{direction}")
            _id(port.id, f"{organ.id}.{direction}.id")
            if port.kind != PORT_KIND:
                _invalid("WRONG_PORT_KIND", port.id)
            if port.direction != direction:
                _invalid("WRONG_PORT_DIRECTION", port.id)
            if port.id in ports:
                _invalid("DUPLICATE_PORT", port.id)
            ports[port.id] = (organ.id, direction)

    _id(graph.source_port, "source_port")
    if graph.source_port not in ports:
        _invalid("UNKNOWN_SOURCE_PORT", graph.source_port)
    if ports[graph.source_port][1] != "inlet":
        _invalid("WRONG_SOURCE_DIRECTION", graph.source_port)
    if not isinstance(graph.load_ports, tuple) or not graph.load_ports:
        _invalid("MISSING_LOAD", "load_ports")
    assigned: set[str] = {graph.source_port}
    for load in graph.load_ports:
        _id(load, "load_port")
        if load not in ports:
            _invalid("UNKNOWN_LOAD_PORT", load)
        if ports[load][1] != "outlet":
            _invalid("WRONG_LOAD_DIRECTION", load)
        if load in assigned:
            _invalid("DUPLICATE_CONNECTION", load)
        assigned.add(load)
    edge_ids: set[str] = set()
    adjacent: dict[str, set[str]] = {name: set() for name in nodes}
    for edge in graph.junctions:
        if not isinstance(edge, AcousticJunction):
            _invalid("WRONG_EDGE_TYPE", "junctions")
        _id(edge.id, "edge.id")
        if edge.id in edge_ids:
            _invalid("DUPLICATE_JUNCTION", edge.id)
        edge_ids.add(edge.id)
        if edge.law not in (SERIES_LAW, BRANCH_LAW):
            _invalid("UNKNOWN_LAW", edge.id)
        needed = 2 if edge.law == SERIES_LAW else 3
        if not isinstance(edge.ports, tuple) or len(edge.ports) != needed:
            _invalid("JUNCTION_ARITY", edge.id)
        owned: set[str] = set()
        for i, port in enumerate(edge.ports):
            _id(port, f"{edge.id}.port")
            if port not in ports:
                _invalid("UNKNOWN_EDGE_PORT", f"{edge.id}:{port}")
            role = "outlet" if i == 0 else "inlet"
            if ports[port][1] != role:
                _invalid("WRONG_EDGE_DIRECTION", f"{edge.id}:{port}")
            if port in assigned:
                _invalid("DUPLICATE_CONNECTION", f"{edge.id}:{port}")
            assigned.add(port)
            owned.add(ports[port][0])
        if len(owned) != needed:
            _invalid("SELF_CONNECTION", edge.id)
        upstream = ports[edge.ports[0]][0]
        for port in edge.ports[1:]:
            adjacent[upstream].add(ports[port][0])
    unassigned = sorted(set(ports) - assigned)
    if unassigned:
        _invalid("UNCONNECTED_PORT", unassigned[0])

    active: set[str] = set()
    visited: set[str] = set()
    def visit(name: str) -> None:
        if name in active:
            _invalid("CYCLE", name)
        if name in visited:
            return
        active.add(name)
        for other in sorted(adjacent[name]):
            visit(other)
        active.remove(name)
        visited.add(name)
    visit(ports[graph.source_port][0])
    if visited != set(nodes):
        _invalid("DISCONNECTED_GRAPH", ",".join(sorted(set(nodes) - visited)))


def _bits(v: float) -> str:
    """Exact big-endian IEEE-754 binary64 representation; no JS float formatting."""
    return struct.pack(">d", v).hex()


def _canonical(graph: OrganGraphBlueprint) -> bytes:
    return json.dumps({
        "domain": "morphoacoustics.og3.blueprint.v1",
        "schema": graph.schema, "termination": graph.termination,
        "source_port": graph.source_port,
        "load_ports": sorted(graph.load_ports),
        "organs": [
            {"id": n.id, "revision": n.revision,
             "length_m": _bits(float(n.length_m)),
             "area_m2": _bits(float(n.area_m2)),
             "c_m_s": _bits(float(n.sound_speed_m_s)),
             "rho_kg_m3": _bits(float(n.air_density_kg_m3)),
             "inlet": [n.inlet.id, n.inlet.direction, n.inlet.kind],
             "outlet": [n.outlet.id, n.outlet.direction, n.outlet.kind]}
            for n in sorted(graph.organs, key=lambda n: n.id)
        ],
        "junctions": [
            {"id": j.id, "law": j.law, "ports": list(j.ports)}
            for j in sorted(graph.junctions, key=lambda j: j.id)
        ],
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")


def _hash(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class PreparedPhysicalGraph:
    blueprint: OrganGraphBlueprint
    organs_in_path_order: tuple[PassiveTubeOrgan, PassiveTubeOrgan]
    tubes_in_path_order: tuple[UniformTube, UniformTube]
    junction: AcousticJunction
    port_mapping: tuple[tuple[str, str, str], ...]
    blueprint_digest: str
    preparation_digest: str
    backend_id: str = BACKEND_ID

    def to_snapshot(self) -> dict[str, Any]:
        return {"schema": "og3.prepared.snapshot.v1",
                "backend_id": self.backend_id,
                "blueprint": graph_to_dict(self.blueprint),
                "blueprint_digest": self.blueprint_digest,
                "preparation_digest": self.preparation_digest}


def prepare_graph(graph: OrganGraphBlueprint) -> PreparedPhysicalGraph:
    validate_graph(graph)
    if (len(graph.organs) != 2 or len(graph.junctions) != 1 or
            graph.junctions[0].law != SERIES_LAW or len(graph.load_ports) != 1):
        raise GraphError("UNSUPPORTED", "FIXED2_SERIAL_ONLY", BACKEND_ID)
    first = next(n for n in graph.organs if n.inlet.id == graph.source_port)
    last = next(n for n in graph.organs if n.outlet.id == graph.load_ports[0])
    edge = graph.junctions[0]
    if first.id == last.id or edge.ports != (first.outlet.id, last.inlet.id):
        _invalid("EDGE_PATH_MISMATCH", edge.id)
    if (float(first.sound_speed_m_s) != float(last.sound_speed_m_s) or
            float(first.air_density_kg_m3) != float(last.air_density_kg_m3)):
        raise GraphError("UNSUPPORTED", "MIXED_MEDIUM", edge.id)
    ordered = (first, last)
    tubes = tuple(UniformTube(
        length_m=float(n.length_m), area_m2=float(n.area_m2),
        sound_speed_m_s=float(n.sound_speed_m_s),
        air_density_kg_m3=float(n.air_density_kg_m3)
    ) for n in ordered)
    mapping = tuple((n.id, n.inlet.id, n.outlet.id) for n in ordered)
    bp_digest = _hash(_canonical(graph))
    encoded = json.dumps({
        "domain": "morphoacoustics.og3.preparation.v1",
        "digest_version": DIGEST_VERSION,
        "backend_id": BACKEND_ID, "blueprint_digest": bp_digest,
        "port_mapping": mapping, "junction_law": edge.law
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return PreparedPhysicalGraph(graph, ordered, (tubes[0], tubes[1]), edge,
                                 mapping, bp_digest, _hash(encoded))


def restore_prepared(snapshot: dict[str, Any]) -> PreparedPhysicalGraph:
    if not isinstance(snapshot, dict) or set(snapshot) != {
        "schema", "backend_id", "blueprint", "blueprint_digest", "preparation_digest"
    } or snapshot["schema"] != "og3.prepared.snapshot.v1":
        _invalid("WRONG_SNAPSHOT", "snapshot")
    if snapshot["backend_id"] != BACKEND_ID:
        raise GraphError("UNSUPPORTED", "SNAPSHOT_BACKEND", "backend_id")
    try:
        graph = graph_from_dict(snapshot["blueprint"])
        prepared = prepare_graph(graph)
    except (TypeError, ValueError, KeyError) as ex:
        if isinstance(ex, GraphError):
            raise
        _invalid("MALFORMED_SNAPSHOT", "blueprint")
    if (prepared.blueprint_digest != snapshot["blueprint_digest"] or
            prepared.preparation_digest != snapshot["preparation_digest"]):
        _invalid("SNAPSHOT_DIGEST_MISMATCH", "snapshot")
    return prepared


@dataclass(frozen=True, slots=True)
class ComplexTransferObservation:
    frequencies_hz: tuple[float, ...]
    rows_re_im: tuple[tuple[tuple[float, float], ...], ...]
    preparation_digest: str
    observation_digest: str
    backend_id: str = BACKEND_ID
    kind: str = "unloaded_full_complex_two_port"

    def matrix_numpy(self) -> np.ndarray:
        result = np.array([
            [complex(re, im) for re, im in row]
            for row in self.rows_re_im
        ], dtype=np.complex128)
        return result.reshape(len(self.frequencies_hz), 2, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend_id": self.backend_id, "kind": self.kind,
            "frequencies_hz": list(self.frequencies_hz),
            "transfer_matrix_rowmajor_re_im": [
                [list(pair) for pair in row] for row in self.rows_re_im
            ],
            "preparation_digest": self.preparation_digest,
            "observation_digest": self.observation_digest,
        }


def observe_transfer(
    graph: PreparedPhysicalGraph, frequencies_hz: npt.ArrayLike,
) -> ComplexTransferObservation:
    """Return immutable full complex *unloaded* two-port, not source or WAV."""
    if not isinstance(graph, PreparedPhysicalGraph) or graph.backend_id != BACKEND_ID:
        raise GraphError("UNSUPPORTED", "WRONG_PREPARED_BACKEND", "prepared")
    try:
        grid = np.asarray(frequencies_hz)
    except (ValueError, TypeError, OverflowError) as error:
        raise GraphError("INVALID", "BAD_FREQUENCY_SHAPE", "frequencies_hz") from error
    if (grid.ndim != 1 or not (1 <= grid.size <= MAX_FREQUENCY_POINTS) or
            grid.dtype.kind not in "ifu"):
        _invalid("BAD_FREQUENCY_SHAPE", "frequencies_hz")
    fs: list[float] = []
    for value in grid:
        if isinstance(value, (bool, np.bool_)):
            _invalid("BAD_FREQUENCY_TYPE", "frequencies_hz")
        try:
            f = float(value)
        except (ValueError, OverflowError):
            _invalid("BAD_FREQUENCY_TYPE", "frequencies_hz")
        if not math.isfinite(f) or f < 0:
            _invalid("NEGATIVE_OR_NONFINITE_FREQUENCY", "frequencies_hz")
        if f > MAX_FREQUENCY_HZ:
            raise GraphError("UNSUPPORTED", "FREQUENCY_CAPABILITY", "frequencies_hz")
        fs.append(0.0 if f == 0.0 else f)  # -0.0 canonicalizes before digest
    farray = np.asarray(fs, dtype=np.float64)
    a, b = graph.tubes_in_path_order
    with np.errstate(all="ignore"):
        raw = a.transfer_matrix(farray) @ b.transfer_matrix(farray)
        z = a.characteristic_impedance_pa_s_m3
        scaled = np.empty(raw.shape, dtype=np.complex128)
        scaled[:, 0, 0] = raw[:, 0, 0]
        scaled[:, 0, 1] = raw[:, 0, 1] / z
        scaled[:, 1, 0] = raw[:, 1, 0] * z
        scaled[:, 1, 1] = raw[:, 1, 1]
    if not np.all(np.isfinite(scaled)) or not np.all(np.isfinite(raw)):
        raise GraphError("NUMERICALLY_UNRESOLVED", "NONFINITE_TRANSFER", "matrix")
    rows = tuple(
        tuple((float(v.real), float(v.imag)) for v in scaled[i].reshape(4))
        for i in range(len(fs))
    )
    packed = json.dumps({
        "domain": "morphoacoustics.og3.observation.v1",
        "backend": BACKEND_ID, "prepared": graph.preparation_digest,
        "kind": "unloaded_full_complex_two_port",
        "frequencies_be64": [_bits(f) for f in fs],
        "matrix_re_im_be64": [
            [[_bits(pair[0]), _bits(pair[1])] for pair in row] for row in rows
        ],
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return ComplexTransferObservation(tuple(fs), rows, graph.preparation_digest, _hash(packed))
