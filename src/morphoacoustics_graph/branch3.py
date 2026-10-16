"""Gate B candidate: bounded lossless 3-tube acoustic branch, separate from OG-3.

This module implements the approved OG-4 branch3 v1 API, not a general organ
graph, speech synthesizer, or a Studio contract. No experiment code is imported.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
import math
import re
import struct
from typing import Any, NoReturn, cast

import numpy as np

from morphoacoustics.acoustics.uniform_tube import UniformTube
from morphoacoustics_graph.model import graph_from_dict
from morphoacoustics_graph.preparation import restore_prepared, validate_graph

SCHEMA = "og4.passive.branch3.v1"
SNAPSHOT_SCHEMA = "og4.branch3.prepared.snapshot.v1"
OBSERVATION_SCHEMA = "og4.branch3.observation.v1"
BACKEND_ID = "og4.fixed.passive.branch3.pu.v1"
DIGEST_VERSION = "og4.canonical.binary.v1"
PHASOR_SCHEMA = "og4.peak.exp_plus_i.v1"
PORT_IDS = ["A.in", "A.out", "B.in", "B.out", "C.in", "C.out"]
PORT_MAPPING = [[f"{name}.{end}", name, role] for name in "ABC"
                for end, role in (("in", "inlet"), ("out", "outlet"))]
FREQUENCIES = frozenset((80., 250., 400., 733., 997., 1200., 2000., 4000.))
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


class Branch3Error(ValueError):
    """Typed, fail-closed acoustic preparation/observation failure."""

    def __init__(self, status: str, code: str, path: str) -> None:
        self.status, self.code, self.path = status, code, path
        super().__init__(f"{status}:{code}:{path}")


def _err(status: str, code: str, path: str) -> NoReturn:
    raise Branch3Error(status, code, path)


def _encode(value: Any) -> bytes:
    if type(value) in (int, float):
        v = float(value)
        if not math.isfinite(v):
            raise ValueError("nonfinite canonical number")
        return b"d" + struct.pack(">d", 0. if v == 0. else v)
    if type(value) is str:
        raw = value.encode("ascii")
        return b"s" + struct.pack(">I", len(raw)) + raw
    if type(value) is list:
        return b"l" + struct.pack(">I", len(value)) + b"".join(map(_encode, value))
    if type(value) is dict and all(type(k) is str for k in value):
        keys = sorted(value, key=lambda k: k.encode("ascii"))
        return b"m" + struct.pack(">I", len(keys)) + b"".join(
            _encode(k) + _encode(value[k]) for k in keys)
    raise ValueError("unsupported canonical field")


def _digest(kind: str, payload: dict[str, Any]) -> str:
    clean = deepcopy(payload)
    if kind == "blueprint":
        for field, key in (("organs", "id"), ("junctions", "id"), ("loads", "port")):
            clean[field].sort(key=lambda row: row[key].encode("ascii"))
    elif kind == "observation":
        clean.pop("observation_digest", None)
    domain = f"morphoacoustics.og4.{kind}.v1".encode("ascii")
    return "sha256:" + sha256(domain + b"\0" + _encode(clean)).hexdigest()


class _Schema:
    """Gather field-level errors first, retaining the smallest JSON Pointer."""

    def __init__(self) -> None:
        self.paths: list[str] = []

    def problem(self, path: str) -> None:
        self.paths.append(path)

    def obj(self, value: Any, fields: set[str], path: str) -> dict[str, Any]:
        if type(value) is not dict:
            self.problem(path)
            return {}
        for field in (value.keys() | fields) - (value.keys() & fields):
            if type(field) is not str:
                self.problem(path)
            else:
                self.problem(path + "/" + field)
        return value

    def array(self, value: Any, path: str, nonempty: bool = True) -> list[Any]:
        if type(value) is not list or (nonempty and not value):
            self.problem(path)
            return []
        return value

    def ident(self, value: Any, path: str) -> str:
        if type(value) is not str or IDENTIFIER.fullmatch(value) is None:
            self.problem(path)
            return ""
        return value

    def literal(self, value: Any, options: tuple[str, ...], path: str) -> str:
        if type(value) is not str or value not in options:
            self.problem(path)
            return ""
        return value

    def num(self, value: Any, path: str, positive: bool = False) -> float:
        if type(value) not in (int, float):
            self.problem(path)
            return 0.
        try:
            v = float(value)
        except (OverflowError, ValueError):
            self.problem(path)
            return 0.
        if not math.isfinite(v) or (positive and v <= 0.):
            self.problem(path)
            return 0.
        return 0. if v == 0. else v

    def complex(self, value: Any, path: str) -> dict[str, float]:
        data = self.obj(value, {"real", "imag"}, path)
        return {key: self.num(data.get(key), path + "/" + key)
                for key in ("real", "imag")}

    def finish(self) -> None:
        if self.paths:
            _err("INVALID", "BLUEPRINT_STRUCTURE", min(self.paths))


def _normalize_blueprint(raw: Any) -> dict[str, Any]:
    s = _Schema()
    d = s.obj(raw, {"schema", "organs", "junctions", "source", "loads"}, "")
    s.literal(d.get("schema"), (SCHEMA,), "/schema")
    organs: list[dict[str, Any]] = []
    for i, entry in enumerate(s.array(d.get("organs"), "/organs")):
        root = f"/organs/{i}"
        o = s.obj(entry, {"id", "revision", "length_m", "area_m2",
                          "sound_speed_m_s", "air_density_kg_m3", "inlet", "outlet"}, root)
        clean: dict[str, Any] = {}
        for k in ("id", "revision"):
            clean[k] = s.ident(o.get(k), root + "/" + k)
        for k in ("length_m", "area_m2", "sound_speed_m_s", "air_density_kg_m3"):
            clean[k] = s.num(o.get(k), root + "/" + k, positive=True)
        for end, direction in (("inlet", "inlet"), ("outlet", "outlet")):
            pth = root + "/" + end
            p = s.obj(o.get(end), {"id", "kind", "direction"}, pth)
            clean[end] = {
                "id": s.ident(p.get("id"), pth + "/id"),
                "kind": s.literal(p.get("kind"), ("acoustic.p_u",), pth + "/kind"),
                "direction": s.literal(p.get("direction"), (direction,), pth + "/direction")}
        if all(clean[k] > 0 for k in ("area_m2", "sound_speed_m_s", "air_density_kg_m3")):
            z = (clean["air_density_kg_m3"] * clean["sound_speed_m_s"]) / clean["area_m2"]
            if not math.isfinite(z) or z <= 0 or not math.isfinite(1. / z) or 1. / z <= 0:
                s.problem(root + "/area_m2")
        organs.append(clean)
    junctions: list[dict[str, Any]] = []
    for i, entry in enumerate(s.array(d.get("junctions"), "/junctions")):
        root = f"/junctions/{i}"
        j = s.obj(entry, {"id", "law", "ports"}, root)
        law = s.literal(j.get("law"), ("ideal.series.p_u", "ideal.branch3.p_u"), root + "/law")
        ports = [s.ident(p, root + f"/ports/{k}") for k, p in enumerate(
            s.array(j.get("ports"), root + "/ports"))]
        if law and len(ports) != (2 if law == "ideal.series.p_u" else 3):
            s.problem(root + "/ports")
        junctions.append({"id": s.ident(j.get("id"), root + "/id"),
                          "law": law, "ports": ports})
    source = s.obj(d.get("source"), {"kind", "phasor_schema", "port",
                                     "amplitude_m3_s", "scale"}, "/source")
    src: dict[str, Any] = {"kind": s.literal(source.get("kind"), ("prescribed_volume_flow",), "/source/kind"),
           "phasor_schema": s.literal(source.get("phasor_schema"), (PHASOR_SCHEMA,),
                                      "/source/phasor_schema"),
           "port": s.ident(source.get("port"), "/source/port"),
           "amplitude_m3_s": s.complex(source.get("amplitude_m3_s"), "/source/amplitude_m3_s"),
           "scale": s.num(source.get("scale"), "/source/scale")}
    if not all(math.isfinite(src["amplitude_m3_s"][z] * src["scale"]) for z in ("real", "imag")):
        s.problem("/source/scale")
    loads: list[dict[str, Any]] = []
    for i, entry in enumerate(s.array(d.get("loads"), "/loads")):
        root = f"/loads/{i}"
        if type(entry) is not dict:
            s.problem(root)
            continue
        kind = s.literal(entry.get("kind"), ("matched", "pressure_release",
                          "rigid_closed", "fixed_impedance"), root + "/kind")
        fields = {"port", "kind", "impedance_pa_s_m3"} if kind == "fixed_impedance" else {"port", "kind"}
        v = s.obj(entry, fields, root)
        load: dict[str, Any] = {"port": s.ident(v.get("port"), root + "/port"), "kind": kind}
        if kind == "fixed_impedance":
            z = s.complex(v.get("impedance_pa_s_m3"), root + "/impedance_pa_s_m3")
            if z["real"] <= 0:
                s.problem(root + "/impedance_pa_s_m3/real")
            load["impedance_pa_s_m3"] = z
        loads.append(load)
    s.finish()
    clean_bp = {"schema": SCHEMA, "organs": organs, "junctions": junctions,
                "source": src, "loads": loads}
    # Validate graph relationships independently from narrow backend capability.
    ids = [o["id"] for o in organs]
    port_owner = {p["id"]: (o["id"], end) for o in organs
             for end in ("inlet", "outlet") for p in (o[end],)}
    raw_port_ids = [o[end]["id"] for o in organs for end in ("inlet", "outlet")]
    if len(set(ids)) != len(ids) or len(set(raw_port_ids)) != len(raw_port_ids):
        _err("INVALID", "BLUEPRINT_STRUCTURE", "/organs")
    if len({j["id"] for j in junctions}) != len(junctions):
        _err("INVALID", "BLUEPRINT_STRUCTURE", "/junctions")
    assignments: list[str] = []
    source_id = src["port"]
    if source_id not in port_owner or port_owner[source_id][1] != "inlet":
        _err("INVALID", "BLUEPRINT_STRUCTURE", "/source/port")
    assignments.append(source_id)
    for j in junctions:
        jports = j["ports"]
        owners = [port_owner.get(pid) for pid in jports]
        if (any(a is None for a in owners) or
                owners[0][1] != "outlet" or
                any(a[1] != "inlet" for a in owners[1:]) or
                len({a[0] for a in owners}) != len(owners) or
                len(set(jports)) != len(jports)):
            _err("INVALID", "BLUEPRINT_STRUCTURE", "/junctions")
        assignments.extend(jports)
    load_ids = [x["port"] for x in loads]
    if any(pid not in port_owner or port_owner[pid][1] != "outlet" for pid in load_ids):
        _err("INVALID", "BLUEPRINT_STRUCTURE", "/loads")
    assignments.extend(load_ids)
    if len(assignments) != len(set(assignments)):
        _err("INVALID", "BLUEPRINT_STRUCTURE", "/junctions")
    if len(assignments) != len(raw_port_ids):
        _err("INVALID", "BLUEPRINT_STRUCTURE", "")
    # Undirected, iterative connectivity; a well-formed larger graph is UNSUPPORTED.
    adjacency: dict[str, set[str]] = {name: set() for name in ids}
    for j in junctions:
        upstream = port_owner[j["ports"][0]][0]
        for pid in j["ports"][1:]:
            down = port_owner[pid][0]
            adjacency[upstream].add(down)
            adjacency[down].add(upstream)
    visited: set[str] = set()
    stack = [port_owner[source_id][0]]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            stack.extend(adjacency[node] - visited)
    if len(visited) != len(organs):
        _err("INVALID", "BLUEPRINT_STRUCTURE", "")
    return clean_bp


def _check_capability(bp: dict[str, Any]) -> None:
    organs = {o["id"]: o for o in bp["organs"]}
    if (len(organs) != 3 or set(organs) != set("ABC") or len(bp["junctions"]) != 1 or
            bp["junctions"][0] != {"id": "J", "law": "ideal.branch3.p_u",
                                    "ports": ["A.out", "B.in", "C.in"]} or
            any(organs[n][end]["id"] != f"{n}.{suffix}" for n in "ABC"
                for end, suffix in (("inlet", "in"), ("outlet", "out")))):
        _err("UNSUPPORTED", "BRANCH3_TOPOLOGY_ONLY", "/junctions")
    if any(o["air_density_kg_m3"] != 1.2 or o["sound_speed_m_s"] != 343.
           for o in organs.values()):
        _err("UNSUPPORTED", "FROZEN_MEDIUM", "/organs")
    for name, length, areas in (("A", .08, (.0003,)), ("B", .09, (.0003,)),
                                ("C", .06, (.00015, .0003, .0006))):
        if organs[name]["length_m"] != length or organs[name]["area_m2"] not in areas:
            _err("UNSUPPORTED", "FROZEN_GEOMETRY", "/organs")
    source = bp["source"]
    if (source["port"] != "A.in" or source["amplitude_m3_s"] !=
            {"real": 1e-6, "imag": 4e-7} or source["scale"] not in (1., .5, -1.)):
        _err("UNSUPPORTED", "FROZEN_SOURCE", "/source")
    loads = {x["port"]: x for x in bp["loads"]}
    if (len(loads) != 2 or set(loads) != {"B.out", "C.out"} or
            loads["B.out"] != {"port": "B.out", "kind": "matched"} or
            (loads["C.out"]["kind"] == "fixed_impedance" and
             loads["C.out"]["impedance_pa_s_m3"] != {"real": 1372000., "imag": 0.})):
        _err("UNSUPPORTED", "FROZEN_LOAD", "/loads")


def _fresh(bp: dict[str, Any]) -> "PreparedBranch3":
    organs = {o["id"]: o for o in bp["organs"]}
    tubes = cast(tuple[UniformTube, UniformTube, UniformTube], tuple(UniformTube(
        length_m=organs[n]["length_m"], area_m2=organs[n]["area_m2"],
        sound_speed_m_s=organs[n]["sound_speed_m_s"],
        air_density_kg_m3=organs[n]["air_density_kg_m3"]) for n in "ABC"))
    bd = _digest("blueprint", bp)
    pd = _digest("preparation", {
        "digest_version": DIGEST_VERSION, "backend_id": BACKEND_ID,
        "blueprint_digest": bd, "port_mapping": PORT_MAPPING})
    return PreparedBranch3(json.dumps(bp, sort_keys=True, separators=(",", ":")),
                           tubes, bd, pd)


@dataclass(frozen=True, slots=True)
class PreparedBranch3:
    _blueprint_json: str
    _tubes: tuple[UniformTube, UniformTube, UniformTube]
    blueprint_digest: str
    preparation_digest: str

    def _binding(self) -> dict[str, Any]:
        try:
            bp = json.loads(self._blueprint_json)
            checked = _normalize_blueprint(bp)
            _check_capability(checked)
            fresh = _fresh(checked)
            if (self._blueprint_json != fresh._blueprint_json or
                    self._tubes != fresh._tubes or
                    self.blueprint_digest != fresh.blueprint_digest or
                    self.preparation_digest != fresh.preparation_digest):
                raise ValueError("binding mismatch")
            return checked
        except (ValueError, TypeError, KeyError, AttributeError, Branch3Error) as exc:
            _err("INVALID", "PREPARED_BINDING_MISMATCH", "")

    def to_snapshot(self) -> dict[str, Any]:
        bp = self._binding()
        return {"schema": SNAPSHOT_SCHEMA, "digest_version": DIGEST_VERSION,
                "backend_id": BACKEND_ID, "blueprint": bp,
                "blueprint_digest": self.blueprint_digest,
                "preparation_digest": self.preparation_digest}

    def response(self, frequencies_hz: list[int | float]) -> dict[str, Any]:
        bp = self._binding()
        if type(frequencies_hz) is not list or not frequencies_hz or any(
                type(x) is list for x in frequencies_hz):
            _err("INVALID", "FREQUENCY_SHAPE", "/frequencies_hz")
        fs: list[float] = []
        for i, x in enumerate(frequencies_hz):
            if type(x) not in (int, float):
                _err("INVALID", "FREQUENCY_VALUE", f"/frequencies_hz/{i}")
            try:
                f = float(x)
            except (ValueError, OverflowError):
                _err("INVALID", "FREQUENCY_VALUE", f"/frequencies_hz/{i}")
            if not math.isfinite(f) or f < 0:
                _err("INVALID", "FREQUENCY_VALUE", f"/frequencies_hz/{i}")
            fs.append(0. if f == 0. else f)
        if len(fs) > 256:
            _err("UNSUPPORTED", "FREQUENCY_POINT_LIMIT", "/frequencies_hz")
        for i, f in enumerate(fs):
            if f not in FREQUENCIES:
                _err("UNSUPPORTED", "FREQUENCY_NOT_YET_VERIFIED", f"/frequencies_hz/{i}")
        organ = {o["id"]: o for o in bp["organs"]}
        loads = {x["port"]: x for x in bp["loads"]}
        pref = 1e-6 * self._tubes[0].characteristic_impedance_pa_s_m3
        uref = 1e-6
        pressures: list[list[dict[str, float]]] = []
        flows: list[list[dict[str, float]]] = []
        powers: list[list[float]] = []
        diagnostics: list[dict[str, float]] = []
        for i, f in enumerate(fs):
            path = f"/frequencies_hz/{i}"
            m, rhs = _system(self._tubes, loads, complex(
                bp["source"]["amplitude_m3_s"]["real"],
                bp["source"]["amplitude_m3_s"]["imag"]) * bp["source"]["scale"], f)
            try:
                cond = float(np.linalg.cond(m))
                if not math.isfinite(cond) or cond > 1e8:
                    _err("NUMERICALLY_UNRESOLVED", "CONDITION_OR_SOLVE", path)
                solution = np.linalg.solve(m, rhs)
                if not np.all(np.isfinite(solution)):
                    _err("NUMERICALLY_UNRESOLVED", "CONDITION_OR_SOLVE", path)
                denom = max(float(np.linalg.norm(m, ord=np.inf) *
                                  np.linalg.norm(solution, ord=np.inf) +
                                  np.linalg.norm(rhs, ord=np.inf)), 1e-300)
                backwards = float(np.linalg.norm(m @ solution - rhs, ord=np.inf) / denom)
            except (np.linalg.LinAlgError, FloatingPointError, OverflowError, ValueError) as exc:
                if isinstance(exc, Branch3Error):
                    raise
                _err("NUMERICALLY_UNRESOLVED", "CONDITION_OR_SOLVE", path)
            if not math.isfinite(backwards):
                _err("NUMERICALLY_UNRESOLVED", "CONDITION_OR_SOLVE", path)
            if backwards > 1e-12:
                _err("NUMERICALLY_UNRESOLVED", "BACKWARD_RESIDUAL", path)
            p = solution[0::2] * pref
            u = solution[1::2] * uref
            watts = np.array([.5 * (p[k] * np.conj(u[k])).real for k in range(6)])
            jp = max(abs(solution[2] - solution[4]), abs(solution[2] - solution[8]))
            ju = abs(solution[3] - solution[5] - solution[9])
            scale = abs(bp["source"]["scale"])
            power = abs(watts[0] - watts[3] - watts[5]) / (
                .5 * pref * uref * scale * scale)
            diagnostic = {"condition_2": cond, "backward_error": backwards,
                          "junction_pressure_error": float(jp),
                          "junction_flow_error": float(ju),
                          "power_error": float(power)}
            if not all(math.isfinite(v) and v >= 0 for v in diagnostic.values()):
                _err("NUMERICALLY_UNRESOLVED", "CONDITION_OR_SOLVE", path)
            if max(float(jp), float(ju), float(power)) > 1e-10:
                _err("NUMERICALLY_UNRESOLVED", "PHYSICAL_RESIDUAL", path)
            pressures.append([{"real": _zero(z.real), "imag": _zero(z.imag)} for z in p])
            flows.append([{"real": _zero(z.real), "imag": _zero(z.imag)} for z in u])
            powers.append([_zero(v) for v in watts])
            diagnostics.append({key: _zero(value) for key, value in diagnostic.items()})
        response: dict[str, Any] = {
            "schema": OBSERVATION_SCHEMA, "status": "OK",
            "digest_version": DIGEST_VERSION, "backend_id": BACKEND_ID,
            "preparation_digest": self.preparation_digest,
            "frequencies_hz": fs, "port_ids": list(PORT_IDS),
            "pressure_pa": pressures, "volume_flow_m3_s": flows,
            "mean_power_w": powers, "diagnostics": diagnostics}
        response["observation_digest"] = _digest("observation", response)
        return response


def _zero(value: Any) -> float:
    v = float(value)
    return 0. if v == 0. else v


def _system(tubes: tuple[UniformTube, ...], loads: dict[str, dict[str, Any]],
            source: complex, f: float) -> tuple[np.ndarray, np.ndarray]:
    """Fixed 12x12 physical diagnostic matrix in Gate A's declared row order."""
    m = np.zeros((12, 12), dtype=np.complex128)
    rhs = np.zeros(12, dtype=np.complex128)
    za = tubes[0].characteristic_impedance_pa_s_m3
    for i, tube in enumerate(tubes):
        t = tube.transfer_matrix(float(f))
        k = 4 * i
        m[2*i, k] = 1.
        m[2*i, k+2] = -t[0, 0]
        m[2*i, k+3] = -t[0, 1] / za
        m[2*i+1, k+1] = 1.
        m[2*i+1, k+2] = -t[1, 0] * za
        m[2*i+1, k+3] = -t[1, 1]
    m[6, 2], m[6, 4] = 1., -1.
    m[7, 2], m[7, 8] = 1., -1.
    m[8, 3], m[8, 5], m[8, 9] = 1., -1., -1.
    for row, k, organ in ((9, 6, "B"), (10, 10, "C")):
        load = loads[organ + ".out"]
        kind = load["kind"]
        if kind == "rigid_closed":
            m[row, k+1] = 1.
        else:
            m[row, k] = 1.
            if kind == "matched":
                zload: complex = tubes["ABC".index(organ)].characteristic_impedance_pa_s_m3
            elif kind == "fixed_impedance":
                z = load["impedance_pa_s_m3"]
                zload = complex(z["real"], z["imag"])
            else:  # pressure_release
                zload = 0.
            m[row, k+1] = -zload / za
    m[11, 1] = 1.
    rhs[11] = source / 1e-6
    return m, rhs


