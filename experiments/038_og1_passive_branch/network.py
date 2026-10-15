"""Experiment-local typed passive graph. Not a production morphology API."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite

import numpy as np
from morphoacoustics.acoustics import UniformTube

MODEL_VERSION = "og1-experimental-v1"
U_REF = 1e-6
CONDITION_LIMIT = 1e8


class InvalidGraph(ValueError):
    status = "INVALID"


class UnsupportedGraph(ValueError):
    status = "UNSUPPORTED"


class NumericallyUnresolved(ArithmeticError):
    status = "NUMERICALLY_UNRESOLVED"


@dataclass(frozen=True)
class Tube:
    id: str
    length_m: float
    area_m2: float


@dataclass(frozen=True)
class Junction:
    id: str
    ports: tuple[str, ...] = ("a", "b", "c")
    law: str = "ideal_acoustic_junction"


@dataclass(frozen=True, order=True)
class Port:
    node: str
    name: str
    kind: str = "acoustic"

    @property
    def key(self) -> str:
        return f"{self.node}.{self.name}"


@dataclass(frozen=True)
class Edge:
    left: Port
    right: Port


@dataclass(frozen=True)
class Boundary:
    port: Port
    kind: str
    value: complex = 0j


@dataclass(frozen=True)
class Graph:
    tubes: tuple[Tube, ...]
    junctions: tuple[Junction, ...]
    edges: tuple[Edge, ...]
    boundaries: tuple[Boundary, ...]
    rho: float = 1.2
    speed: float = 343.0


def _positive(value: object, label: str) -> None:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not isfinite(value) or value <= 0):
        raise InvalidGraph(f"{label} must be finite and positive")


def _id(value: object) -> None:
    if not isinstance(value, str) or not value.strip() or "." in value:
        raise InvalidGraph("IDs must be nonempty strings without '.'")


def _complex(value: object) -> complex:
    if isinstance(value, bool) or not isinstance(value, (int, float, complex)):
        raise InvalidGraph("boundary value must be a finite number")
    z = complex(value)
    if not (isfinite(z.real) and isfinite(z.imag)):
        raise InvalidGraph("boundary value must be finite")
    return z


def validate(graph: Graph) -> None:
    """Validate the ENTIRE schema before checking backend capability."""
    if not isinstance(graph, Graph):
        raise InvalidGraph("expected Graph")
    for values in (graph.tubes, graph.junctions, graph.edges, graph.boundaries):
        if not isinstance(values, tuple):
            raise InvalidGraph("graph collections must be immutable tuples")
    _positive(graph.rho, "rho")
    _positive(graph.speed, "speed")
    ids: set[str] = set()
    ports: set[Port] = set()
    for tube in graph.tubes:
        if not isinstance(tube, Tube):
            raise InvalidGraph("expected Tube")
        _id(tube.id)
        if tube.id in ids:
            raise InvalidGraph("duplicate node ID")
        ids.add(tube.id)
        _positive(tube.length_m, "length")
        _positive(tube.area_m2, "area")
        # Strictly validate the derived p/U impedance before accepting a
        # nominally positive finite but numerically pathological geometry.
        characteristic_z = graph.rho * graph.speed / tube.area_m2
        if (not isfinite(characteristic_z) or characteristic_z <= 0
                or not isfinite(1.0 / characteristic_z)):
            raise InvalidGraph(f"nonfinite derived impedance for {tube.id}")
        ports.update((Port(tube.id, "in"), Port(tube.id, "out")))
    for junction in graph.junctions:
        if not isinstance(junction, Junction):
            raise InvalidGraph("expected Junction")
        _id(junction.id)
        if junction.id in ids:
            raise InvalidGraph("duplicate node ID")
        ids.add(junction.id)
        if not isinstance(junction.ports, tuple) or len(junction.ports) < 2:
            raise InvalidGraph("junction needs an immutable tuple of >=2 ports")
        for name in junction.ports:
            _id(name)
        if len(set(junction.ports)) != len(junction.ports):
            raise InvalidGraph("duplicate junction port")
        if junction.law != "ideal_acoustic_junction":
            raise InvalidGraph("unknown junction law")
        ports.update(Port(junction.id, name) for name in junction.ports)
    if not ids:
        raise InvalidGraph("empty graph")
    used: set[Port] = set()
    adjacency: dict[str, set[str]] = {name: set() for name in ids}

    def claim(port: Port) -> None:
        if not isinstance(port, Port):
            raise InvalidGraph("expected physical Port")
        _id(port.node)
        _id(port.name)
        if port.kind != "acoustic" or port not in ports:
            raise InvalidGraph("unknown or incompatible port")
        if port in used:
            raise InvalidGraph("a port must not be connected/bounded twice")
        used.add(port)

    for edge in graph.edges:
        if not isinstance(edge, Edge):
            raise InvalidGraph("expected Edge")
        claim(edge.left)
        claim(edge.right)
        if edge.left.node == edge.right.node:
            raise InvalidGraph("self-node connection")
        adjacency[edge.left.node].add(edge.right.node)
        adjacency[edge.right.node].add(edge.left.node)
    for boundary in graph.boundaries:
        if not isinstance(boundary, Boundary):
            raise InvalidGraph("expected Boundary")
        claim(boundary.port)
        if boundary.port.node not in {tube.id for tube in graph.tubes}:
            raise InvalidGraph("boundary must terminate a tube port")
        if boundary.kind not in {"inlet_flow", "matched", "pressure_release", "rigid_closed", "impedance"}:
            raise InvalidGraph("unknown boundary kind")
        z = _complex(boundary.value)
        if boundary.kind == "impedance" and z.real < 0:
            raise InvalidGraph("passive impedance requires nonnegative real part")
        if boundary.kind not in {"impedance", "inlet_flow"} and z != 0:
            raise InvalidGraph("unused nonzero boundary value")
    if used != ports:
        raise InvalidGraph("required port is dangling")
    visited: set[str] = set()
    pending = [next(iter(ids))]
    while pending:
        node = pending.pop()
        if node not in visited:
            visited.add(node)
            pending.extend(adjacency[node] - visited)
    if visited != ids:
        raise InvalidGraph("graph is disconnected")


def graph_payload(graph: Graph) -> dict:
    """Canonical physical identity, independent of tuple ordering/wire direction."""
    validate(graph)
    return {
        "model_version": MODEL_VERSION,
        "rho": float(graph.rho), "speed": float(graph.speed),
        "tubes": [{"id": t.id, "length_m": float(t.length_m), "area_m2": float(t.area_m2)}
                  for t in sorted(graph.tubes, key=lambda t: t.id)],
        "junctions": [{"id": j.id, "ports": sorted(j.ports), "law": j.law}
                      for j in sorted(graph.junctions, key=lambda j: j.id)],
        "edges": sorted([sorted([e.left.key, e.right.key]) for e in graph.edges]),
        "boundaries": [{"port": b.port.key, "kind": b.kind,
                        "value_re_im": [float(complex(b.value).real), float(complex(b.value).imag)]}
                       for b in sorted(graph.boundaries, key=lambda b: b.port.key)],
    }


def digest(payload: object) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class PreparedBranch:
    graph: Graph
    tubes: tuple[Tube, Tube, Tube]  # driven tube then two branches
    terminals: tuple[Boundary, Boundary]
    source: Boundary
    graph_digest: str

    @property
    def p_ref(self) -> float:
        return self.graph.rho * self.graph.speed / self.tubes[0].area_m2 * U_REF


def prepare(graph: Graph) -> PreparedBranch:
    validate(graph)
    if len(graph.tubes) != 3 or len(graph.junctions) != 1 or len(graph.junctions[0].ports) != 3:
        raise UnsupportedGraph("backend requires three tubes and one three-port junction")
    sources = [b for b in graph.boundaries if b.kind == "inlet_flow"]
    if len(sources) != 1:
        raise InvalidGraph("one prescribed inlet-flow boundary required")
    source = sources[0]
    if source.port.name != "in":
        raise UnsupportedGraph("driving an outlet is outside this backend")
    driven = next(t for t in graph.tubes if t.id == source.port.node)
    branches = sorted((t for t in graph.tubes if t.id != driven.id), key=lambda t: t.id)
    junction = graph.junctions[0]
    neighbors = {}
    for edge in graph.edges:
        if edge.left.node == junction.id:
            neighbors[edge.right] = edge.left
        elif edge.right.node == junction.id:
            neighbors[edge.left] = edge.right
        else:
            raise UnsupportedGraph("all three edges must meet the single junction")
    required = {Port(driven.id, "out"), *(Port(t.id, "in") for t in branches)}
    if set(neighbors) != required:
        raise UnsupportedGraph("backend requires driven outlet and branch inlets at junction")
    terminals = []
    for tube in branches:
        matches = [b for b in graph.boundaries if b.port == Port(tube.id, "out")]
        if len(matches) != 1 or matches[0].kind == "inlet_flow":
            raise InvalidGraph("one passive boundary per branch outlet required")
        terminals.append(matches[0])
    return PreparedBranch(graph, (driven, branches[0], branches[1]),
                          (terminals[0], terminals[1]), source, digest(graph_payload(graph)))


def fixture(area_ratio: float = 1.0, load_c: str = "matched", scale: complex = 1.0) -> Graph:
    c_kind = "impedance" if load_c == "fixed_impedance" else load_c
    return Graph(
        (Tube("A", .08, 3e-4), Tube("B", .09, 3e-4), Tube("C", .06, 3e-4 * area_ratio)),
        (Junction("J"),),
        (Edge(Port("A", "out"), Port("J", "a")),
         Edge(Port("J", "b"), Port("B", "in")),
         Edge(Port("J", "c"), Port("C", "in"))),
        (Boundary(Port("A", "in"), "inlet_flow", U_REF * (1 + .4j) * scale),
         Boundary(Port("B", "out"), "matched"),
         Boundary(Port("C", "out"), c_kind, 1.2 * 343 / 3e-4 if c_kind == "impedance" else 0)),
    )


@dataclass(frozen=True)
class Response:
    frequency_hz: float
    ports: dict[str, tuple[complex, complex]]
    condition: float
    backward_error: float
    junction_pressure_error: float
    junction_flow_error: float
    powers_w: tuple[float, float, float]
    power_error: float


def solve(body: PreparedBranch, frequency_hz: float, *, _mutation: str | None = None) -> Response:
    """12x12 harmonic solve; mutation option is ONLY for diagnostic negative controls."""
    if (isinstance(frequency_hz, bool) or not isinstance(frequency_hz, (int, float))
            or not isfinite(frequency_hz) or frequency_hz < 0):
        raise InvalidGraph("frequency must be finite and >=0")
    if _mutation not in {None, "wrong_sign", "particle_velocity"}:
        raise InvalidGraph("unknown diagnostic mutation")
    p_ref = body.p_ref
    z_ref = p_ref / U_REF
    matrix = np.zeros((12, 12), dtype=np.complex128)
    rhs = np.zeros(12, dtype=np.complex128)
    for i, tube in enumerate(body.tubes):
        local = UniformTube(tube.length_m, tube.area_m2, body.graph.speed, body.graph.rho)
        transfer = local.transfer_matrix(frequency_hz)
        offset = 4 * i
        matrix[2*i, offset] = 1
        matrix[2*i, offset+2] = -transfer[0, 0]
        matrix[2*i, offset+3] = -transfer[0, 1] / z_ref
        matrix[2*i+1, offset+1] = 1
        matrix[2*i+1, offset+2] = -transfer[1, 0] * z_ref
        matrix[2*i+1, offset+3] = -transfer[1, 1]
    matrix[6, 2], matrix[6, 4] = 1, -1
    matrix[7, 2], matrix[7, 8] = 1, -1
    matrix[8, 3] = 1
    matrix[8, 5], matrix[8, 9] = -1, -1
    if _mutation == "wrong_sign":
        matrix[8, 5], matrix[8, 9] = 1, 1
    elif _mutation == "particle_velocity":
        matrix[8, 5] = -body.tubes[0].area_m2 / body.tubes[1].area_m2
        matrix[8, 9] = -body.tubes[0].area_m2 / body.tubes[2].area_m2
    for i, boundary in enumerate(body.terminals):
        tube = body.tubes[i+1]
        offset = 4 * (i+1) + 2
        if boundary.kind == "rigid_closed":
            matrix[9+i, offset+1] = 1
        else:
            load = (body.graph.rho * body.graph.speed / tube.area_m2
                    if boundary.kind == "matched" else complex(boundary.value))
            matrix[9+i, offset] = 1
            matrix[9+i, offset+1] = -load / z_ref
    matrix[11, 1] = 1
    rhs[11] = body.source.value / U_REF
    condition = float(np.linalg.cond(matrix))
    if not isfinite(condition) or condition > CONDITION_LIMIT:
        raise NumericallyUnresolved(f"condition number {condition:.6g} exceeds {CONDITION_LIMIT:g}")
    try:
        state = np.linalg.solve(matrix, rhs)
    except np.linalg.LinAlgError as exc:
        raise NumericallyUnresolved("no unique finite harmonic solution") from exc
    if not np.all(np.isfinite(state)):
        raise NumericallyUnresolved("nonfinite harmonic state")
    denominator = np.linalg.norm(matrix, np.inf) * np.linalg.norm(state, np.inf) + np.linalg.norm(rhs, np.inf)
    residual = float(np.linalg.norm(matrix @ state - rhs, np.inf) / max(float(denominator), 1e-300))
    ports = {}
    for i, tube in enumerate(body.tubes):
        for j, name in enumerate(("in", "out")):
            ports[f"{tube.id}.{name}"] = (complex(state[4*i+2*j] * p_ref),
                                          complex(state[4*i+2*j+1] * U_REF))
    a, b, c = body.tubes
    pa, ua = ports[f"{a.id}.out"]
    pb, ub = ports[f"{b.id}.in"]
    pc, uc = ports[f"{c.id}.in"]
    def mean_power(state: tuple[complex, complex]) -> float:
        p, u = state
        return float(.5 * np.real(p * np.conjugate(u)))
    powers = (mean_power(ports[f"{a.id}.in"]),
              mean_power(ports[f"{b.id}.out"]),
              mean_power(ports[f"{c.id}.out"]))
    scale = abs(body.source.value / (U_REF * (1 + .4j)))
    power_ref = .5 * p_ref * U_REF * (scale**2 if scale else 1.0)
    return Response(float(frequency_hz), ports, condition, residual,
                    float(max(abs(pa-pb), abs(pa-pc)) / p_ref),
                    float(abs(ua-ub-uc) / U_REF), powers,
                    float(abs(powers[0]-powers[1]-powers[2]) / power_ref))


def local_scatter(areas: tuple[float, float, float], incident: np.ndarray) -> np.ndarray:
    """Solve local continuity equations, independently of analytic scattering formula."""
    for area in areas:
        _positive(area, "local port area")
    waves = np.asarray(incident, dtype=np.complex128)
    if waves.shape != (3,) or not np.all(np.isfinite(waves)):
        raise InvalidGraph("three finite complex incident amplitudes required")
    # Ratios are bounded by one, avoiding spurious overflow if the
    # first port is small. Fail closed if a positive ratio underflows.
    y = np.asarray(areas, dtype=float) / max(areas)  # rho*c cancels
    if not np.all(np.isfinite(y)) or np.any(y <= 0):
        raise InvalidGraph("nonrepresentable local port admittance ratio")
    matrix = np.array([[1, -1, 0], [1, 0, -1], y], dtype=np.complex128)
    rhs = np.array([waves[1]-waves[0], waves[2]-waves[0], y @ waves])
    return np.linalg.solve(matrix, rhs)
