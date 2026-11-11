PRAGMA journal_mode=WAL;
CREATE TABLE dim_date(date TEXT PRIMARY KEY, month TEXT NOT NULL);
CREATE TABLE dim_country(country TEXT PRIMARY KEY);
CREATE TABLE dim_product(stock_code TEXT PRIMARY KEY, description TEXT);
CREATE TABLE dim_customer(customer TEXT PRIMARY KEY);
CREATE TABLE fact_line(
 line_id INTEGER PRIMARY KEY, invoice TEXT NOT NULL,
 date TEXT REFERENCES dim_date(date), stock_code TEXT REFERENCES dim_product(stock_code),
 customer TEXT REFERENCES dim_customer(customer), country TEXT REFERENCES dim_country(country),
 quantity INTEGER NOT NULL, unit_milli INTEGER NOT NULL CHECK(unit_milli>0),
 amount_milli INTEGER NOT NULL, is_credit INTEGER CHECK(is_credit IN (0,1))
);
CREATE INDEX fact_date_country ON fact_line(date,country);
CREATE INDEX fact_customer ON fact_line(customer);
