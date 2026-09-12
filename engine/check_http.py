"""Unauthenticated public endpoint and payload checks; no login cookies or bypass tokens."""
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

root=Path(__file__).resolve().parents[1]
origin=sys.argv[1] if len(sys.argv)>1 else 'https://mosaic-mix-lab-ajay.ochre-deer-1487.chatgpt.site'
checks=[]
for endpoint,local in [('/',root/'dist/index.html'),('/results/report.json',root/'public/results/report.json'),('/results/records.json',root/'public/results/records.json'),('/results/allocation.csv',root/'public/results/allocation.csv'),('/results/records.csv',root/'public/results/records.csv'),('/demo/mosaic-mix-lab-demo.mp4',root/'public/demo/mosaic-mix-lab-demo.mp4'),('/demo/demo.srt',root/'public/demo/demo.srt')]:
    with urlopen(Request(origin+endpoint,headers={'User-Agent':'MosaicMixLab-PublicVerification/1.0'}),timeout=60) as response:
        body=response.read(); status=response.status; url=response.url; kind=response.headers.get('Content-Type')
    assert status==200 and url.startswith(origin+'/'), (endpoint,status,url)
    # Sites may inject hosting instrumentation into HTML; data and media must match exactly.
    if endpoint=='/': assert b'Mosaic Mix Lab' in body and b'/assets/' in body
    else: assert hashlib.sha256(body).digest()==hashlib.sha256(local.read_bytes()).digest(), endpoint
    checks.append({'endpoint':endpoint,'status':status,'contentType':kind,'bytes':len(body),'exactBytesMatch':endpoint!='/'})
artifact={'checkedAt':datetime.now(timezone.utc).isoformat(),'origin':origin,'authenticated':False,'cookiesSent':False,'bypassTokenUsed':False,'passed':True,'checks':checks}
(root/'artifacts/http-validation.json').write_text(json.dumps(artifact,indent=2),encoding='utf-8')
print(json.dumps(artifact,indent=2))
