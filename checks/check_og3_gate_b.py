"""Generate fresh, exact-HEAD OG-3 Draft evidence; not a public adoption decision."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

from morphoacoustics_graph.model import (
    SCHEMA, AcousticPort, AcousticJunction, PassiveTubeOrgan,
    OrganGraphBlueprint, SERIES_LAW,
)
from morphoacoustics_graph.preparation import prepare_graph, observe_transfer


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-head-sha", required=True)
    args = parser.parse_args()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if head != args.expected_head_sha:
        raise RuntimeError("HEAD_SHA_MISMATCH")
    if args.output_dir.exists() or args.output_dir.is_symlink():
        raise FileExistsError("requires a fresh output directory")
    tracked = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],text=True)
    if tracked.strip():
        raise RuntimeError("TRACKED_CHECKOUT_DIRTY")
    a = PassiveTubeOrgan("organ-A", "r1", 0.08, 0.0003,
                         AcousticPort("organ-A.in", "inlet"),
                         AcousticPort("organ-A.out", "outlet"))
    b = PassiveTubeOrgan("organ-B", "r1", 0.09, 0.0006,
                         AcousticPort("organ-B.in", "inlet"),
                         AcousticPort("organ-B.out", "outlet"))
    graph = OrganGraphBlueprint(
        SCHEMA, (a,b),
        (AcousticJunction("edge-AB", SERIES_LAW, ("organ-A.out","organ-B.in")),),
        "organ-A.in", ("organ-B.out",), "matched"
    )
    prepared = prepare_graph(graph)
    grid = [80.,200.,400.,733.,1200.,2200.,4000.]
    observed = observe_transfer(prepared,grid)
    oracle_path = Path("experiments/039_og2_prepared_graph/wolfram/og2_oracle.json")
    oracle_bytes = oracle_path.read_bytes()
    oracle = json.loads(oracle_bytes)
    expected = np.asarray(oracle["normalized_matrix_rowmajor_re_im"], dtype=float)
    reference = (expected[...,0]+1j*expected[...,1]).reshape(-1,2,2)
    error = float(np.max(np.abs(observed.matrix_numpy()-reference)))
    if not error <= 1e-10:
        raise RuntimeError("ORACLE_MISMATCH")
    payload = {
        "schema":"og3.gate_b.evidence.v1",
        "status":"PROVISIONAL_NUMERICAL_PASS_REVIEW_PENDING_NOT_ADOPTED",
        "scope":"two fixed passive rigid lossless uniform tubes, ideal series p/U",
        "head_sha":head,
        "old_oracle_sha256":hashlib.sha256(oracle_bytes).hexdigest(),
        "blueprint_digest":prepared.blueprint_digest,
        "preparation_digest":prepared.preparation_digest,
        "port_mapping":prepared.port_mapping,
        "result":observed.to_dict(),
        "max_complex_error_vs_frozen_oracle":error,
        "threshold":1e-10,
        "numpy_version":np.__version__,
    }
    canonical=(json.dumps(payload,ensure_ascii=False,sort_keys=True,
                          separators=(",",":"),allow_nan=False)+"\n").encode("utf-8")
    args.output_dir.mkdir(parents=True,exist_ok=False)
    (args.output_dir/"observation.json").write_bytes(canonical)
    (args.output_dir/"sha256.txt").write_text(hashlib.sha256(canonical).hexdigest()+"\n")
    print("PROVISIONAL_NUMERICAL_PASS_REVIEW_PENDING_NOT_ADOPTED",head,error)


if __name__=="__main__":
    run()
