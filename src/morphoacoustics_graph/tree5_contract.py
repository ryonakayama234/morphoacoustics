"""OG-5 frozen Gate A/A1 contract adapter (Gate B2 draft).

Separate from the physical B1 20x20 solver. No legacy ABI changes and no general
graph, phonation, or Studio claim. No source/oracle fixture is imported at runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
import struct
from typing import Any, NoReturn, cast

SCHEMA = "og5.passive.tree5.v1"
SNAPSHOT_SCHEMA = "og5.tree5.prepared.snapshot.v1"
OBSERVATION_SCHEMA = "og5.tree5.observation.v1"
DIGEST_VERSION = "og5.canonical.binary.v1"
BACKEND_ID = "og5.fixed.passive.tree5.pu.v1"
_DOMAINS = {
    "blueprint": "morphoacoustics.og5.blueprint.v1",
    "preparation": "morphoacoustics.og5.preparation.v1",
    "observation": "morphoacoustics.og5.observation.v1",
}
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
_CODES = ("EXPECTED_OBJECT", "EXPECTED_LIST", "MISSING_FIELD", "UNKNOWN_FIELD",
          "INVALID_STRING", "INVALID_NUMBER", "NUMBER_OUT_OF_RANGE",
          "INVALID_CARDINALITY", "PORT_TYPE_MISMATCH", "PORT_DIRECTION_MISMATCH",
          "DUPLICATE_ID", "UNKNOWN_PORT", "DUPLICATE_BINDING", "UNBOUND_PORT",
          "INVALID_CONNECTION", "GRAPH_CYCLE", "GRAPH_DISCONNECTED",
          "IDENTITY_MISMATCH", "PREPARED_BINDING_INVALID", "EMPTY_REQUEST")
_CODE_RANK = {v: i for i, v in enumerate(_CODES)}
_FIXED = {
    "A": (.08, .0003), "B": (.09, .0003), "C": (.06, None),
    "D": (.07, .0003), "E": (.05, .0006),
}
_ORGAN = {"id": "id", "revision": "id", "length_m": "pos",
          "area_m2": "pos", "sound_speed_m_s": "pos",
          "air_density_kg_m3": "pos", "inlet": "port", "outlet": "port"}
_PORT = {"id": "id", "kind": "marker", "direction": "marker"}
_JUNCTION = {"id": "id", "law": "marker", "ports": "strlist"}
_SOURCE = {"kind": "marker", "phasor_schema": "marker", "port": "id",
           "amplitude_m3_s": "complex", "scale": "number"}
_LOAD = {"port": "id", "kind": "marker"}
_BP = {"schema": "marker", "organs": "organs", "junctions": "junctions",
       "source": "source", "loads": "loads"}
_SNAPSHOT = {"schema": "marker", "digest_version": "marker",
             "backend_id": "marker", "blueprint": "blueprint",
             "blueprint_digest": "digest", "preparation_digest": "digest"}


class Tree5Error(ValueError):
    """Normative status, code and escaped RFC6901 path; never a partial result."""

    def __init__(self, status: str, code: str, path: str) -> None:
        self.status, self.code, self.path = status, code, path
        super().__init__(f"{status}:{code}:{path}")

    def receipt(self) -> dict[str, str]:
        return {"status": self.status, "code": self.code, "path": self.path}


def _ptr(part: object) -> str:
    return str(part).replace("~", "~0").replace("/", "~1")


def _raise(status: str, code: str, path: str) -> NoReturn:
    raise Tree5Error(status, code, path)


def _fail(errors: list[tuple[str, str]]) -> None:
    if errors:
        path, code = min(errors, key=lambda x: (x[0].encode("ascii"), _CODE_RANK.get(x[1], 999)))
        _raise("INVALID", code, path)


def _string(v: object, path: str, errors: list[tuple[str, str]], kind: str) -> object:
    if type(v) is not str:
        errors.append((path, "INVALID_STRING"))
        return None
    s = cast(str, v)
    try:
        b = s.encode("ascii")
    except UnicodeError:
        errors.append((path, "INVALID_STRING"))
        return None
    ok = bool(_ID.fullmatch(s)) if kind == "id" else (
        bool(_DIGEST.fullmatch(s)) if kind == "digest" else 0 < len(b) <= 128)
    if not ok:
        errors.append((path, "INVALID_STRING"))
    return s


def _number(v: object, path: str, errors: list[tuple[str, str]], positive: bool = False) -> object:
    if type(v) not in (int, float):
        errors.append((path, "INVALID_NUMBER"))
        return None
    try:
        x = float(cast(float, v))
    except (ValueError, OverflowError):
        errors.append((path, "INVALID_NUMBER"))
        return None
    if not math.isfinite(x):
        errors.append((path, "INVALID_NUMBER"))
        return None
    if positive and x <= 0.:
        errors.append((path, "NUMBER_OUT_OF_RANGE"))
    return 0. if x == 0. else x


def _scan(v: object, spec: object, path: str, errors: list[tuple[str, str]]) -> object:
    if spec in ("id", "marker", "digest"):
        return _string(v, path, errors, cast(str, spec))
    if spec in ("number", "pos"):
        return _number(v, path, errors, positive=spec == "pos")
    if spec == "strlist":
        if type(v) is not list:
            errors.append((path, "EXPECTED_LIST"))
            return None
        seq = cast(list[object], v)
        if len(seq) != 3:
            errors.append((path, "INVALID_CARDINALITY"))
        return [_string(x, path + "/" + str(i), errors, "id") for i, x in enumerate(seq)]
    maps: dict[str, dict[str, str]] = {
        "port": _PORT, "source": _SOURCE, "load": _LOAD,
        "junction": _JUNCTION, "organ": _ORGAN, "blueprint": _BP,
        "snapshot": _SNAPSHOT, "complex": {"real": "number", "imag": "number"},
    }
    if spec in ("organs", "junctions", "loads"):
        if type(v) is not list:
            errors.append((path, "EXPECTED_LIST"))
            return None
        seq = cast(list[object], v)
        if spec in ("organs", "loads") and not seq:
            errors.append((path, "INVALID_CARDINALITY"))
        elem = {"organs": "organ", "junctions": "junction", "loads": "load"}[cast(str, spec)]
        return [_scan(z, elem, path + "/" + str(i), errors) for i, z in enumerate(seq)]
    fields = maps.get(cast(str, spec))
    if fields is None:
        raise AssertionError("internal invalid scan specification")
    if type(v) is not dict:
        errors.append((path, "EXPECTED_OBJECT"))
        return None
    obj = cast(dict[object, object], v)
    if any(type(k) is not str or not cast(str, k).isascii() for k in obj):
        errors.append((path, "INVALID_STRING"))
        return None
    out: dict[str, object] = {}
    for key in obj:
        skey = cast(str, key)
        if skey not in fields:
            errors.append((path + "/" + _ptr(skey), "UNKNOWN_FIELD"))
    for key, member in fields.items():
        child = path + "/" + _ptr(key)
        if key not in obj:
            errors.append((child, "MISSING_FIELD"))
        else:
            out[key] = _scan(obj[key], member, child, errors)
    if spec == "port":
        if out.get("kind") is not None and out["kind"] != "acoustic.p_u":
            errors.append((path + "/kind", "PORT_TYPE_MISMATCH"))
        if out.get("direction") is not None and out["direction"] not in ("inlet", "outlet"):
            errors.append((path + "/direction", "PORT_DIRECTION_MISMATCH"))
    return out


def _relations(bp: dict[str, Any], prefix: str) -> None:
    errors: list[tuple[str, str]] = []
    organs = bp["organs"]
    # Ownership uses input object positions until uniqueness is established.
    # Reusing an organ ID must not turn distinct physical owners into a false
    # self-connection that sorts before the actual duplicate identity error.
    ports: dict[str, tuple[int, str, str]] = {}
    ambiguous_ports: set[str] = set()
    organ_ids: dict[str, str] = {}
    seen_junctions: dict[str, str] = {}
    for i, organ in enumerate(organs):
        oid = organ["id"]
        ip = f"{prefix}/organs/{i}/id"
        if oid in organ_ids:
            errors.append((ip, "DUPLICATE_ID"))
        organ_ids[oid] = ip
        for side in ("inlet", "outlet"):
            port = organ[side]
            path = f"{prefix}/organs/{i}/{side}/id"
            ident = port["id"]
            if ident in ports:
                errors.append((path, "DUPLICATE_ID"))
                ambiguous_ports.add(ident)
            else:
                ports[ident] = (i, side, path)
            expected_direction = "inlet" if side == "inlet" else "outlet"
            if port["direction"] != expected_direction:
                errors.append((f"{prefix}/organs/{i}/{side}/direction",
                               "PORT_DIRECTION_MISMATCH"))
    for i, junc in enumerate(bp["junctions"]):
        path = f"{prefix}/junctions/{i}/id"
        if junc["id"] in seen_junctions:
            errors.append((path, "DUPLICATE_ID"))
        seen_junctions[junc["id"]] = path
    bindings: dict[str, list[str]] = {key: [] for key in ports}
    edges: list[tuple[str, str]] = []

    def bind(ident: str, path: str, expected: str) -> int | None:
        p = ports.get(ident)
        if p is None:
            errors.append((path, "UNKNOWN_PORT"))
            return None
        bindings[ident].append(path)
        if ident in ambiguous_ports:
            return None
        if p[1] != expected:
            errors.append((path, "INVALID_CONNECTION"))
        return p[0]

    src = bp["source"]
    bind(src["port"], prefix + "/source/port", "inlet")
    for i, load in enumerate(bp["loads"]):
        bind(load["port"], f"{prefix}/loads/{i}/port", "outlet")
    for i, junc in enumerate(bp["junctions"]):
        ids = junc["ports"]
        if len(ids) != 3:
            continue
        parent = bind(ids[0], f"{prefix}/junctions/{i}/ports/0", "outlet")
        children = [bind(ids[k], f"{prefix}/junctions/{i}/ports/{k}", "inlet")
                    for k in (1, 2)]
        if parent is not None and all(x is not None for x in children):
            if parent in children or children[0] == children[1]:
                errors.append((f"{prefix}/junctions/{i}/ports/0", "INVALID_CONNECTION"))
            else:
                edges.extend((organs[parent]["id"], organs[cast(int, x)]["id"]) for x in children)
    for ident, refs in bindings.items():
        if ident in ambiguous_ports:
            continue
        if len(refs) > 1:
            errors.append((sorted(refs, key=lambda z: z.encode("ascii"))[-1], "DUPLICATE_BINDING"))
        if not refs:
            errors.append((ports[ident][2], "UNBOUND_PORT"))
    _fail(errors)

    # Cycle before connectivity, independent of source/root; no recursive DFS.
    graph: dict[str, list[str]] = {o["id"]: [] for o in organs}
    for a, b in edges:
        graph[a].append(b)
    indegrees = {n: 0 for n in graph}
    for outs in graph.values():
        for b in outs:
            indegrees[b] += 1
    stack = [n for n, d in indegrees.items() if d == 0]
    visited = 0
    while stack:
        n = stack.pop()
        visited += 1
        for child in graph[n]:
            indegrees[child] -= 1
            if indegrees[child] == 0:
                stack.append(child)
    if visited != len(graph):
        _raise("INVALID", "GRAPH_CYCLE", prefix + "/junctions")
    undirected: dict[str, set[str]] = {n: set() for n in graph}
    for a, b in edges:
        undirected[a].add(b)
        undirected[b].add(a)
    reached: set[str] = set()
    search = [src["port"]]
    if src["port"] in ports:
        search = [organs[ports[src["port"]][0]]["id"]]
    while search:
        cur = search.pop()
        if cur in reached:
            continue
        reached.add(cur)
        search.extend(undirected[cur] - reached)
    if len(reached) != len(graph):
        _raise("INVALID", "GRAPH_DISCONNECTED", prefix + "/organs")


def _normalize_blueprint(value: object, prefix: str = "") -> dict[str, Any]:
    errs: list[tuple[str, str]] = []
    bp = _scan(value, "blueprint", prefix, errs)
    _fail(errs)
    clean = cast(dict[str, Any], bp)
    _relations(clean, prefix)
    for collection, key in (("organs", "id"), ("junctions", "id"), ("loads", "port")):
        clean[collection].sort(key=lambda x: x[key])
    return clean


def _capability(bp: dict[str, Any], prefix: str = "") -> None:
    from . import tree5 as physics

    if bp["schema"] != SCHEMA:
        _raise("UNSUPPORTED", "VERSION_NOT_SUPPORTED", prefix + "/schema")
    source = bp["source"]
    if source["phasor_schema"] != "og5.peak.exp_plus_i.v1":
        _raise("UNSUPPORTED", "VERSION_NOT_SUPPORTED", prefix + "/source/phasor_schema")
    for j in bp["junctions"]:
        if j["law"] != "ideal.branch3.p_u":
            index = bp["junctions"].index(j)
            _raise("UNSUPPORTED", "LAW_NOT_SUPPORTED", prefix + f"/junctions/{index}/law")
    if (source["kind"] != "prescribed_volume_flow" or
            source["port"] != "A.in" or
            source["amplitude_m3_s"] != {"real": 1e-6, "imag": 4e-7} or
            source["scale"] not in (1., .5, -1.)):
        _raise("UNSUPPORTED", "SOURCE_NOT_SUPPORTED", prefix + "/source")
    for i, load in enumerate(bp["loads"]):
        if load["kind"] not in ("matched", "rigid_closed"):
            _raise("UNSUPPORTED", "LOAD_NOT_SUPPORTED", prefix + f"/loads/{i}/kind")
    if (set(o["id"] for o in bp["organs"]) != set("ABCDE")
            or len(bp["organs"]) != 5 or len(bp["junctions"]) != 2
            or bp["junctions"] != [
                {"id": "J1", "law": "ideal.branch3.p_u",
                 "ports": ["A.out", "B.in", "C.in"]},
                {"id": "J2", "law": "ideal.branch3.p_u",
                 "ports": ["B.out", "D.in", "E.in"]},
            ] or any(o["inlet"]["id"] != o["id"] + ".in" or
                     o["outlet"]["id"] != o["id"] + ".out" for o in bp["organs"])
            or set(x["port"] for x in bp["loads"]) != {"C.out", "D.out", "E.out"}):
        _raise("UNSUPPORTED", "TOPOLOGY_NOT_SUPPORTED", prefix + "/organs")
    for i, o in enumerate(bp["organs"]):
        name = o["id"]
        length, area = _FIXED[name]
        for key, expected in (("length_m", length), ("area_m2", area),
                              ("sound_speed_m_s", 343.), ("air_density_kg_m3", 1.2)):
            if (key == "area_m2" and name == "C"
                    and o[key] in physics.AREAS_C):
                continue
            if o[key] != expected:
                _raise("UNSUPPORTED", "GEOMETRY_NOT_SUPPORTED",
                       prefix + f"/organs/{i}/{key}")
    for x in bp["loads"]:
        if x["port"] != "C.out" and x["kind"] != "matched":
            _raise("UNSUPPORTED", "LOAD_NOT_SUPPORTED",
                   prefix + "/loads/" + str(bp["loads"].index(x)) + "/kind")


def _encode(value: object) -> bytes:
    if type(value) in (int, float):
        v = float(cast(float, value))
        if not math.isfinite(v):
            raise ValueError("Nonfinite canonical number")
        return b"d" + struct.pack(">d", 0. if v == 0. else v)
    if type(value) is str:
        raw = value.encode("ascii")
        return b"s" + struct.pack(">I", len(raw)) + raw
    if type(value) is list:
        seq = cast(list[object], value)
        return b"l" + struct.pack(">I", len(seq)) + b"".join(_encode(x) for x in seq)
    if type(value) is dict:
        pairs = cast(dict[str, object], value)
        return b"m" + struct.pack(">I", len(pairs)) + b"".join(
            _encode(k) + _encode(pairs[k]) for k in sorted(pairs, key=lambda x: x.encode("ascii")))
    raise TypeError("Forbidden canonical value")


def _hash(domain: str, payload: object) -> str:
    return "sha256:" + hashlib.sha256(_DOMAINS[domain].encode("ascii") + b"\0" +
                                      _encode(payload)).hexdigest()


def _snapshot(bp: dict[str, Any]) -> dict[str, Any]:
    head = {"schema": SNAPSHOT_SCHEMA, "digest_version": DIGEST_VERSION,
            "backend_id": BACKEND_ID, "blueprint_digest": _hash("blueprint", bp)}
    return {**head, "blueprint": bp,
            "preparation_digest": _hash("preparation", head)}


def _fresh(bp: dict[str, Any]) -> PreparedTree5:
    snap = _snapshot(bp)
    return PreparedTree5(json.dumps(snap, sort_keys=True, separators=(",", ":")),
                         snap["blueprint_digest"], snap["preparation_digest"])


@dataclass(frozen=True, slots=True)
class PreparedTree5:
    _snapshot_json: str
    blueprint_digest: str
    preparation_digest: str

    def _binding(self) -> dict[str, Any]:
        try:
            snap = json.loads(self._snapshot_json)
            validated = _restore_impl(snap)
            if (validated._snapshot_json != self._snapshot_json or
                    validated.blueprint_digest != self.blueprint_digest or
                    validated.preparation_digest != self.preparation_digest):
                raise ValueError("binding identity changed")
            return cast(dict[str, Any], snap)
        except (Tree5Error, ValueError, TypeError, KeyError, AttributeError, RecursionError):
            _raise("INVALID", "PREPARED_BINDING_INVALID", "/prepared")

    def to_snapshot(self) -> dict[str, Any]:
        return self._binding()

    def response(self, frequencies_hz: list[int | float]) -> dict[str, Any]:
        from . import tree5 as physics

        snap = self._binding()
        if type(frequencies_hz) is not list:
            _raise("INVALID", "EXPECTED_LIST", "/frequencies_hz")
        seq: list[float] = []
        errs: list[tuple[str, str]] = []
        for i, item in enumerate(frequencies_hz):
            path = f"/frequencies_hz/{i}"
            f = _number(item, path, errs)
            if f is not None and cast(float, f) < 0:
                errs.append((path, "NUMBER_OUT_OF_RANGE"))
            seq.append(cast(float, f))
        _fail(errs)
        if not seq:
            _raise("INVALID", "EMPTY_REQUEST", "/frequencies_hz")
        if len(seq) > 256:
            _raise("UNSUPPORTED", "REQUEST_TOO_LARGE", "/frequencies_hz")
        for i, f in enumerate(seq):
            if f not in physics.FREQUENCIES:
                _raise("UNSUPPORTED", "FREQUENCY_NOT_SUPPORTED", f"/frequencies_hz/{i}")
        bp = snap["blueprint"]
        c_area = next(o["area_m2"] for o in bp["organs"] if o["id"] == "C")
        c_load = next(x["kind"] for x in bp["loads"] if x["port"] == "C.out")
        scale = bp["source"]["scale"]
        pressure: list[list[dict[str, float]]] = []
        flows: list[list[dict[str, float]]] = []
        powers: list[list[float]] = []
        diags: list[dict[str, float]] = []
        for i, f in enumerate(seq):
            try:
                sample = physics._solve_fixture(c_area, c_load, scale, f)
            except physics.Tree5NumericalError as exc:
                _raise("NUMERICALLY_UNRESOLVED", exc.code, f"/frequencies_hz/{i}")
            pressure.append([_complex(z) for z in sample.pressure_pa])
            flows.append([_complex(z) for z in sample.volume_flow_m3_s])
            powers.append([_finite(w) for w in sample.mean_power_w])
            diags.append({
                "condition_number_2": _finite(sample.condition_number_2),
                "scaled_linear_residual": _finite(sample.scaled_linear_residual),
                "j1_scaled_pressure_residual": _finite(sample.j1_scaled_pressure_residual),
                "j2_scaled_pressure_residual": _finite(sample.j2_scaled_pressure_residual),
                "j1_scaled_flow_residual": _finite(sample.j1_scaled_flow_residual),
                "j2_scaled_flow_residual": _finite(sample.j2_scaled_flow_residual),
                "relative_power_defect": _finite(sample.relative_power_defect),
            })
        out: dict[str, Any] = {
            "schema": OBSERVATION_SCHEMA, "digest_version": DIGEST_VERSION,
            "backend_id": BACKEND_ID, "blueprint_digest": snap["blueprint_digest"],
            "preparation_digest": snap["preparation_digest"],
            "status": "SUCCESS", "frequencies_hz": seq,
            "port_ids": list(physics.PORT_IDS),
            "pressure_pa": pressure, "volume_flow_m3_s": flows,
            "mean_power_w": powers, "diagnostics": diags,
        }
        out["observation_digest"] = _hash("observation", out)
        return out


def _finite(x: float) -> float:
    from . import tree5 as physics

    value = float(x)
    if not math.isfinite(value):
        raise physics.Tree5NumericalError("NUMERIC_NONFINITE")
    return 0. if value == 0. else value


def _complex(z: complex) -> dict[str, float]:
    return {"real": _finite(z.real), "imag": _finite(z.imag)}


def prepare_tree5(blueprint: dict[str, object]) -> PreparedTree5:
    bp = _normalize_blueprint(blueprint)
    _capability(bp)
    return _fresh(bp)


def _restore_impl(snapshot: object) -> PreparedTree5:
    errors: list[tuple[str, str]] = []
    outer = _scan(snapshot, "snapshot", "", errors)
    _fail(errors)
    snap = cast(dict[str, Any], outer)
    bp = cast(dict[str, Any], snap["blueprint"])
    _relations(bp, "/blueprint")
    # _scan validates the shape; relation normalization now sorts only unordered collections.
    for collection, key in (("organs", "id"), ("junctions", "id"), ("loads", "port")):
        bp[collection].sort(key=lambda x: x[key])
    if snap["schema"] != SNAPSHOT_SCHEMA:
        _raise("UNSUPPORTED", "VERSION_NOT_SUPPORTED", "/schema")
    if snap["digest_version"] != DIGEST_VERSION:
        _raise("UNSUPPORTED", "VERSION_NOT_SUPPORTED", "/digest_version")
    if snap["backend_id"] != BACKEND_ID:
        _raise("UNSUPPORTED", "BACKEND_NOT_SUPPORTED", "/backend_id")
    _capability(bp, "/blueprint")
    expected = _snapshot(bp)
    for name in ("blueprint_digest", "preparation_digest"):
        if snap[name] != expected[name]:
            _raise("INVALID", "IDENTITY_MISMATCH", "/" + name)
    return _fresh(bp)


def restore_tree5(snapshot: dict[str, object]) -> PreparedTree5:
    return _restore_impl(snapshot)


class _Pairs(list):
    """Preserve raw duplicate JSON keys until their escaped paths are known."""


def decode_tree5_json(raw: str) -> object:
    """Optional strict JSON adapter; duplicate member keys refuse before dict loss."""
    if type(raw) is not str:
        _raise("INVALID", "INVALID_STRING", "")
    try:
        candidate = json.loads(raw, object_pairs_hook=_Pairs,
                               parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
    except (ValueError, TypeError):
        _raise("INVALID", "INVALID_NUMBER", "")

    def unwrap(v: object, path: str) -> object:
        if isinstance(v, _Pairs):
            out: dict[str, object] = {}
            for pair in v:
                key, child = cast(tuple[str, object], pair)
                name = path + "/" + _ptr(key)
                if key in out:
                    _raise("INVALID", "DUPLICATE_JSON_KEY", name)
                out[key] = unwrap(child, name)
            return out
        if type(v) is list:
            return [unwrap(child, path + "/" + str(i)) for i, child in enumerate(cast(list[object], v))]
        return v
    return unwrap(candidate, "")
