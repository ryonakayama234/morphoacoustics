"""Reviewer end-to-end engineering acceptance for BODYMAP-B2-PREREG/1.

Owned by the supervisor/reviewer. Runs the candidate's eight registered
engineering cases plus the separate-process M0 null repeat, and compares
every primary observable against the independent reviewer oracle under
the frozen FZ-T1 tolerances. Also adjudicates the nine FZ-N1 mutation
families, exercises the pack/0 writer and fresh-process readback, and
emits a JSON evidence report. This is engineering acceptance only: it
authorizes no scientific study evaluation (the registered 15 cases are
never touched here).

Usage:
  python -m experiments.bodymap_b2_passive_loss.reviewer_oracle.run_acceptance \
      --repo /path/to/core --candidate-head <sha> --out report.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np


def _norm_err(cand: complex, ref: complex, scale: float) -> float:
    return abs(complex(cand) - complex(ref)) / scale


def _tol(ref: complex, scale: float, tight: bool) -> float:
    if tight:
        return 1e-12 + 1e-10 * abs(ref) / scale
    return 1e-10 + 1e-8 * abs(ref) / scale


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--candidate-head", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "src"))

    from mpmath import mp, mpf
    from experiments.bodymap_b2_passive_loss.prereg_binding import (
        FREQUENCIES_HZ, LAMBDAS, Refusal)
    from experiments.bodymap_b2_passive_loss.geometry_binding import (
        resolve_geometry)
    from experiments.bodymap_b2_passive_loss.source_binding import (
        consumed_source)
    from experiments.bodymap_b2_passive_loss.candidate.transfer import (
        compute_case)
    from experiments.bodymap_b2_passive_loss.candidate.pressure import (
        projected_pressure)
    from experiments.bodymap_b2_passive_loss.verification.physics import (
        inspect as cand_inspect)
    from experiments.bodymap_b2_passive_loss.verification import mutations
    from experiments.bodymap_b2_passive_loss.reviewer_oracle.series import (
        f_ratio, f_ratio_bulk)
    from experiments.bodymap_b2_passive_loss.reviewer_oracle.recursion import (
        evaluate_case)
    from experiments.bodymap_b2_passive_loss.reviewer_oracle.quadrature import (
        dissipation)
    from experiments.bodymap_b2_passive_loss.reviewer_oracle.direct_pressure import (
        direct_pressure)

    report: dict = {"candidate_head": args.candidate_head, "checks": {},
                    "cases": {}, "failures": []}

    def record(name: str, ok: bool, detail: object) -> None:
        report["checks"][name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            report["failures"].append(name)

    # ---- shared fixture inputs (read-only, content-addressed) ----------
    geometries = {name: resolve_geometry(name)
                  for name in ("U6_REF", "U19_REF", "M0_REST")}
    source = consumed_source()
    my_src_sha = hashlib.sha256(source["buffer"].tobytes()).hexdigest()
    record("source_sha_matches_binding",
           my_src_sha == source["source_sha256_le_f64"], my_src_sha)
    record("m0_digest", geometries["M0_REST"]["preparation_digest"]
           == "sha256:a98d484f8740bf40a419ac117a2deb41ab659dea095577874455aec0713258de",
           geometries["M0_REST"]["preparation_digest"])

    # ---- certification lattice: bulk series vs 400/450-digit series ----
    with mp.workdps(80):
        rho, mu, kap, cp = mpf("1.21"), mpf("1.81e-5"), mpf("0.0257"), mpf("1005")
        worst = mpf(0)
        for radius in {r for g in geometries.values() for r in g["radii_m"]}:
            a = mpf(repr(radius))
            for f in range(100, 801, 100):
                w = 2 * mp.pi * f
                for q in (a * mp.sqrt(-1j * w * rho / mu),
                          a * mp.sqrt(-1j * w * rho * cp / kap)):
                    qs = (str(mp.re(q)), str(mp.im(q)))
                    cert, _info = f_ratio(*qs)
                    bulk = f_ratio_bulk(*qs)
                    d = abs(cert - bulk) / max(mpf(1), abs(cert))
                    worst = max(worst, d)
        record("series_bulk_vs_certified_lattice", worst <= mpf("1e-60"),
               f"max relative difference {worst}")

    # ---- engineering cases: candidate vs oracle, full grid -------------
    hp_star = 1.21 * 2 * math.pi * 800 / (4 * math.pi * 0.20)
    case_defs = [("U6_REF", 0.0), ("U6_REF", 1e-6), ("U6_REF", 0.5),
                 ("U6_REF", 1.0), ("U19_REF", 0.0), ("U19_REF", 1.0),
                 ("M0_REST", 0.0), ("M0_REST", 1.0)]
    cand_cases: dict[tuple[str, float], dict] = {}
    cand_press: dict[tuple[str, float], dict] = {}
    for gname, lam in case_defs:
        g = geometries[gname]
        radii_f = tuple(float(r) for r in g["radii_m"])
        lengths_f = tuple(float(l) for l in g["lengths_m"])
        cand = compute_case(radii_f, lengths_f, lam)
        cand_cases[(gname, lam)] = cand
        press = projected_pressure(source["buffer"], cand["Hp"])
        cand_press[(gname, lam)] = press
        oracle = evaluate_case(list(FREQUENCIES_HZ),
                               [repr(r) for r in radii_f],
                               [repr(l) for l in lengths_f],
                               repr(lam), bulk=True)
        zstar = 1.21 * 343.0 / (math.pi * radii_f[0] ** 2)
        tight = lam == 0.0
        worst: dict[str, float] = {}
        ok = True
        for i, f in enumerate(FREQUENCIES_HZ):
            woc = (2 * math.pi * f) / 343.0
            ob = oracle[i]
            oc = ob["coeffs"]
            fields = (
                ("HU", cand["HU"][i], complex(float(mp.re(ob["HU"])),
                 float(mp.im(ob["HU"]))), 1.0),
                ("Zin", cand["Zin"][i], complex(float(mp.re(ob["Zin"])),
                 float(mp.im(ob["Zin"]))), zstar),
                ("Hp", cand["Hp"][i], complex(float(mp.re(ob["Hp"])),
                 float(mp.im(ob["Hp"]))), hp_star),
                ("detT", abs(cand["detT"][i] - 1), 0.0, 1.0),
            )
            for name, cv, ov, scale in fields:
                if name == "detT":
                    err, tol = float(cv), 1e-8
                else:
                    err = _norm_err(cv, ov, scale)
                    tol = _tol(ov, scale, tight)
                key = f"max_err_{name}"
                worst[key] = max(worst.get(key, 0.0), err)
                if err > tol:
                    ok = False
            for s in range(len(radii_f)):
                for name, carr, okey, scale in (
                        ("z", cand["z"], "z", zstar),
                        ("y", cand["y"], "y", 1.0 / zstar),
                        ("gamma", cand["gamma"], "gamma", woc),
                        ("zc", cand["zc"], "zc", zstar)):
                    ov = complex(float(mp.re(oc[s][okey])),
                                 float(mp.im(oc[s][okey])))
                    err = _norm_err(carr[i, s], ov, scale)
                    key = f"max_err_{name}"
                    worst[key] = max(worst.get(key, 0.0), err)
                    if err > _tol(ov, scale, tight):
                        ok = False
        # raw waveform: oracle direct sum vs candidate irfft projection
        hp_or = np.array([complex(float(mp.re(o["Hp"])), float(mp.im(o["Hp"])))
                          for o in oracle])
        mine = np.empty(24000)
        for lo in range(0, 24000, 2000):
            idx = np.arange(lo, min(lo + 2000, 24000))
            mine[idx] = direct_pressure(source["Q"], hp_or, idx)
        ref = cand_press[(gname, lam)]["pressure_pa"]
        raw_l2 = float(np.linalg.norm(mine - ref) / np.linalg.norm(ref))
        worst["raw_l2_vs_oracle"] = raw_l2
        if raw_l2 > 1e-8:
            ok = False
        diag = cand_inspect(cand)
        report["cases"][f"{gname}@{lam}"] = {
            "ok": ok, **worst,
            "candidate_physics": {k: diag[k] for k in (
                "max_s_scatter", "min_zin_norm_real", "max_det_error",
                "max_balance_normalized",
                "max_gauss16_32_difference_normalized")}}
        record(f"case_{gname}_{lam}", ok, worst)

    # ---- near-null ordering (U6, lambda = 1e-6, candidate outputs) -----
    d_near = np.max(np.abs(cand_cases[("U6_REF", 1e-6)]["HU"]
                           - cand_cases[("U6_REF", 0.0)]["HU"]))
    d_full = np.max(np.abs(cand_cases[("U6_REF", 1.0)]["HU"]
                           - cand_cases[("U6_REF", 0.0)]["HU"]))
    record("near_null_ordering_candidate",
           bool(d_near <= 1e-2 * d_full + 1e-4),
           {"d_near": float(d_near), "d_full": float(d_full)})

    # ---- oracle power balance / dissipation on a bin subset ------------
    quad_bins = [100, 250, 400, 600, 800]
    for gname, lam in (("U6_REF", 1.0), ("U19_REF", 1.0),
                       ("M0_REST", 1.0), ("M0_REST", 0.0)):
        g = geometries[gname]
        radii_s = [repr(float(r)) for r in g["radii_m"]]
        lengths_s = [repr(float(l)) for l in g["lengths_m"]]
        oracle = evaluate_case(quad_bins, radii_s, lengths_s, repr(lam),
                               bulk=True)
        zstar = 1.21 * 343.0 / (math.pi * float(g["radii_m"][0]) ** 2)
        worst_bal = worst_conv = 0.0
        min_d = float("inf")
        ok = True
        for ob in oracle:
            p_in, u_in = ob["states"][0]
            p_out, u_out = ob["states"][-1]
            with mp.workdps(80):
                pin = 0.5 * float(mp.re(p_in * mp.conj(u_in)))
                pout = 0.5 * float(ob["load_R"]) * float(abs(u_out)) ** 2
                pstar = 0.5 * zstar * float(abs(u_in)) ** 2
                d16 = float(dissipation(ob, lengths_s, 16))
                d32 = float(dissipation(ob, lengths_s, 32))
            worst_bal = max(worst_bal, abs(pin - pout - d32) / pstar)
            worst_conv = max(worst_conv, abs(d32 - d16) / pstar)
            min_d = min(min_d, d32 / pstar)
            if lam == 0.0 and abs(d32) / pstar > 1e-10:
                ok = False
        ok = ok and worst_bal <= 1e-8 and worst_conv <= 1e-10 \
            and min_d >= -1e-10
        record(f"oracle_power_{gname}_{lam}", ok,
               {"max_balance": worst_bal, "max_16_32_diff": worst_conv,
                "min_d32_over_pstar": min_d, "bins": quad_bins})

    # ---- FZ-N1 mutations: candidate probes + oracle adjudication -------
    geo_u6 = geometries["U6_REF"]
    case_dict = {"case": "U6_REF", "radii_m": geo_u6["radii_m"],
                 "lengths_m": geo_u6["lengths_m"],
                 "preparation_digest": None}
    probe_results = {}
    for name in mutations.EXPECTED:
        r = mutations.run_one(
            name, case=case_dict,
            null=cand_cases[("U6_REF", 0.0)], full=cand_cases[("U6_REF", 1.0)],
            pressure_null=cand_press[("U6_REF", 0.0)]["pressure_pa"],
            pressure_full=cand_press[("U6_REF", 1.0)]["pressure_pa"],
            source=source)
        probe_results[name] = r["verdict"]
    record("mutations_candidate_probes",
           all(v == "CANDIDATE_REFUSAL_OBSERVED"
               for v in probe_results.values()), probe_results)
    # oracle adjudication: a doubled z must be caught by FZ-T1 comparison
    z_or = evaluate_case([200], [repr(float(r)) for r in geo_u6["radii_m"]],
                         [repr(float(l)) for l in geo_u6["lengths_m"]],
                         "1.0", bulk=True)[0]["coeffs"][0]["z"]
    z_ref = complex(float(mp.re(z_or)), float(mp.im(z_or)))
    z_cand = complex(cand_cases[("U6_REF", 1.0)]["z"][50, 0])
    zstar_u6 = 1.21 * 343.0 / (math.pi * 0.006 ** 2)
    err_true = _norm_err(z_cand, z_ref, zstar_u6)
    err_swap = _norm_err(2 * z_cand, z_ref, zstar_u6)
    record("oracle_adjudication_swap_coeff",
           err_true <= _tol(z_ref, zstar_u6, False) < err_swap,
           {"err_true": err_true, "err_if_swapped": err_swap})

    # ---- pack/0 write, readback, tamper --------------------------------
    from experiments.bodymap_b2_passive_loss.verification.pack_v0 import (
        new_pack, write_once, old_reader)
    out_dir = Path(args.out).resolve().parent
    coeff_manifest = json.dumps(
        {"law": "b2.lrf.circular-rigid-isothermal/1", "lambda": 1.0,
         "case": "M0_REST", "oracle": "reviewer_oracle/1"},
        sort_keys=True).encode()
    pack = new_pack(
        evidence_id="b2-eng-acceptance-20261112",
        utc="2026-11-12T00:00:00Z", case_id="ENG-M0-FULL",
        run_head=args.candidate_head, verification_head=None,
        geometry=geometries["M0_REST"],
        source={"recomputed_samples_sha256": my_src_sha,
                "evidence_class": "RECOMPUTED"},
        raw_sha256=cand_press[("M0_REST", 1.0)]["raw_sha256_le_f64"],
        coefficient_ref="reviewer_oracle:coefficients/1",
        coefficient_sha256=hashlib.sha256(coeff_manifest).hexdigest(),
        loss=1.0, status="ENGINEERING_ACCEPTANCE_RECORDED")
    pack_path = out_dir / "b2-eng-pack.json"
    if pack_path.exists():
        pack_path.unlink()
    digest = write_once(pack_path, pack)
    readback = old_reader(pack_path, digest)
    tampered = out_dir / "b2-eng-pack-tampered.json"
    raw = bytearray(pack_path.read_bytes())
    raw[len(raw) // 2] ^= 1
    tampered.write_bytes(bytes(raw))
    tamper_refused = False
    try:
        old_reader(tampered, digest)
    except Refusal:
        tamper_refused = True
    overwrite_refused = False
    try:
        write_once(pack_path, pack)
    except Refusal:
        overwrite_refused = True
    record("pack_v0_write_readback_tamper",
           readback["origin"]["take_id"] is None and tamper_refused
           and overwrite_refused,
           {"pack_sha256": digest, "tamper_refused": tamper_refused,
            "overwrite_refused": overwrite_refused})

    # ---- separate-process M0 null repeat --------------------------------
    snippet = (
        "import sys; sys.path.insert(0, %r); sys.path.insert(0, %r);"
        "from experiments.bodymap_b2_passive_loss.geometry_binding import resolve_geometry;"
        "from experiments.bodymap_b2_passive_loss.source_binding import consumed_source;"
        "from experiments.bodymap_b2_passive_loss.candidate.transfer import compute_case;"
        "from experiments.bodymap_b2_passive_loss.candidate.pressure import projected_pressure;"
        "g = resolve_geometry('M0_REST'); s = consumed_source();"
        "c = compute_case(tuple(g['radii_m']), tuple(g['lengths_m']), 0.0);"
        "p = projected_pressure(s['buffer'], c['Hp']);"
        "print(p['raw_sha256_le_f64'])"
        % (str(repo), str(repo / "src")))
    proc = subprocess.run([sys.executable, "-c", snippet],
                          capture_output=True, text=True, timeout=1200)
    repeat_sha = proc.stdout.strip()
    record("separate_process_m0_null_repeat",
           repeat_sha == cand_press[("M0_REST", 0.0)]["raw_sha256_le_f64"],
           {"repeat_sha256": repeat_sha,
            "in_process_sha256":
                cand_press[("M0_REST", 0.0)]["raw_sha256_le_f64"]})

    report["verdict"] = "PASS" if not report["failures"] else "FAIL"
    Path(args.out).write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps({"verdict": report["verdict"],
                      "failures": report["failures"]}, indent=2))
    return 0 if not report["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
