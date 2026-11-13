"""Input-only audit. Never imports or invokes candidate/oracle evaluation."""
import contextlib
import datetime as dt
import hashlib
import importlib.metadata as md
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(__file__).resolve().parent
PIN = '0bb60cc227d231ec1cb67b701a849172ed92164b'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a): return subprocess.check_output(['git', '-C', str(ROOT), *a], text=True).strip()
def write(name, obj):
    with (OUT/name).open('x') as f: json.dump(obj, f, indent=2, ensure_ascii=False, allow_nan=False)

assert git('rev-parse', 'HEAD') == PIN
assert not git('status', '--porcelain=v1', '--untracked-files=all')
expected = {
    'manifest.md':'e662141d1f79c7f1bb3663acdd33e476e2c949bf757fcf734a97005ede27aca8',
    'aux.lock.txt':'884ca8de62840b3e41b0204872936ae696504d308b1b16394893c1889d759d22',
    'addendum-01.md':'6214dba2532d1b567ac1876cabbf84429ffdc42bed26fecf5ef5ef21fffb581f',
    'prereg.md':'9a022469264b4789c2d677d163470c4f7f393451635b264920463e6d70d3e41e'}
for name, digest in expected.items(): assert sha(OUT/'inputs'/name) == digest
assert sha(ROOT/'requirements/bodymap-b2-physical-py311.lock.txt') == 'c0bd046498882beb61408440d9eadd1b9708ad8a49ad0035e0bdbaa5d3a6afd7'
assert platform.python_version() == '3.11.18'
packages = {d.metadata['Name'].lower().replace('_','-'):d.version for d in md.distributions()}
assert packages == {'attrs':'26.1.0', 'iniconfig':'2.3.1', 'jsonschema':'4.26.0',
    'jsonschema-specifications':'2025.9.1', 'mpmath':'1.4.1', 'numpy':'2.4.6',
    'packaging':'26.3', 'pluggy':'1.7.0', 'pygments':'2.21.0', 'pytest':'9.2.0',
    'referencing':'0.37.0', 'rpds-py':'2026.9.1', 'scipy':'1.17.1', 'typing-extensions':'4.16.0'}
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import scipy
from experiments.bodymap_b2_passive_loss.geometry_binding import resolve_geometry
from experiments.bodymap_b2_passive_loss.source_binding import consumed_source
geometries = {name:resolve_geometry(name) for name in ('M0_REST','U6_REF','U19_REF')}
g = geometries['M0_REST']
assert g['preparation_digest'] == 'sha256:a98d484f8740bf40a419ac117a2deb41ab659dea095577874455aec0713258de'
diameters = np.array(g['radii_m'])*2000
assert np.allclose(diameters,[12,12,26,16,12,14,20,26,30,34,38,34,34,30,28,32],rtol=0,atol=1e-8)
assert tuple(g['lengths_m']) == (.010,)*16
src = consumed_source()
assert hashlib.sha256(src['buffer'].tobytes()).hexdigest() == src['source_sha256_le_f64']
assert np.array_equal(np.fft.rfft(src['buffer']),src['Q'])
with (OUT/'source.le-f64').open('xb') as f: f.write(src['buffer'].tobytes())
with (OUT/'source-dft.le-c128').open('xb') as f: f.write(np.ascontiguousarray(src['Q'],dtype='<c16').tobytes())
inventory = {}
paths = git('ls-files','experiments/bodymap_b2_passive_loss','requirements/bodymap-b2-physical-py311.lock.txt').splitlines()
paths += sorted(set(src['transitive_pins']) | set(g['source_pin_inventory']))
for rel in sorted(set(paths)):
    inventory[rel] = {'sha256':sha(ROOT/rel),'git_blob_oid':git('rev-parse',f'{PIN}:{rel}')}
write('pinned-inventory.json',inventory)
config=io.StringIO()
with contextlib.redirect_stdout(config): np.show_config(); scipy.show_config()
assert not git('status','--porcelain=v1','--untracked-files=all')
write('preflight-receipt.json',{
    'recorded_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
    'status':'INPUT_PREFLIGHT_PASS', 'core_head':PIN,'clean_before_and_after':True,
    'supervisor_input_commit':'27b37acbe1950529b04f68c5e77a168dbc519152',
    'input_sha256':expected, 'python':platform.python_version(), 'packages':packages,
    'os':platform.platform(),'arch':platform.machine(),'libc':platform.libc_ver(),
    'python_executable':sys.executable,'numpy_scipy_build_config':config.getvalue(),
    'threads':{k:os.environ.get(k) for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')},
    'installation':'fresh venv; uv pip install --require-hashes --only-binary=:all: -r B2-lock -r auxiliary-lock',
    'geometries':geometries,'m0_diameters_mm_observed':diameters.tolist(),
    'source':{k:v for k,v in src.items() if k not in ('buffer','Q')},
    'source_evidence_class':'RECOMPUTED','full_verified_source_state':'UNKNOWN',
    'scientific_evaluations':0, 'engineering_evaluations':0,'negative_invocations':0})
print(json.dumps({'status':'INPUT_PREFLIGHT_PASS','m0_digest':g['preparation_digest'],
    'source_sha256':src['source_sha256_le_f64'],'source_dft_sha256':src['dft_sha256_le_complex128']}))
