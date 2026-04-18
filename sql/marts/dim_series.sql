CREATE OR REPLACE TABLE dim_series AS
SELECT DISTINCT
    source,
    query,
    category
FROM (
    SELECT 'fred' AS source, query, category FROM stg_fred
    UNION
    SELECT 'bls' AS source, query, category FROM stg_bls
    UNION
    SELECT 'serp' AS source, query, category FROM stg_serp
)
ORDER BY source, query, category;