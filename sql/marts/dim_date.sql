CREATE OR REPLACE TABLE dim_date AS
SELECT DISTINCT
    date,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    STRFTIME(date, '%Y-%m') AS year_month
FROM (
    SELECT date FROM stg_fred
    UNION
    SELECT date FROM stg_bls
    UNION
    SELECT date FROM stg_serp
)
ORDER BY date;