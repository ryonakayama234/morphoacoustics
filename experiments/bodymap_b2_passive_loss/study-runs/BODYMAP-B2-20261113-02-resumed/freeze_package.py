import datetime, hashlib, json
from pathlib import Path
p=Path(__file__).resolve().parent
files=['study_runner.py','preflight.py','preflight-receipt.json','pinned-inventory.json','source.le-f64','source-dft.le-c128']+[str(f.relative_to(p)) for f in sorted((p/'inputs').iterdir())]
record={'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scientific_evaluations_at_freeze':0,'engineering_evaluations_at_freeze':0,'files':{f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files}}
with (p/'runner-freeze.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record,indent=2))
