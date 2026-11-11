import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline.build import normalize

class NormalizationTests(unittest.TestCase):
    def row(self,**changes):
        fields={'invoice':'536365','sku':'85123A','name':'WHITE HANGING HEART','quantity':'6','serial':'40513.3541666667','price':'2.55','customer':'17850','country':'United Kingdom'}
        fields.update(changes)
        return list(fields.values())
    def test_exact_integer_money(self):
        r,e=normalize(self.row());self.assertIsNone(e)
        self.assertEqual(r[1],'2010-12-01');self.assertEqual(r[7],2550);self.assertEqual(r[8],15300)
    def test_credit_preserved_and_signed(self):
        r,e=normalize(self.row(invoice='C536365',quantity='-6'))
        self.assertEqual(r[8],-15300);self.assertEqual(r[9],1)
    def test_credit_prefix_wins_even_for_positive_quantity(self):
        r,_=normalize(self.row(invoice='C536365'));self.assertEqual(r[8],-15300)
    def test_missing_customer_stays_missing(self):
        r,_=normalize(self.row(customer=''));self.assertIsNone(r[4])
    def test_stable_pseudonym_and_no_raw_customer_id(self):
        a,_=normalize(self.row());b,_=normalize(self.row());self.assertEqual(a[4],b[4]);self.assertNotIn('17850',a[4])
    def test_nonpositive_price_excluded(self):
        for price in ['0','-5']:
            r,e=normalize(self.row(price=price));self.assertIsNone(r);self.assertEqual(e,'nonpositive_price')
    def test_milli_pound_precision(self):
        r,_=normalize(self.row(price='0.001',quantity='3'));self.assertEqual(r[8],3)
    def test_invalid_numeric_rejected(self):
        r,e=normalize(self.row(quantity='not-a-number'));self.assertIsNone(r);self.assertEqual(e,'invalid_numeric')

if __name__=='__main__':unittest.main()
