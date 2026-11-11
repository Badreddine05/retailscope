import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {selectData,toCsv} from '../src/analytics.js';
const data=JSON.parse(fs.readFileSync(new URL('../public/data/analytics.json',import.meta.url)));
const manifest=JSON.parse(fs.readFileSync(new URL('../public/data/manifest.json',import.meta.url)));
const all=selectData(data,{country:'All',start:'2010-12',end:'2011-12'});
test('source quality totals reconcile without silently dropped rows',()=>{
 assert.equal(manifest.counts.source_rows,541909);
 assert.equal(manifest.counts.source_rows,manifest.counts.accepted_rows+manifest.counts.duplicates_removed+manifest.counts.nonpositive_price);
 assert.equal(all.totals.lines,manifest.counts.accepted_rows);
});
test('net revenue reconciles warehouse, monthly slices and products to the milli-pound',()=>{
 assert.equal(all.totals.net,manifest.net_milli);
 assert.equal(all.series.reduce((s,r)=>s+r.net,0),all.totals.net);
 assert.equal(all.products.reduce((s,r)=>s+r.net,0),all.totals.net);
 assert.equal(all.countries.reduce((s,r)=>s+r.net,0),all.totals.net);
});
test('purchase invoice count and value reconcile independent exports',()=>{
 assert.equal(all.totals.orders,data.orders.length);
 assert.equal(data.orders.reduce((s,r)=>s+r[4],0),all.totals.gross);
 assert.equal(new Set(data.orders.map(r=>r[0])).size,all.totals.orders);
});
test('country and period filters apply equally to all business views',()=>{
 const s=selectData(data,{country:'France',start:'2011-02',end:'2011-05'});
 assert.equal(s.series.length,4);
 assert.equal(s.countries.length,1);
 assert.equal(s.countries[0].country,'France');
 assert.ok(s.filteredOrders.every(r=>r[2]==='France'&&r[1]>='2011-02-01'&&r[1]<'2011-06-01'));
 assert.equal(s.products.reduce((a,p)=>a+p.net,0),s.totals.net);
 assert.equal(s.filteredOrders.length,s.totals.orders);
 assert.equal(s.customers.length,new Set(s.filteredOrders.filter(o=>o[3]).map(o=>o[3])).size);
});
test('empty selections do not leak markets or invent ratios without denominator',()=>{
 const s=selectData(data,{country:'Not a market',start:'2011-01',end:'2011-03'});
 assert.equal(s.totals.net,0);assert.equal(s.totals.aov,null);assert.equal(s.totals.creditRate,null);
 assert.equal(s.products.length,0);assert.equal(s.customers.length,0);assert.equal(s.cohorts.length,0);
});
test('credit-only months preserve losses and have undefined sales ratios',()=>{
 const s=selectData(data,{country:'Saudi Arabia',start:'2011-03',end:'2011-03'});
 assert.equal(s.totals.net,-14750);assert.equal(s.totals.orders,0);
 assert.equal(s.totals.creditRate,null);assert.equal(s.totals.aov,null);
});
test('RFM segments are disjoint, exhaustive and do not contain anonymous buyers',()=>{
 assert.equal(all.segments.reduce((s,r)=>s+r.count,0),all.customers.length);
 assert.ok(all.customers.every(c=>c.id&&c.frequency>0&&c.recency>=1));
 assert.equal(all.identifiedOrders,all.customers.reduce((s,c)=>s+c.frequency,0));
 const c=all.customers.find(c=>c.segment==='Champions');assert.ok(c.frequency>=3&&c.recency<=60);
});
test('cohorts exclude partial December, encode censoring as null and preserve denominator',()=>{
 assert.equal(all.cohorts.length,12);
 assert.equal(all.cohorts.at(-1).month,'2011-11');
 for(const row of all.cohorts){assert.equal(row.retention[0],1);assert.ok(row.retention.every(v=>v===null||(v>=0&&v<=1)));}
 assert.equal(all.cohorts.at(-1).retention[1],null);
 const narrow=selectData(data,{country:'All',start:'2011-07',end:'2011-11'});
 assert.equal(narrow.cohorts[0].size,all.cohorts.find(r=>r.month==='2011-07').size);
});
test('CSV handles quotes, semicolons, newlines and spreadsheet formula injection',()=>{
 const csv=toCsv(['label','value'],[['a;"b\nc',12],['=SUM(A1:A2)','-123']]);
 assert.ok(csv.startsWith('\uFEFF'));assert.ok(csv.includes('"a;""b\nc"'));
 assert.ok(csv.includes('"\'=SUM(A1:A2)"'));assert.ok(csv.includes('"-123"'));
});
