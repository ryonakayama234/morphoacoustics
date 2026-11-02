"""Check independently regenerated ECMAScript oracle against immutable B2 blob.

The generator is mathematical wave scattering, not a physical experiment.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
import sys

EXPECTED_BLOB = "0c3476899de4d3cdeaad46816895b8318b43cde0"
ORIGINAL = Path(__file__).resolve().parent / "holdout_oracle_24.json"


def verify(rebuilt_path: Path) -> tuple[float, float]:
    original = ORIGINAL.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(original)).encode() + b"\0" + original).hexdigest()
    if blob != EXPECTED_BLOB:
        raise AssertionError("Frozen original Git blob was modified")
    frozen, generated = json.loads(original), json.loads(rebuilt_path.read_bytes())
    if set(frozen) != set(generated):
        raise AssertionError("Schema/provenance keys differ")
    for key in frozen:
        if key == "rows":
            continue
        if frozen[key] != generated[key]:
            raise AssertionError(f"Reference metadata differs: {key}")
    if len(frozen["rows"]) != len(generated["rows"]) or len(frozen["rows"]) != 24:
        raise AssertionError("Expected same 24 rows")
    # A plain zip(left,right) *silently ignores missing trailing columns*.
    # Explicitly require the full original 15-column independent observation.
    column_count = len(frozen["columns"])
    if column_count != 15:
        raise AssertionError("Expected exactly 15 B2 reference columns")
    if any(not isinstance(row, list) or len(row) != column_count
           for row in frozen["rows"]):
        raise AssertionError("Frozen reference row lacks all 15 columns")
    if any(not isinstance(row, list) or len(row) != column_count
           for row in generated["rows"]):
        raise AssertionError("Regenerated reference row lacks all 15 columns")
    max_p, max_scaled_u = 0., 0.
    for left,right in zip(frozen["rows"],generated["rows"]):
        if tuple(left[:3]) != tuple(right[:3]):
            raise AssertionError("Reference fixture identity changed")
        if any(not isinstance(v,(int,float)) or not math.isfinite(v)
               for v in [*left,*right]):
            raise AssertionError("Nonfinite regenerated oracle")
        for i,(x,y) in enumerate(zip(left,right)):
            e=abs(x-y)
            if i in (3,4,5,6):
                max_p=max(max_p,e)
                if e>1e-11:
                    raise AssertionError(f"Pressure component mismatch {e}")
            elif i in (7,8,9,10):
                zc=1.21*343/left[0]
                max_scaled_u=max(max_scaled_u,e*zc)
                if e*zc>1e-11:
                    raise AssertionError(f"Volume-flow component mismatch {e*zc}")
            elif i in (11,12,13,14):
                if e>max(1e-13,1e-10*max(abs(x),abs(y),1e-12)):
                    raise AssertionError(f"Power mismatch {e}")
            elif e!=0.:
                raise AssertionError(f"Fixture parameter mismatch at column {i}")
    return max_p,max_scaled_u


if __name__=="__main__":
    errors = verify(Path(sys.argv[1]))
    print(f"Regenerated 24 B2 rows against pinned ECMAScript oracle: PASS; maximum errors {errors}")
