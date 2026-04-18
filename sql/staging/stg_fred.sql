CREATE OR REPLACE TABLE stg_fred AS
SELECT
    CAST(date AS DATE) AS date,
    CAST(category AS VARCHAR) AS category,
    CAST(query AS VARCHAR) AS query,
    CAST(value AS DOUBLE) AS value,
    'fred' AS source
FROM read_parquet('data/raw/fred_api/fred_raw.parquet')
WHERE value IS NOT NULL;