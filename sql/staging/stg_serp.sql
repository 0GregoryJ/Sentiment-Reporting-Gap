CREATE OR REPLACE TABLE stg_serp AS
SELECT
    CAST(date AS DATE) AS date,
    CAST(category AS VARCHAR) AS category,
    CAST(query AS VARCHAR) AS query,
    CAST(value AS DOUBLE) AS value,
    'serp' AS source
FROM read_parquet('data/raw/serp_api/serp_raw.parquet')
WHERE value IS NOT NULL;