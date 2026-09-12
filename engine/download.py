"""Download original bytes and reject unannounced source changes."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
root=Path(__file__).resolve().parents[1]
url='https://mosaicfellowship.in/data/marketing_daily.json'
data=urlopen(url,timeout=60).read()
report=root/'public/results/report.json'
if report.exists():
    expected=json.loads(report.read_text())['source']['sha256']
    if hashlib.sha256(data).hexdigest()!=expected: raise SystemExit('Official file changed; review before replacing the pinned dataset.')
(root/'data').mkdir(exist_ok=True)
(root/'data/marketing_daily.json').write_bytes(data)
print('Downloaded',len(data),'bytes; SHA-256',hashlib.sha256(data).hexdigest())
