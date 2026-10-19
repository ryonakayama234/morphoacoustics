"""Generate/check design contract constants. No production graph API or solver.

python docs/research/og5-contract-fixtures.py --write
python docs/research/og5-contract-fixtures.py --check
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOMAINS = {
    "blueprint": "morphoacoustics.og5.blueprint.v1",
    "preparation": "morphoacoustics.og5.preparation.v1",
    "observation": "morphoacoustics.og5.observation.v1",
}


def encode(value: object) -> bytes:
    if type(value) in (int, float):
        return b"d" + struct.pack(">d", 0.0 if value == 0 else float(value))
    if type(value) is str:
        data = value.encode("ascii")
        return b"s" + struct.pack(">I", len(data)) + data
    if type(value) is list:
        return b"l" + struct.pack(">I", len(value)) + b"".join(map(encode, value))
    if type(value) is dict:
        return b"m" + struct.pack(">I", len(value)) + b"".join(
            encode(k) + encode(value[k]) for k in sorted(value)
        )
    raise TypeError(type(value))


def normalize(value: object) -> object:
    if type(value) in (int, float):
        return 0.0 if value == 0 else float(value)
    if type(value) is list:
        return [normalize(v) for v in value]
    if type(value) is dict:
        return {k: normalize(v) for k, v in value.items()}
    return value


def canonical_blueprint(value: dict) -> dict:
    out = normalize(copy.deepcopy(value))
    for collection, key in (("organs", "id"), ("junctions", "id"), ("loads", "port")):
        out[collection].sort(key=lambda x: x[key])
    return out


def hash_vector(kind: str, payload: dict) -> dict:
    data = encode(payload)
    domain = DOMAINS[kind]
    prefixed = domain.encode("ascii") + b"\0" + data
    return {
        "domain": domain,
        "canonical_hex": data.hex(),
        "domain_prefixed_hex": prefixed.hex(),
        "digest": "sha256:" + hashlib.sha256(prefixed).hexdigest(),
    }


def snapshot(blueprint: dict) -> dict:
    bp = canonical_blueprint(blueprint)
    identity = {
        "schema": "og5.tree5.prepared.snapshot.v1",
        "digest_version": "og5.canonical.binary.v1",
        "backend_id": "og5.fixed.passive.tree5.pu.v1",
        "blueprint_digest": hash_vector("blueprint", bp)["digest"],
    }
    return {
        **identity,
        "blueprint": bp,
        "preparation_digest": hash_vector("preparation", identity)["digest"],
    }


def preparation_payload(snap: dict) -> dict:
    return {k: snap[k] for k in ("schema", "digest_version", "backend_id", "blueprint_digest")}


def observation(snap: dict, records: list[dict], frequencies: list[int]) -> dict:
    ports = [n + "." + e for n in "ABCDE" for e in ("in", "out")]
    rows = [next(r for r in records if r["frequency_hz"] == f and
                 r["c_area_m2"] == .00015 and r["c_load"] == "matched")
            for f in frequencies]
    data = {
        "schema": "og5.tree5.observation.v1",
        "digest_version": snap["digest_version"],
        "backend_id": snap["backend_id"],
        "blueprint_digest": snap["blueprint_digest"],
        "preparation_digest": snap["preparation_digest"],
        "status": "SUCCESS",
        "frequencies_hz": frequencies,
        "port_ids": ports,
        "pressure_pa": [], "volume_flow_m3_s": [], "mean_power_w": [],
        "diagnostics": [],
    }
    # Freeze constants from the archived eight records, not a runtime solver.
    for row in rows:
        p = [complex(*row["port_states"][k]["p_pa"]) for k in ports]
        u = [complex(*row["port_states"][k]["u_m3_s"]) for k in ports]
        data["pressure_pa"].append([{"real": v.real, "imag": v.imag} for v in p])
        data["volume_flow_m3_s"].append([{"real": v.real, "imag": v.imag} for v in u])
        power = [.5 * (a * b.conjugate()).real for a, b in zip(p, u)]
        data["mean_power_w"].append(power)
        # Diagnostic constants are taken from the same archived global solve.
        d = {k: row[k] for k in (
            "condition_number_2", "j1_scaled_pressure_residual",
            "j2_scaled_pressure_residual", "j1_scaled_flow_residual", "j2_scaled_flow_residual",
        )}
        d["scaled_linear_residual"] = row["global_scaled_linear_residual"]
        d["relative_power_defect"] = abs(
            power[0] - sum(power[i] for i in (5, 7, 9))
        ) / max(abs(power[0]), .5 * 1.372 * 1e-6)
        data["diagnostics"].append(d)
    data = normalize(data)
    data["observation_digest"] = hash_vector("observation", data)["digest"]
    return data


def build() -> dict:
    old = json.loads((ROOT / "og5-blueprint-goldens.json").read_text())
    records = json.loads((ROOT / "og5-wolfram-gate-a-result.json").read_text())["records"]
    baseline = old["baseline_blueprint"]
    variants = {}
    for key in ("baseline", "c_area_0006", "c_revision_r2", "reversed_collection_order",
                "source_negative", "source_half", "c_closed", "signed_zero"):
        bp = copy.deepcopy(baseline)
        if key == "c_area_0006": bp["organs"][2]["area_m2"] = .0006
        if key == "c_revision_r2": bp["organs"][2]["revision"] = "r2"
        if key == "reversed_collection_order":
            for k in ("organs", "junctions", "loads"): bp[k].reverse()
        if key == "source_negative": bp["source"]["scale"] = -1
        if key == "source_half": bp["source"]["scale"] = .5
        if key == "c_closed": bp["loads"][0]["kind"] = "rigid_closed"
        if key == "signed_zero": bp["source"]["amplitude_m3_s"]["imag"] = -0.0
        snap = snapshot(bp)
        # The zero imaginary source is intentionally outside fixed capability.
        # This variant checks canonical bytes only and must not be prepared.
        variants[key] = {"input": bp, "snapshot": snap,
                         "prepare_status": "UNSUPPORTED" if key == "signed_zero" else "SUCCESS",
                         "restore_status": "UNSUPPORTED" if key == "signed_zero" else "SUCCESS",
                         "snapshot_role": "canonical bytes only, not an API result" if key == "signed_zero" else "expected API result"}
        if key in old["expected"]:
            assert snap["blueprint_digest"] == old["expected"][key]
    base_snap = variants["baseline"]["snapshot"]
    obs = observation(base_snap, records, [733])
    ordered = observation(base_snap, records, [997, 733, 997])
    vectors = {
        "baseline_blueprint": hash_vector("blueprint", base_snap["blueprint"]),
        "baseline_preparation": hash_vector("preparation", preparation_payload(base_snap)),
        "baseline_observation": hash_vector("observation", {k: v for k, v in obs.items() if k != "observation_digest"}),
        "ordered_duplicate_observation": hash_vector("observation", {k: v for k, v in ordered.items() if k != "observation_digest"}),
        "negative_zero": hash_vector("blueprint", {"number": -0.0}),
        "positive_zero": hash_vector("blueprint", {"number": 0.0}),
    }
    assert vectors["negative_zero"] == vectors["positive_zero"]
    errors = []

    def error(name: str, operation: str, inp: object, status: str, code: str, path: str) -> None:
        errors.append({"name": name, "operation": operation, "input": inp,
                       "expected_error": {"status": status, "code": code, "path": path},
                       "expected_message": f"{status}:{code}:{path}"})

    def bp_change(name, change, status, code, path):
        bp = copy.deepcopy(baseline); change(bp)
        error(name, "prepare", bp, status, code, path)

    bp_change("malformed_before_unknown_version", lambda b: (b.update(schema="og5.unknown.v2"),
              b["organs"][4].update(length_m=True)), "INVALID", "INVALID_NUMBER", "/organs/4/length_m")
    bp_change("lexical_leaf_priority", lambda b: (b["organs"][4].update(length_m=True),
              b["organs"][0].update(area_m2=True)), "INVALID", "INVALID_NUMBER", "/organs/0/area_m2")
    bp_change("escaped_pointer_priority", lambda b: b.update({"a/": 1, "a0": 1}),
              "INVALID", "UNKNOWN_FIELD", "/a0")
    bp_change("escaped_slash", lambda b: b.update({"x/y": 1}), "INVALID", "UNKNOWN_FIELD", "/x~1y")
    bp_change("escaped_tilde", lambda b: b.update({"x~y": 1}), "INVALID", "UNKNOWN_FIELD", "/x~0y")
    bp_change("duplicate_organ_id", lambda b: b["organs"][1].update(id="A"),
              "INVALID", "DUPLICATE_ID", "/organs/1/id")
    bp_change("unknown_port_before_unknown_law", lambda b: b["junctions"][0].update(
              law="unknown.law", ports=["A.out", "missing.in", "C.in"]),
              "INVALID", "UNKNOWN_PORT", "/junctions/0/ports/1")
    bp_change("unknown_schema", lambda b: b.update(schema="og5.unknown.v2"),
              "UNSUPPORTED", "VERSION_NOT_SUPPORTED", "/schema")
    bp_change("unknown_law", lambda b: b["junctions"][0].update(law="unknown.law"),
              "UNSUPPORTED", "LAW_NOT_SUPPORTED", "/junctions/0/law")
    bp_change("physical_port_type", lambda b: b["organs"][0]["inlet"].update(kind="mechanical.f_v"),
              "INVALID", "PORT_TYPE_MISMATCH", "/organs/0/inlet/kind")
    bp_change("unsupported_area", lambda b: b["organs"][0].update(area_m2=.0004),
              "UNSUPPORTED", "GEOMETRY_NOT_SUPPORTED", "/organs/0/area_m2")
    bp_change("child_slot_permutation", lambda b: b["junctions"][1].update(ports=["B.out", "E.in", "D.in"]),
              "UNSUPPORTED", "TOPOLOGY_NOT_SUPPORTED", "/organs")
    bp_change("cycle_with_single_bindings", lambda b: (
        b.update(junctions=[{"id": "J1", "law": "ideal.branch3.p_u", "ports": ["B.out", "C.in", "D.in"]},
                            {"id": "J2", "law": "ideal.branch3.p_u", "ports": ["C.out", "B.in", "E.in"]}]),
        b.update(loads=[{"port": x, "kind": "matched"} for x in ["A.out", "D.out", "E.out"]])),
        "INVALID", "GRAPH_CYCLE", "/junctions")
    larger = copy.deepcopy(baseline)
    for n, length in [("F", .04), ("G", .03)]:
        o = copy.deepcopy(larger["organs"][0]); o.update(id=n, length_m=length)
        o["inlet"]["id"] = n + ".in"; o["outlet"]["id"] = n + ".out"
        larger["organs"].append(o)
    larger["junctions"].append({"id": "J3", "law": "ideal.branch3.p_u", "ports": ["C.out", "F.in", "G.in"]})
    larger["loads"] = [x for x in larger["loads"] if x["port"] != "C.out"] + [
        {"port": n + ".out", "kind": "matched"} for n in "FG"]
    error("valid_seven_organ_tree", "prepare", larger, "UNSUPPORTED", "TOPOLOGY_NOT_SUPPORTED", "/organs")
    for key, val in [("blueprint_digest", "sha256:" + "0" * 64), ("preparation_digest", "sha256:" + "0" * 64)]:
        s = copy.deepcopy(base_snap); s[key] = val
        error("forged_" + key, "restore", s, "INVALID", "IDENTITY_MISMATCH", "/" + key)
    s = copy.deepcopy(base_snap); s["blueprint"]["organs"][2]["revision"] = "r2"
    error("revision_tamper", "restore", s, "INVALID", "IDENTITY_MISMATCH", "/blueprint_digest")
    s = copy.deepcopy(base_snap); s.update(schema="unknown.snapshot.v2", extra=1)
    error("snapshot_extra_before_version", "restore", s, "INVALID", "UNKNOWN_FIELD", "/extra")
    s = copy.deepcopy(base_snap); s.update(schema="unknown.snapshot.v2")
    error("unknown_snapshot_version", "restore", s, "UNSUPPORTED", "VERSION_NOT_SUPPORTED", "/schema")
    for name, freq, status, code, path in [
        ("empty", [], "INVALID", "EMPTY_REQUEST", "/frequencies_hz"),
        ("oversize", [733] * 257, "UNSUPPORTED", "REQUEST_TOO_LARGE", "/frequencies_hz"),
        ("late_bool_before_size", [733] * 256 + [True], "INVALID", "INVALID_NUMBER", "/frequencies_hz/256"),
        ("negative", [-1], "INVALID", "NUMBER_OUT_OF_RANGE", "/frequencies_hz/0"),
        ("unsupported_zero", [0], "UNSUPPORTED", "FREQUENCY_NOT_SUPPORTED", "/frequencies_hz/0"),
        ("unsupported_frequency", [733, 734], "UNSUPPORTED", "FREQUENCY_NOT_SUPPORTED", "/frequencies_hz/1"),
    ]:
        error(name, "response", {"receiver_snapshot": base_snap, "frequencies_hz": freq}, status, code, path)
    corrupt = copy.deepcopy(base_snap); corrupt["preparation_digest"] = "sha256:" + "0" * 64
    error("corrupted_receiver", "response_corrupted_receiver_test_seam",
          {"stored_snapshot": corrupt, "frequencies_hz": [733]}, "INVALID", "PREPARED_BINDING_INVALID", "/prepared")
    errors.append({"name": "duplicate_json_key", "operation": "decode_json",
                   "raw_json": '{"schema":"og5.passive.tree5.v1","schema":"og5.unknown.v2"}',
                   "expected_error": {"status": "INVALID", "code": "DUPLICATE_JSON_KEY", "path": "/schema"},
                   "expected_message": "INVALID:DUPLICATE_JSON_KEY:/schema"})
    numeric = []
    for name, seam, code, frequencies, index in [
        ("rank", "duplicate_last_row_and_rhs", "MATRIX_RANK_DEFICIENT", [733], 0),
        ("condition", "diagonal_last_value_1e_minus5", "MATRIX_ILL_CONDITIONED", [733], 0),
        ("nonfinite", "matrix_nan", "NUMERIC_NONFINITE", [733], 0),
        ("convergence", "backend_convergence_failure", "SOLVE_FAILED", [733], 0),
        ("residual", "solution_coordinate_plus_1e_minus3", "RESIDUAL_TOO_LARGE", [733], 0),
        ("late_atomicity", "duplicate_last_row_and_rhs", "MATRIX_RANK_DEFICIENT", [733, 997], 1),
    ]:
        numeric.append({"name": name, "receiver_snapshot": base_snap, "frequencies_hz": frequencies,
                        "solver_test_seam": seam, "inject_at_sample_index": index,
                        "expected_error": {"status": "NUMERICALLY_UNRESOLVED", "code": code,
                                           "path": f"/frequencies_hz/{index}"},
                        "observation_must_be_absent": True, "digest_must_be_absent": True})
    return {"schema": "og5.design.contract.goldens.a1", "status": "DESIGN_FIXTURES_NOT_CORE_EVIDENCE",
            "domains": DOMAINS, "blueprint_snapshot_variants": variants,
            "baseline_observation": obs, "ordered_duplicate_observation": ordered,
            "byte_vectors": vectors, "error_contract_fixtures": errors,
            "numeric_refusal_test_seams": numeric}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    assert args.write != args.check, "select --write or --check"
    result = build(); path = ROOT / "og5-contract-goldens.json"
    encoded = json.dumps(result, ensure_ascii=True, allow_nan=False, indent=2) + "\n"
    if args.write: path.write_text(encoded)
    else:
        assert path.read_text() == encoded, "goldens differ from archived constants/generator"
        print(json.dumps({"status": "PASS", "snapshot_variants": len(result["blueprint_snapshot_variants"]),
                          "byte_vectors": len(result["byte_vectors"]),
                          "error_contract_fixtures": len(result["error_contract_fixtures"]),
                          "numeric_refusal_test_seams": len(result["numeric_refusal_test_seams"]),
                          "scope": "design fixture regeneration, not validator/solver execution"}))


if __name__ == "__main__": main()
