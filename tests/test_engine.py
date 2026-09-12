import copy
import unittest
from decimal import Decimal as D
from fractions import Fraction as F
from engine.analyze import allocate, fixed, load, validate, ROOT, CHANNELS, BUDGET, CAPS, scenario

class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=load(ROOT/'data/marketing_daily.json')
    def one(self): return copy.deepcopy(self.rows[0])
    def test_complete_official_dataset(self):
        rows,issues=validate(self.rows)
        self.assertEqual(len(rows),10950); self.assertEqual(issues,[])
        self.assertEqual(len({(r['date'],r['channel']) for r in rows}),10950)
        self.assertEqual(set(r['channel'] for r in rows),set(CHANNELS))
    def test_malformed_and_missing(self):
        for value in [None,{},dict(self.one(),spend='oops'),dict(self.one(),date='bad'),dict(self.one(),channel='Unknown')]:
            with self.subTest(value=value):
                accepted,issues=validate([value]); self.assertEqual(len(accepted),0); self.assertEqual(len(issues),1)
    def test_negative_nonfinite_and_fractional_counts(self):
        for field,value in [('revenue',D('-1')),('spend',D('NaN')),('clicks',D('1.5')),('spend',D('1.001')),('roas',True)]:
            with self.subTest(field=field,value=value): self.assertEqual(len(validate([dict(self.one(),**{field:value})])[0]),0)
    def test_weekday_and_date_range(self):
        for patch in [{'day_of_week':'Mon'},{'date':'2026-01-01'}]:
            self.assertEqual(len(validate([dict(self.one(),**patch)])[0]),0)
    def test_zero_spend(self): self.assertEqual(validate([dict(self.one(),spend=D(0))])[1][0]['categories'],['zero_spend'])
    def test_exact_duplicates_not_double_counted(self):
        r=self.one(); accepted,issues=validate([r,r,r]); self.assertEqual(len(accepted),1); self.assertEqual(len(issues),2)
    def test_conflicting_duplicates_quarantine_every_version(self):
        r=self.one(); accepted,issues=validate([r,dict(r,revenue=D(1))]); self.assertEqual(len(accepted),0); self.assertEqual(len(issues),2)
    def test_overlapping_errors_excluded_once(self):
        r=dict(self.one(),spend=D(-1),date='bad',channel='Unknown'); accepted,issues=validate([r]); self.assertEqual(len(issues),1); self.assertEqual(len(issues[0]['categories']),3); self.assertEqual(accepted,[])
    def test_missing_coverage_detectable(self):
        rows,_=validate(self.rows[:-1]); self.assertEqual(len(rows),10949)
    def test_decimal_half_up(self):
        self.assertEqual(fixed(F('1.005')),'1.01'); self.assertEqual(fixed(F('-1.005')),'-1.01')
        self.assertEqual(fixed(F('0.1')+F('0.2')),'0.30')
    def test_proportional_redistribution_and_caps(self):
        out=allocate({'Email':F(10),'SMS':F(5),'A':F(1)},100,{'Email':20,'SMS':30})
        self.assertEqual(out,{'Email':20,'SMS':30,'A':50})
    def test_largest_remainder_ties(self):
        self.assertEqual(allocate({'B':F(1),'A':F(1),'C':F(1)},100,{}),{'B':33,'A':34,'C':33})
    def test_linear_exchange_optimality(self):
        means={'Email':F(9),'SMS':F(6),'Affiliate':F(5),'Other':F(4)}
        out=allocate(means,100,{'Email':30,'SMS':20},'linear')
        self.assertEqual(out,{'Email':30,'SMS':20,'Affiliate':50,'Other':0})
        optimum=sum(out[c]*means[c] for c in means)
        for email in range(31):
            for sms in range(21): self.assertLessEqual(email*9+sms*6+(100-email-sms)*5,optimum)
    def test_invalid_capacity(self):
        with self.assertRaises(ValueError): allocate({'A':F(1)},100,{'A':50})
    def test_zero_weights(self): self.assertEqual(sum(allocate({'A':F(0),'B':F(0)},101,{}).values()),101)
    def test_official_reconciliation(self):
        groups={c:[r for r in self.rows if r['channel']==c] for c in CHANNELS}
        means={c:sum(F(r['roas']) for r in rs)/len(rs) for c,rs in groups.items()}
        for mode,total in [('proportional','26568802.42'),('linear','33853561.64')]:
            s=scenario(means,mode)
            self.assertEqual(s['total'],total)
            self.assertEqual(sum(F(x) for x in s['allocation'].values()),F(BUDGET,100))
            self.assertEqual(sum(F(x) for x in s['revenue'].values())+F(s['roundingAdjustment']),F(s['total']))
            for c,cap in CAPS.items(): self.assertLessEqual(F(s['allocation'][c]),F(cap,100))

if __name__=='__main__': unittest.main()
