CREATE OR REPLACE TABLE stg_bls AS
SELECT
    CAST(date AS DATE) AS date,
    CAST(category AS VARCHAR) AS category,
    CAST(query AS VARCHAR) AS query,
    CAST(value AS DOUBLE) AS value,
    'bls' AS source
FROM read_parquet('data/raw/bls_api/bls_raw.parquet')
WHERE value IS NOT NULL;