def prepare_branch3(blueprint: dict[str, object]) -> PreparedBranch3:
    if type(blueprint) is not dict or type(blueprint.get("schema")) is not str:
        _err("INVALID", "BLUEPRINT_STRUCTURE", "/schema")
    if blueprint["schema"] == "og3.passive.fixed2.v1":
        try:
            validate_graph(graph_from_dict(blueprint))
        except (ValueError, KeyError, TypeError):
            _err("INVALID", "LEGACY_INVALID", "")
        _err("UNSUPPORTED", "SCHEMA_NOT_BRANCH3", "/schema")
    if blueprint["schema"] != SCHEMA:
        _err("UNSUPPORTED", "UNKNOWN_SCHEMA", "/schema")
    clean = _normalize_blueprint(blueprint)
    _check_capability(clean)
    return _fresh(clean)


def restore_branch3(snapshot: dict[str, object]) -> PreparedBranch3:
    if type(snapshot) is not dict:
        _err("INVALID", "SNAPSHOT_STRUCTURE", "")
    if snapshot.get("schema") == "og3.prepared.snapshot.v1":
        try:
            restore_prepared(snapshot)
        except (ValueError, TypeError, KeyError):
            _err("INVALID", "LEGACY_INVALID", "")
        _err("UNSUPPORTED", "SCHEMA_NOT_BRANCH3", "/schema")
    expected = {"schema", "digest_version", "backend_id", "blueprint",
                "blueprint_digest", "preparation_digest"}
    bad = sorted(expected ^ set(snapshot))
    if bad or type(snapshot.get("schema")) is not str:
        _err("INVALID", "SNAPSHOT_STRUCTURE", "/" + bad[0] if bad else "/schema")
    for key in ("digest_version", "backend_id", "blueprint_digest", "preparation_digest"):
        value = snapshot[key]
        if type(value) is not str or (key.endswith("digest") and DIGEST.fullmatch(value) is None):
            _err("INVALID", "SNAPSHOT_STRUCTURE", "/" + key)
    if snapshot["schema"] != SNAPSHOT_SCHEMA:
        _err("UNSUPPORTED", "SNAPSHOT_SCHEMA", "/schema")
    for key, expected_value in (("digest_version", DIGEST_VERSION),
                                ("backend_id", BACKEND_ID)):
        if snapshot[key] != expected_value:
            _err("UNSUPPORTED", "SNAPSHOT_VERSION", "/" + key)
    if type(snapshot["blueprint"]) is not dict:
        _err("INVALID", "SNAPSHOT_STRUCTURE", "/blueprint")
    prepared = prepare_branch3(cast(dict[str, object], snapshot["blueprint"]))
    for field in ("blueprint_digest", "preparation_digest"):
        if snapshot[field] != getattr(prepared, field):
            _err("INVALID", "SNAPSHOT_DIGEST_MISMATCH", "/" + field)
    return prepared
