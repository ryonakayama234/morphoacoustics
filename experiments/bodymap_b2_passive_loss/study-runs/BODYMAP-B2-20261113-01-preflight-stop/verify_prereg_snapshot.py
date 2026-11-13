from pathlib import Path
import hashlib
import sys

data = Path(sys.argv[1]).read_bytes()
expected = '9a022469264b4789c2d677d163470c4f7f393451635b264920463e6d70d3e41e'
actual = hashlib.sha256(data).hexdigest()
assert actual == expected, (actual, expected)
print(actual)
