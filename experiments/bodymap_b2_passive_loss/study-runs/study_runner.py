"""BODYMAP B2 registered study runner (supervisor executor tooling).

Executes the preregistered BODYMAP-B2-PREREG/1 study under run manifest
BODYMAP-B2-RUNMANIFEST-20261113-01 + ADDENDUM-01/02:
  mode=engineering : the 8 known engineering cases, candidate vs the
                     independent reviewer oracle (reproduction gate only;
                     KNOWN_ENGINEERING_DATA, never study data).
  mode=study       : the 12 primary cases + 3 separate-process repeated
                     nulls + FZ-N1 negative families, full FZ-T1 checks,
                     packs, arrays, and the two-axis verdict.
  mode=repeat      : one geometry's lambda=0 case in a fresh process
                     (invoked by mode=study via subprocess).

The candidate and oracle code are imported from the pinned Core clone
(--repo); this runner contains no physics of its own beyond the frozen
FZ-T1 comparisons. No tolerance is relaxed anywhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HP_STAR = 1.21 * 2 * math.pi * 800 / (4 * math.pi * 0.20)
QUAD_BINS = [100, 250, 400, 600, 800]
GEOMS = ("M0_REST", "U6_REF", "U19_REF")
LAMBDAS = (0.0, 1e-6, 0.5, 1.0)
ENG_CASES = [("U6_REF", 0.0), ("U6_REF", 1e-6), ("U6_REF", 0.5),
             ("U6_REF", 1.0), ("U19_REF", 0.0), ("U19_REF", 1.0),
             ("M0_REST", 0.0), ("M0_REST", 1.0)]


def norm_err(cand, ref, scale):
    return abs(complex(cand) - complex(ref)) / scale


def tol(ref, scale, tight):
    if tight:
        return 1e-12 + 1e-10 * abs(ref) / scale
    return 1e-10 + 1e-8 * abs(ref) / scale


def load_context(repo: Path):
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "src"))
    from experiments.bodymap_b2_passive_loss.prereg_binding import (
        FREQUENCIES_HZ, Refusal)
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
    from experiments.bodymap_b2_passive_loss.reviewer_oracle.recursion import (
        evaluate_case)
    from experiments.bodymap_b2_passive_loss.reviewer_oracle.quadrature import (
        dissipation)
    from experiments.bodymap_b2_passive_loss.reviewer_oracle.direct_pressure import (
        direct_pressure)
    return {
        "FREQUENCIES_HZ": FREQUENCIES_HZ, "Refusal": Refusal,
        "resolve_geometry": resolve_geometry,
        "consumed_source": consumed_source, "compute_case": compute_case,
        "projected_pressure": projected_pressure,
        "cand_inspect": cand_inspect, "mutations": mutations,
        "evaluate_case": evaluate_case, "dissipation": dissipation,
        "direct_pressure": direct_pressure,
    }


def to_c(mp, v) -> complex:
    return complex(float(mp.re(v)), float(mp.im(v)))


def evaluate_full(ctx, mp, gname, lam, geometries, source, save_dir=None):
    """Candidate vs independent oracle over the full 351-bin grid."""
    g = geometries[gname]
    radii_f = tuple(float(r) for r in g["radii_m"])
    lengths_f = tuple(float(l) for l in g["lengths_m"])
    cand = ctx["compute_case"](radii_f, lengths_f, lam)
    press = ctx["projected_pressure"](source["buffer"], cand["Hp"])
    oracle = ctx["evaluate_case"](list(ctx["FREQUENCIES_HZ"]),
                                  [repr(r) for r in radii_f],
                                  [repr(l) for l in lengths_f],
                                  repr(lam), bulk=True)
    zstar = 1.21 * 343.0 / (math.pi * radii_f[0] ** 2)
    tight = lam == 0.0
    worst: dict[str, float] = {}
    ok = True

    def bump(key, err, limit):
        nonlocal ok
        worst[key] = max(worst.get(key, 0.0), err)
        if err > limit:
            ok = False

    for i, f in enumerate(ctx["FREQUENCIES_HZ"]):
        woc = (2 * math.pi * f) / 343.0
        ob, oc = oracle[i], oracle[i]["coeffs"]
        for name, cv, ov, scale in (
                ("HU", cand["HU"][i], to_c(mp, ob["HU"]), 1.0),
                ("Zin", cand["Zin"][i], to_c(mp, ob["Zin"]), zstar),
                ("Hp", cand["Hp"][i], to_c(mp, ob["Hp"]), HP_STAR)):
            bump(f"max_err_{name}", norm_err(cv, ov, scale),
                 tol(ov, scale, tight))
        bump("max_err_detT", float(abs(cand["detT"][i] - 1)), 1e-8)
        for s in range(len(radii_f)):
            for name, carr, okey, scale in (
                    ("z", cand["z"], "z", zstar),
                    ("y", cand["y"], "y", 1.0 / zstar),
                    ("gamma", cand["gamma"], "gamma", woc),
                    ("zc", cand["zc"], "zc", zstar)):
                ov = to_c(mp, oc[s][okey])
                bump(f"max_err_{name}",
                     norm_err(carr[i, s], ov, scale), tol(ov, scale, tight))
    hp_or = np.array([to_c(mp, o["Hp"]) for o in oracle])
    mine = np.empty(24000)
    for lo in range(0, 24000, 2000):
        idx = np.arange(lo, min(lo + 2000, 24000))
        mine[idx] = ctx["direct_pressure"](source["Q"], hp_or, idx)
    ref = press["pressure_pa"]
    raw_l2 = float(np.linalg.norm(mine - ref) / np.linalg.norm(ref))
    worst["raw_l2_vs_oracle"] = raw_l2
    if raw_l2 > 1e-8:
        ok = False
    diag = ctx["cand_inspect"](cand)
    entry = {"ok": ok, **worst,
             "candidate_physics": {k: diag[k] for k in (
                 "max_s_scatter", "min_zin_norm_real", "max_det_error",
                 "max_balance_normalized",
                 "max_gauss16_32_difference_normalized",
                 "min_d32_normalized")},
             "d32_over_pstar_max": float(max(diag["d32_over_pstar"])),
             "raw_sha256": press["raw_sha256_le_f64"]}
    if save_dir is not None:
        np.savez_compressed(
            Path(save_dir) / f"{gname}_lam{lam}.npz",
            frequency_hz=cand["frequency_hz"], HU=cand["HU"],
            Zin=cand["Zin"], Hp=cand["Hp"], z=cand["z"], y=cand["y"],
            gamma=cand["gamma"], zc=cand["zc"], detT=cand["detT"],
            states=cand["states"], pressure_pa=ref,
            oracle_HU=np.array([to_c(mp, o["HU"]) for o in oracle]),
            oracle_Zin=np.array([to_c(mp, o["Zin"]) for o in oracle]),
            oracle_Hp=hp_or,
            d32_over_pstar=np.array(diag["d32_over_pstar"]))
    return entry, cand, press


def oracle_power(ctx, mp, gname, lam, geometries):
    """Independent oracle dissipation on the registered quad-bin subset."""
    g = geometries[gname]
    radii_s = [repr(float(r)) for r in g["radii_m"]]
    lengths_s = [repr(float(l)) for l in g["lengths_m"]]
    oracle = ctx["evaluate_case"](QUAD_BINS, radii_s, lengths_s,
                                  repr(lam), bulk=True)
    zstar = 1.21 * 343.0 / (math.pi * float(g["radii_m"][0]) ** 2)
    worst_bal = worst_conv = 0.0
    min_d = float("inf")
    dvals = {}
    ok = True
    for ob in oracle:
        p_in, u_in = ob["states"][0]
        _p_out, u_out = ob["states"][-1]
        with mp.workdps(80):
            pin = 0.5 * float(mp.re(p_in * mp.conj(u_in)))
            pout = 0.5 * float(ob["load_R"]) * float(abs(u_out)) ** 2
            pstar = 0.5 * zstar * float(abs(u_in)) ** 2
            d16 = float(ctx["dissipation"](ob, lengths_s, 16))
            d32 = float(ctx["dissipation"](ob, lengths_s, 32))
        worst_bal = max(worst_bal, abs(pin - pout - d32) / pstar)
        worst_conv = max(worst_conv, abs(d32 - d16) / pstar)
        min_d = min(min_d, d32 / pstar)
        dvals[str(int(float(ob["f"])))] = d32 / pstar
        if lam == 0.0 and abs(d32) / pstar > 1e-10:
            ok = False
    ok = ok and worst_bal <= 1e-8 and worst_conv <= 1e-10 and min_d >= -1e-10
    return {"ok": ok, "max_balance": worst_bal,
            "max_16_32_diff": worst_conv, "min_d32_over_pstar": min_d,
            "d32_over_pstar_by_bin": dvals, "bins": QUAD_BINS}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pin", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--mode", choices=("engineering", "study", "repeat"),
                    required=True)
    ap.add_argument("--repeat-case", default=None)
    ap.add_argument("--repeat-out", default=None)
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    ctx = load_context(repo)
    from mpmath import mp

    if args.mode == "repeat":
        g = ctx["resolve_geometry"](args.repeat_case)
        s = ctx["consumed_source"]()
        c = ctx["compute_case"](tuple(g["radii_m"]), tuple(g["lengths_m"]),
                                0.0)
        p = ctx["projected_pressure"](s["buffer"], c["Hp"])
        np.save(args.repeat_out, p["pressure_pa"])
        print(p["raw_sha256_le_f64"])
        return 0

    t0 = time.time()
    report: dict = {"mode": args.mode, "pin": args.pin, "checks": {},
                    "cases": {}, "failures": [], "timings_s": {}}

    def record(name, ok, detail):
        report["checks"][name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            report["failures"].append(name)

    geometries = {name: ctx["resolve_geometry"](name) for name in GEOMS}
    source = ctx["consumed_source"]()
    src_sha = hashlib.sha256(source["buffer"].tobytes()).hexdigest()
    record("source_sha_matches_binding",
           src_sha == source["source_sha256_le_f64"], src_sha)
    record("m0_digest",
           geometries["M0_REST"]["preparation_digest"]
           == "sha256:a98d484f8740bf40a419ac117a2deb41ab659dea095577874455aec0713258de",
           geometries["M0_REST"]["preparation_digest"])
    report["source"] = {"sha256_le_f64": src_sha,
                         "dft_sha256": source["dft_sha256_le_complex128"],
                         "status": source["source_status"]}

    cases = ENG_CASES if args.mode == "engineering" else [
        (g, lam) for g in GEOMS for lam in LAMBDAS]
    save_dir = None
    if args.mode == "study":
        save_dir = out_dir / "arrays"
        save_dir.mkdir(exist_ok=True)
    cand_cases, cand_press = {}, {}
    for gname, lam in cases:
        t = time.time()
        entry, cand, press = evaluate_full(
            ctx, mp, gname, lam, geometries, source, save_dir)
        cand_cases[(gname, lam)] = cand
        cand_press[(gname, lam)] = press
        report["cases"][f"{gname}@{lam}"] = entry
        report["timings_s"][f"case_{gname}_{lam}"] = round(time.time() - t, 2)
        record(f"case_{gname}_{lam}", entry["ok"],
               {k: entry[k] for k in entry if k.startswith("max_err")
                or k == "raw_l2_vs_oracle"})
    report["timings_s"]["all_cases"] = round(time.time() - t0, 2)


    # ---- oracle power subset for every evaluated case ------------------
    t = time.time()
    for gname, lam in cases:
        pw = oracle_power(ctx, mp, gname, lam, geometries)
        report["cases"][f"{gname}@{lam}"]["oracle_power"] = pw
        record(f"oracle_power_{gname}_{lam}", pw["ok"],
               {"max_balance": pw["max_balance"],
                "max_16_32_diff": pw["max_16_32_diff"],
                "min_d32_over_pstar": pw["min_d32_over_pstar"]})
    report["timings_s"]["oracle_power"] = round(time.time() - t, 2)

    if args.mode == "engineering":
        report["verdict"] = ("ENGINEERING_REPRODUCED"
                             if not report["failures"] else "FAIL")
        (out_dir / "engineering-report.json").write_text(
            json.dumps(report, indent=2, default=str))
        print(json.dumps({"verdict": report["verdict"],
                          "failures": report["failures"],
                          "timings_s": report["timings_s"]}, indent=2))
        return 0 if not report["failures"] else 1

    # ---- near-null (registered FZ-T1, per geometry) --------------------
    near = {}
    for gname in GEOMS:
        g = geometries[gname]
        zstar = 1.21 * 343.0 / (math.pi * float(g["radii_m"][0]) ** 2)
        worst_ratio = 0.0
        for key, scale in (("HU", 1.0), ("Zin", zstar), ("Hp", HP_STAR)):
            x0 = cand_cases[(gname, 0.0)][key] / scale
            xl = cand_cases[(gname, 1e-6)][key] / scale
            ratio = np.max(np.abs(xl - x0) / np.maximum(1.0, np.abs(x0)))
            worst_ratio = max(worst_ratio, float(ratio))
        raw_l2 = float(np.linalg.norm(
            cand_press[(gname, 1e-6)]["pressure_pa"]
            - cand_press[(gname, 0.0)]["pressure_pa"])
            / np.linalg.norm(cand_press[(gname, 0.0)]["pressure_pa"]))
        ok = worst_ratio <= 1e-4 and raw_l2 <= 1e-4
        near[gname] = {"max_ratio": worst_ratio, "raw_l2": raw_l2, "ok": ok}
        record(f"near_null_{gname}", ok, near[gname])
    report["near_null"] = near

    # ---- effect test (M0, registered floor) -----------------------------
    hp0 = cand_cases[("M0_REST", 0.0)]["Hp"]
    hp1 = cand_cases[("M0_REST", 1.0)]["Hp"]
    eff_hp = float(np.max(np.abs(hp1 - hp0)
                          / np.maximum(HP_STAR, np.abs(hp0))))
    eff_raw = float(np.linalg.norm(
        cand_press[("M0_REST", 1.0)]["pressure_pa"]
        - cand_press[("M0_REST", 0.0)]["pressure_pa"])
        / np.linalg.norm(cand_press[("M0_REST", 0.0)]["pressure_pa"]))
    d_oracle = report["cases"]["M0_REST@1.0"]["oracle_power"][
        "d32_over_pstar_by_bin"]
    eff_d = float(max(d_oracle.values()))
    effect = {"max_hp_ratio": eff_hp, "raw_l2": eff_raw,
              "max_oracle_d32_over_pstar_quadbins": eff_d,
              "criteria": {"hp": eff_hp > 1e-6, "raw": eff_raw > 1e-6,
                           "d": eff_d > 1e-10}}
    effect["detected"] = all(effect["criteria"].values())
    report["effect_m0"] = effect


    # ---- FZ-N1 negatives -------------------------------------------------
    mut = ctx["mutations"]
    probes = {}
    for gname in ("U6_REF", "M0_REST"):
        geo = geometries[gname]
        case_dict = {"case": gname, "radii_m": geo["radii_m"],
                     "lengths_m": geo["lengths_m"],
                     "preparation_digest":
                         geo["preparation_digest"]}
        names = list(mut.EXPECTED) if gname == "U6_REF" else [
            "SWAP-GEOM-PORT"]
        for name in names:
            r = mut.run_one(
                name, case=case_dict,
                null=cand_cases[(gname, 0.0)],
                full=cand_cases[(gname, 1.0)],
                pressure_null=cand_press[(gname, 0.0)]["pressure_pa"],
                pressure_full=cand_press[(gname, 1.0)]["pressure_pa"],
                source=source)
            probes[f"{name}@{gname}"] = r["verdict"]
    report["mutations"] = probes
    record("mutations_all_refused",
           all(v == "CANDIDATE_REFUSAL_OBSERVED" for v in probes.values()),
           probes)
    # oracle adjudication of SWAP-COEFF (doubled z must be caught)
    geo_u6 = geometries["U6_REF"]
    z_or = ctx["evaluate_case"](
        [200], [repr(float(r)) for r in geo_u6["radii_m"]],
        [repr(float(l)) for l in geo_u6["lengths_m"]], "1.0",
        bulk=True)[0]["coeffs"][0]["z"]
    z_ref = to_c(mp, z_or)
    z_cand = complex(cand_cases[("U6_REF", 1.0)]["z"][50, 0])
    zstar_u6 = 1.21 * 343.0 / (math.pi * 0.006 ** 2)
    err_true = norm_err(z_cand, z_ref, zstar_u6)
    err_swap = norm_err(2 * z_cand, z_ref, zstar_u6)
    record("oracle_adjudication_swap_coeff",
           err_true <= tol(z_ref, zstar_u6, False) < err_swap,
           {"err_true": err_true, "err_if_swapped": err_swap})

    # ---- packs (one per primary case) ------------------------------------
    from experiments.bodymap_b2_passive_loss.verification.pack_v0 import (
        new_pack, write_once, old_reader)
    packs_dir = out_dir / "packs"
    packs_dir.mkdir(exist_ok=True)
    pack_info = {}
    for gname, lam in [(g, l) for g in GEOMS for l in LAMBDAS]:
        coeff_manifest = json.dumps(
            {"law": "b2.lrf.circular-rigid-isothermal/1", "lambda": lam,
             "case": gname, "oracle": "reviewer_oracle/1"},
            sort_keys=True).encode()
        ev = f"b2-study-20261113-{gname.lower()}-lam{lam}"
        pack = new_pack(
            evidence_id=ev, utc="2026-11-13T00:00:00Z",
            case_id=f"STUDY-{gname}-{lam}", run_head=args.pin,
            verification_head=None, geometry=geometries[gname],
            source={"recomputed_samples_sha256": src_sha,
                    "evidence_class": "RECOMPUTED"},
            raw_sha256=cand_press[(gname, lam)]["raw_sha256_le_f64"],
            coefficient_ref="reviewer_oracle:coefficients/1",
            coefficient_sha256=hashlib.sha256(coeff_manifest).hexdigest(),
            loss=lam, status="STUDY_RUN_RECORDED")
        pth = packs_dir / f"{ev}.json"
        digest = write_once(pth, pack)
        rb = old_reader(pth, digest)
        pack_info[f"{gname}@{lam}"] = {
            "pack_sha256": digest,
            "take_id_is_null": rb["origin"]["take_id"] is None}
    report["packs"] = pack_info
    record("packs_write_readback",
           all(v["take_id_is_null"] for v in pack_info.values()),
           {"count": len(pack_info)})


    # ---- repeated nulls (separate processes) ------------------------------
    rep_dir = out_dir / "repeats"
    rep_dir.mkdir(exist_ok=True)
    repeats = {}
    for gname in GEOMS:
        out_npy = rep_dir / f"{gname}_null_repeat.npy"
        import os
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()),
             "--mode", "repeat", "--repo", str(repo), "--pin", args.pin,
             "--out-dir", str(out_dir), "--repeat-case", gname,
             "--repeat-out", str(out_npy)],
            capture_output=True, text=True, timeout=1200, env=env)
        rep_sha = proc.stdout.strip()
        arr = np.load(out_npy)
        orig = cand_press[(gname, 0.0)]["pressure_pa"]
        l2 = float(np.linalg.norm(arr - orig) / np.linalg.norm(orig))
        ok = proc.returncode == 0 and l2 <= 1e-12
        repeats[gname] = {"repeat_sha256": rep_sha,
                          "in_process_sha256":
                              cand_press[(gname, 0.0)]["raw_sha256_le_f64"],
                          "raw_l2": l2, "ok": ok}
        record(f"repeat_null_{gname}", ok, repeats[gname])
    report["repeats"] = repeats

    # ---- two-axis verdict (registered FZ-T1) ------------------------------
    conformance = "PASS" if not report["failures"] else "FAIL"
    if conformance == "PASS":
        effect_axis = "DETECTED" if effect["detected"] else "NOT_DETECTED"
    else:
        effect_axis = "UNKNOWN"
    report["verdict"] = {"IMPLEMENTATION_CONFORMANCE": conformance,
                         "EFFECT": effect_axis}
    report["timings_s"]["total"] = round(time.time() - t0, 2)
    (out_dir / "study-report.json").write_text(
        json.dumps(report, indent=2, default=str))
    print(json.dumps({"verdict": report["verdict"],
                      "failures": report["failures"],
                      "effect_m0": effect,
                      "timings_s": report["timings_s"]}, indent=2))
    return 0 if not report["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
