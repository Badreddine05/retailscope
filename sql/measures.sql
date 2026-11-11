-- All stored monetary values are integer milli-GBP, not floating point pounds.
-- Filter both queries with the same date/country predicates when comparing them.
SELECT d.month, c.country,
 SUM(CASE WHEN f.is_credit=0 THEN f.amount_milli ELSE 0 END)/1000.0 AS gross_gbp,
 -SUM(CASE WHEN f.is_credit=1 THEN f.amount_milli ELSE 0 END)/1000.0 AS credits_gbp,
 SUM(f.amount_milli)/1000.0 AS net_gbp,
 COUNT(DISTINCT CASE WHEN f.is_credit=0 THEN f.invoice END) AS orders,
 SUM(CASE WHEN f.is_credit=0 THEN f.amount_milli ELSE 0 END)/1000.0 /
 NULLIF(COUNT(DISTINCT CASE WHEN f.is_credit=0 THEN f.invoice END),0) AS average_order_gbp
FROM fact_line f
JOIN dim_date d USING(date)
JOIN dim_country c USING(country)
GROUP BY d.month,c.country
ORDER BY d.month,c.country;

-- Reconciliation: sum of monthly net revenue must equal this result.
SELECT SUM(amount_milli) AS exact_net_milli, COUNT(*) AS accepted_rows FROM fact_line;

-- Referential integrity should yield no rows.
PRAGMA foreign_key_check;
