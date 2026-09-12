"""Reproducible official-data analysis. No binary floating point in money or ROAS."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANNELS = ['Meta Ads', 'Google Search', 'Google Display', 'YouTube', 'Instagram Reels', 'Email', 'SMS', 'Influencer', 'Affiliate', 'Organic Social']
CAPS = {'Email': 150000000, 'SMS': 120000000}  # paise
BUDGET = 500000000

def rounded(x):
    """Exact ROUND_HALF_UP to an integer, including negative values."""
    x = F(x)
    return (1 if x >= 0 else -1) * ((2 * abs(x.numerator) + x.denominator) // (2 * x.denominator))

def fixed(x, digits=2):
    n = rounded(F(x) * 10 ** digits)
    return ('-' if n < 0 else '') + f'{abs(n)//10**digits}.{abs(n)%10**digits:0{digits}d}'

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), parse_float=Decimal, parse_int=Decimal)

def validate(rows):
    accepted, issues, buckets = [], [], defaultdict(list)
    numeric = ['spend','revenue','roas','impressions','clicks','conversions','new_customers','ctr','cpc','cpa','aov']
    for i, row in enumerate(rows, 1):
        reasons = []
        if not isinstance(row, dict):
            issues.append({'row':i,'categories':['malformed'],'explanation':'Record is not an object.'}); continue
        try:
            dt = date.fromisoformat(row.get('date',''))
            if not date(2023,1,1) <= dt <= date(2025,12,30): reasons.append('out_of_range_date')
            if row.get('day_of_week') != dt.strftime('%a'): reasons.append('weekday_mismatch')
        except (TypeError,ValueError): reasons.append('invalid_date')
        if row.get('channel') not in CHANNELS: reasons.append('unknown_channel')
        for key in numeric:
            value = row.get(key)
            if isinstance(value,bool) or not isinstance(value,(Decimal,int,float)):
                reasons.append('missing_or_malformed_'+key); continue
            value = Decimal(str(value))
            if not value.is_finite() or value < 0: reasons.append('invalid_'+key)
            elif key in ['spend','revenue'] and value != value.quantize(Decimal('.01')): reasons.append('sub_paise_'+key)
            elif key in ['impressions','clicks','conversions','new_customers'] and value != value.to_integral_value(): reasons.append('fractional_'+key)
        if reasons:
            issues.append({'row':i,'categories':reasons,'explanation':'Quarantined once, regardless of overlapping validation failures.','record':row}); continue
        if row['spend'] == 0:
            issues.append({'row':i,'categories':['zero_spend'],'explanation':'Cannot validate return on spend; quarantined.','record':row}); continue
        buckets[(row['date'],row['channel'])].append((i,row))
    for key, versions in buckets.items():
        if any(r != versions[0][1] for _,r in versions):
            for i,r in versions: issues.append({'row':i,'categories':['conflicting_duplicate'],'explanation':'All conflicting date/channel versions quarantined.','record':r})
            continue
        i,r = versions[0]
        accepted.append(dict(r,source_row=i,record_id=f'{key[0]}|{key[1]}'))
        for j,r in versions[1:]: issues.append({'row':j,'categories':['exact_duplicate'],'explanation':f'Excluded duplicate of source row {i}.','record':r})
    return sorted(accepted,key=lambda r:r['source_row']), issues

def allocate(means, budget=BUDGET, caps=CAPS, mode='proportional'):
    if budget < 0 or not means or any(v < 0 for v in means.values()): raise ValueError('Invalid budget or means')
    if any(v < 0 for v in caps.values()): raise ValueError('Negative cap')
    if sum(caps.get(c,budget) for c in means) < budget: raise ValueError('Insufficient capacity')
    if mode == 'linear':
        out = dict.fromkeys(means,0); remaining = budget
        for c in sorted(means,key=lambda c:(-means[c],c)):
            out[c] = min(remaining,caps.get(c,budget)); remaining -= out[c]
        return out
    if mode != 'proportional': raise ValueError('Unknown allocation mode')
    raw, active, remaining = {}, set(means), F(budget)
    while active:
        total = sum(means[c] for c in active)
        proposals = {c:remaining*means[c]/total if total else remaining/len(active) for c in active}
        saturated = [c for c in active if proposals[c] > caps.get(c,budget)]
        if not saturated: raw.update(proposals); break
        for c in saturated:
            raw[c] = F(caps[c]); remaining -= raw[c]; active.remove(c)
    out = {c:int(raw[c]) for c in means}
    # Largest remainders: exact budget to the paise, stable alphabetical tie-break.
    for c in sorted(means,key=lambda c:(-(raw[c]-out[c]),c))[:budget-sum(out.values())]: out[c] += 1
    return out

def scenario(means, mode):
    alloc = allocate(means,mode=mode)
    exact = {c:F(alloc[c],100)*means[c] for c in means}
    total = sum(exact.values())
    return {'mode':mode,'allocation':{c:fixed(F(v,100)) for c,v in alloc.items()},
            'revenue':{c:fixed(v) for c,v in exact.items()},'total':fixed(total),
            'sumRoundedRows':fixed(sum(F(fixed(v)) for v in exact.values())),
            'roundingAdjustment':fixed(F(fixed(total))-sum(F(fixed(v)) for v in exact.values())),
            'exactTotalFraction':f'{total.numerator}/{total.denominator}'}

def serialize(x):
    if isinstance(x,Decimal): return str(x)
    if isinstance(x,F): return fixed(x,12)
    raise TypeError(type(x).__name__)

def run():
    path=ROOT/'data/marketing_daily.json'; raw=load(path)
    if not isinstance(raw,list): raise ValueError('Dataset must be an array')
    rows,issues=validate(raw)
    grouped=defaultdict(list)
    for r in rows: grouped[r['channel']].append(r)
    keys={(r['date'],r['channel']) for r in rows}
    missing=[]
    for n in range(1095):
        d=(date(2023,1,1)+timedelta(days=n)).isoformat()
        for c in CHANNELS:
            if (d,c) not in keys: missing.append({'date':d,'channel':c})
    if missing or set(grouped)!=set(CHANNELS):
        (ROOT/'artifacts/validation-failure.json').write_text(json.dumps({'issues':issues,'missing':missing},default=serialize,indent=2))
        raise ValueError('Incomplete official date/channel coverage; see artifacts/validation-failure.json')
    means={c:sum(F(r['roas']) for r in grouped[c])/len(grouped[c]) for c in CHANNELS}
    channels=[]
    observations=[]
    for c in CHANNELS:
        group=grouped[c]; spend=sum(F(r['spend']) for r in group); revenue=sum(F(r['revenue']) for r in group)
        def avg(rs): return sum(F(r['roas']) for r in rs)/len(rs) if rs else F(0)
        weekdays=[r for r in group if r['day_of_week'] not in ['Sat','Sun']]
        weekends=[r for r in group if r['day_of_week'] in ['Sat','Sun']]
        ordered=sorted(group,key=lambda r:r['spend']); bins=[]
        for i in range(4):
            sample=ordered[i*len(group)//4:(i+1)*len(group)//4]
            bins.append({'quartile':i+1,'count':len(sample),'meanSpend':fixed(sum(F(r['spend']) for r in sample)/len(sample)), 'minSpend':str(sample[0]['spend']),'maxSpend':str(sample[-1]['spend']),'roas':fixed(avg(sample),6)})
        months=[]
        for m in range(1,13):
            sample=[r for r in group if int(r['date'][5:7])==m]
            months.append({'month':m,'count':len(sample),'roas':fixed(avg(sample),6)})
        channels.append({'channel':c,'count':len(group),'meanRoas':fixed(means[c],12),'roasSum':fixed(sum(F(r['roas']) for r in group)), 'weightedRoas':fixed(revenue/spend,6),'spend':fixed(spend),'revenue':fixed(revenue),'cap':fixed(F(CAPS[c],100)) if c in CAPS else None,'weekdayRoas':fixed(avg(weekdays),6),'weekendRoas':fixed(avg(weekends),6),'quartiles':bins,'months':months})
        for r in group:
            expected=F(r['spend'])*F(r['roas']); diff=F(r['revenue'])-expected
            if abs(F(r['revenue'])/F(r['spend'])-F(r['roas'])) > F(1,200):
                observations.append({'row':r['source_row'],'category':'rounded_roas_discrepancy','record_id':r['record_id']})
            r['expected_at_reported_roas']=fixed(expected); r['revenue_difference']=fixed(diff)
            r['explanation']='Reported ROAS has two decimals. Spend × reported ROAS can differ from recorded revenue; this is a rounding diagnostic, not an invoice overcharge.'
    report={'source':{'url':'https://mosaicfellowship.in/data/marketing_daily.json','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rowCount':len(raw),'acceptedRows':len(rows),'channels':10,'days':1095,'start':'2023-01-01','end':'2025-12-30'},
        'budget':'5000000.00','primaryConvention':'proportional','channels':channels,
        'scenarios':{m:scenario(means,m) for m in ['proportional','linear']},
        'validation':{'excludedRows':len(issues),'issues':issues,'missingRecords':missing,'diagnosticCount':len(observations),'diagnostics':observations,'countsByCategory':dict(Counter(cat for issue in issues for cat in issue['categories']))},
        'methodology':{'mean':'Arithmetic mean of supplied daily ROAS across all 1,095 rows per channel, without pre-rounding. Revenue/spend weighted ROAS is a separate diagnostic.', 'proportional':'Allocate in proportion to mean ROAS; iteratively cap and redistribute; apportion remaining paise by largest remainders, alphabetical ties.','linear':'Sort by mean ROAS and fill highest-return channels to their caps. Globally optimal for the stated constant-ROAS linear formula; not a causal marketing forecast.', 'rounding':'Rational arithmetic internally. Allocations are integer paise. ROUND_HALF_UP only on final outputs. A separate adjustment reconciles rounded channel rows to the rounded total.', 'ambiguity':'The brief recommends proportional allocation while asking for optimal allocation. Proportional is the suggested baseline, not the mathematical maximum. Both are supplied; neither is verified against the private answer key.'}}
    out=ROOT/'public/results'; out.mkdir(parents=True,exist_ok=True)
    for name,obj in [('report',report),('records',rows)]: (out/f'{name}.json').write_text(json.dumps(obj,default=serialize,indent=2),encoding='utf-8')
    with (out/'allocation.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['scenario','channel','average_roas','allocation_inr','expected_revenue_inr'])
        for mode,s in report['scenarios'].items():
            for c in CHANNELS: w.writerow([mode,c,fixed(means[c],12),s['allocation'][c],s['revenue'][c]])
            w.writerow([mode,'ROUNDING ADJUSTMENT','','',s['roundingAdjustment']]); w.writerow([mode,'TOTAL','',report['budget'],s['total']])
    with (out/'records.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(json.dumps({'source':report['source'],'scenarios':report['scenarios'],'excluded':len(issues),'diagnostics':len(observations)},indent=2))

if __name__=='__main__': run()
