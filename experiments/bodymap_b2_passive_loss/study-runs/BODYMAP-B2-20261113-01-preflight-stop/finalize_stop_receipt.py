"""Record prior input-readback failure; no solver or input loader is called."""
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

repo = Path(sys.argv[1]).resolve()
dest = Path(__file__).resolve().parent
pin = '0bb60cc227d231ec1cb67b701a849172ed92164b'
def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert git('rev-parse', 'HEAD') == pin
assert not git('status', '--porcelain=v1', '--untracked-files=all')
lock = repo / 'requirements/bodymap-b2-physical-py311.lock.txt'
assert sha(lock) == 'c0bd046498882beb61408440d9eadd1b9708ad8a49ad0035e0bdbaa5d3a6afd7'
versions = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
assert platform.python_version() == '3.11.18'
assert all(versions[k] == v for k, v in {'numpy': '2.4.6', 'scipy': '1.17.1', 'mpmath': '1.4.1'}.items())
assert 'jsonschema' not in versions
import numpy as np
import scipy
config = io.StringIO()
with contextlib.redirect_stdout(config):
    np.show_config()
    scipy.show_config()
failure = (dest / 'input-readback-failure.log').read_text()
assert "ModuleNotFoundError: No module named 'jsonschema'" in failure
inventory = {}
for rel in git('ls-files', 'experiments/bodymap_b2_passive_loss', 'requirements/bodymap-b2-physical-py311.lock.txt', 'tools/cc_a2_live.py', 'tools/od2_body_cli.py', 'pyproject.toml').splitlines():
    inventory[rel] = {'sha256': sha(repo / rel), 'git_blob_oid': git('rev-parse', f'{pin}:{rel}')}
receipt = {
    'schema': 'bodymap-b2-study-preflight-stop/1',
    'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'STOP_BEFORE_ENGINEERING_AND_STUDY',
    'go': {
        'owner_go_confirmed': True,
        'core_comment': 'https://github.com/ryonakayama234/morphoacoustics/pull/294#issuecomment-6842652177',
        'studio_comment': 'https://github.com/ryonakayama234/morphoacoustics-studio/issues/61#issuecomment-6842658326',
        'go_revoked': False,
    },
    'run_manifest': {
        'id': 'BODYMAP-B2-RUNMANIFEST-20261113-01',
        'expected_sha256': 'e662141d1f79c7f1bb3663acdd33e476e2c949bf757fcf734a97005ede27aca8',
        'observed_sha256': None,
        'status': 'ORIGINAL_BYTES_NOT_RETRIEVED',
        'lookup_scope': ['Core pinned main recursive tree', 'Studio current main recursive tree', 'Core PR 294 body and discussion', 'Studio Issue 61 body and discussion', 'Connected file exact-title and shorter-title searches'],
        'inference_limit': 'Not found in these inspected sources; does not prove nonexistence elsewhere.',
    },
    'core_head': pin,
    'clean_checkout_at_input_attempt': True,
    'clean_checkout_at_environment_record': True,
    'lock': {'path': lock.relative_to(repo).as_posix(), 'sha256': sha(lock)},
    'environment': {
        'python': platform.python_version(),
        'python_executable': sys.executable,
        'os': platform.platform(), 'machine': platform.machine(), 'libc': platform.libc_ver(),
        'packages': versions,
        'installation': 'uv pip install --require-hashes --only-binary=:all: -r requirements/bodymap-b2-physical-py311.lock.txt in a fresh Python 3.11.18 venv',
        'resolver': subprocess.check_output(['uv', '--version'], text=True).strip(),
        'numpy_scipy_build_config': config.getvalue(),
        'threads': {k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')},
        'environment_matches_manifest': 'UNRESOLVED_ORIGINAL_MANIFEST_UNAVAILABLE',
    },
    'input_readback': {
        'status': 'FAILED_BEFORE_NUMERICAL_EVALUATION',
        'attempts': 1,
        'entry_point': 'geometry_binding.resolve_geometry(M0_REST)',
        'failure': "ModuleNotFoundError: No module named 'jsonschema'",
        'dependency_edge': 'geometry_binding.trusted_m0 -> tools/od2_body_cli.py::_load_context -> tools/cc_a2_live.py -> jsonschema.Draft202012Validator',
        'failure_log_ref': 'input-readback-failure.log',
        'failure_log_sha256': sha(dest / 'input-readback-failure.log'),
        'm0_digest_observed': None,
        'm0_diameters_observed': None,
        'source_sha256_observed': None,
        'source_evidence_class': 'UNKNOWN',
        'source_full_verified_state': 'UNKNOWN',
        'scientific_code_changes': [],
        'lock_changes': [],
        'supplemental_dependencies_installed': [],
    },
    'execution_ledger': {
        'engineering_candidate_evaluations': 0, 'engineering_oracle_evaluations': 0,
        'scientific_evaluations_started': 0, 'scientific_evaluations_completed': 0,
        'negative_invocations': 0, 'study_attempts_started': 0,
        'study_retries': 0, 'study_wall_seconds': 0, 'packs_issued': 0,
        'input_preflight_process_exit_code': 1,
        'input_preflight_wall_seconds': 0.428456588,
        'input_preflight_timing_source': 'executor command wall_time_seconds; launcher/process overhead included',
        'notes': 'Input audit only. No scientific case was started or interrupted. No results-zero retry was consumed.',
    },
    'study_runner_sha256': None,
    'runner_state': 'NOT_FROZEN_NOT_EXECUTED',
    'implementation_conformance': 'UNRESOLVED', 'effect': 'UNKNOWN',
    'pinned_file_inventory': inventory,
}
(dest / 'preflight-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
print(json.dumps({'status': receipt['status'], 'packages': versions, 'ledger': receipt['execution_ledger']}, indent=2))
