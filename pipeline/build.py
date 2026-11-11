"""Reproducible UCI Online Retail pipeline. Python 3.11+, standard library only."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import argparse, csv, hashlib, io, json, sqlite3, urllib.request, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://archive.ics.uci.edu/static/public/352/online+retail.zip'
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

def rows_from_xlsx(content):
    with zipfile.ZipFile(io.BytesIO(content)) as book:
        strings = []
        with book.open('xl/sharedStrings.xml') as f:
            for _, el in ET.iterparse(f, events=('end',)):
                if el.tag == NS+'si':
                    strings.append(''.join(t.text or '' for t in el.iter(NS+'t')))
                    el.clear()
        with book.open('xl/worksheets/sheet1.xml') as f:
            for _, el in ET.iterparse(f, events=('end',)):
                if el.tag != NS+'row': continue
                values = [''] * 8
                for cell in el:
                    col = ''.join(c for c in cell.get('r', '') if c.isalpha())
                    if len(col) != 1 or not ('A' <= col <= 'H'): continue
                    v = cell.find(NS+'v')
                    raw = '' if v is None else v.text or ''
                    values[ord(col)-65] = strings[int(raw)] if cell.get('t') == 's' and raw else raw
                yield values
                el.clear()

def normalize(row):
    invoice, sku, name, quantity, serial, price, customer, country = row
    if not invoice or not sku or not serial: return None, 'missing_key'
    try:
        q = int(Decimal(quantity)); p = int((Decimal(price)*1000).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        date = (datetime(1899,12,30) + timedelta(days=float(serial))).strftime('%Y-%m-%d')
    except (ValueError, ArithmeticError): return None, 'invalid_numeric'
    if p <= 0: return None, 'nonpositive_price'
    if q == 0: return None, 'zero_quantity'
    # Anonymous source IDs receive a stable pseudonym; missing stays missing.
    client = 'C-'+hashlib.sha256(customer.encode()).hexdigest()[:10] if customer else None
    credit = q < 0 or invoice.upper().startswith('C')
    amount = -abs(q*p) if credit else q*p
    return (invoice,date,sku,name.strip() or sku,client,country.strip() or 'Unknown',q,p,amount,int(credit)), None

def compact_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

def build(refresh=False):
    raw = ROOT/'data/raw/online-retail.zip'; raw.parent.mkdir(parents=True,exist_ok=True)
    if refresh or not raw.exists():
        print('Downloading official UCI source...',flush=True)
        request = urllib.request.Request(URL,headers={'User-Agent':'RetailScope/1.0 reproducible educational project'})
        with urllib.request.urlopen(request,timeout=180) as response: raw.write_bytes(response.read())
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    manifest_path = ROOT/'public/data/manifest.json'
    if manifest_path.exists() and not refresh:
        expected = json.loads(manifest_path.read_text(encoding='utf-8'))['source_sha256']
        if digest != expected: raise RuntimeError('UCI checksum changed; inspect source before --refresh.')
    with zipfile.ZipFile(raw) as archive:
        xlsx = archive.read(next(n for n in archive.namelist() if n.lower().endswith('.xlsx')))
    db_path = ROOT/'data/warehouse/retailscope.sqlite'; db_path.parent.mkdir(parents=True,exist_ok=True)
    if db_path.exists(): db_path.unlink()
    db=sqlite3.connect(db_path)
    db.executescript((ROOT/'sql/schema.sql').read_text(encoding='utf-8'))
    seen=set(); products={}; dates=set(); countries=set(); customers=set(); counts=Counter(); batch=[]
    for i,row in enumerate(rows_from_xlsx(xlsx)):
        if i==0: continue
        counts['source_rows']+=1
        exact=tuple(row)
        if exact in seen: counts['duplicates_removed']+=1; continue
        seen.add(exact)
        line,reason=normalize(row)
        if reason: counts[reason]+=1; continue
        invoice,date,sku,name,customer,country,q,p,amount,credit=line
        products[sku]=name; dates.add(date); countries.add(country)
        if customer: customers.add(customer)
        else: counts['missing_customer_kept']+=1
        counts['accepted_rows']+=1
        batch.append((invoice,date,sku,customer,country,q,p,amount,credit))
    db.executemany('INSERT INTO dim_date VALUES (?,?)',[(d,d[:7]) for d in sorted(dates)])
    db.executemany('INSERT INTO dim_product VALUES (?,?)',sorted(products.items()))
    db.executemany('INSERT INTO dim_country VALUES (?)',[(c,) for c in sorted(countries)])
    db.executemany('INSERT INTO dim_customer VALUES (?)',[(c,) for c in sorted(customers)])
    db.executemany('INSERT INTO fact_line(invoice,date,stock_code,customer,country,quantity,unit_milli,amount_milli,is_credit) VALUES (?,?,?,?,?,?,?,?,?)',batch)
    db.commit(); del batch,seen,xlsx
    # Values remain integer milli-GBP until display; exact additive reconciliation.
    slices=db.execute("""SELECT substr(date,1,7),country,
        SUM(CASE WHEN is_credit=0 THEN amount_milli ELSE 0 END),
        -SUM(CASE WHEN is_credit=1 THEN amount_milli ELSE 0 END),
        COUNT(DISTINCT CASE WHEN is_credit=0 THEN invoice END),COUNT(*),
        SUM(CASE WHEN is_credit=0 THEN quantity ELSE 0 END)
        FROM fact_line GROUP BY 1,2 ORDER BY 1,2""").fetchall()
    product_rows=db.execute("""SELECT substr(date,1,7),country,stock_code,SUM(amount_milli),
        SUM(CASE WHEN is_credit=0 THEN quantity ELSE 0 END)
        FROM fact_line GROUP BY 1,2,3 ORDER BY 1,2,3""").fetchall()
    orders=db.execute("""SELECT invoice,MIN(date),country,customer,SUM(amount_milli)
        FROM fact_line WHERE is_credit=0 GROUP BY invoice,country,customer ORDER BY 2,1""").fetchall()
    payload={'months':sorted({d[:7] for d in dates}),'countries':sorted(countries),'products':products,
             'slices':slices,'productRows':product_rows,'orders':orders}
    compact_write(ROOT/'public/data/analytics.json',payload)
    totals=db.execute('SELECT SUM(amount_milli),COUNT(*),MIN(date),MAX(date) FROM fact_line').fetchone()
    manifest={'dataset':'UCI Online Retail (352)','citation':'Chen, D. (2015). Online Retail. UCI Machine Learning Repository. DOI:10.24432/C5BW33',
              'url':'https://archive.ics.uci.edu/dataset/352/online+retail','download_url':URL,
              'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
              'source_sha256':digest,'xlsx_sha256':hashlib.sha256(archive_bytes(raw)).hexdigest(),
              'generated_at':datetime.now(timezone.utc).isoformat(),'counts':dict(counts),
              'min_date':totals[2],'max_date':totals[3],'last_complete_month':'2011-11',
              'net_milli':totals[0],'order_count':len(orders),'money_scale':1000,
              'dimensions':{'countries':len(countries),'products':len(products),'identified_customers':len(customers)},
              'schema':{'slices':['month','country','gross_milli','credit_milli','orders','lines','positive_units'],
                        'productRows':['month','country','stock_code','net_milli','positive_units'],
                        'orders':['invoice','date','country','customer_pseudonym_or_null','gross_milli']}}
    compact_write(manifest_path,manifest)
    exports=ROOT/'data/warehouse/exports'; exports.mkdir(exist_ok=True)
    for table in ['dim_date','dim_product','dim_country','dim_customer','fact_line']:
        cursor=db.execute('SELECT * FROM '+table)
        with (exports/(table+'.csv')).open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.writer(f); writer.writerow([x[0] for x in cursor.description]);writer.writerows(cursor)
    db.close()
    print(json.dumps({'counts':dict(counts),'net_gbp':totals[0]/1000,'orders':len(orders),'source_sha256':digest},indent=2))

def archive_bytes(raw):
    with zipfile.ZipFile(raw) as archive:
        return archive.read(next(n for n in archive.namelist() if n.lower().endswith('.xlsx')))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true')
    build(parser.parse_args().refresh)
