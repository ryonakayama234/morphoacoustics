"""Read-only input/environment audit. Does not import or execute B2 solvers."""
from pathlib import Path
import contextlib
import datetime
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import subprocess
import sys
import time

repo = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
started = time.perf_counter()
sys.path[:0] = [str(repo), str(repo / 'src')]

def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

pin = '0bb60cc227d231ec1cb67b701a849172ed92164b'
lock = repo / 'requirements/bodymap-b2-physical-py311.lock.txt'
assert git('rev-parse', 'HEAD') == pin
assert not git('status', '--porcelain=v1', '--untracked-files=all')
expected_versions = {'numpy': '2.4.6', 'scipy': '1.17.1', 'mpmath': '1.4.1'}
assert platform.python_version() == '3.11.18'
assert sha(lock) == 'c0bd046498882beb61408440d9eadd1b9708ad8a49ad0035e0bdbaa5d3a6afd7'
versions = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
assert all(importlib.metadata.version(k) == v for k, v in expected_versions.items())

import numpy as np
import scipy
from experiments.bodymap_b2_passive_loss.geometry_binding import resolve_geometry
from experiments.bodymap_b2_passive_loss.source_binding import consumed_source
from experiments.bodymap_b2_passive_loss.prereg_binding import M0_DIGEST, M0_DIAMETERS_MM

geometries = {name: resolve_geometry(name) for name in ('M0_REST', 'U6_REF', 'U19_REF')}
assert geometries['M0_REST']['preparation_digest'] == M0_DIGEST
source = consumed_source()
source_meta = {k: v for k, v in source.items() if k not in ('buffer', 'Q')}
source_meta.update({
    'evidence_class': 'RECOMPUTED',
    'actual_run_samples_sha256': None,
    'full_verified_source_state': 'UNKNOWN',
    'reason': 'No B2 candidate or study execution; no in-run consumption attestation.',
    'buffer_shape': list(source['buffer'].shape),
    'buffer_dtype': source['buffer'].dtype.str,
    'sample_rate_hz': 48000,
    'prescribed_seed': 0,
    'prescribed_seed_basis': 'Owner instruction; unchanged pinned Exp013 build_sources',
})
cfg = io.StringIO()
with contextlib.redirect_stdout(cfg):
    np.show_config()
    scipy.show_config()

inventory = {}
for base in ('experiments/bodymap_b2_passive_loss', 'requirements'):
    for p in sorted((repo / base).rglob('*')):
        rel = p.relative_to(repo).as_posix()
        if p.is_file() and '__pycache__' not in rel and (base != 'requirements' or p == lock):
            inventory[rel] = {'sha256': sha(p), 'git_blob_oid': git('rev-parse', f'{pin}:{rel}')}

result = {
    'schema': 'bodymap-b2-study-preflight-stop/1',
    'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'STOP_BEFORE_ENGINEERING_AND_STUDY',
    'reason_code': 'RUN_MANIFEST_BYTES_UNAVAILABLE',
    'expected_run_manifest_id': 'BODYMAP-B2-RUNMANIFEST-20261113-01',
    'expected_run_manifest_sha256': 'e662141d1f79c7f1bb3663acdd33e476e2c949bf757fcf734a97005ede27aca8',
    'observed_run_manifest_sha256': None,
    'go_validity': 'OWNER_GO_CONFIRMED; NOT_REVOKED',
    'core_head': pin,
    'checkout_clean_before': True,
    'checkout_clean_after': not bool(git('status', '--porcelain=v1', '--untracked-files=all')),
    'lock': {'path': lock.relative_to(repo).as_posix(), 'sha256': sha(lock)},
    'environment': {
        'python': platform.python_version(), 'python_executable': sys.executable,
        'os': platform.platform(), 'machine': platform.machine(),
        'libc': platform.libc_ver(), 'packages': versions,
        'thread_environment': {k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')},
        'numpy_scipy_build_config': cfg.getvalue(),
    },
    'geometry_readback': geometries,
    'registered_m0_diameters_mm': list(M0_DIAMETERS_MM),
    'source_readback': source_meta,
    'pinned_file_inventory': inventory,
    'execution_ledger': {
        'engineering_candidate_evaluations': 0,
        'engineering_oracle_evaluations': 0,
        'scientific_evaluations_started': 0,
        'scientific_evaluations_completed': 0,
        'negative_invocations': 0,
        'study_attempts_started': 0,
        'study_retries': 0,
        'study_wall_seconds': 0,
        'packs_issued': 0,
        'preflight_wall_seconds': time.perf_counter() - started,
    },
    'implementation_conformance': 'UNRESOLVED', 'effect': 'UNKNOWN',
    'next_gate': 'Obtain exact supervisor run manifest bytes, verify expected SHA; then prepare/freeze runner and reproduce known engineering cases before study.',
}
assert result['checkout_clean_after']
out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
print(json.dumps({k: result[k] for k in ('status', 'reason_code', 'core_head', 'execution_ledger')}, indent=2))
