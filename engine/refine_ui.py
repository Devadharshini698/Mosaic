from pathlib import Path
p=Path('src/main.tsx')
s=p.read_text(encoding='utf-8')
s=s.replace('Allowing fractional paise in proportional allocations produces a different total. See the independent reconciliation artifact for that value.', 'Allowing fractional paise in proportional allocations produces ₹2,65,68,802.44, versus ₹2,65,68,802.42 with whole-paise allocations. Both were independently reconciled.')
s=s.replace('Math.min(100,Number(d.value)/15*100)', "Number(d.value)/Math.max(...(metric==='seasonal'?active.months.map(m=>Number(m.roas)):metric==='spend'?active.quartiles.map(q=>Number(q.roas)):[Number(active.weekdayRoas),Number(active.weekendRoas)]),1)*100")
p.write_text(s,encoding='utf-8')
