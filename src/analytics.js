export const monthLabel = (m, long=false) => new Intl.DateTimeFormat('fr-FR',{month:long?'long':'short',year:'2-digit',timeZone:'UTC'}).format(new Date(m+'-01T00:00:00Z'));
export const money = (n, compact=false) => new Intl.NumberFormat('fr-FR',{style:'currency',currency:'GBP',maximumFractionDigits:compact?1:0,notation:compact?'compact':'standard'}).format(n/1000);
export const number = n => new Intl.NumberFormat('fr-FR').format(n);
export const percent = n => new Intl.NumberFormat('fr-FR',{style:'percent',maximumFractionDigits:1}).format(n);
export function selectData(data,{country='All',start,end}) {
  const inCountry = c => country==='All'||c===country;
  const inPeriod = m => m>=start&&m<=end;
  const slices=data.slices.filter(r=>inCountry(r[1])&&inPeriod(r[0]));
  const totals=slices.reduce((a,r)=>({gross:a.gross+r[2],credit:a.credit+r[3],orders:a.orders+r[4],lines:a.lines+r[5],units:a.units+r[6]}),{gross:0,credit:0,orders:0,lines:0,units:0});
  totals.net=totals.gross-totals.credit;totals.aov=totals.orders?totals.gross/totals.orders:null;totals.creditRate=totals.gross?totals.credit/totals.gross:null;
  const series=data.months.filter(inPeriod).map(month=>{const rows=slices.filter(r=>r[0]===month);const gross=rows.reduce((s,r)=>s+r[2],0);const credit=rows.reduce((s,r)=>s+r[3],0);return {month,label:monthLabel(month),gross,credit,net:gross-credit,orders:rows.reduce((s,r)=>s+r[4],0)};});
  const cm=new Map();for(const r of slices){const x=cm.get(r[1])||{country:r[1],gross:0,net:0,orders:0};x.gross+=r[2];x.net+=r[2]-r[3];x.orders+=r[4];cm.set(r[1],x);}
  const countries=[...cm.values()].sort((a,b)=>b.net-a.net);
  const pm=new Map();for(const r of data.productRows){if(!inCountry(r[1])||!inPeriod(r[0]))continue;const p=pm.get(r[2])||{sku:r[2],name:data.products[r[2]],net:0,units:0};p.net+=r[3];p.units+=r[4];pm.set(r[2],p);}
  const products=[...pm.values()].sort((a,b)=>b.net-a.net);
  const filteredOrders=data.orders.filter(r=>inCountry(r[2])&&inPeriod(r[1].slice(0,7)));
  const snapshot=Math.min(Date.parse(end+'-01T00:00:00Z')+32*86400000,Date.parse('2011-12-10T00:00:00Z'));
  const endOfMonth=Date.UTC(Number(end.slice(0,4)),Number(end.slice(5,7)),1);
  const reference=Math.min(snapshot,endOfMonth);
  const clients=new Map();let identifiedOrders=0;
  for(const r of filteredOrders){if(!r[3])continue;identifiedOrders++;const c=clients.get(r[3])||{id:r[3],frequency:0,monetary:0,last:r[1]};c.frequency++;c.monetary+=r[4];if(r[1]>c.last)c.last=r[1];clients.set(r[3],c);}
  const monetary=[...clients.values()].map(c=>c.monetary).sort((a,b)=>a-b);
  const q75=monetary[Math.floor((monetary.length-1)*0.75)]||0;
  const customers=[...clients.values()].map(c=>{const recency=Math.floor((reference-Date.parse(c.last+'T00:00:00Z'))/86400000);const segment=recency>90?'À réactiver':recency<=60&&c.frequency>=3&&c.monetary>=q75?'Champions':c.frequency>=2?'Fidèles':recency<=30?'Nouveaux observés':'Occasionnels';return {...c,recency,segment};}).sort((a,b)=>b.monetary-a.monetary);
  const segments=['Champions','Fidèles','Nouveaux observés','Occasionnels','À réactiver'].map(name=>({name,count:customers.filter(c=>c.segment===name).length,monetary:customers.filter(c=>c.segment===name).reduce((s,c)=>s+c.monetary,0)}));
  // First purchase is inferred over the whole available history in the selected country.
  // Incomplete December 2011 is excluded; unobservable follow-up remains null, never zero.
  const history=new Map();const lastComplete=end<'2011-11'?end:'2011-11';
  for(const r of data.orders){const m=r[1].slice(0,7);if(!r[3]||!inCountry(r[2])||m>lastComplete)continue;const months=history.get(r[3])||new Set();months.add(m);history.set(r[3],months);}
  const cohortMap=new Map();for(const months of history.values()){const first=[...months].sort()[0];if(first<start||first>lastComplete)continue;const c=cohortMap.get(first)||{month:first,clients:[]};c.clients.push(months);cohortMap.set(first,c);}
  const monthIndex=m=>Number(m.slice(0,4))*12+Number(m.slice(5,7))-1;
  const cohorts=[...cohortMap.values()].sort((a,b)=>a.month.localeCompare(b.month)).map(c=>({month:c.month,size:c.clients.length,retention:Array.from({length:12},(_,age)=>{if(monthIndex(c.month)+age>monthIndex(lastComplete))return null;return c.clients.filter(months=>[...months].some(m=>monthIndex(m)-monthIndex(c.month)===age)).length/c.clients.length;})}));
  return {totals,series,countries,products,customers,segments,cohorts,identifiedOrders,filteredOrders};
}
export function csvEscape(value){const s=String(value??'');const numeric=/^-?\d+(\.\d+)?$/.test(s);const safe=!numeric&&/^[=+@\-\t\r]/.test(s)?"'"+s:s;return '"'+safe.replaceAll('"','""')+'"';}
export function toCsv(headers,rows){return '\uFEFF'+[headers,...rows].map(r=>r.map(csvEscape).join(';')).join('\r\n');}
